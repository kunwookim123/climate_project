import streamlit as st
from streamlit_folium import st_folium
from solar.solar_map import SolarMap
from rain.rain_map import RainMap

st.title("🌤️ 전국 기상 데이터 지도 시각화")

# ------------------------------
# 데이터 종류 선택
# ------------------------------
data_type = st.selectbox(
    "표시할 데이터 선택",
    ["🌡️ 평균지면온도", "☀️ 합계일사량", "🌧️ 일강수량"]
)

# ------------------------------
# 날짜 선택
# ------------------------------
year = st.selectbox("연도 선택", [2020, 2021, 2022, 2023, 2024], index=4)
month = st.selectbox("월 선택", list(range(1, 13)))
day = st.selectbox("일 선택", list(range(1, 32)))

# ------------------------------
# 파일 및 클래스 선택
# ------------------------------
csv_file = "data/2020~2024.csv"  # 🔹 최신 파일로 변경

if data_type in ["🌡️ 평균지면온도", "☀️ 합계일사량"]:
    map_class = SolarMap
else:
    map_class = RainMap

# ------------------------------
# 지도 생성 및 표시
# ------------------------------
mapper = map_class(csv_file)
filtered = mapper.filter_data(year, month, day)
m = mapper.draw_markers(filtered, data_type=data_type)
st_folium(m, width=850, height=600)
