from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

app = Flask(__name__)

# 크롤링 함수
def crawl_watcha_movies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 백그라운드에서 실행되도록 설정
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 크롬 드라이버 경로 설정 (운영 체제에 맞게 변경 필요)
    driver = webdriver.Chrome(options=chrome_options)

    # Watcha 사이트 열기
    url = 'https://pedia.watcha.com/ko-KR'
    driver.get(url)
    
    time.sleep(5)  # 페이지 로딩 대기
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    movies_data = []

    # 영화 리스트 추출
    movies = soup.find_all('li', class_='_DV31')

    # 전체 순위를 추적할 변수
    overall_rank = 1

    for movie in movies:
        # 영화 제목
        title = movie.find('div', class_='ZADAQ x_ja6')
        title_text = title.text if title else 'N/A'
        
        # 영화 순위
        rank = movie.find('div', class_='pfQ5u')
        
        # 순위가 페이지 내에서 1부터 다시 시작하므로, 전체 순위로 대체
        if rank:
            rank_text = str(overall_rank)
        else:
            rank_text = 'N/A'
        
        # 예매율 및 누적 관객 수 추출
        booking_info = movie.find('div', class_='ycnKW G41oJ')
        
        if booking_info:
            booking_info_text = booking_info.text
            booking_rate = booking_info_text.split(' ・ ')[0].replace("예매율 ", "")
            audience_count = booking_info_text.split(' ・ ')[1].replace("누적 관객 ", "") if ' ・ ' in booking_info_text else 'N/A'
        else:
            booking_rate = 'N/A'
            audience_count = 'N/A'
        
        # 영화 세부 정보 저장
        movies_data.append({
            '순위': rank_text,
            '제목': title_text,
            '예매율': booking_rate,
            '누적 관객 수': audience_count
        })
        
        # 전체 순위 증가
        overall_rank += 1

    # 드라이버 종료
    driver.quit()

    # pandas를 이용하여 데이터를 데이터프레임으로 변환
    df = pd.DataFrame(movies_data)
    return df

# 기본 라우트
@app.route('/')
def index():
    df = crawl_watcha_movies()  # 크롤링 실행
    movies_list = df.to_dict('records')  # 데이터프레임을 딕셔너리로 변환
    return render_template('index.html', movies=movies_list)

# Flask 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
