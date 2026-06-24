from flask import Flask, render_template, request, jsonify
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

app = Flask(__name__)

# ==========================================
# ☁️ [1단계] 구글 Firebase Firestore 클라우드 연결
# ==========================================
KEY_PATH = "firebase_key.json"

if os.path.exists(KEY_PATH):
    try:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("🚀 [SUCCESS] 구글 Firebase Firestore 클라우드가 정상 연결되었습니다!")
    except Exception as e:
        print(f"❌ [ERROR] Firebase 연결 오류: {e}")
        db = None
else:
    print(f"⚠ [WARNING] 최상위 폴더에 '{KEY_PATH}' 파일이 없습니다. DB 저장 기능 없이 시뮬레이션 모드로 작동합니다.")
    db = None


# ==========================================
# 🏛️ 웹 화면 라우팅
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')


# ==========================================
# ⚡ [2단계] 핵심 알고리즘 가동 API (비밀 보장 통계 연산)
# ==========================================
@app.route('/api/audit-dataset', methods=['POST'])
def audit_dataset():
    if 'file' not in request.files:
        return jsonify({'error': '업로드된 파일이 없습니다.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400

    try:
        # 1. 어떤 컬럼 구조든 다 읽어들이는 가변형 Pandas 데이터 수용
        df = pd.read_csv(file)
        total_rows = len(df)
        
        if total_rows == 0:
            return jsonify({'error': '데이터 행이 전혀 없는 빈 파일입니다.'}), 400

        # 데이터 전처리: 시스템 역추적을 차단하기 위해 식별자 컬럼(이름, ID 등)은 조합 연산에서 제외
        exclude_keywords = ['id', 'name', '이름', '번호', '주민', '전화', 'phone']
        calc_columns = [col for col in df.columns if not any(key in col.lower() for key in exclude_keywords)]
        
        # 만약 전부 제외되었을 경우 예외 방지용 전체 컬럼 복구
        if not calc_columns:
            calc_columns = list(df.columns)

        # 2. 🛡️ 1순위 심사: K-익명성(K=3) 전수조사 수식
        # 동일 조건의 행 패턴끼리 묶어서 카운트 계산
        group_counts = df.groupby(calc_columns).size().reset_index(name='count')
        
        # 동일 조합의 개수가 3개 이하(K <= 3)인 고유 식별 취약 행 필터링
        risk_groups = group_counts[group_counts['count'] <= 3]
        risk_rows_count = int(risk_groups['count'].sum())
        
        # 통계적 재식별 위험도 비율 산정 (%)
        risk_ratio = round((risk_rows_count / total_rows) * 100, 1)

        # 3. 📉 2순위 심사: 데이터 희소성(결측치율) 분석
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)

        # 4. 🏆 엄격한 우선순위 기준 등급(Grade) 매기기
        # 1순위 조건(위험도)과 2순위 조건(결측률) 결합 평가
        if risk_ratio == 0.0 and null_ratio < 5.0:
            grade = 'S'
        elif risk_ratio <= 5.0 and null_ratio < 10.0:
            grade = 'A'
        elif risk_ratio <= 20.0:
            grade = 'B'
        else:
            grade = 'C'

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 5. ☁️ 외부 노출 없이 안전하게 Firebase DB에 심사 통계 결과만 아카이빙
        audit_report = {
            'filename': file.filename,
            'audit_time': current_time,
            'total_rows': total_rows,
            'risk_ratio': risk_ratio,
            'null_ratio': null_ratio,
            'grade': grade
        }

        if db:
            try:
                # Firestore 내 'security_audits' 컬렉션에 실시간 기록 적재
                db.collection('security_audits').add(audit_report)
                print(f"☁️ [FIREBASE] '{file.filename}' 심사 통계 클라우드 영속 보관 완료!")
            except Exception as firebase_err:
                print(f"❌ [FIREBASE ERROR] DB 전송 중 에러: {firebase_err}")

        # 프론트엔드로는 프라이버시가 엄격히 보장된 통계 결과만 리턴
        return jsonify(audit_report)

    except Exception as e:
        return jsonify({'error': f'파일 분석 과정 중 에러가 발생했습니다: {str(e)}'}), 500


if __name__ == '__main__':
    # 5000번 포트로 플라스크 데몬 가동
    app.run(debug=True, port=5000)