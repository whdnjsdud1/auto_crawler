# -*- coding: utf-8 -*-
import datetime
import json
import time
import urllib.request
import pandas as pd
import re

# import redis
from bs4 import BeautifulSoup
from selenium import webdriver


def gbsa_cralwer():
    client_id = "7cG4gVI1sjuj5Y3ZHvn6"
    client_secret = "ITvzFu4ZfE"
    start = 1
    display = 5

    url_list = []
    date_list = []
    content_list = []

    search_type = 'kin'
    search_text = "판교테크노밸리"

    encText = urllib.parse.quote(search_text)
    print(encText)
    url = "https://openapi.naver.com/v1/search/" + search_type + "?display=" + str(display) + "&start=" + str(start) + "&sort=sim&query=" + encText  # json 결과

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(request, timeout=30)
    except Exception as e:
        print('bad request : ', e)

    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        resp = response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)
        resp = ''

    if resp:
        j = json.loads(resp)

        for item in j["items"]:
            print('item : ', item)
            url = str(item["link"]).replace("?Redirect=Log&amp;logNo=", "/")
            print(url)

            # item 안에 post_date가 없을 시(KeyError) None 처리
            try:
                post_date = item["postdate"]
            except KeyError as e:
                post_date = None
    #             print('KeyError : ', e)

            try:
                # 웹드라이버 실행
                options = webdriver.ChromeOptions()
                options.add_argument('headless')

                driver = webdriver.Chrome(
                    executable_path='/home/ec2-user/auto_crawler/chromedriver',
                    chrome_options=options)
                driver.get(url)
                driver.switch_to.default_content()

                # 내용 선언
                contents = ''

                # 지식인
                if not url.find('kin.naver.com') == -1:
                    page = driver.page_source
                    soup = BeautifulSoup(page, 'html.parser')

                    # 질문만 수집
                    contents = soup.find("div", {"class": "c-heading"})

                    # 지식인은 api에 날짜가 포함되어 있지 않으므로 웹에서 수집
                    post_date = soup.find("span", {"class": "c-userinfo__date"}).text.replace('작성일', '')

                    if not contents:
                        contents = soup.select_one('.srch_area')

            except Exception as e:
                print(e)

            # 내용 html을 파싱
            content = ''
            # 네이버가 아닐시 태그가 다르기 때문에 오류 처리
            try:
                for string in contents.stripped_strings:
                    content += repr(string)
            except Exception as e:
                print('content none error', url)

            content = content.replace('\\xa0', ' ').replace('\\r\\n', ' ').replace('\'', '').replace(',', ' ')

            if not content == '':
                # 사이트 url
                url_list.append(url)
                date_list.append(post_date)
                content_list.append(content)

            # 드라이버 종료
            driver.quit()

        # 검색 단어명으로 엑셀 저장
        naver_info_df = {"content_list": content_list, "date_list": date_list,
                         "url_list": url_list}

        df = pd.DataFrame(naver_info_df)

        file_name = 'naver_info_' + search_text + '.csv'
        df.to_csv('crawler_data/' + file_name, sep=",", index=True, encoding='ms949')
        print("저장 완료!")