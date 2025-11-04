import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

# ===== 한글 폰트 설정 =====
font_path = "C:/Windows/Fonts/malgun.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)
plt.rcParams['axes.unicode_minus'] = False

# ===== 데이터 불러오기 =====
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"
weather = pd.read_csv(f"{base_path}\\2020~2024.csv", encoding="utf-8")
pred = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")

# ===== 날짜 처리 =====
weather["일시"] = pd.to_datetime(weather["일시"])
pred["일시"] = pd.to_datetime(pred["일시"])

# ===== 병합 =====
merged = pd.merge(pred, weather, on=["지점명", "일시"], how="left")

# ===== 장마 기간 정의 =====
rainy_periods = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-07-03", "2021-07-26"),
    2022: ("2022-06-23", "2022-07-26"),
    2023: ("2023-06-25", "2023-07-30"),
    2024: ("2024-06-23", "2024-07-28"),
}

# ===== 장마/비장마 구분 컬럼 생성 =====
merged["기간구분"] = "비장마철"
for year, (start, end) in rainy_periods.items():
    mask = (merged["일시"] >= pd.to_datetime(start)) & (merged["일시"] <= pd.to_datetime(end))
    merged.loc[mask, "기간구분"] = "장마철"

# ===== 그래프 =====
plt.figure(figsize=(10, 7))
sns.scatterplot(
    data=merged,
    x="일강수량(mm)",
    y="예측발전량_PR고정(kWh)",
    hue="기간구분",
    alpha=0.4,
    palette={"장마철": "#1F77B4", "비장마철": "#FF7F0E"}
)

# 회귀선 (선형추세)
sns.regplot(
    data=merged[merged["기간구분"] == "장마철"],
    x="일강수량(mm)",
    y="예측발전량_PR고정(kWh)",
    scatter=False,
    color="#1F77B4",
    line_kws={"lw": 2, "label": "장마철 추세선"}
)

sns.regplot(
    data=merged[merged["기간구분"] == "비장마철"],
    x="일강수량(mm)",
    y="예측발전량_PR고정(kWh)",
    scatter=False,
    color="#FF7F0E",
    line_kws={"lw": 2, "label": "비장마철 추세선"}
)

plt.title("장마철 vs 비장마철 강수량과 예측 발전량 상관관계 비교", fontsize=15, fontweight="bold")
plt.xlabel("일강수량 (mm)", fontsize=12)
plt.ylabel("예측 발전량 (kWh)", fontsize=12)
plt.legend(title="기간구분")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
