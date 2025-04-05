import streamlit as st

# 페이지 설정 
st.set_page_config(
    page_title="FairWork",
    page_icon="🗺️",
    layout="wide"
)

import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# CSV 파일 로드
df = pd.read_csv("map.csv")
df = df.dropna(subset=['위도', '경도'])

# 체불액을 정수로 변환
df['체불액(원)'] = df['체불액(원)'].astype(int)

# 시군구 정보 추출 함수
def extract_city(addr):
    try:
        return addr.split()[1]
    except:
        return None

df['시군구'] = df['소재지(사업장)'].apply(extract_city)

# 소재지 선택 UI
소재지들 = ['전체'] + sorted(df['소재지'].dropna().unique())
선택_소재지 = st.selectbox("소재지 선택", 소재지들)

# 시군구 필터
if 선택_소재지 == '전체':
    선택_데이터 = df.copy()
else:
    시군구들 = ['전체'] + sorted(df[df['소재지'] == 선택_소재지]['시군구'].dropna().unique())
    선택_시군구 = st.selectbox("시/군/구 선택", 시군구들)
    
    if 선택_시군구 == '전체':
        선택_데이터 = df[df['소재지'] == 선택_소재지]
    else:
        선택_데이터 = df[(df['소재지'] == 선택_소재지) & (df['시군구'] == 선택_시군구)]

# 지도 중심 좌표 계산
center_lat = 선택_데이터['위도'].mean()
center_lon = 선택_데이터['경도'].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=6 if 선택_소재지 == '전체' else 11)

# 마커 클러스터 생성
marker_cluster = MarkerCluster().add_to(m)

# 기본 마커 추가
for _, row in 선택_데이터.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"{row['사업장명']}<br>체불액: {row['체불액(원)']}원",
        tooltip=row['사업장명']
    ).add_to(marker_cluster)

# 지도 표시
st_folium(m, width=1000, height=600)

# 표 표시
st.markdown("### 📋 사업장 목록")
st.dataframe(선택_데이터[['사업장명', '소재지(사업장)', '체불액(원)']].reset_index(drop=True))


