from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/audit-dataset', methods=['POST'])
def audit_dataset():
    if 'file' not in request.files:
        return jsonify({'error': '업로드된 파일이 없습니다.'}), 400
        
    file = request.files['file']
    k_value = 3

    try:
        # 1. 스마트 인코딩 리더 (한글 깨짐 완전 방지)
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

        # ⭐ [수정 핵심] 필터링 없이 엑셀에 있는 모든 컬럼을 정직하게 검사합니다.
        calc_columns = list(df.columns)

        # 2. 🛡️ K-익명성 검사 (K=3 기준)
        group_counts = df.groupby(calc_columns).size().reset_index(name='count')
        risk_groups = group_counts[group_counts['count'] <= k_value]
        risk_rows_count = int(risk_groups['count'].sum())
        risk_ratio = round((risk_rows_count / total_rows) * 100, 1)

        # 3. 📉 결측치율 계산
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)

        # 4. 🏆 완화된 실무형 등급 수식
        if risk_ratio <= 5.0 and null_ratio < 5.0:
            grade = 'S'
        elif risk_ratio <= 25.0 and null_ratio < 10.0:
            grade = 'A'
        elif risk_ratio <= 55.0:
            grade = 'B'
        else:
            grade = 'C'

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify({
            'filename': file.filename,
            'audit_time': current_time,
            'total_rows': total_rows,
            'risk_ratio': risk_ratio,
            'null_ratio': null_ratio,
            'grade': grade,
            'applied_k': k_value
        })

    except Exception as e:
        return jsonify({'error': f'파일 분석 에러: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)