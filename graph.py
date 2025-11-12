import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# ===== 파일 경로 =====
weather_path = "data/2020~2024_수정본.csv"
power_path = "data/예측발전량_PR가변_수정.csv"
OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

# ===== CSV 로드 =====
weather = pd.read_csv(weather_path, encoding="utf-8")
power = pd.read_csv(power_path, encoding="utf-8")

# ===== 일시 파싱 =====
for df in [weather, power]:
    df["일시"] = pd.to_datetime(df["일시"], errors="coerce")

# ===== 지점명 → 시도명 매핑 =====
mapping = {
    "서울":"서울특별시","인천":"인천광역시","수원":"경기도","성남":"경기도","안산":"경기도","의정부":"경기도",
    "동두천":"경기도","파주":"경기도","속초":"강원특별자치도","철원":"강원특별자치도","춘천":"강원특별자치도",
    "원주":"강원특별자치도","강릉":"강원특별자치도","청주":"충청북도","충주":"충청북도","서산":"충청남도",
    "대전":"대전광역시","세종":"세종특별자치시","전주":"전북특별자치도","군산":"전북특별자치도",
    "광주":"광주광역시","목포":"전라남도","여수":"전라남도","대구":"대구광역시","포항":"경상북도",
    "부산":"부산광역시","울산":"울산광역시","창원":"경상남도","진주":"경상남도","제주":"제주특별자치도"
}
weather["시도명"] = weather["지점명"].map(mapping).fillna("기타")

# ===== 지역구분 =====
north = ["경기도","강원특별자치도","충청북도","충청남도","세종특별자치시","대전광역시"]
south = ["전북특별자치도","전라남도","경상북도","경상남도","광주광역시","대구광역시","부산광역시","울산광역시","제주특별자치도"]

def classify_region(sido):
    if sido in north: return "중북부"
    if sido in south: return "남부"
    return "기타"

weather["지역구분"] = weather["시도명"].apply(classify_region)

# ===== 병합 =====
merged = pd.merge(weather, power, on=["지점명","일시"], how="inner")

# ===== 장마철 여부 =====
merged["월"] = merged["일시"].dt.month
merged["장마철여부"] = merged["월"].apply(lambda x: "장마철" if 6 <= x <= 7 else "비장마철")

# ===== 손실량 계산 =====
irr_col = [c for c in merged.columns if "합계 일사량" in c][0]
region_means = (
    merged[merged["지역구분"].isin(["중북부","남부"])]
    .groupby(["지역구분","장마철여부"])[irr_col]
    .mean()
    .unstack()
    .dropna()
)
region_means["손실량(kWh)"] = (region_means["비장마철"] - region_means["장마철"]) * 20.835
region_pivot = region_means.reset_index()

# ===== 강수량 구간별 PR 변화 =====
bins = [0, 1, 5, 10, 20, 50, 100, merged["일강수량(mm)"].max()]
labels = ["0~1","1~5","5~10","10~20","20~50","50~100","100+"]
merged["강수량_구간"] = pd.cut(merged["일강수량(mm)"], bins=bins, labels=labels, include_lowest=True)
pr_by_rain = merged.groupby("강수량_구간")["PR(가변)"].mean().reset_index()

# ===== 그래프1: PR(가변) 변화 =====
fig_pr = px.line(
    pr_by_rain, x="강수량_구간", y="PR(가변)", markers=True,
    title="💧 강수량 구간별 평균 PR(가변) 변화"
)
fig_pr.update_traces(
    line=dict(width=3, color="royalblue"),
    marker=dict(size=8, color="royalblue"),
    hovertemplate="강수량 구간: %{x}<br>평균 PR: %{y:.2f}%<extra></extra>"
)
fig_pr.update_layout(
    plot_bgcolor="rgb(240,245,255)",
    paper_bgcolor="rgb(240,245,255)",
    font=dict(size=14),
    template="plotly_white",
)

# ===== 그래프2: 손실량 =====
fig_loss = px.bar(
    region_pivot,
    x="지역구분", 
    y="손실량(kWh)",
    color="지역구분",
    color_discrete_map={
        "중북부": "royalblue",
        "남부": "lightskyblue"
    },
    text=region_pivot["손실량(kWh)"].round(1),
    title="🌦️ 중북부 vs 남부 — 장마철 손실량 비교"
)

fig_loss.update_traces(
    textposition="outside",
    marker_line_width=0,
    hovertemplate="지역: %{x}<br>손실량: %{y:.1f} kWh<extra></extra>"
)

fig_loss.update_layout(
    plot_bgcolor="rgb(245,248,255)",
    paper_bgcolor="rgb(245,248,255)",
    bargap=0.6,  # ✅ 막대 간격 넓히기 (폭 줄이기)
    showlegend=False,
    font=dict(size=14),
    template="plotly_white",
    xaxis_title="지역구분",
    yaxis_title="손실량 (kWh)"
)


# ===== HTML로만 저장 =====
pio.write_html(fig_pr, file=str(OUT_DIR / "강수량구간_PR_개선.html"), auto_open=True)
pio.write_html(fig_loss, file=str(OUT_DIR / "지역별_손실량_개선.html"), auto_open=True)
print("✅ 그래프 생성 완료: output 폴더에 저장됨")
