# -*- coding: utf-8 -*-
"""
✅ 완전 안정화 버전 - economic_loss_final.py
- 합계 일사량(MJ/m2)_x, _y 중복 자동 처리
- 장마철 여부 생성
- 연도별 / 지역별 / 전국 손실액 모두 계산 및 시각화
- 전력 판매 단가: SMP (도매가)
- 결과물: output 폴더 내 HTML 3종
"""

import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.io import write_html

# -----------------------------
# 경로 및 기본 설정
# -----------------------------
DATA_WEATHER = "data/2020~2024_수정본.csv"
DATA_POWER   = "data/예측발전량_PR가변_수정.csv"
DATA_CAP     = "data/2020~2024_설비용량.csv"
OUTPUT_DIR   = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 발전사업자 기준 SMP(원/kWh)
SMP = {
    2020: 68.87,
    2021: 94.34,
    2022: 196.65,
    2023: 167.11,
    2024: 128.39
}

# 회귀식 기울기
SLOPE = 20.835

# 장마 기간
RAINY_SEASON = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-07-03", "2021-07-26"),
    2022: ("2022-06-23", "2022-07-26"),
    2023: ("2023-06-25", "2023-07-26"),
    2024: ("2024-06-21", "2024-07-23")
}

# 지역 분류 기준
SOUTH = ["전북", "전남", "경북", "경남", "광주", "대구", "부산", "울산", "제주"]
NC = ["경기", "강원", "충북", "충남", "세종", "대전", "서울", "인천"]

# -----------------------------
# 데이터 로드 및 전처리
# -----------------------------
weather = pd.read_csv(DATA_WEATHER, encoding="utf-8")
power = pd.read_csv(DATA_POWER, encoding="utf-8")
cap = pd.read_csv(DATA_CAP, encoding="utf-8")

# 날짜형 변환
for df in [weather, power]:
    if "일시" in df.columns:
        df["일시"] = pd.to_datetime(df["일시"], errors="coerce")

weather["연도"] = weather["일시"].dt.year

# 장마철 여부 컬럼 생성
def is_rainy(row):
    y = row["연도"]
    if y not in RAINY_SEASON or pd.isna(row["일시"]):
        return False
    s, e = RAINY_SEASON[y]
    return pd.to_datetime(s) <= row["일시"] <= pd.to_datetime(e)
weather["장마철여부"] = weather.apply(is_rainy, axis=1)

# 병합
need_cols = ["지점명", "일시", "일강수량(mm)", "합계 일사량(MJ/m2)", "장마철여부"]
merged = pd.merge(power, weather[need_cols], on=["지점명", "일시"], how="inner")

# 🧩 중복 컬럼 정리 (합계 일사량_x/_y 방지)
for col in merged.columns:
    if "합계 일사량" in col and col != "합계 일사량(MJ/m2)":
        merged.rename(columns={col: "합계 일사량(MJ/m2)"}, inplace=True)

merged["연도"] = merged["일시"].dt.year
merged["합계 일사량(MJ/m2)"] = pd.to_numeric(merged["합계 일사량(MJ/m2)"], errors="coerce")

# -----------------------------
# 연도별 장마 vs 비장마 평균 일사량
# -----------------------------
solar_mean = merged.groupby(["연도", "장마철여부"])["합계 일사량(MJ/m2)"].mean().reset_index()
pivot_irr = solar_mean.pivot(index="연도", columns="장마철여부", values="합계 일사량(MJ/m2)").fillna(0)
pivot_irr.columns = ["비장마철", "장마철"]
pivot_irr["차이(비장마-장마)"] = pivot_irr["비장마철"] - pivot_irr["장마철"]
nat = pivot_irr.reset_index()

# -----------------------------
# 설비용량 데이터 처리
# -----------------------------
cap_total = cap.set_index("연도").sum(axis=1).reset_index()
cap_total.columns = ["연도", "총설비용량(MW)"]

def sum_bucket(df, keywords):
    cols = [c for c in df.columns if any(k in c for k in keywords)]
    result = df[["연도"]].copy()
    result["설비용량(MW)"] = df[cols].sum(axis=1, numeric_only=True)
    return result

south_cap = sum_bucket(cap, SOUTH)
south_cap["지역구분"] = "남부"

nc_cap = sum_bucket(cap, NC)
nc_cap["지역구분"] = "중북부"

cap_region = pd.concat([south_cap, nc_cap], ignore_index=True)

# -----------------------------
# 전국 손실량 및 손실액 계산
# -----------------------------
nat["손실량(kWh/MW)"] = nat["차이(비장마-장마)"] * SLOPE
nat = pd.merge(nat, cap_total, on="연도", how="left")
nat["총손실량(kWh)"] = nat["손실량(kWh/MW)"] * nat["총설비용량(MW)"]
nat["SMP(원/kWh)"] = nat["연도"].map(SMP)
nat["손실액(억 원)"] = nat["총손실량(kWh)"] * nat["SMP(원/kWh)"] / 1e8

# -----------------------------
# 지역별 손실량 및 손실액 계산
# -----------------------------
def tag_region(name):
    name = str(name)
    if any(k in name for k in SOUTH): return "남부"
    if any(k in name for k in NC): return "중북부"
    return "기타"
merged["지역구분"] = merged["지점명"].apply(tag_region)

rg = (
    merged.groupby(["연도", "지역구분", "장마철여부"])["합계 일사량(MJ/m2)"]
    .mean()
    .reset_index()
    .pivot(index=["연도", "지역구분"], columns="장마철여부", values="합계 일사량(MJ/m2)")
    .fillna(0)
    .reset_index()
)
rg.columns = ["연도", "지역구분", "비장마철", "장마철"]
rg["차이(비장마-장마)"] = rg["비장마철"] - rg["장마철"]
rg["손실량(kWh/MW)"] = rg["차이(비장마-장마)"] * SLOPE

rg = pd.merge(rg, cap_region, on=["연도", "지역구분"], how="left").fillna(0)
rg["총손실량(kWh)"] = rg["손실량(kWh/MW)"] * rg["설비용량(MW)"]
rg["SMP(원/kWh)"] = rg["연도"].map(SMP)
rg["손실액(억 원)"] = rg["총손실량(kWh)"] * rg["SMP(원/kWh)"] / 1e8
rg_viz = rg[rg["지역구분"].isin(["남부", "중북부"])]

# -----------------------------
# 시각화
# -----------------------------
PAPER_BG = "#f5f5f5"

# (1) 연도별 장마철 vs 비장마철 평균 일사량
fig1 = go.Figure()
fig1.add_bar(x=nat["연도"], y=nat["비장마철"], name="비장마철", marker_color="#1f77b4")
fig1.add_bar(x=nat["연도"], y=nat["장마철"], name="장마철", marker_color="#ff7f0e")
fig1.update_layout(
    title="🌦️ 연도별 장마철 vs 비장마철 평균 일사량 비교",
    barmode="group", xaxis_title="연도", yaxis_title="평균 일사량 (MJ/m²)",
    template="plotly_white", paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG
)
write_html(fig1, f"{OUTPUT_DIR}/1_연도별_일사량비교.html", include_plotlyjs="cdn")

# (2) 전국 손실액
fig2 = go.Figure()
fig2.add_bar(x=nat["연도"], y=nat["손실액(억 원)"], marker_color="#c44e52", text=nat["손실액(억 원)"].round(1), textposition="outside")
fig2.update_layout(
    title="🌍 전국 연도별 장마철 손실액 (억 원, SMP 반영)",
    xaxis_title="연도", yaxis_title="손실액 (억 원)",
    template="plotly_white", paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG
)
write_html(fig2, f"{OUTPUT_DIR}/2_전국_손실액_연도별.html", include_plotlyjs="cdn")

# (3) 지역별 손실액
fig3 = px.bar(
    rg_viz, x="연도", y="손실액(억 원)", color="지역구분",
    barmode="group", text=rg_viz["손실액(억 원)"].round(1),
    color_discrete_map={"중북부": "#1f77b4", "남부": "#ff7f0e"},
    title="🗺️ 남부 vs 중북부 연도별 손실액 (억 원, SMP 반영)",
    template="plotly_white"
)
fig3.update_traces(textposition="outside")
fig3.update_layout(
    paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG,
    xaxis_title="연도", yaxis_title="손실액 (억 원)",
)
write_html(fig3, f"{OUTPUT_DIR}/3_지역별_손실액_연도별.html", include_plotlyjs="cdn")

print("✅ 완료: output 폴더에 3개 HTML 저장 완료!")
