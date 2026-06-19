from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
# data.py 파일에서 가명 처리된 유동인구 데이터셋(telecom_data)을 가져옵니다.
from data import telecom_data

app = Flask(__name__)

# 프론트엔드(HTML)와 백엔드(Flask) 간의 포트(Port)가 다를 때 발생하는
# CORS(Cross-Origin Resource Sharing) 에러를 방지하기 위해 설정합니다.
CORS(app)


# 1. 메인 페이지 라우터
@app.route('/')
def home():
    # templates 폴더 안에 있는 index.html 파일을 웹 브라우저에 띄워줍니다.
    return render_template('index.html')


# 2. 재식별 위험성 검증 및 가명 데이터 반출 심사 API 엔드포인트
@app.route('/api/check-security', methods=['POST'])
def check_security():
    # 프론트엔드가 보낸 JSON 데이터를 파이썬 딕셔너리 형태로 받아옵니다.
    request_data = request.get_json()
    
    # 사용자가 선택한 4가지 조건(행정동, 시간대, 연령대, 성별)을 추출합니다.
    selected_region = request_data.get('region')
    selected_time_slot = request_data.get('timeSlot')
    selected_age_group = request_data.get('ageGroup')
    selected_gender = request_data.get('gender')
    
    # [데이터 필터링 로직] 
    # 전체 데이터(telecom_data) 중에서 사용자가 고른 4가지 조건과 '모두 일치'하는 데이터만 골라냅니다.
    filtered_rows = []
    for row in telecom_data:
        if (row['region'] == selected_region and
            row['timeSlot'] == reversed_time_slot_matching(selected_time_slot) and
            row['ageGroup'] == selected_age_group and
            row['gender'] == selected_gender):
            filtered_rows.append(row)
            
    # 조건문 단순화를 위해 리스트 컴프리헨션을 적용해도 좋지만, 고등학생 수준에서 이해하기 쉽게 풀어서 작성했습니다.
    # (참고: data.py의 키값과 index.html의 변수명이 완벽히 일치하므로 바로 비교가 가능합니다.)
    filtered_rows = [
        row for row in telecom_data
        if row['region'] == selected_region and
           row['timeSlot'] == selected_time_slot and
           row['ageGroup'] == selected_age_group and
           row['gender'] == selected_gender
    ]
    
    # 필터링된 데이터의 개수(표본 수)를 파악합니다.
    match_count = len(filtered_rows)
    
    # ------------------------------------------------------------------
    # [K-익명성 검증 및 응답 조건 분기]
    # ------------------------------------------------------------------
    
    # [CASE 1] 조건에 맞는 데이터가 아예 없는 경우 (0건)
    if match_count == 0:
        return jsonify({
            "status": "no_data",
            "message": "조건에 매칭되는 유동인구 데이터가 존재하지 않습니다."
        })
        
    # [CASE 2] 데이터가 존재하지만 3건 이하인 경우 (K-익명성 미달 -> 재식별 위험 차단)
    elif 1 <= match_count <= 3:
        return jsonify({
            "status": "blocked",
            "message": f"조회된 데이터가 {match_count}건 이하입니다. 타 정보(결합키 등)와의 결합을 통한 개인 재식별 위험성이 존재하므로 데이터 반출이 원천 차단됩니다."
        })
        
    # [CASE 3] 데이터가 4건 이상으로 충분히 안전한 경우 (반출 성공)
    else:
        return jsonify({
            "status": "success",
            "count": match_count,
            "rows": filtered_rows
        })


if __name__ == '__main__':
    # 로컬 호스트의 5000번 포트에서 서버를 실행합니다.
    # debug=True 설정을 통해 코드를 수정하면 서버가 알아서 재시작되도록 합니다.
    app.run(host='127.0.0.1', port=5000, debug=True)