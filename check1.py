import pandas as pd
import plotly.express as px

# ===== 1️⃣ 데이터 불러오기 =====
weather = pd.read_csv("data/2020~2024.csv", encoding="utf-8")
power = pd.read_csv("data/예측발전량_PR고정_수정.csv", encoding="utf-8")

# ===== 2️⃣ 날짜 변환 =====
weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce", format="mixed")
power["일시"] = pd.to_datetime(power["일시"], errors="coerce", format="mixed")

# ===== 3️⃣ 병합 =====
merged = pd.merge(
    power,
    weather[["지점명", "일시", "일강수량(mm)", "합계 일사량(MJ/m2)"]],
    on=["지점명", "일시"],
    how="inner"
)

# ===== 4️⃣ 실제 컬럼명 확인 (자동으로 처리) =====
for col in merged.columns:
    if "일사량" in col:
        irr_col = col
        break

print(f"✅ 실제 일사량 컬럼명 인식됨: {irr_col}")

# ===== 5️⃣ 결측치 제거 =====
merged = merged.dropna(subset=[irr_col, "예측발전량_PR고정(kWh)"])

# ===== 6️⃣ 장마철 구분 =====
rainy_periods = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-07-03", "2021-07-26"),
    2022: ("2022-06-23", "2022-07-26"),
    2023: ("2023-06-25", "2023-07-30"),
    2024: ("2024-06-23", "2024-07-28"),
}

def 장마여부(dt):
    y = dt.year
    if y in rainy_periods:
        s, e = pd.to_datetime(rainy_periods[y][0]), pd.to_datetime(rainy_periods[y][1])
        return "장마철" if s <= dt <= e else "비장마철"
    return "비장마철"

merged["장마철여부"] = merged["일시"].apply(장마여부)
merged["연도"] = merged["일시"].dt.year

# ===== 7️⃣ 평균 일사량 계산 =====
avg_irr = (
    merged.groupby(["연도", "장마철여부"])[irr_col]
    .mean()
    .reset_index()
)

# ===== 8️⃣ 비장마 - 장마 일사량 차이 및 발전량 손실 계산 =====
result = avg_irr.pivot(index="연도", columns="장마철여부", values=irr_col).reset_index()
result["일사량 감소(MJ/m2)"] = result["비장마철"] - result["장마철"]
result["예상 발전량 손실(kWh)"] = result["일사량 감소(MJ/m2)"] * 20.835

print("\n✅ 연도별 장마철 vs 비장마철 평균 일사량 및 발전량 손실 추정")
print(result.round(3))

# ===== 9️⃣ 시각화 =====
fig = px.bar(
    avg_irr,
    x="연도",
    y=irr_col,
    color="장마철여부",
    barmode="group",
    text=irr_col,
    color_discrete_map={"장마철": "#1f77b4", "비장마철": "#ff7f0e"},
    title="☀️ 연도별 장마철 vs 비장마철 평균 일사량 비교",
    labels={irr_col: "평균 일사량 (MJ/m²)"}
)

fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', opacity=0.85)
fig.update_layout(
    yaxis_title="평균 일사량 (MJ/m²)",
    xaxis_title="연도",
    legend_title="기간 구분",
    template="plotly_white"
)

fig.show()
