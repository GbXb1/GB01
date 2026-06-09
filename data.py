# 📡 재식별 방지 시스템용 가명 유동인구 데이터셋 (총 82건)
# 개인정보 가이드라인(K-익명성, K=3) 검증을 위한 시나리오 기반 맞춤형 데이터

telecom_data = [
    # ======================================================================
    # 🚨 [불가능 경우 1] 행복동 / 새벽 시간대 / 10대 / 여자 -> 딱 1건 존재 (원천 차단 대상)
    # ======================================================================
    {"user_id": "M_ID_0001", "region": "행복동", "timeSlot": "새벽 시간대 (04:00~06:00)", "ageGroup": "10대", "gender": "여자"},

    # ======================================================================
    # 🚨 [불가능 경우 2] 우정동 / 심야 시간대 / 60대 이상 / 남자 -> 딱 2건 존재 (원천 차단 대상)
    # ======================================================================
    {"user_id": "M_ID_0002", "region": "우정동", "timeSlot": "심야 시간대 (00:00~04:00)", "ageGroup": "60대 이상", "gender": "남자"},
    {"user_id": "M_ID_0003", "region": "우정동", "timeSlot": "심야 시간대 (00:00~04:00)", "ageGroup": "60대 이상", "gender": "남자"},

    # ======================================================================
    # 🚨 [불가능 경우 3] 기쁨동 / 점심 시간대 / 4-50대 / 여자 -> 딱 3건 존재 (K=3 경계선 원천 차단 대상)
    # ======================================================================
    {"user_id": "M_ID_0004", "region": "기쁨동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "4-50대", "gender": "여자"},
    {"user_id": "M_ID_0005", "region": "기쁨동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "4-50대", "gender": "여자"},
    {"user_id": "M_ID_0006", "region": "기쁨동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "4-50대", "gender": "여자"},

    # ======================================================================
    # ✅ [성공 시연 구역 1] 소망동 / 출근 시간대 / 30대 / 남자 -> 총 12건 (반출 승인 및 대량 출력)
    # ======================================================================
    {"user_id": "M_ID_1001", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1002", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1003", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1004", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1005", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1006", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1007", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1008", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1009", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1010", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1011", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_1012", "region": "소망동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},

    # ======================================================================
    # ✅ [성공 시연 구역 2] 행운동 / 퇴근 시간대 / 20대 / 여자 -> 총 15건 (반출 승인 및 대량 출력)
    # ======================================================================
    {"user_id": "M_ID_2001", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2002", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2003", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2004", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2005", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2006", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2007", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2008", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2009", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2010", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2011", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2012", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2013", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2014", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_2015", "region": "행운동", "timeSlot": "퇴근 시간대 (17:00~19:00)", "ageGroup": "20대", "gender": "여자"},

    # ======================================================================
    # 👥 [백그라운드 채우기용] 시스템 볼륨감을 위한 무작위 분배 데이터 (총 52건)
    # ======================================================================
    {"user_id": "M_ID_5001", "region": "사랑동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_5002", "region": "사랑동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_5003", "region": "사랑동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_5004", "region": "사랑동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_5005", "region": "사랑동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "4-50대", "gender": "남자"},
    
    {"user_id": "M_ID_5006", "region": "희망동", "timeSlot": "밤 시간대 (19:00~24:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_5007", "region": "희망동", "timeSlot": "밤 시간대 (19:00~24:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_5008", "region": "희망동", "timeSlot": "밤 시간대 (19:00~24:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_5009", "region": "희망동", "timeSlot": "밤 시간대 (19:00~24:00)", "ageGroup": "20대", "gender": "여자"},
    
    {"user_id": "M_ID_5010", "region": "행복동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "30대", "gender": "여자"},
    {"user_id": "M_ID_5011", "region": "행복동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "30대", "gender": "여자"},
    {"user_id": "M_ID_5012", "region": "행복동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "30대", "gender": "여자"},
    {"user_id": "M_ID_5013", "region": "행복동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "30대", "gender": "여자"},
    {"user_id": "M_ID_5014", "region": "행복동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "30대", "gender": "여자"},

    {"user_id": "M_ID_5015", "region": "소망동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "20대", "gender": "남자"},
    {"user_id": "M_ID_5016", "region": "소망동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "20대", "gender": "남자"},
    {"user_id": "M_ID_5017", "region": "소망동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "20대", "gender": "남자"},
    {"user_id": "M_ID_5018", "region": "소망동", "timeSlot": "점심 시간대 (12:00~14:00)", "ageGroup": "20대", "gender": "남자"},

    # (아래 데이터는 시스템 내부 카운팅용 랜덤 성비/연령 분배 데이터들입니다)
    {"user_id": "M_ID_6001", "region": "행운동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_6002", "region": "행운동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_6003", "region": "행운동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_6004", "region": "행운동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "4-50대", "gender": "남자"},
    {"user_id": "M_ID_6005", "region": "행운동", "timeSlot": "낮 시간대 (10:00~12:00)", "ageGroup": "4-50대", "gender": "남자"},
    
    {"user_id": "M_ID_7001", "region": "기쁨동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_7002", "region": "기쁨동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_7003", "region": "기쁨동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_7004", "region": "기쁨동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "20대", "gender": "여자"},
    {"user_id": "M_ID_7005", "region": "기쁨동", "timeSlot": "오후 시간대 (14:00~17:00)", "ageGroup": "20대", "gender": "여자"},
    
    {"user_id": "M_ID_8001", "region": "우정동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_8002", "region": "우정동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_8003", "region": "우정동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_8004", "region": "우정동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"},
    {"user_id": "M_ID_8005", "region": "우정동", "timeSlot": "출근 시간대 (7:00~10:00)", "ageGroup": "30대", "gender": "남자"}
]