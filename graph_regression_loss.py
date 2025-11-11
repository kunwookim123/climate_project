import pandas as pd
import numpy as np

# === 파일 경로 ===
file_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data\2020~2024_보정.csv"
data = pd.read_csv(file_path, encoding="utf-8")

# === 날짜 처리 ===
data["일시"] = pd.to_datetime(data["일시"], errors="coerce")

# === 장마 기간 정의 ===
rainy_periods = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-07-03", "2021-07-26"),
    2022: ("2022-06-23", "2022-07-26"),
    2023: ("2023-06-25", "2023-07-30"),
    2024: ("2024-06-23", "2024-07-28"),
}

# === 연도별 평균 일사량 계산 ===
results = []
for year, (start, end) in rainy_periods.items():
    start, end = pd.to_datetime(start), pd.to_datetime(end)
    yearly = data[data["일시"].dt.year == year]

    rainy = yearly[(yearly["일시"] >= start) & (yearly["일시"] <= end)]
    non_rainy = yearly[(yearly["일시"] < start) | (yearly["일시"] > end)]

    rainy_mean = rainy["합계 일사량(MJ/m2)"].mean()
    non_rainy_mean = non_rainy["합계 일사량(MJ/m2)"].mean()

    loss = (non_rainy_mean - rainy_mean) * 20.835  # 발전 손실량 계산

    results.append({
        "연도": year,
        "장마철 평균 일사량": round(rainy_mean, 2),
        "비장마철 평균 일사량": round(non_rainy_mean, 2),
        "손실량(kWh)": round(loss, 2)
    })

# === 결과표 출력 ===
result_df = pd.DataFrame(results)
print("🌧 비장마철 대비 장마철 일사량 손실량")
print(result_df)

# === 시각화 ===
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Bar(
    x=result_df["연도"],
    y=result_df["손실량(kWh)"],
    name="예상 발전 손실량 (kWh)",
    marker_color="tomato"
))

fig.update_layout(
    title="연도별 장마철 발전 손실량 (비장마철 대비)",
    xaxis_title="연도",
    yaxis_title="손실량 (kWh)",
    template="plotly_white",
    font=dict(family="Malgun Gothic", size=14)
)

fig.show()
