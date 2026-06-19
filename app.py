from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
# data.py 파일로부터 가명 처리된 유동인구 데이터셋(telecom_data)을 가져옵니다.
from data import telecom_data

# Flask 애플리케이션 초기화
app = Flask(__name__)

# [보안/통신 설정] 프론트엔드(HTML)와 백엔드(Flask) 간의 포트가 다를 때 발생하는
# CORS(Cross-Origin Resource Sharing) 에러를 방지하기 위해 설정합니다.
CORS(app)


# ------------------------------------------------------------------
# 기능 1: 메인 페이지 라우팅 (대문 열어주기)
# ------------------------------------------------------------------
@app.route('/')
def home():
    """
    사용자가 브라우저 주소창에 'http://127.0.0.1:5000/'을 입력하면,
    templates 폴더 안의 'index.html' 파일을 읽어서 화면에 렌더링(출력)합니다.
    """
    return render_template('index.html')


# ------------------------------------------------------------------
# 기능 2: K-익명성 기반 재식별 위험성 검증 API 엔드포인트
# ------------------------------------------------------------------
@app.route('/api/check-security', methods=['POST'])
def check_security():
    """
    프론트엔드가 보낸 4가지 검색 조건(행정동, 시간대, 연령대, 성별)을 분석하여
    K-익명성 가이드라인(K=3)에 맞춰 가명 데이터의 반출 승인 여부를 심사합니다.
    """
    # 1. 프론트엔드가 HTTP Body에 실어 보낸 JSON 데이터를 파이썬 딕셔너리로 수신합니다.
    request_data = request.get_json()
    
    # 2. 사용자가 화면에서 최종 선택한 4가지 다차원 속성(준식별자) 값을 추출합니다.
    selected_region = request_data.get('region')
    selected_time_slot = request_data.get('timeSlot')
    selected_age_group = request_data.get('ageGroup')
    selected_gender = request_data.get('gender')
    
    # 3. 데이터 필터링: 전체 데이터셋에서 사용자가 고른 조건과 '모두 일치'하는 표본을 탐색합니다.
    filtered_rows = []
    for row in telecom_data:
        if (row['region'] == selected_region and
            row['timeSlot'] == selected_time_slot and
            row['ageGroup'] == selected_age_group and
            row['gender'] == selected_gender):
            filtered_rows.append(row)
            
    # 4. 필터링된 동질 집합(Equivalence Class)의 레코드 개수(표본 수)를 파악합니다.
    match_count = len(filtered_rows)
    
    # 5. K-익명성(K=3) 프라이버시 보호 모델 검증 및 조건 분기
    
    # [CASE 1] 매칭되는 표본 데이터가 전혀 없는 경우 (0건)
    if match_count == 0:
        return jsonify({
            "status": "no_data",
            "message": "조건에 매칭되는 유동인구 데이터가 존재하지 않습니다."
        })
        
    # [CASE 2] 데이터가 존재하나 3건 이하인 경우 (K-익명성 미달로 인한 재식별 위험군)
    elif 1 <= match_count <= 3:
        return jsonify({
            "status": "blocked",
            "message": f"조회된 데이터가 {match_count}건 이하입니다. 타 정보와의 결합을 통한 개인 재식별 위험성이 존재하므로 데이터 반출이 원천 차단됩니다."
        })
        
    # [CASE 3] 동질 집합의 크기가 4건 이상으로 개인을 식별하기 어려운 안전한 상태 (반출 승인)
    else:
        return jsonify({
            "status": "success",
            "count": match_count,
            "rows": filtered_rows
        })


# 백엔드 서버 기동 설정
if __name__ == '__main__':
    # 127.0.0.1(로컬 호스트)의 5000번 포트에서 웹 서버를 상시 가동합니다.
    # debug=True 설정을 통해 코드를 수정하고 저장하면 서버가 자동으로 리로드됩니다.
    app.run(host='127.0.0.1', port=5000, debug=True)