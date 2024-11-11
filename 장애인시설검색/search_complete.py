import subprocess
import json
import streamlit as st
import requests
import pandas as pd

# API URL 설정
base_url = 'https://api.odcloud.kr/api/15071029/v1/uddi:7c6a4eaa-179a-469e-bb19-cd39e221190c'
service_key = 'BQBdGk7ivmswO2MVuwRXPForbZ%2F3vUjq1QgzyqK7exzFmS5F54XRmmrvGv6v8TXIcWT8lMVYbtkt%2Bl4YOHeEDg%3D%3D'

all_data = []  # 모든 데이터를 저장할 리스트

# 페이지를 반복하여 호출
page = 1
while True:
    url = f"{base_url}?page={page}&perPage=73&serviceKey={service_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        all_data.extend(data['data'])  # 데이터를 리스트에 추가
        if len(data['data']) < 73:  # 데이터가 더 이상 없으면 종료
            break
        page += 1  # 다음 페이지로 이동
    else:
        st.error(f"API 호출 실패: {response.status_code}")
        break

# 시_도 이름 정규화 함수 (API에 있는 시_도 기반)
def normalize_city_name(city_name):
    city_name = city_name.replace(" ", "")  # 공백 제거
    if "서울" in city_name:
        return "서울"
    elif "부산" in city_name:
        return "부산"
    elif "대구" in city_name:
        return "대구"
    elif "인천" in city_name:
        return "인천"
    elif "광주" in city_name:
        return "광주"
    elif "대전" in city_name:
        return "대전"
    elif "울산" in city_name:
        return "울산"
    elif "세종" in city_name:
        return "세종"
    elif "경기" in city_name:
        return "경기도"
    elif "강원" in city_name:
        return "강원도"
    elif "충북" in city_name:
        return "충청북도"
    elif "충남" in city_name:
        return "충청남도"
    elif "전북" in city_name:
        return "전라북도"
    elif "전남" in city_name:
        return "전라남도"
    elif "경북" in city_name:
        return "경상북도"
    elif "경남" in city_name:
        return "경상남도"
    elif "제주" in city_name:
        return "제주도"
    else:
        return city_name

# Streamlit 인터페이스
st.title('장애인 전용 체육시설 찾기🏃')
user_input = st.text_input("찾으시려는 지역을 이야기 해주세요.")

if user_input:
    def chatbot_with_ollama(user_input):
        # 사용자 입력에 role 추가 (user 역할로 전달)
        role_based_input = f"role: user\ncontent: Find sports facilities for disabled people in {user_input}."

        # Ollama CLI를 통해 모델을 실행하고 결과를 받아옴
        ollama_command = ["ollama", "run", "llama2", "--prompt", role_based_input]
        
        # subprocess로 Ollama CLI 호출
        result = subprocess.run(ollama_command, stdout=subprocess.PIPE)
        
        # 결과를 문자열로 변환
        llm_output = result.stdout.decode('utf-8')
        
        return llm_output

    # 결과 처리
    response = chatbot_with_ollama(user_input)

    # 예시: 응답으로 받은 데이터를 DataFrame에 넣을 수 있도록 변환
    results = []

    # '시_도'와 '소재지'를 기준으로 검색
    for item in all_data:
        si_do = (item.get('시_도') or "").replace(" ", "")  # 시_도 값에서 공백 제거
        so_jae_ji = (item.get('소재지') or "").replace(" ", "")  # 소재지 값에서 공백 제거

        # 시_도 정규화 및 비교
        normalized_si_do = normalize_city_name(si_do)

        # 사용자 입력과 시설 정보 비교
        if normalize_city_name(user_input) in normalized_si_do or normalize_city_name(user_input) in so_jae_ji:
            results.append({
                '시설명': item['시설명'],
                '주소': f"{normalized_si_do} {so_jae_ji}",
                '전화번호': item['전화번호'],
                '홈페이지': item.get('홈페이지', '없음')
            })

    if results:
        st.write(f"네! 말씀하신 지역에 있는 체육시설 목록입니다.")
        # 결과를 DataFrame으로 변환하여 테이블 출력 (인덱스를 1부터 시작)
        df = pd.DataFrame(results)
        df.index = df.index + 1
        st.table(df)  # Streamlit의 테이블 형태로 출력
    else:
        st.write("찾으시는 지역에는 체육 시설이 없습니다. 다른 곳에서 찾으시겠습니까?")
