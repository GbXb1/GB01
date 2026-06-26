<<<<<<< HEAD
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
    has_pii = request.form.get('has_pii', 'no') # 프론트엔드 선택창 값 수신

    try:
        # 인코딩 방어 적용하며 CSV 로드
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

        # -------------------------------------------------------------
        # 📊 [진짜 연산] 6대 데이터 보안 심사 기준 알고리즘
        # -------------------------------------------------------------
        
        # [기준 1] K-익명성 위험도 (K=3)
        group_counts = df.groupby(list(df.columns)).size().reset_index(name='count')
        risk_groups = group_counts[group_counts['count'] < 3]
        risk_rows_count = int(risk_groups['count'].sum())
        risk_ratio = round((risk_rows_count / total_rows) * 100, 1)

        # [기준 2] 데이터 결측치율
        total_cells = df.size
        null_cells = int(df.isnull().sum().sum())
        null_ratio = round((null_cells / total_cells) * 100, 1)

        # [기준 3] 고유식별정보(PII) 컬럼 검출율
        pii_keywords = ['주민', '전화', '이름', '성명', '폰', '이메일', '주소', 'id', 'sn', 'email', 'phone', 'address']
        pii_cols = [col for col in df.columns if any(kw in col.lower() for kw in pii_keywords)]
        pii_ratio = round((len(pii_cols) / len(df.columns)) * 100, 1) if len(df.columns) > 0 else 0

        # [기준 4] 데이터 통계적 이상치(Outlier) 비율 (IQR 방식)
        num_cols = df.select_dtypes(include=['number']).columns
        total_outliers = 0
        total_numeric_elements = 0
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
            total_outliers += len(outliers)
            total_numeric_elements += len(df)
        outlier_ratio = round((total_outliers / total_numeric_elements) * 100, 1) if total_numeric_elements > 0 else 0

        # [기준 5] 준식별자 결합 및 재식별 고유성 위험도
        unique_combos = len(df.drop_duplicates())
        combo_ratio = round((unique_combos / total_rows) * 100, 1)

        # [기준 6] 데이터 표본 규모 적정성 (행 수 계산)
        # (행 수가 너무 적으면 통계적 추론 및 재식별 위험이 매우 높음)

        # -------------------------------------------------------------
        # 🏆 6대 항목별 개별 등급 판정 로직
        # -------------------------------------------------------------
        # 1. K-익명성 등급
        risk_grade = 'S' if risk_ratio <= 5.0 else 'A' if risk_ratio <= 25.0 else 'B' if risk_ratio <= 55.0 else 'C'
        # 2. 결측치율 등급
        null_grade = 'S' if null_ratio < 5.0 else 'A' if null_ratio < 10.0 else 'B' if null_ratio < 20.0 else 'C'
        # 3. 개인정보 매칭 무결성 등급 (선택창 검증)
        if has_pii == 'no' and pii_ratio > 0: pii_grade = 'C' # 없다고 했는데 발견됨 (감점)
        elif has_pii == 'yes' and pii_ratio > 30.0: pii_grade = 'B' # 너무 날것의 개인정보가 많음
        else: pii_grade = 'S'
        # 4. 이상치 등급
        outlier_grade = 'S' if outlier_ratio <= 3.0 else 'A' if outlier_ratio <= 8.0 else 'B' if outlier_ratio <= 15.0 else 'C'
        # 5. 결합 위험도 등급
        linkage_grade = 'S' if combo_ratio <= 20.0 else 'A' if combo_ratio <= 50.0 else 'B' if combo_ratio <= 80.0 else 'C'
        # 6. 규모 적정성 등급
        row_grade = 'S' if total_rows >= 1000 else 'A' if total_rows >= 300 else 'B' if total_rows >= 50 else 'C'

        # ⚖️ 종합 점수 산출 (과목별 가중치 평균)
        score_map = {'S': 4, 'A': 3, 'B': 2, 'C': 1}
        total_score = (score_map[risk_grade]*2.5 + score_map[null_grade]*1.5 + score_map[pii_grade]*2.0 + score_map[outlier_grade] + score_map[linkage_grade]*1.5 + score_map[row_grade]) / 9.5
        
        grade = 'S' if total_score >= 3.5 else 'A' if total_score >= 2.8 else 'B' if total_score >= 1.8 else 'C'
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify({
            'filename': file.filename,
            'audit_time': current_time,
            'grade': grade,
            # 6대 세부 심사 결과 데이터 송신
            'risk_ratio': risk_ratio, 'risk_grade': risk_grade,
            'null_ratio': null_ratio, 'null_grade': null_grade,
            'pii_ratio': pii_ratio, 'pii_grade': pii_grade,
            'outlier_ratio': outlier_ratio, 'outlier_grade': outlier_grade,
            'combo_ratio': combo_ratio, 'linkage_grade': linkage_grade,
            'total_rows': total_rows, 'row_grade': row_grade
        })

    except Exception as e:
        return jsonify({'error': f'분석 중 에러 발생: {str(e)}'}), 500

if __name__ == '__main__':
=======
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
>>>>>>> 82beec7c21ba5b65ebe07bbd286d4457b1a5b22c
    app.run(debug=True, port=5001)