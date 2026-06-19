from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from data import telecom_data  # 우리가 만든 가짜 데이터셋(data.py) 불러오기

# Flask 서버 앱 생성 및 CORS(통신 오류 방지) 설정
app = Flask(__name__)
CORS(app)

# 🌐 기본 라우터: 'http://127.0.0.1:5000/' 접속 시 index.html 화면 띄우기
@app.route('/')
def index():
    return render_template('index.html')

# 📡 API 라우터: 프론트엔드가 승인 요청을 보내면 심사하는 곳
@app.route('/api/check-security', methods=['POST'])
def check_security():
    
    # 1. 프론트엔드(화면)에서 사용자가 고른 4가지 조건 꺼내기
    req_data = request.get_json()
    target_region = req_data.get('region')
    target_timeSlot = req_data.get('timeSlot')
    target_ageGroup = req_data.get('ageGroup')
    target_gender = req_data.get('gender')

    # 2. 데이터 필터링 (조건 4개가 완벽히 일치하는 사람만 골라내기)
    matched_data = []
    for person in telecom_data:
        if (person['region'] == target_region and 
            person['timeSlot'] == target_timeSlot and 
            person['ageGroup'] == target_ageGroup and 
            person['gender'] == target_gender):
            
            # 조건이 맞으면 바구니에 담기
            matched_data.append(person)
            
    # 바구니에 담긴 사람 수 세기
    count = len(matched_data)

    # 3. K-익명성(K=3) 가이드라인에 따른 결과 판별 및 응답 보내기
    if count == 0:
        # [CASE 1] 데이터가 0건일 때 ➡️ 주의 안내
        return jsonify({
            "status": "no_data",
            "message": "조건에 매칭되는 유동인구 데이터가 존재하지 않습니다."
        })
        
    elif 1 <= count <= 3:
        # [CASE 2] 데이터가 3건 이하일 때 (위험) ➡️ 원천 차단 조치
        return jsonify({
            "status": "blocked",
            "message": "조회된 데이터가 3건 이하입니다. 타 정보와의 결합을 통한 개인 재식별 위험성이 존재하므로 데이터 반출이 원천 차단됩니다."
        })
        
    else:
        # [CASE 3] 데이터가 4건 이상일 때 (안전) ➡️ 데이터 반출 승인
        return jsonify({
            "status": "success",
            "count": count,
            "rows": matched_data
        })

# 파이썬 파일 실행 시 서버 기동
if __name__ == '__main__':
    # debug=True 로 설정하면 코드를 수정할 때마다 서버가 자동으로 재시작됩니다.
    app.run(debug=True)