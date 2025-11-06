import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# ====== 경로 설정 ======
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"

# ====== 데이터 불러오기 ======
weather = pd.read_csv(f"{base_path}\\2020~2024.csv", encoding="utf-8")
pred = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")

weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce")
pred["일시"] = pd.to_datetime(pred["일시"], errors="coerce")

merged = pd.merge(pred, weather, on=["지점명", "일시"], how="left")

# ====== 1️⃣ 산점도 + 회귀선 ======
x = merged["일강수량(mm)"]
y = merged["예측발전량_PR고정(kWh)"]

coeffs = np.polyfit(x, y, 1)
line = np.poly1d(coeffs)
line_x = np.linspace(0, x.max(), 100)
line_y = line(line_x)

fig1 = go.Figure()

# 산점도
fig1.add_trace(go.Scatter(
    x=x, y=y,
    mode='markers',
    marker=dict(size=6, color=x, colorscale="Blues", opacity=0.6),
    name='데이터',
    hovertemplate='💧강수량: %{x:.1f}mm<br>⚡발전량: %{y:.2f}kWh<extra></extra>'
))

# 회귀선
fig1.add_trace(go.Scatter(
    x=line_x, y=line_y,
    mode='lines',
    name='회귀선',
    line=dict(color='red', width=2)
))

fig1.update_layout(
    title="💧 강수량과 ⚡ 예측 발전량의 상관관계",
    xaxis_title="일강수량 (mm)",
    yaxis_title="예측 발전량 (kWh)",
    template="plotly_white",
    legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.7)'),
    hovermode="closest"
)

# ====== 2️⃣+3️⃣ 강수량 구간별 평균 발전량 + 감소율 ======
merged["강수량_구간"] = pd.cut(
    merged["일강수량(mm)"],
    bins=[0, 1, 5, 10, 20, 999],
    labels=["0~1mm", "1~5mm", "5~10mm", "10~20mm", "20mm 이상"]
)

mean_power = merged.groupby("강수량_구간")["예측발전량_PR고정(kWh)"].mean().reset_index()
baseline = mean_power.iloc[0, 1]
mean_power["감소율(%)"] = (1 - mean_power["예측발전량_PR고정(kWh)"] / baseline) * 100

# --- 이중축 그래프 ---
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# 왼쪽: 평균 발전량 (꺾은선)
fig2.add_trace(go.Scatter(
    x=mean_power["강수량_구간"],
    y=mean_power["예측발전량_PR고정(kWh)"],
    name="평균 발전량 (kWh)",
    mode="lines+markers",
    line=dict(color="#FF7F0E", width=3),
    marker=dict(size=8, color="#FF7F0E"),
    hovertemplate="💧강수량 구간: %{x}<br>⚡평균 발전량: %{y:.2f}kWh<extra></extra>"
), secondary_y=False)

# 오른쪽: 감소율 (막대)
fig2.add_trace(go.Bar(
    x=mean_power["강수량_구간"],
    y=mean_power["감소율(%)"],
    name="감소율 (%)",
    marker_color="#1F77B4",
    opacity=0.6,
    hovertemplate="📉감소율: %{y:.1f}%<extra></extra>"
), secondary_y=True)

fig2.update_layout(
    title="⚡ 강수량 구간별 평균 발전량 및 감소율 비교",
    xaxis_title="강수량 구간 (mm)",
    yaxis_title="평균 발전량 (kWh)",
    template="plotly_white",
    legend=dict(x=0.05, y=0.95, bgcolor="rgba(255,255,255,0.7)"),
    hovermode="x unified"
)
fig2.update_yaxes(title_text="감소율 (%)", secondary_y=True)

# ====== HTML 각각 저장 ======
fig1.write_html(os.path.join(base_path, "1_산점도.html"))
fig2.write_html(os.path.join(base_path, "2_이중축그래프.html"))

# ====== 슬라이드 HTML 생성 ======
slides_html = f"""
<html>
<head>
<meta charset="utf-8">
<title>강수량 영향 분석 슬라이드</title>
<style>
body {{
  margin: 0;
  background-color: white;
  overflow: hidden;
}}
iframe {{
  width: 100%;
  height: 100vh;
  border: none;
}}
.page-number {{
  position: fixed;
  bottom: 20px;
  right: 40px;
  font-size: 18px;
  color: gray;
}}
</style>
<script>
let slides = ['1_산점도.html', '2_이중축그래프.html'];
let current = 0;
function showSlide(n) {{
  document.getElementById('frame').src = slides[n];
  document.getElementById('page').innerText = (n+1) + '/' + slides.length;
}}
document.addEventListener('keydown', (e) => {{
  if (e.key === ' ' || e.key === 'ArrowRight') {{
    current = (current + 1) % slides.length;
    showSlide(current);
  }} else if (e.key === 'ArrowLeft') {{
    current = (current - 1 + slides.length) % slides.length;
    showSlide(current);
  }}
}});
window.onload = () => showSlide(0);
</script>
</head>
<body>
<iframe id="frame"></iframe>
<div id="page" class="page-number"></div>
</body>
</html>
"""

slide_path = os.path.join(base_path, "강수량_영향분석_슬라이드.html")
with open(slide_path, "w", encoding="utf-8") as f:
    f.write(slides_html)

print(f"✅ 슬라이드 생성 완료: {slide_path}")
