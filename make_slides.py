import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# === 1️⃣ 데이터 불러오기 ===
weather = pd.read_csv("data/2020~2024.csv", encoding="utf-8")
power = pd.read_csv("data/예측발전량_PR고정_수정.csv", encoding="utf-8")

# === 2️⃣ 공통 키(지점명+일시)로 병합 ===
merged = pd.merge(
    weather[["지점명", "일시", "일강수량(mm)"]],
    power[["지점명", "일시", "예측발전량_PR고정(kWh)"]],
    on=["지점명", "일시"],
    how="inner"
)

# === 3️⃣ 강수량 구간 분류 ===
bins = [0, 1, 5, 10, 20, 50, 100, 200]
labels = ["0~1", "1~5", "5~10", "10~20", "20~50", "50~100", "100~200"]
merged["강수량_구간"] = pd.cut(merged["일강수량(mm)"], bins=bins, labels=labels, right=False)

# === 4️⃣ 평균 발전량 및 감소율 계산 ===
mean_power = merged.groupby("강수량_구간")["예측발전량_PR고정(kWh)"].mean().reset_index()
mean_power.rename(columns={"예측발전량_PR고정(kWh)": "평균발전량(kWh)"}, inplace=True)

baseline = mean_power.loc[0, "평균발전량(kWh)"]  # 기준: 첫 구간
mean_power["감소율(%)"] = (1 - (mean_power["평균발전량(kWh)"] / baseline)) * 100

# === 5️⃣ 그래프 생성 ===
# (1) 슬라이드1: 산점도 + 회귀선
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=merged["일강수량(mm)"],
    y=merged["예측발전량_PR고정(kWh)"],
    mode="markers",
    marker=dict(color="rgba(99, 158, 255, 0.4)", size=4),
    name="개별 데이터"
))

# 회귀선 추가
import numpy as np
coef = np.polyfit(merged["일강수량(mm)"], merged["예측발전량_PR고정(kWh)"], 1)
poly1d_fn = np.poly1d(coef)
x_vals = np.linspace(0, merged["일강수량(mm)"].max(), 100)
fig1.add_trace(go.Scatter(
    x=x_vals,
    y=poly1d_fn(x_vals),
    mode="lines",
    line=dict(color="red", width=2),
    name="회귀선"
))
fig1.update_layout(
    title="☔ 강수량 vs 예측 발전량 (산점도 + 회귀선)",
    xaxis_title="일강수량 (mm)",
    yaxis_title="예측 발전량 (kWh)",
    template="plotly_white"
)

# (2) 슬라이드2: 평균 발전량 + 감소율 (이중축)
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

fig2.add_trace(
    go.Scatter(
        x=mean_power["강수량_구간"],
        y=mean_power["평균발전량(kWh)"],
        mode="lines+markers",
        name="평균 발전량 (kWh)",
        line=dict(color="orange", width=3),
        marker=dict(size=8, color="orange", opacity=0.8)
    ),
    secondary_y=False,
)

fig2.add_trace(
    go.Bar(
        x=mean_power["강수량_구간"],
        y=mean_power["감소율(%)"],
        name="감소율 (%)",
        marker_color="rgba(200,50,50,0.5)",
        opacity=0.7
    ),
    secondary_y=True,
)

fig2.update_layout(
    title="⚡ 강수량 구간별 평균 발전량 및 감소율",
    xaxis_title="강수량 구간 (mm)",
    yaxis_title="평균 발전량 (kWh)",
    template="plotly_white",
    legend=dict(x=0.8, y=1.1, orientation="h"),
)
fig2.update_yaxes(title_text="평균 발전량 (kWh)", secondary_y=False)
fig2.update_yaxes(title_text="감소율 (%)", secondary_y=True)

# === 6️⃣ 슬라이드 HTML로 통합 ===
html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>강수량 & 예측 발전량 분석 슬라이드</title>
<style>
  body {{ margin:0; background:white; overflow:hidden; }}
  iframe {{ width:100vw; height:100vh; border:none; display:none; }}
  iframe.active {{ display:block; }}
</style>
</head>
<body>

<iframe srcdoc='{fig1.to_html(include_plotlyjs="cdn", full_html=False)}' class="active"></iframe>
<iframe srcdoc='{fig2.to_html(include_plotlyjs="cdn", full_html=False)}'></iframe>

<script>
let slides = document.querySelectorAll('iframe');
let i = 0;
document.addEventListener('keydown', e => {{
  if (e.key === ' ' || e.key === 'ArrowRight') {{
    slides[i].classList.remove('active');
    i = (i + 1) % slides.length;
    slides[i].classList.add('active');
  }} else if (e.key === 'ArrowLeft') {{
    slides[i].classList.remove('active');
    i = (i - 1 + slides.length) % slides.length;
    slides[i].classList.add('active');
  }}
}});
</script>

</body>
</html>
"""

Path("강수량_영향분석_슬라이드.html").write_text(html_code, encoding="utf-8")
print("✅ '강수량_영향분석_슬라이드.html' 파일이 생성되었습니다!")
