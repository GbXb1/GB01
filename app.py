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
    # 총괄님 지시대로 K값은 실무 표준인 3으로 완전 고정
    k_value = 3

    try:
        # 스마트 인코딩 리더 (공공기관 파일 한글 깨짐 방지 완벽 자동 대응)
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

        # 식별자(ID, 이름 등) 자동 필터링
        exclude_keywords = ['id', 'name', '이름', '번호', '주민', '전화', 'phone', '순번']
        calc_columns = [col for col in df.columns if not any(key in col.lower() for key in exclude_keywords)]
        if not calc_columns:
            calc_columns = list(df.columns)

        # 🛡️ 1순위 심사: K-익명성 계산 (K=3 기준)
        group_counts = df.groupby(calc_columns).size().reset_index(name='count')
        risk_groups = group_counts[group_counts['count'] <= k_value]
        risk_rows_count = int(risk_groups['count'].sum())
        risk_ratio = round((risk_rows_count / total_rows) * 100, 1)

        # 📉 2순위 심사: 결측치율 계산
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)

        # 🏆 완화된 실무형 등급 커트라인 수식 (공공데이터 통과 구간 제공)
        if risk_ratio <= 5.0 and null_ratio < 5.0:
            grade = 'S'
        elif risk_ratio <= 25.0 and null_ratio < 10.0:
            grade = 'A'  # 위험도가 25%까지 나와도 무난하게 실무 통과(A등급)
        elif risk_ratio <= 55.0:
            grade = 'B'
        else:
            grade = 'C'

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 외부 클라우드 통신을 완전히 도려내어 구글 403 에러 차단 및 로컬 즉시 반환
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