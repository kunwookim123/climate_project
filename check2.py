import pandas as pd

df = pd.read_csv("data/2020~2024_수정본.csv", encoding="utf-8")

# 1️⃣ 일시 포맷 확인
print(df["일시"].head())
print("일시 파싱 성공 비율:", pd.to_datetime(df["일시"], errors="coerce").notna().mean())

# 2️⃣ 합계 일사량 값 확인
print(df["합계 일사량(MJ/m2)"].describe())

# 3️⃣ 지점명 예시 확인
print(df["지점명"].unique()[:30])
