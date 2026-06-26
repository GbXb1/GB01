from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import uuid

# [추가된 기능] 파이어베이스 라이브러리 연동
import firebase_admin
from firebase_admin import credentials, firestore

# 파이어베이스 초기화 (서버 재시작 시 중복 방지)
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase_key.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"🔥 Firebase 연결 에러: {e}")
    db = None

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/audit-dataset', methods=['POST'])
def audit_dataset():
    if 'file' not in request.files:
        return jsonify({'error': '업로드된 파일이 없습니다.'}), 400
        
    file = request.files['file']
    
    # [추가된 기능] 프론트엔드 체크리스트 값 받아오기
    has_personal_info = request.form.get('has_personal_info') == 'true'
    data_type = request.form.get('data_type')

    try:
        # 기존 훌륭한 인코딩 방어 로직 유지
        try:
            df = pd.read_csv(file)
        except:
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='cp949')
            except:
                file.seek(0)
                df = pd.read_csv(file, encoding='euc-kr')
        
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        total_rows = len(df)
        if total_rows == 0:
            return jsonify({'error': '데이터셋에 행이 존재하지 않습니다.'}), 400

        # ==========================================
        # 🛡️ 1순위: K-익명성(K=3) 위험도 (체크리스트 연동)
        # ==========================================
        if has_personal_info:
            group_counts = df.groupby(list(df.columns)).size().reset_index(name='count')
            risk_groups = group_counts[group_counts['count'] < 3]
            risk_rows_count = int(risk_groups['count'].sum())
            risk_ratio = round((risk_rows_count / total_rows) * 100, 1)
        else:
            # 환경/통계 데이터 등 개인정보가 없다고 체크된 경우 위험도 0%로 패스
            risk_ratio = 0.0 

        # ==========================================
        # 📉 2순위: 데이터 결측치율(완결성) 계산
        # ==========================================
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)
        
        # (기타 누락되었던 편향성, 유효성 등은 백엔드 확장을 위해 자리는 비워두고, 
        # 우선 기존에 짜신 완화된 등급 룰북을 그대로 반영합니다.)

        # ==========================================
        # 🏆 기존 완화된 실무형 등급 산출
        # ==========================================
        if risk_ratio <= 5.0 and null_ratio < 5.0:
            grade = 'S'
        elif risk_ratio <= 25.0 and null_ratio < 10.0:
            grade = 'A'
        elif risk_ratio <= 55.0:
            grade = 'B'
        else:
            grade = 'C'

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ==========================================
        # 💾 [추가된 기능] 파이어베이스 Firestore DB 저장 로직
        # ==========================================
        saved_to_db = False
        if db is not None:
            doc_id = f"eval_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
            eval_data = {
                "document_id": doc_id,
                "meta_info": {
                    "file_name": file.filename,
                    "uploaded_at": current_time,
                    "checklist": {
                        "has_personal_info": has_personal_info,
                        "data_type": data_type
                    }
                },
                "results": {
                    "risk_ratio_percent": risk_ratio,
                    "null_ratio_percent": null_ratio,
                    "final_grade": grade
                }
            }
            db.collection("evaluations").document(doc_id).set(eval_data)
            saved_to_db = True

        return jsonify({
            'filename': file.filename,
            'audit_time': current_time,
            'total_rows': total_rows,
            'risk_ratio': risk_ratio,
            'null_ratio': null_ratio,
            'grade': grade,
            'applied_k': 3,
            'saved_to_db': saved_to_db  # DB 저장 성공 여부를 프론트로 전달
        })

    except Exception as e:
        return jsonify({'error': f'파일 연산 중 에러 발생: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)