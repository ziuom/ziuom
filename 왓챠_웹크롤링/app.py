from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def box_office():
    url = 'https://pedia.watcha.com/ko-KR'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    #영화 정보를 담을 리스트
    movies = []
    
    #데이터 추출
    for item in soup.find_all('li', class_='_DV31'):
        title = item.find('div', class_='ZADAQ x_ja6').text.strip()  # 영화 제목
        year = item.find('div', class_='isWsX Zcvzh').text.strip()   # 개봉 연도
        ticket_rate = item.find('div', class_='ycnKW G41oJ').text.strip() if item.find('div', class_='ycnKW G41oJ') else 'N/A'  # 예매율

        movies.append({'title': title, 'year': year, 'ticket_rate': ticket_rate})

    #box_office.html 렌더링
    return render_template('box_office.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)
