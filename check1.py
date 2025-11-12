import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# ===== 1️⃣ 데이터 로드 =====
weather = pd.read_csv("data/2020~2024_수정본.csv", encoding="utf-8")
power = pd.read_csv("data/예측발전량_PR가변_수정.csv", encoding="utf-8")

for df in [weather, power]:
    df["일시"] = pd.to_datetime(df["일시"], errors="coerce")

merged = pd.merge(weather, power, on=["지점명", "일시"], how="inner")

# ===== 2️⃣ 지역 분류 =====
north = ["경기도", "강원특별자치도", "충청북도", "충청남도", "세종특별자치시", "대전광역시"]
south = ["전북특별자치도", "전라남도", "경상북도", "경상남도", "광주광역시", "대구광역시", "부산광역시", "울산광역시", "제주특별자치도"]

def classify_region(name):
    for r in north:
        if r in name:
            return "중북부"
    for r in south:
        if r in name:
            return "남부"
    return "기타"

merged["지역구분"] = merged["지점명"].apply(classify_region)
print(merged["지역구분"].value_counts())

# ===== 3️⃣ 장마철 여부 =====
merged["월"] = merged["일시"].dt.month
merged["장마철여부"] = merged["월"].apply(lambda x: "장마철" if 6 <= x <= 7 else "비장마철")

# ===== 4️⃣ 손실량 계산 =====
region_stats = (
    merged.groupby(["지역구분", "장마철여부"])["합계 일사량(MJ/m2)_x"]
    .mean()
    .unstack()
    .dropna()
)
region_stats["손실량(kWh)"] = (region_stats["비장마철"] - region_stats["장마철"]) * 20.835
region_stats = region_stats.reset_index()

# ===== 5️⃣ 강수량 구간별 PR =====
bins = [0, 1, 5, 10, 20, 50, 100, 300]
labels = ["0~1", "1~5", "5~10", "10~20", "20~50", "50~100", "100+"]

merged["강수량_구간"] = pd.cut(merged["일강수량(mm)"], bins=bins, labels=labels, include_lowest=True)
pr_by_rain = merged.groupby("강수량_구간")["PR(가변)"].mean().reset_index()

# ===== 6️⃣ 그래프 1: 손실량 비교 =====
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=region_stats["지역구분"],
    y=region_stats["손실량(kWh)"],
    text=region_stats["손실량(kWh)"].round(1),
    textposition="outside",
    marker_color=["#4C72B0", "#DD8452"]
))
fig1.update_layout(
    title="🌦️ 중북부 vs 남부 지역 장마철 손실량 비교",
    xaxis_title="지역구분",
    yaxis_title="손실량 (kWh)",
    template="plotly_white"
)

# ===== 7️⃣ 그래프 2: 강수량 구간별 PR 변화 =====
fig2 = px.line(pr_by_rain, x="강수량_구간", y="PR(가변)",
               markers=True, title="💧 강수량 구간별 평균 PR 변화")
fig2.update_traces(line=dict(color="#2ca02c", width=3))
fig2.update_layout(template="plotly_white")

# ===== 8️⃣ HTML로 각각 저장 =====
Path("output").mkdir(exist_ok=True)

pio.write_html(fig1, file="output/손실량_비교.html", auto_open=True)
pio.write_html(fig2, file="output/PR_변화.html", auto_open=True)

print("✅ 그래프 저장 완료!")
print("📁 output/손실량_비교.html")
print("📁 output/PR_변화.html")
