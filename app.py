from flask import Flask, render_template, request, jsonify
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

app = Flask(__name__)

# 구글 Firebase 연결
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
    print(f"⚠ [WARNING] 시뮬레이션 모드로 작동합니다.")
    db = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/audit-dataset', methods=['POST'])
def audit_dataset():
    if 'file' not in request.files:
        return jsonify({'error': '업로드된 파일이 없습니다.'}), 400
        
    file = request.files['file']
    # 프론트엔드에서 넘겨준 K값 수존 (기본값 3)
    k_value = int(request.form.get('k_value', 3))

    try:
        # 스마트 인코딩 리더 (한글 깨짐 방지)
        try:
            df = pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='cp949')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='euc-kr')
                
        total_rows = len(df)
        if total_rows == 0:
            return jsonify({'error': '데이터 행이 없습니다.'}), 400

        # 식별자 제외
        exclude_keywords = ['id', 'name', '이름', '번호', '주민', '전화', 'phone', '순번']
        calc_columns = [col for col in df.columns if not any(key in col.lower() for key in exclude_keywords)]
        if not calc_columns:
            calc_columns = list(df.columns)

        # 🛡️ 1순위 심사: 가변형 K-익명성 전수조사 (전송받은 k_value 적용)
        group_counts = df.groupby(calc_columns).size().reset_index(name='count')
        
        # 설정된 K값 이하인 경우를 위험군으로 감지
        risk_groups = group_counts[group_counts['count'] <= k_value]
        risk_rows_count = int(risk_groups['count'].sum())
        risk_ratio = round((risk_rows_count / total_rows) * 100, 1)

        # 📉 2순위 심사: 결측치율
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)

        # 🏆 [총괄님 지시 반영] 대폭 완화된 실무형 등급 커트라인 수식
        if risk_ratio <= 5.0 and null_ratio < 5.0:
            grade = 'S'  # 위험도 5% 미만이면 최상급 인정
        elif risk_ratio <= 25.0 and null_ratio < 10.0:
            grade = 'A'  # 위험도가 25%까지 포함되어도 실무 배포 가능 등급 부여 (공공데이터 통과 구간)
        elif risk_ratio <= 55.0:
            grade = 'B'  # 절반 수준까지는 조건부 허용
        else:
            grade = 'C'  # 거부

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audit_report = {
            'filename': file.filename,
            'audit_time': current_time,
            'total_rows': total_rows,
            'risk_ratio': risk_ratio,
            'null_ratio': null_ratio,
            'grade': grade,
            'applied_k': k_value
        }

        if db:
            db.collection('security_audits').add(audit_report)

        return jsonify(audit_report)

    except Exception as e:
        return jsonify({'error': f'파일 분석 에러: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)