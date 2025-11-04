import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import numpy as np

# ===== 경로 설정 =====
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"
output_dir = os.path.join(base_path, "slides")
os.makedirs(output_dir, exist_ok=True)

# ===== 데이터 불러오기 =====
weather = pd.read_csv(f"{base_path}\\2020~2024.csv", encoding="utf-8")
pred = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")
coords = pd.read_csv(f"{base_path}\\좌표.csv", encoding="utf-8")

# ===== 날짜 처리 =====
weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce")
pred["일시"] = pd.to_datetime(pred["일시"], errors="coerce")

# ===== 병합 =====
merged = pd.merge(pred, weather, on=["지점명", "일시"], how="left")
merged = pd.merge(merged, coords, on="지점명", how="left")

# ===== 장마철 직접 지정 날짜 =====
rainy_days_fixed = {
    2020: "2020-07-13",
    2021: "2021-07-03",
    2022: "2022-07-09",
    2023: "2023-07-18",
    2024: "2024-06-29"
}

# ===== 장마 기간 참고용 (비장마 구분용) =====
rainy_periods = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-07-03", "2021-07-26"),
    2022: ("2022-06-23", "2022-07-26"),
    2023: ("2023-06-25", "2023-07-30"),
    2024: ("2024-06-23", "2024-07-28"),
}

# ===== 색상 스케일 (진한 색상 적용) =====
rain_scale = [[0, "#9ecae1"], [0.4, "#3182bd"], [1, "#08306b"]]  # 파랑 계열
power_scale = [[0, "#fed976"], [0.5, "#fd8d3c"], [1, "#bd0026"]]  # 주황-빨강 계열

# ===== 지도 생성 함수 =====
def make_map(data, date, label):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"☔ 일강수량 (mm) — {label}",
                        f"⚡ 예측 발전량 (kWh) — {label}"),
        specs=[[{"type": "scattermap"}, {"type": "scattermap"}]],
        horizontal_spacing=0.02
    )

    # --- 왼쪽 지도 (강수량) ---
    fig.add_trace(
        go.Scattermap(
            lat=data["위도"], lon=data["경도"],
            text=[f"{r['지점명']} : {r['일강수량(mm)']}mm" for _, r in data.iterrows()],
            hoverinfo="text",
            marker=dict(
                size=np.clip(data["일강수량(mm)"] / data["일강수량(mm)"].max() * 45 + 6, 6, 45),
                color=data["일강수량(mm)"],
                colorscale=rain_scale,
                cmin=0, cmax=data["일강수량(mm)"].max(),
                opacity=1.0,
                showscale=False
            ),
            name="일강수량"
        ),
        row=1, col=1
    )

    # --- 오른쪽 지도 (예측 발전량) ---
    fig.add_trace(
        go.Scattermap(
            lat=data["위도"], lon=data["경도"],
            text=[f"{r['지점명']} : {r['예측발전량_PR고정(kWh)']:.2f}kWh" for _, r in data.iterrows()],
            hoverinfo="text",
            marker=dict(
                size=np.clip(data["예측발전량_PR고정(kWh)"] / data["예측발전량_PR고정(kWh)"].max() * 45 + 6, 6, 45),
                color=data["예측발전량_PR고정(kWh)"],
                colorscale=power_scale,
                cmin=0, cmax=data["예측발전량_PR고정(kWh)"].max(),
                opacity=1.0,
                showscale=False
            ),
            name="예측 발전량"
        ),
        row=1, col=2
    )

    # --- 지도 스타일 ---
    fig.update_layout(
        map=dict(style="open-street-map", center=dict(lat=36, lon=128), zoom=6),
        map2=dict(style="open-street-map", center=dict(lat=36, lon=128), zoom=6),
        height=900,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        title=dict(text=f"강수량과 예측 발전량 비교 — {label}",
                   font=dict(size=22, family="Malgun Gothic", color="black")),
        font=dict(color="black"),
        margin=dict(l=20, r=20, t=80, b=20)
    )

    save_path = os.path.join(output_dir, f"{label.replace('-', '_')}.png")
    fig.write_image(save_path, scale=2)
    print(f"✅ 저장 완료: {save_path}")

# ===== 지도 생성 =====
for year, date_str in rainy_days_fixed.items():
    date = pd.to_datetime(date_str)
    rain_data = merged[merged["일시"].dt.date == date.date()]
    if not rain_data.empty:
        make_map(rain_data, date, f"장마_{year}-{date.month:02d}-{date.day:02d}")

    # 비장마철 구간
    start, end = pd.to_datetime(rainy_periods[year][0]), pd.to_datetime(rainy_periods[year][1])
    non_rainy = merged[
        (merged["일시"].dt.year == year) &
        ((merged["일시"] < start) | (merged["일시"] > end)) &
        (merged["일강수량(mm)"].between(0.5, 5))
    ]

    if not non_rainy.empty:
        random_day = non_rainy["일시"].sample(1, random_state=42).iloc[0]
        non_rainy_data = merged[merged["일시"] == random_day]
        make_map(non_rainy_data, random_day, f"비장마_{year}-{random_day.month:02d}-{random_day.day:02d}")

print("\n🎉 지정한 장마철 및 비장마철 지도 이미지가 모두 생성되었습니다!")
print(f"📁 저장 위치: {output_dir}")
