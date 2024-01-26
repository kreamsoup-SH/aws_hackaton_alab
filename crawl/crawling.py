# if there isn't a directory name 'data', make it
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def gov_portal_get_url_title(url:str = "https://www.gov.kr/portal/rcvfvrSvc/svcFind/svcSearchAll"):
    df = pd.DataFrame(columns=['url', 'title', 'content'])
    response = requests.get(url)
    if response.status_code == 200:
       html = response.text
       soup = BeautifulSoup(html, 'html.parser')
    # 모든 'a' 태그를 찾습니다.
    links = soup.find_all('a', attrs = {'class':'card-title'})
    urls = []
    titles = []
    button = False
    # 각 'a' 태그의 'href' 속성과 텍스트를 출력합니다.
    for idx, link in enumerate(links):
        url = link.get('href')  # 'href' 속성을 가져옵니다.
        if (button) :
            if(url == urls[0]) :
                break
        urls.append(url) #url을 urls에 저장
        title = link.text  # 텍스트를 가져옵니다.
        titles.append(title) #title을 titles에 저장
        df.loc[idx] = [url, title, '']
        button = True
        print(f"주소 : {url}, 제목 : {title}")
    return df

def gov_portal_get_content(df):
    for idx in range(df.shape[0]):
        url_ = df.iloc[idx]['url']
        url = f"https://www.gov.kr/{url_}"
        df.iloc[idx]['url'] = url

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to request url : {url}")
        html = response.text
        # Assuming 'html' is your HTML document
        soup = BeautifulSoup(html, 'html.parser')
        # Find 'tbody' tag
        tabs = soup.find_all('div', attrs={'class':'tab-content'})
        texts = []
        for tab in tabs:
            text = tab.text.replace('\t', '').replace('\r', '')
            texts.append(text)
        df.loc[idx]['content'] = texts

mydf = gov_portal_get_url_title()
gov_portal_get_content(mydf)

if not os.path.isdir('data'):
    os.mkdir('data')
mydf.to_csv('data/gov_portal.csv', index=False, encoding='utf-8')