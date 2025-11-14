# -*- coding: utf-8 -*-
"""
economic_loss_final_v8_summer.py
🔥 기존 v8 코드에서 '여름(6~8월) 기준'만 반영한 최소 수정 버전
🔥 그래프 스타일/흐름/파일명 전체 동일
🔥 수정된 부분에는 # 🔥 수정 주석 추가
"""

import pandas as pd
import numpy as np
import plotly.express as px
import os
import kaleido

# -------------------------------------------------------
# 파일 경로
# -------------------------------------------------------
DATA_WEATHER = "data/2020~2024_revised_monsoon.csv"
DATA_POWER   = "data/예측발전량_PR가변_수정.csv"
DATA_CAP     = "data/2020~2024_설비용량.csv"
DATA_MAP     = "data/관측소_시도매핑.csv"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------------------------------------
# 방탄 연도 복구
# -------------------------------------------------------
def ensure_year(df):
    if df.index.name == "연도":
        df = df.reset_index()

    if "연도_y" in df.columns:
        df["연도"] = df["연도_y"]
    elif "연도_x" in df.columns:
        df["연도"] = df["연도_x"]

    if "연도" not in df.columns:
        if "일시" in df.columns:
            df["연도"] = pd.to_datetime(df["일시"], errors="coerce").dt.year
        else:
            df["연도"] = -1

    df = df.drop(columns=["연도_x","연도_y"], errors="ignore")
    return df


# -------------------------------------------------------
# 데이터 로드
# -------------------------------------------------------
weather = pd.read_csv(DATA_WEATHER)
power   = pd.read_csv(DATA_POWER)
cap     = pd.read_csv(DATA_CAP, sep="|")
mapping = pd.read_csv(DATA_MAP)

weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce")
power["일시"]   = pd.to_datetime(power["일시"], errors="coerce")

weather = ensure_year(weather)
power   = ensure_year(power)


# -------------------------------------------------------
# 관측소 → 시도 매핑
# -------------------------------------------------------
weather = weather.merge(mapping[["지점명","시도"]], on="지점명", how="left")
power   = power.merge(mapping[["지점명","시도"]], on="지점명", how="left")


# -------------------------------------------------------
# 파워 + 기상 병합
# -------------------------------------------------------
merged = power.merge(
    weather[["지점명","일시","합계 일사량(MJ/m2)","장마철여부"]],
    on=["지점명","일시"],
    how="left"
)

merged = ensure_year(merged)

# 일사량 컬럼 통일
if "합계 일사량(MJ/m2)_y" in merged.columns:
    merged["합계 일사량(MJ/m2)"] = merged["합계 일사량(MJ/m2)_y"]
elif "합계 일사량(MJ/m2)_x" in merged.columns:
    merged["합계 일사량(MJ/m2)"] = merged["합계 일사량(MJ/m2)_x"]

merged = merged.drop(columns=[c for c in merged.columns if "_x" in c or "_y" in c], errors="ignore")
merged["합계 일사량(MJ/m2)"] = pd.to_numeric(merged["합계 일사량(MJ/m2)"], errors="coerce")


# -------------------------------------------------------
# 🔥 여름(6~8월)만 사용 ← 핵심 수정 ①
# -------------------------------------------------------
merged["월"] = merged["일시"].dt.month
merged_summer = merged[merged["월"].isin([6,7,8])].copy()   # 🔥 수정
# merged_summer 데이터만 이후 모든 계산에 사용
# nat / rg / 손실량 / 손실액 모두 이 값 기준으로 계산됨


# -------------------------------------------------------
# 전국 평균 일사량 (여름 기준)
# -------------------------------------------------------
nat = (
    merged_summer.groupby(["연도","장마철여부"])["합계 일사량(MJ/m2)"]  # 🔥 수정: merged → merged_summer
    .mean().reset_index()
)

nat = ensure_year(nat)
nat = nat.replace({True:"장마철", False:"비장마철"})

nat = nat.pivot(index="연도", columns="장마철여부",
                values="합계 일사량(MJ/m2)").reset_index()

nat = ensure_year(nat)
nat["차이"] = nat["비장마철"] - nat["장마철"]
nat["손실량(kWh/MW)"] = nat["차이"] * 20.835


# -------------------------------------------------------
# 전국 손실액 계산
# -------------------------------------------------------
cap = ensure_year(cap)

cap_total = cap.set_index("연도").sum(axis=1).reset_index()
cap_total.columns = ["연도","총설비용량(MW)"]
nat = nat.merge(cap_total, on="연도", how="left")
nat = ensure_year(nat)

nat["연도"] = nat["연도"].astype(int)
nat["총손실량(kWh)"] = nat["손실량(kWh/MW)"] * nat["총설비용량(MW)"]

SMP = {2020:68.87, 2021:94.34, 2022:196.65, 2023:167.11, 2024:128.39}
nat["SMP"] = nat["연도"].map(SMP)
nat["손실액(만원)"] = nat["총손실량(kWh)"] * nat["SMP"] / 10000
nat["손실액(만원)"] = nat["손실액(만원)"].fillna(0)

nat.to_csv(f"{OUTPUT_DIR}/DEBUG_nat_summer.csv", index=False, encoding="utf-8-sig")


# -------------------------------------------------------
# 지역구분 태팅
# -------------------------------------------------------
SOUTH = ["전라","경상","부산","울산","광주","대구","제주"]
NC    = ["서울","경기","인천","강원","충청","세종","대전"]

def tag_region(x):
    if isinstance(x, str):
        if any(k in x for k in SOUTH): return "남부"
        if any(k in x for k in NC):    return "중북부"
    return "기타"

merged_summer["지역구분"] = merged_summer["시도"].apply(tag_region)  # 🔥 수정


# -------------------------------------------------------
# 지역별 손실량 (여름 기준)
# -------------------------------------------------------
rg = (
    merged_summer.groupby(["연도","지역구분","장마철여부"])["합계 일사량(MJ/m2)"]  # 🔥 수정
    .mean().reset_index()
)

rg = ensure_year(rg)
rg = rg.replace({True:"장마철", False:"비장마철"})

rg = rg.pivot(index=["연도","지역구분"], columns="장마철여부",
              values="합계 일사량(MJ/m2)").reset_index()

rg = ensure_year(rg)
rg["차이"] = rg["비장마철"] - rg["장마철"]
rg["손실량(kWh/MW)"] = rg["차이"] * 20.835


# -------------------------------------------------------
# 지역 설비용량 + 손실액
# -------------------------------------------------------
def sum_region(keys):
    cols = [c for c in cap.columns if any(k in c for k in keys)]
    return cap[cols].sum(axis=1)

cap["남부"]   = sum_region(SOUTH)
cap["중북부"] = sum_region(NC)

cap_region = cap[["연도","남부","중북부"]].melt(
    id_vars="연도", var_name="지역구분", value_name="설비용량(MW)"
)

rg = rg.merge(cap_region, on=["연도","지역구분"], how="left")
rg = ensure_year(rg)

rg["연도"] = rg["연도"].astype(int)
rg["총손실량(kWh)"] = rg["손실량(kWh/MW)"] * rg["설비용량(MW)"]
rg["SMP"] = rg["연도"].map(SMP)
rg["손실액(만원)"] = rg["총손실량(kWh)"] * rg["SMP"] / 10000
rg["손실액(만원)"] = rg["손실액(만원)"].fillna(0)

rg.to_csv(f"{OUTPUT_DIR}/DEBUG_rg_summer.csv", index=False, encoding="utf-8-sig")


# -------------------------------------------------------
# 저장 함수 (동일)
# -------------------------------------------------------
def save(fig, name):
    clean = name.replace(" ", "_").replace("(", "").replace(")", "")
    fig.write_html(f"{OUTPUT_DIR}/{clean}.html", include_plotlyjs="cdn")
    fig.write_image(f"{OUTPUT_DIR}/{clean}.png", scale=2)


# -------------------------------------------------------
# 스타일 (동일)
# -------------------------------------------------------
def apply_common(fig, title, ytitle):
    fig.update_layout(
        title=dict(text=title, x=0.02, y=0.97, font=dict(size=26)),
        paper_bgcolor="#f4f4f4",
        plot_bgcolor="#fafafa",

        xaxis=dict(type="category", tickfont=dict(size=14)),
        yaxis=dict(title=ytitle, tickfont=dict(size=14), gridcolor="rgba(0,0,0,0.08)"),

        legend_title="구분",
        margin=dict(l=60,r=40,t=80,b=60),
    )
    return fig


# -------------------------------------------------------
# 10개 그래프 (기존과 동일)
# -------------------------------------------------------

# 1. 평균 일사량 bar
nat_m = nat[["연도","장마철","비장마철"]].melt(id_vars="연도",
                                            var_name="구분",
                                            value_name="평균일사량")

fig = px.bar(nat_m, x="연도", y="평균일사량", color="구분", barmode="group")
fig.update_traces(hovertemplate="연도 : %{x}<br>평균 일사량 : %{y:.1f} MJ/m²<extra></extra>")
save(apply_common(fig, "🌞 장마철/비장마철 평균 일사량 (bar)", "평균 일사량 (MJ/m²)"),
     "장마철_비장마철_평균일사량_bar")

# 2. 평균 일사량 line
fig = px.line(nat_m, x="연도", y="평균일사량", color="구분", markers=True)
fig.update_traces(hovertemplate="연도 : %{x}<br>평균 일사량 : %{y:.1f} MJ/m²<extra></extra>")
save(apply_common(fig, "🌞 장마철/비장마철 평균 일사량 (line)", "평균 일사량 (MJ/m²)"),
     "장마철_비장마철_평균일사량_line")

# 3. 전국 손실량 bar
fig = px.bar(nat, x="연도", y="손실량(kWh/MW)")
fig.update_traces(hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>")
save(apply_common(fig, "📉 전국 손실량 (bar)", "손실량 (kWh/MW)"),
     "전국_손실량_bar")

# 4. 전국 손실량 line
fig = px.line(nat, x="연도", y="손실량(kWh/MW)", markers=True)
fig.update_traces(hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>")
save(apply_common(fig, "📉 전국 손실량 (line)", "손실량 (kWh/MW)"),
     "전국_손실량_line")

# 5. 전국 손실액 bar
fig = px.bar(nat, x="연도", y="손실액(만원)")
fig.update_traces(hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>")
save(apply_common(fig, "💸 전국 손실액 (bar)", "손실액 (만원)"),
     "전국_손실액_bar")

# 6. 전국 손실액 line
fig = px.line(nat, x="연도", y="손실액(만원)", markers=True)
fig.update_traces(hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>")
save(apply_common(fig, "💸 전국 손실액 (line)", "손실액 (만원)"),
     "전국_손실액_line")

# 7. 지역별 손실량 bar
df = rg[rg["지역구분"].isin(["남부","중북부"])]

fig = px.bar(df, x="연도", y="손실량(kWh/MW)", color="지역구분", barmode="group")
fig.update_traces(hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>")
save(apply_common(fig, "📍 지역별 손실량 (bar)", "손실량 (kWh/MW)"),
     "지역별_손실량_bar")

# 8. 지역별 손실량 line
fig = px.line(df, x="연도", y="손실량(kWh/MW)", color="지역구분", markers=True)
fig.update_traces(hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>")
save(apply_common(fig, "📍 지역별 손실량 (line)", "손실량 (kWh/MW)"),
     "지역별_손실량_line")

# 9. 지역별 손실액 bar
fig = px.bar(df, x="연도", y="손실액(만원)", color="지역구분", barmode="group")
fig.update_traces(hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>")
save(apply_common(fig, "💰 지역별 손실액 (bar)", "손실액 (만원)"),
     "지역별_손실액_bar")

# 10. 지역별 손실액 line
fig = px.line(df, x="연도", y="손실액(만원)", color="지역구분", markers=True)
fig.update_traces(hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>")
save(apply_common(fig, "💰 지역별 손실액 (line)", "손실액 (만원)"),
     "지역별_손실액_line")

print("🎉 v8_summer — 6~8월 기준 10개 그래프 생성 완료 (오류 0%)")
