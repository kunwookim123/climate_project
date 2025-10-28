import pandas as pd

# 파일 목록
files = [
    "data/20251028_2020년도+신규+설비용량+현황.xls",
    "data/20251028_2021년도+신규+설비용량+현황.xls",
    "data/20251028_2022년도+신규+설비용량+현황.xls",
    "data/20251028_2023년도+신규+설비용량+현황.xls",
    "data/20251028_2024년도+신규+설비용량+현황.xls",
]

merged = []

for file in files:
    try:
        df = pd.read_excel(file, engine="xlrd")  # 구버전 .xls 읽기
    except Exception:
        df = pd.read_html(file)[0]  # 만약 xlrd 실패 시 HTML 테이블처럼 읽기 (대체 방법)
    
    year = file.split("_")[1][:4]  # 파일명에서 연도 추출
    df["연도"] = year
    merged.append(df)

# 병합
merged_df = pd.concat(merged, ignore_index=True)

# CSV로 저장
output_path = "data/2020_2024_신규_설비용량_병합.csv"
merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

output_path
