import pandas as pd

weather = pd.read_csv("data/2020~2024.csv", encoding="utf-8")
power = pd.read_csv("data/예측발전량_PR고정_수정.csv", encoding="utf-8")

print("✅ weather 컬럼 목록:", weather.columns.tolist())
print("✅ power 컬럼 목록:", power.columns.tolist())