import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ===== 데이터 불러오기 =====
weather = pd.read_csv("data/2020~2024.csv", encoding="utf-8")
pred = pd.read_csv("data/예측발전량_PR고정_수정.csv", encoding="utf-8")

weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce")
pred["일시"] = pd.to_datetime(pred["일시"], errors="coerce")

merged = pd.merge(pred, weather, on=["지점명", "일시"], how="inner")

output_dir = "./그래프_저장"
os.makedirs(output_dir, exist_ok=True)
plt.rc("font", family="Malgun Gothic")

# ① 산점도 + 회귀선
plt.figure(figsize=(6,5))
sns.regplot(x="일강수량(mm)", y="예측발전량_PR고정(kWh)", data=merged, scatter_kws={"alpha":0.4})
plt.title("강수량 vs 예측 발전량 (회귀선 포함)")
plt.xlabel("일강수량 (mm)")
plt.ylabel("예측 발전량 (kWh)")
plt.savefig(os.path.join(output_dir, "강수량_vs_예측발전량.png"), dpi=300)
plt.close()

# ② Boxplot
merged["강수량_구간"] = pd.cut(merged["일강수량(mm)"], bins=[0, 1, 5, 10, 20, 50, 200], include_lowest=True)
plt.figure(figsize=(6,5))
sns.boxplot(x="강수량_구간", y="예측발전량_PR고정(kWh)", data=merged)
plt.title("강수량 구간별 예측 발전량 분포")
plt.xlabel("강수량 구간 (mm)")
plt.ylabel("예측 발전량 (kWh)")
plt.savefig(os.path.join(output_dir, "강수량구간별_예측발전량.png"), dpi=300)
plt.close()

# ③ 누적 평균 그래프
merged_sorted = merged.sort_values("일강수량(mm)")
merged_sorted["누적평균_발전량"] = merged_sorted["예측발전량_PR고정(kWh)"].expanding().mean()
plt.figure(figsize=(6,5))
plt.plot(merged_sorted["일강수량(mm)"], merged_sorted["누적평균_발전량"], color="orange")
plt.title("강수량 증가에 따른 누적 평균 발전량 변화")
plt.xlabel("일강수량 (mm)")
plt.ylabel("누적 평균 발전량 (kWh)")
plt.savefig(os.path.join(output_dir, "누적평균_그래프.png"), dpi=300)
plt.close()

print(f"✅ 그래프 3개가 '{output_dir}' 폴더에 저장되었습니다!")
