# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import timedelta

st.set_page_config(layout="wide")

# ---------------------------------------------------------
# 파일 로드 & 유틸
# ---------------------------------------------------------
def clean_columns(df):
    new_cols = {}
    drop_cols = []
    for col in df.columns:
        if col.endswith("_x") or col.endswith("_y"):
            base = col[:-2]
            if base in df.columns:
                drop_cols.append(col)
            else:
                new_cols[col] = base
    df.rename(columns=new_cols, inplace=True)
    df.drop(columns=drop_cols, inplace=True)
    return df


# ---------------------------------------------------------
# CSV 로드
# ---------------------------------------------------------
weather = pd.read_csv("data/2020~2024_revised_monsoon.csv")
power   = pd.read_csv("data/예측발전량_PR가변_수정.csv")
mapping = pd.read_csv("data/관측소_시도매핑.csv")

weather = clean_columns(weather)
power   = clean_columns(power)
mapping = clean_columns(mapping)

weather["일시"] = pd.to_datetime(weather["일시"])
power["일시"]   = pd.to_datetime(power["일시"])
weather["연도"] = weather["일시"].dt.year

# ---------------------------------------------------------
# Merge weather + power
# ---------------------------------------------------------
merged = weather.merge(
    power[["지점명", "일시", "예측발전량_PR가변(kWh)"]],
    on=["지점명", "일시"],
    how="left"
)
merged = clean_columns(merged)

# ---------------------------------------------------------
# 시도 / 위경도 merge
# ---------------------------------------------------------
merged = merged.merge(mapping, on="지점명", how="left")
merged = clean_columns(merged)

# ---------------------------------------------------------
# 6~8월 필터 (여름)
# ---------------------------------------------------------
merged["월"] = merged["일시"].dt.month
merged_summer = merged[merged["월"].isin([6,7,8])].copy()

# ---------------------------------------------------------
# 장마철/비장마철 날짜 범위 계산
# ---------------------------------------------------------
monsoon_ranges = (
    merged_summer[merged_summer["장마철여부"] == "장마철"]
    .groupby("연도")["일시"]
    .agg(["min", "max"])
    .rename(columns={"min": "start", "max": "end"})
)

non_monsoon_ranges = {}
for year in monsoon_ranges.index:
    mon = monsoon_ranges.loc[year]
    before = (pd.Timestamp(f"{year}-06-01"), mon.start - timedelta(days=1))
    after  = (mon.end + timedelta(days=1), pd.Timestamp(f"{year}-08-31"))
    non_monsoon_ranges[year] = {"before": before, "after": after}

# ---------------------------------------------------------
# SMP 설정 (연도별)
# ---------------------------------------------------------
SMP = {2020:68.87, 2021:94.34, 2022:196.65, 2023:167.11, 2024:128.39}

# ---------------------------------------------------------
# 비장마철 평균 일사량(연도별)
# ---------------------------------------------------------
summer_nonmon = merged_summer[merged_summer["장마철여부"] == "비장마철"]
nonmon_mean = summer_nonmon.groupby("연도")["합계 일사량(MJ/m2)"].mean().to_dict()


# ---------------------------------------------------------
# 손실량/손실액 계산 함수 (옵션 B)
# ---------------------------------------------------------
def compute_losses(df):

    df = df.copy()
    df["연도"] = df["일시"].dt.year

    df["비장평균"] = df["연도"].map(nonmon_mean)

    # 손실량 계산
    df["손실량(kWh/MW)"] = (df["비장평균"] - df["합계 일사량(MJ/m2)"]) * 20.835

    # 시도 설비용량 매핑 (없으면 1MW 처리 또는 0 처리)
    # 지금은 1MW로 처리 (원하면 시도별 설비용량 CSV 반영해줄게)
    df["설비용량(MW)"] = 1  

    # 손실액 계산
    df["SMP"] = df["연도"].map(SMP)
    df["손실액(만원)"] = df["손실량(kWh/MW)"] * df["설비용량(MW)"] * df["SMP"] / 10000

    return df


merged_summer = compute_losses(merged_summer)

# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------
left, right = st.columns([8,2])

with right:

    st.markdown("""
        <style>
        .small-font { font-size: 14px !important; }
        .stSelectbox label, .stRadio label { font-size: 14px !important; }
        .title-nowrap h3 { white-space: nowrap; font-size: 16px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="small-font">', unsafe_allow_html=True)

    # --- 값 선택 ---
    st.markdown("### 표시할 값")
    value_choice = st.radio(
        "",
        ["강수량 🌧", "일사량 ☀", "발전량 ⚡", "손실량 🔥", "손실액 💸"]
    )

    # --- 장마철 날짜 선택 ---
    st.markdown("""
    <div style="white-space: nowrap; font-size: 16px; font-weight: 600;
                margin-bottom: 4px; margin-top: -2px;">
        🌧 장마철 분석 날짜 선택 (6~8월)
    </div>
""", unsafe_allow_html=True)

    years = ["선택해주세요"] + list(monsoon_ranges.index)
    y1 = st.selectbox("연도", years)

    m1 = d1 = None
    if y1 != "선택해주세요":
        mon = monsoon_ranges.loc[y1]
        months = sorted({d.month for d in pd.date_range(mon.start, mon.end)})
        m1 = st.selectbox("월", ["선택해주세요"] + months)
        if m1 != "선택해주세요":
            days = sorted({d.day for d in pd.date_range(mon.start, mon.end) if d.month == m1})
            d1 = st.selectbox("일", ["선택해주세요"] + days)

    # --- 비장마철 날짜 선택 ---
    st.markdown("""
    <div style="white-space: nowrap; font-size: 16px; font-weight: 600;
                margin-bottom: 4px; margin-top: -2px;">
        ☀ 비장마철 분석 날짜 선택 (6~8월)
    </div>
""", unsafe_allow_html=True)

    y2 = st.selectbox("연도 ", years)
    m2 = d2 = None

    if y2 != "선택해주세요":
        before = non_monsoon_ranges[y2]["before"]
        after  = non_monsoon_ranges[y2]["after"]

        months_total = sorted(list(
            {d.month for d in pd.date_range(before[0], before[1])} |
            {d.month for d in pd.date_range(after[0], after[1])}
        ))

        m2 = st.selectbox("월 ", ["선택해주세요"] + months_total)
        if m2 != "선택해주세요":
            days_total = sorted(list(
                {d.day for d in pd.date_range(before[0], before[1]) if d.month == m2} |
                {d.day for d in pd.date_range(after[0], after[1]) if d.month == m2}
            ))
            d2 = st.selectbox("일 ", ["선택해주세요"] + days_total)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# 마커 추가 함수
# ---------------------------------------------------------
def add_circle_markers(m, df, value_col, emoji):

    if df.empty:
        return

    # 기본 색상
    base_color = {
        "🌧": (91, 143, 249),
        "☀": (255, 107, 107),
        "⚡": (80, 170, 80),
        "🔥": (255, 90, 160),
        "💸": (155, 80, 255)
    }

    unit_map = {
        "🌧": "mm",
        "☀": "MJ/m²",
        "⚡": "kWh",
        "🔥": "kWh/MW",
        "💸": "만원"
    }

    vals = df[value_col].astype(float)
    vmin, vmax = vals.min(), vals.max()

    df["_norm"] = (vals - vmin) / (vmax - vmin + 1e-9)

    for _, row in df.iterrows():

        value = row[value_col]

        # 🔥 손실량 음수 → 검정색
        if emoji == "🔥" and value < 0:
            fill_color = "rgba(0,0,0,0.75)"
        else:
            r,g,b = base_color[emoji]
            opacity = 0.55 + (row["_norm"] * 0.75)
            fill_color = f"rgba({r},{g},{b},{opacity})"

        tooltip_html = f"""
            <b>{row['지점명']}</b><br>
            {emoji} {value_col} : {value:.2f} {unit_map[emoji]}
        """

        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=11,
            color=None,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.85,
            tooltip=tooltip_html,
        ).add_to(m)


# ---------------------------------------------------------
# 지도 생성
# ---------------------------------------------------------
with left:

    map_left_col, map_right_col = st.columns(2)

    # 🌧 장마철 지도
    with map_left_col:
        st.markdown("#### 🌧 장마철 지도")
        m_left = folium.Map(location=[36.0,128.7], zoom_start=7)

        if y1!="선택해주세요" and m1 not in (None,"선택해주세요") and d1 not in (None,"선택해주세요"):
            date_left = f"{y1}-{m1:02d}-{d1:02d}"
            df_left = merged_summer[merged_summer["일시"] == date_left]

            if "강수량" in value_choice:
                add_circle_markers(m_left, df_left, "일강수량(mm)", "🌧")
            elif "일사량" in value_choice:
                add_circle_markers(m_left, df_left, "합계 일사량(MJ/m2)", "☀")
            elif "발전량" in value_choice:
                add_circle_markers(m_left, df_left, "예측발전량_PR가변(kWh)", "⚡")
            elif "손실량" in value_choice:
                add_circle_markers(m_left, df_left, "손실량(kWh/MW)", "🔥")
            else:
                add_circle_markers(m_left, df_left, "손실액(만원)", "💸")

        st_folium(m_left, height=700, width=600, key="left_map")

    # ☀ 비장마철 지도
    with map_right_col:
        st.markdown("#### ☀ 비장마철 지도")
        m_right = folium.Map(location=[36.0,128.7], zoom_start=7)

        if y2!="선택해주세요" and m2 not in (None,"선택해주세요") and d2 not in (None,"선택해주세요"):
            date_right = f"{y2}-{m2:02d}-{d2:02d}"
            df_right = merged_summer[merged_summer["일시"] == date_right]

            if "강수량" in value_choice:
                add_circle_markers(m_right, df_right, "일강수량(mm)", "🌧")
            elif "일사량" in value_choice:
                add_circle_markers(m_right, df_right, "합계 일사량(MJ/m2)", "☀")
            elif "발전량" in value_choice:
                add_circle_markers(m_right, df_right, "예측발전량_PR가변(kWh)", "⚡")
            elif "손실량" in value_choice:
                add_circle_markers(m_right, df_right, "손실량(kWh/MW)", "🔥")
            else:
                add_circle_markers(m_right, df_right, "손실액(만원)", "💸")

        st_folium(m_right, height=700, width=600, key="right_map")
