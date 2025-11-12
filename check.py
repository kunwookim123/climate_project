import pandas as pd

# 파일 불러오기
data = pd.read_csv(r"C:\Users\UserK\Documents\GitHub\climate_project\data\2020~2024_수정본.csv", encoding="utf-8")
data["일시"] = pd.to_datetime(data["일시"], errors="coerce")

# 장마 기간 정의
rainy_periods = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-07-03", "2021-07-26"),
    2022: ("2022-06-23", "2022-07-26"),
    2023: ("2023-06-25", "2023-07-30"),
    2024: ("2024-06-23", "2024-07-28"),
}

# 결과 저장용
results = []

for year, (start, end) in rainy_periods.items():
    year_data = data[data["일시"].dt.year == year]
    if year_data.empty:
        continue

    start, end = pd.to_datetime(start), pd.to_datetime(end)

    # 장마철 / 비장마철 구분
    rainy = year_data[(year_data["일시"] >= start) & (year_data["일시"] <= end)]
    non_rainy = year_data[(year_data["일시"] < start) | (year_data["일시"] > end)]

    # 평균 계산 (결측 제외)
    rainy_mean = rainy["합계 일사량(MJ/m2)"].dropna().mean()
    non_rainy_mean = non_rainy["합계 일사량(MJ/m2)"].dropna().mean()
    diff = non_rainy_mean - rainy_mean

    results.append({
        "연도": year,
        "장마철 평균 일사량(MJ/m2)": round(rainy_mean, 2),
        "비장마철 평균 일사량(MJ/m2)": round(non_rainy_mean, 2),
        "차이(비장마 - 장마)": round(diff, 2)
    })

# 결과 테이블 출력
result_df = pd.DataFrame(results)
print(result_df)
