# app.py

import streamlit as st
from streamlit_folium import st_folium
from solar.solar_map import SolarMap
from rain.rain_map import RainMap

st.title("🌤️ 전국 기상 데이터 지도 시각화")

data_type = st.selectbox(
    "표시할 데이터 선택",
    ["🌡️ 평균지면온도", "☀️ 합계일사량", "🌧️ 일강수량"]
)

year = st.selectbox("연도 선택", [2020, 2021, 2022, 2023, 2024], index=4)
month = st.selectbox("월 선택", list(range(1, 13)))
day = st.selectbox("일 선택", list(range(1, 32)))

csv_file = "data/2020~2024.csv"

if data_type in ["🌡️ 평균지면온도", "☀️ 합계일사량"]:
    mapper = SolarMap(csv_file)
else:
    mapper = RainMap(csv_file)

filtered = mapper.filter_data(year, month, day)
m = mapper.draw_markers(filtered, data_type=data_type)

st_folium(m, width=850, height=600)
