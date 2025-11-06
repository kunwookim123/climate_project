import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ----------------------------
# ✅ 1. 데이터 불러오기
# ----------------------------
weather = pd.read_csv("data/2020~2024.csv", encoding="utf-8")
power = pd.read_csv("data/예측발전량_PR고정_수정.csv", encoding="utf-8")

# ----------------------------
# ✅ 2. 데이터 병합
# ----------------------------
merged = pd.merge(
    weather,
    power[["지점명", "일시", "예측발전량_PR고정(kWh)"]],
    on=["지점명", "일시"],
    how="inner"
)

# ----------------------------
# ✅ 3. 강수량 구간화 및 통계 계산
# ----------------------------
merged["강수량_구간"] = pd.cut(
    merged["일강수량(mm)"],
    bins=[-0.1, 0, 5, 10, 20, 30, 50, 80, 120, merged["일강수량(mm)"].max()],
    labels=["0", "0~5", "5~10", "10~20", "20~30", "30~50", "50~80", "80~120", "120+"],
)

mean_power = merged.groupby("강수량_구간")["예측발전량_PR고정(kWh)"].mean().reset_index()
max_power = mean_power["예측발전량_PR고정(kWh)"].max()
mean_power["감소율(%)"] = (1 - mean_power["예측발전량_PR고정(kWh)"] / max_power) * 100

# ----------------------------
# ✅ 4. 산점도 + 회귀선 그래프
# ----------------------------
fig1 = px.scatter(
    merged,
    x="일강수량(mm)",
    y="예측발전량_PR고정(kWh)",
    opacity=0.4,
    trendline="ols",
    color_discrete_sequence=["#1f77b4"]
)
fig1.update_layout(
    title="☀️ 강수량과 예측 발전량의 관계",
    xaxis_title="일강수량 (mm)",
    yaxis_title="예측 발전량 (kWh)",
    template="plotly_white",
)

# ----------------------------
# ✅ 5. 평균 발전량 + 감소율 (이중축 그래프)
# ----------------------------
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(
    go.Scatter(
        x=mean_power["강수량_구간"],
        y=mean_power["예측발전량_PR고정(kWh)"],
        name="평균 예측 발전량 (kWh)",
        mode="lines+markers",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=8),
        hovertemplate="강수량: %{x}<br>발전량: %{y:.1f} kWh"
    ),
    secondary_y=False
)
fig2.add_trace(
    go.Bar(
        x=mean_power["강수량_구간"],
        y=mean_power["감소율(%)"],
        name="감소율 (%)",
        marker_color="rgba(255,100,100,0.5)",
        hovertemplate="감소율: %{y:.1f}%"
    ),
    secondary_y=True
)
fig2.update_layout(
    title="⚡ 강수량 구간별 평균 예측 발전량 및 감소율",
    xaxis_title="강수량 구간 (mm)",
    yaxis_title="평균 예측 발전량 (kWh)",
    template="plotly_white",
    legend=dict(x=0.02, y=0.98),
)
fig2.update_yaxes(title_text="평균 예측 발전량 (kWh)", secondary_y=False)
fig2.update_yaxes(title_text="감소율 (%)", secondary_y=True)

# ----------------------------
# ✅ 6. HTML 슬라이드로 내보내기
# ----------------------------
html_content = f"""
<html>
<head>
  <title>🌧 강수량이 태양광 발전에 미치는 영향</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    body {{
        background-color: #ffffff;
        color: #333;
        text-align: center;
        font-family: 'Noto Sans KR', sans-serif;
        margin: 0;
    }}
    .slide {{
        display: none;
    }}
    .active {{
        display: block;
    }}
  </style>
</head>
<body>
  <div class="slide active" id="slide1">{fig1.to_html(include_plotlyjs=False, full_html=False)}</div>
  <div class="slide" id="slide2">{fig2.to_html(include_plotlyjs=False, full_html=False)}</div>

  <script>
    const slides = document.querySelectorAll('.slide');
    let current = 0;
    document.addEventListener('keydown', (e) => {{
        if (e.key === ' ' || e.key === 'ArrowRight') {{
            slides[current].classList.remove('active');
            current = (current + 1) % slides.length;
            slides[current].classList.add('active');
        }}
        if (e.key === 'ArrowLeft') {{
            slides[current].classList.remove('active');
            current = (current - 1 + slides.length) % slides.length;
            slides[current].classList.add('active');
        }}
    }});
  </script>
</body>
</html>
"""

with open("강수량_영향분석_슬라이드.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ 슬라이드 파일 생성 완료! → 강수량_영향분석_슬라이드.html")
