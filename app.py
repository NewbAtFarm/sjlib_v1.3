import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from datetime import datetime
from io import StringIO # 이걸로 읽어줘야 URL인데 text인지 html인지 안헷갈린데

my_raw_id = {'sepianohee':'sjLib0620!', 'lllaaa':'sjLib0620!', 'smkim0619':'sjLib0620!', 'sjkim0702':'sjLib0620!'}
my_id = {'1a63fa3009570074bd3191d37ed4b684':'dcff49bc89ab2efde3cdedeccbeb24ce',
           '508128311f9b7e30f49bced99a6b2cb2':'dcff49bc89ab2efde3cdedeccbeb24ce',
           'dbe289d1e48e1a5ba45f0baa8a00dda4':'dcff49bc89ab2efde3cdedeccbeb24ce',
           'b4d585cce63596998e6ed7b5af481ba2':'dcff49bc89ab2efde3cdedeccbeb24ce'}

payload = {
    "site": "sejong",
    "beforeUrl": "",
    "requestUrl": "",
    "type": "",
    "ext_gbn": "",
    "ext_name": "",
    "ext_handphone": "",
    "ext_email": "",
    "returnUrl": "/index.jsp",
    "popup": "N",
    "userId": "1a63fa3009570074bd3191d37ed4b684",   # 복사한 암호화값
    "password": "dcff49bc89ab2efde3cdedeccbeb24ce",  # 복사한 암호화값
    "message": ""
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Referer": "https://sejong.nl.go.kr/html/c7/c701.jsp",
    "Origin": "https://sejong.nl.go.kr",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

daechool_df = []
daechool_url = "https://sejong.nl.go.kr/html/c8/c801.jsp?menuId=O811&upperMenuId=O800&sel=O810"
yeyak_df = []
yeyak_url = "https://sejong.nl.go.kr/html/c8/c835.jsp?menuId=O866&upperMenuId=O800&sel=O860"
for i in range(len(my_id)):
    payload['userId'] = list(my_id.keys())[i]
    payload['password'] = list(my_id.values())[i]
    session = requests.Session()

    # 쿠키 초기화용 페이지 요청
    session.get("https://sejong.nl.go.kr/html/c7/c701.jsp")
    res = session.post("https://sejong.nl.go.kr/lgn/actionLogin2.do", data=payload, headers=headers)

    # 확인
    if "로그아웃" in res.text or "마이페이지" in res.text:
        print(list(my_raw_id.keys())[i], ": ✅ 로그인 성공!")
    else:
        print(list(my_raw_id.keys())[i], ": ❌ 로그인 실패.")

    # 로그인 후 1. 대출 페이지 접근
    resp = session.get(daechool_url, allow_redirects=False, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    # 대출 테이블 추출
    table = soup.find("table", class_="board_table")

    if table:
        print(list(my_raw_id.keys())[i], ": ✅ 테이블 찾음!")
    #     # print(table.prettify())
    else:
        print(list(my_raw_id.keys())[i], ": ❌ 테이블 못 찾음")

    daechool_df.append(pd.read_html(StringIO(str(table)))[0])
    daechool_df[i].insert(0, '아이디', list(my_raw_id.keys())[i]) # 왼쪽에 아이디 열 추가

    # 2. 예약 페이지 접근
    resp = session.get(yeyak_url, allow_redirects=False, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    # 예약 테이블 추출
    table = soup.find("table", class_="board_table")
    
    yeyak_df.append(pd.read_html(StringIO(str(table)))[0].head(10)) # 10개 줄까지만 넣음
    yeyak_df[i].insert(0, '아이디', list(my_raw_id.keys())[i]) # 왼쪽에 아이디 열 추가


daechool_merged_df = pd.concat(daechool_df, ignore_index=True)
# print(daechool_merged_df)
yeyak_merged_df = pd.concat(yeyak_df, ignore_index=True)

#####################
#  여기부터 streamlit
st.set_page_config(layout="wide")  # 넓게 해서 표가 다 보이네
now = datetime.now().strftime("%y-%m-%d %H:%M:%S")
st.write("🕒 읽은 시간:", now)

st.subheader('대출내역')
st.table(daechool_merged_df.reset_index(drop=True))
st.subheader('예약내역')
st.table(yeyak_merged_df.reset_index(drop=True))

# table과 dataframe을 둘 다 보여줘서 나중에 하나만 나오게 하자
st.subheader('대출내역')
st.dataframe(daechool_merged_df.reset_index(drop=True))
st.subheader('예약내역')
st.dataframe(yeyak_merged_df.reset_index(drop=True))
