import pandas as pd
from sklearn.linear_model import LinearRegression

# ===== 파일 경로 =====
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"
weather = pd.read_csv(f"{base_path}\\2020~2024.csv", encoding="utf-8")
power = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")

# ===== 일시 통일 및 병합 =====
weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce")
power["일시"] = pd.to_datetime(power["일시"], errors="coerce")

merged = pd.merge(
    power[["지점명", "일시", "예측발전량_PR고정(kWh)"]],
    weather[["지점명", "일시", "합계 일사량(MJ/m2)"]],
    on=["지점명", "일시"],
    how="inner"
).dropna()

# ===== 회귀 분석 =====
X = merged[["합계 일사량(MJ/m2)"]]
y = merged["예측발전량_PR고정(kWh)"]

model = LinearRegression()
model.fit(X, y)

coef = model.coef_[0]
intercept = model.intercept_

# ===== 결과 출력 =====
print(f"✅ 회귀식: 발전량(kWh) = {coef:.3f} × 일사량(MJ/m²) + {intercept:.3f}")
print(f"👉 즉, 1 MJ/m² 증가 시 약 {coef:.3f} kWh 증가 (기존 20.835와 비교 가능)")
