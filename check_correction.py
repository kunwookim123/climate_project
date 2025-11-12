import pandas as pd
import numpy as np

# ===== 1️⃣ 파일 불러오기 =====
file_path = "data/2020~2024_수정본.csv"  # 실제 경로 맞게 수정
data = pd.read_csv(file_path)

# ===== 2️⃣ 일시 변환 =====
data["일시"] = pd.to_datetime(data["일시"], errors="coerce")
data["연도"] = data["일시"].dt.year  # ✅ 추가: 연도 컬럼 생성

# ===== 3️⃣ 비가 없는데 일사량이 0인 경우 결측 처리 =====
mask = (data["일강수량(mm)"] == 0) & (data["합계 일사량(MJ/m2)"] == 0)
data.loc[mask, "합계 일사량(MJ/m2)"] = np.nan

# ===== 4️⃣ 지점별 보간 =====
data = data.sort_values(["지점명", "일시"])
data["합계 일사량(MJ/m2)"] = (
    data.groupby("지점명")["합계 일사량(MJ/m2)"]
    .transform(lambda x: x.interpolate(method="linear", limit_direction="both"))
)

# ===== 5️⃣ 기상청 기준 장마철 구분 =====
def monsoon_period(row):
    y, date = row["연도"], row["일시"]
    if y == 2020 and pd.Timestamp(2020, 6, 24) <= date <= pd.Timestamp(2020, 8, 16):
        return "장마철"
    elif y == 2021 and pd.Timestamp(2021, 7, 3) <= date <= pd.Timestamp(2021, 7, 26):
        return "장마철"
    elif y == 2022 and pd.Timestamp(2022, 6, 23) <= date <= pd.Timestamp(2022, 7, 26):
        return "장마철"
    elif y == 2023 and pd.Timestamp(2023, 6, 25) <= date <= pd.Timestamp(2023, 7, 29):
        return "장마철"
    elif y == 2024 and pd.Timestamp(2024, 6, 21) <= date <= pd.Timestamp(2024, 7, 23):
        return "장마철"
    else:
        return "비장마철"

data["장마철여부"] = data.apply(monsoon_period, axis=1)

# ===== 6️⃣ 연도별 장마철 vs 비장마철 평균 일사량 계산 =====
annual_means = (
    data.groupby(["연도", "장마철여부"])["합계 일사량(MJ/m2)"]
    .mean()
    .reset_index()
    .pivot(index="연도", columns="장마철여부", values="합계 일사량(MJ/m2)")
    .reset_index()
)

# ===== 7️⃣ CSV 저장 =====
output_path = "data/2020~2024_revised_monsoon.csv"
data.to_csv(output_path, index=False, encoding="utf-8-sig")

print("✅ 기상청 기준 장마철 반영 완료!")
print("📁 저장 위치:", output_path)
print("\n📊 연도별 평균 일사량 (장마철 vs 비장마철):")
print(annual_means.round(2))
