import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# ------------------------------
# 예시 데이터 (연/월/일 + 위치 + 발전량)
# ------------------------------
data = [
    [2020, 1, 10, "서울", 37.5665, 126.9780, 3.2],
    [2020, 2, 15, "서울", 37.5665, 126.9780, 3.6],
    [2021, 3, 5,  "서울", 37.5665, 126.9780, 3.8],
    [2021, 3, 20, "서울", 37.5665, 126.9780, 3.5],
    [2022, 6, 12, "서울", 37.5665, 126.9780, 4.0],
    [2023, 7, 9,  "서울", 37.5665, 126.9780, 3.3],
    [2024, 8, 21, "서울", 37.5665, 126.9780, 3.9],
    [2025, 9, 5,  "서울", 37.5665, 126.9780, 4.2],
]
df = pd.DataFrame(data, columns=["연도", "월", "일", "지역", "위도", "경도", "발전량"])

# ------------------------------
# 🎛️ UI - 날짜 선택
# ------------------------------
st.title("☀️ 태양광 발전량 지도 (날짜별 선택)")

# ✅ 연도 2020~2025 고정
year = st.selectbox("연도 선택", list(range(2020, 2026)), index=0)

# ✅ 월 1~12 고정
month = st.selectbox("월 선택", list(range(1, 13)), index=0)

# ✅ 일 1~31 고정
day = st.selectbox("일 선택", list(range(1, 32)), index=0)

# ------------------------------
# 📅 선택된 날짜 데이터 필터링
# ------------------------------
filtered = df[
    (df["연도"] == year)
    & (df["월"] == month)
    & (df["일"] == day)
]

# ------------------------------
# 🗺️ 지도 생성
# ------------------------------
m = folium.Map(location=[36.5, 127.8], zoom_start=7)

if not filtered.empty:
    for _, row in filtered.iterrows():
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=row["발전량"] * 3,
            color="orange",
            fill=True,
            fill_opacity=0.6,
            popup=(
                f"<b>{row['지역']}</b><br>"
                f"{row['연도']}년 {row['월']}월 {row['일']}일<br>"
                f"🔆 발전량: {row['발전량']} kWh"
            ),
        ).add_to(m)
else:
    folium.Marker(
        [36.5, 127.8],
        popup=f"{year}년 {month}월 {day}일 데이터가 없습니다.",
        icon=folium.Icon(color="gray")
    ).add_to(m)

# ------------------------------
# 지도 출력
# ------------------------------
st_folium(m, width=800, height=600)
