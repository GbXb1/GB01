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

    try:
        # 1. 인코딩 에러 및 공백 문제를 완전 방어하며 CSV 로드
        try:
            df = pd.read_csv(file)
        except:
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='cp949')
            except:
                file.seek(0)
                df = pd.read_csv(file, encoding='euc-kr')
        
        # 컬럼명과 문자열 데이터의 앞뒤 불필요한 공백 제거 (엑셀 변환 시 발생 방지)
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        total_rows = len(df)
        if total_rows == 0:
            return jsonify({'error': '데이터셋에 행이 존재하지 않습니다.'}), 400

        # 2. 🛡️ 진짜 K-익명성(K=3) 위험도 계산
        # 모든 컬럼의 조합을 기준으로 중복된 행의 개수를 세어 줍니다.
        group_counts = df.groupby(list(df.columns)).size().reset_index(name='count')
        
        # 동일한 특성을 가진 사람이 3명 미만(1명 또는 2명)인 그룹이 바로 '위험군'입니다.
        risk_groups = group_counts[group_counts['count'] < 3]
        risk_rows_count = int(risk_groups['count'].sum())
        
        # 위험도 백분율 계산
        risk_ratio = round((risk_rows_count / total_rows) * 100, 1)

        # 3. 📉 데이터 결측치율(Null) 계산
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)

        # 4. 🏆 완화된 실무형 등급 커트라인 수식 그대로 적용
        # S 등급: 위험도 5% 이하, 결측치 5% 미만
        if risk_ratio <= 5.0 and null_ratio < 5.0:
            grade = 'S'
        # A 등급: 위험도 25% 이하, 결측치 10% 미만
        elif risk_ratio <= 25.0 and null_ratio < 10.0:
            grade = 'A'
        # B 등급: 위험도 55% 이하
        elif risk_ratio <= 55.0:
            grade = 'B'
        # C 등급: 위험도 55% 초과 (배포 거부)
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
            'applied_k': 3
        })

    except Exception as e:
        return jsonify({'error': f'파일 연산 중 진짜 에러 발생: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)