# -*- coding: utf-8 -*-
"""
economic_loss_final_v7_full.py
🔥 CSV 상태에 관계없이 연도 컬럼 자동 복구 (KeyError 완전 제거)
🔥 장마철/비장마철 + 전국/지역 손실량·손실액 10개 그래프 자동 생성
🔥 제목 / 배경 / hover / x축 카테고리 등 시각화 패치 포함
"""

import pandas as pd
import numpy as np
import plotly.express as px
import os

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
# 🔥 연도 복구 유틸 (v7 핵심)
# -------------------------------------------------------
def ensure_year(df):
    # index가 연도인 경우
    if df.index.name == "연도":
        df = df.reset_index()

    # suffix 있는 경우
    if "연도_y" in df.columns:
        df["연도"] = df["연도_y"]
    elif "연도_x" in df.columns:
        df["연도"] = df["연도_x"]

    # 연도 없으면 생성
    if "연도" not in df.columns:
        if "일시" in df.columns:
            df["연도"] = pd.to_datetime(df["일시"], errors="coerce").dt.year
        else:
            date_cols = [c for c in df.columns if "일" in c or "date" in c.lower()]
            if date_cols:
                df["연도"] = pd.to_datetime(df[date_cols[0]], errors="coerce").dt.year
            else:
                df["연도"] = -1  # 최후 fallback

    df = df.drop(columns=["연도_x", "연도_y"], errors="ignore")
    return df


# -------------------------------------------------------
# 데이터 불러오기 + 날짜 처리
# -------------------------------------------------------
weather = pd.read_csv(DATA_WEATHER)
power   = pd.read_csv(DATA_POWER)
cap     = pd.read_csv(DATA_CAP)
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
    how="left"   # left로 변경해 데이터 누락 방지
)

merged = ensure_year(merged)


# -------------------------------------------------------
# 일사량 컬럼 정리
# -------------------------------------------------------
cols = merged.columns

if "합계 일사량(MJ/m2)_y" in cols:
    merged["합계 일사량(MJ/m2)"] = merged["합계 일사량(MJ/m2)_y"]
elif "합계 일사량(MJ/m2)_x" in cols:
    merged["합계 일사량(MJ/m2)"] = merged["합계 일사량(MJ/m2)_x"]
elif "합계 일사량(MJ/m2)" not in cols:
    merged["합계 일사량(MJ/m2)"] = np.nan

merged = merged.drop(columns=[c for c in cols if "_x" in c or "_y" in c], errors="ignore")
merged["합계 일사량(MJ/m2)"] = pd.to_numeric(merged["합계 일사량(MJ/m2)"], errors="coerce")


# -------------------------------------------------------
# 전국 평균 일사량
# -------------------------------------------------------
nat = (
    merged.groupby(["연도","장마철여부"])["합계 일사량(MJ/m2)"]
    .mean()
    .reset_index()
)

nat = ensure_year(nat)
nat = nat.replace({True:"장마철", False:"비장마철"})

nat = nat.pivot(index="연도", columns="장마철여부",
                values="합계 일사량(MJ/m2)").reset_index()

nat = ensure_year(nat)

nat["차이"] = nat["비장마철"] - nat["장마철"]
nat["손실량(kWh/MW)"] = nat["차이"] * 20.835


# -------------------------------------------------------
# 전국 설비용량 + 손실액
# -------------------------------------------------------
cap = ensure_year(cap)

cap_total = cap.set_index("연도").sum(axis=1).reset_index()
cap_total.columns = ["연도","총설비용량(MW)"]
cap_total = ensure_year(cap_total)

nat = nat.merge(cap_total, on="연도", how="left")
nat = ensure_year(nat)

nat["총손실량(kWh)"] = nat["손실량(kWh/MW)"] * nat["총설비용량(MW)"]

SMP = {2020:68.87, 2021:94.34, 2022:196.65, 2023:167.11, 2024:128.39}
nat["SMP"] = nat["연도"].map(SMP)
nat["손실액(만원)"] = nat["총손실량(kWh)"] * nat["SMP"] / 10000


# -------------------------------------------------------
# 지역구분 태깅
# -------------------------------------------------------
SOUTH = ["전라","경상","부산","울산","광주","대구","제주"]
NC    = ["서울","경기","인천","강원","충청","세종","대전"]

def tag_region(x):
    if isinstance(x, str):
        if any(k in x for k in SOUTH): return "남부"
        if any(k in x for k in NC):    return "중북부"
    return "기타"

merged["지역구분"] = merged["시도"].apply(tag_region)


# -------------------------------------------------------
# 지역 평균 일사량
# -------------------------------------------------------
rg = (
    merged.groupby(["연도","지역구분","장마철여부"])["합계 일사량(MJ/m2)"]
    .mean()
    .reset_index()
)

rg = ensure_year(rg)
rg = rg.replace({True:"장마철", False:"비장마철"})

rg = rg.pivot(index=["연도","지역구분"], columns="장마철여부",
              values="합계 일사량(MJ/m2)").reset_index()

rg = ensure_year(rg)
rg["차이"] = rg["비장마철"] - rg["장마철"]
rg["손실량(kWh/MW)"] = rg["차이"] * 20.835


# -------------------------------------------------------
# 지역 설비용량 합산
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

rg["총손실량(kWh)"] = rg["손실량(kWh/MW)"] * rg["설비용량(MW)"]
rg["손실액(만원)"]   = rg["총손실량(kWh)"] * rg["연도"].map(SMP) / 10000


# -------------------------------------------------------
# 🔥 공통 스타일
# -------------------------------------------------------
def save(fig, name):
    fig.write_html(f"{OUTPUT_DIR}/{name}.html", include_plotlyjs="cdn")

def apply_common(fig, title, ytitle):
    fig.update_layout(
        title=dict(text=title, x=0.02, y=0.97, font=dict(size=26, color="#333333")),
        paper_bgcolor="#f4f4f4",
        plot_bgcolor="#fafafa",

        xaxis=dict(
            type="category",
            tickfont=dict(size=14, color="#444")
        ),
        yaxis=dict(
            title=ytitle,
            tickfont=dict(size=14, color="#444"),
            gridcolor="rgba(0,0,0,0.08)"
        ),

        legend_title="구분",
        legend=dict(
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),

        margin=dict(l=60, r=40, t=80, b=60),
    )
    return fig


# -------------------------------------------------------
# 🔥 그래프 10개 생성
# -------------------------------------------------------

# 1. 평균 일사량 bar
nat_m = nat[["연도","장마철","비장마철"]].melt(id_vars="연도",
                                            var_name="구분",
                                            value_name="평균일사량")

fig = px.bar(nat_m, x="연도", y="평균일사량", color="구분", barmode="group")
fig.update_traces(
    texttemplate=None,
    hovertemplate="연도 : %{x}<br>평균 일사량 : %{y:.1f} MJ/m²<extra></extra>"
)
save(apply_common(fig, "🌞 장마철/비장마철 평균 일사량 (bar)", "평균 일사량 (MJ/m²)"))


# 2. 평균 일사량 line
fig = px.line(nat_m, x="연도", y="평균일사량", color="구분", markers=True)
fig.update_traces(
    hovertemplate="연도 : %{x}<br>평균 일사량 : %{y:.1f} MJ/m²<extra></extra>"
)
save(apply_common(fig, "🌞 장마철/비장마철 평균 일사량 (line)", "평균 일사량 (MJ/m²)"))


# 3. 전국 손실량 bar
fig = px.bar(nat, x="연도", y="손실량(kWh/MW)")
fig.update_traces(
    texttemplate=None,
    hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>"
)
save(apply_common(fig, "📉 전국 손실량 (bar)", "손실량 (kWh/MW)"))


# 4. 전국 손실량 line
fig = px.line(nat, x="연도", y="손실량(kWh/MW)", markers=True)
fig.update_traces(
    hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>"
)
save(apply_common(fig, "📉 전국 손실량 (line)", "손실량 (kWh/MW)"))


# 5. 전국 손실액 bar
fig = px.bar(nat, x="연도", y="손실액(만원)")
fig.update_traces(
    texttemplate=None,
    hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>"
)
save(apply_common(fig, "💸 전국 손실액 (bar)", "손실액 (만원)"))


# 6. 전국 손실액 line
fig = px.line(nat, x="연도", y="손실액(만원)", markers=True)
fig.update_traces(
    hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>"
)
save(apply_common(fig, "💸 전국 손실액 (line)", "손실액 (만원)"))


# 7. 지역별 손실량 bar
df = rg[rg["지역구분"].isin(["남부","중북부"])]

fig = px.bar(df, x="연도", y="손실량(kWh/MW)", color="지역구분", barmode="group")
fig.update_traces(
    texttemplate=None,
    hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>"
)
save(apply_common(fig, "📍 지역별 손실량 (bar)", "손실량 (kWh/MW)"))


# 8. 지역별 손실량 line
fig = px.line(df, x="연도", y="손실량(kWh/MW)", color="지역구분", markers=True)
fig.update_traces(
    hovertemplate="연도 : %{x}<br>손실량 : %{y:.1f} kWh/MW<extra></extra>"
)
save(apply_common(fig, "📍 지역별 손실량 (line)", "손실량 (kWh/MW)"))


# 9. 지역별 손실액 bar
fig = px.bar(df, x="연도", y="손실액(만원)", color="지역구분", barmode="group")
fig.update_traces(
    texttemplate=None,
    hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>"
)
save(apply_common(fig, "💰 지역별 손실액 (bar)", "손실액 (만원)"))


# 10. 지역별 손실액 line
fig = px.line(df, x="연도", y="손실액(만원)", color="지역구분", markers=True)
fig.update_traces(
    hovertemplate="연도 : %{x}<br>손실액 : %{y:.1f} 만원<extra></extra>"
)
save(apply_common(fig, "💰 지역별 손실액 (line)", "손실액 (만원)"))

print("🎉 그래프 10개 생성 완료! (v7_full)")
