import os
import pandas as pd
import numpy as np

# =====================================
# 1️⃣ 기본 경로 설정
# =====================================
base_dir = r"C:/Users/UserK/Documents/GitHub/climate_project/data"
output_base = os.path.join(base_dir, "결측치보정")
os.makedirs(output_base, exist_ok=True)

# =====================================
# 2️⃣ 결측치 자동 대체 함수
# =====================================
def fill_missing_weather(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["지점명", "일시"]).reset_index(drop=True)

    # 일시를 datetime으로 변환
    if not np.issubdtype(df["일시"].dtype, np.datetime64):
        df["일시"] = pd.to_datetime(df["일시"], errors="coerce")

    # --- 1. 평균기온 ---
    if "평균기온(°C)" in df.columns:
        df["평균기온(°C)"] = (
            df.groupby("지점명")["평균기온(°C)"]
            .transform(lambda x: x.interpolate(method="linear", limit_direction="both"))
        )

    # --- 2. 월합강수량 ---
    if "월합강수량(00~24h만)(mm)" in df.columns:
        df["월합강수량(00~24h만)(mm)"] = (
            df.groupby(["지점명", df["일시"].dt.to_period("M")])["월합강수량(00~24h만)(mm)"]
            .transform(lambda x: x.fillna(x.mean()))
        )

    # --- 3. 평균풍속 ---
    if "평균풍속(m/s)" in df.columns:
        df["평균풍속(m/s)"] = (
            df.groupby("지점명")["평균풍속(m/s)"]
            .transform(lambda x: x.interpolate(method="linear", limit_direction="both"))
        )

    # --- 4. 평균운량 ---
    if "평균운량(1/10)" in df.columns:
        df["평균운량(1/10)"] = (
            df.groupby(["지점명", df["일시"].dt.to_period("M")])["평균운량(1/10)"]
            .transform(lambda x: x.fillna(x.mean()))
        )

    # --- 5. 합계 일조시간 ---
    if "합계 일조시간(hr)" in df.columns:
        df["합계 일조시간(hr)"] = (
            df.groupby("지점명")["합계 일조시간(hr)"]
            .transform(lambda x: x.fillna(x.mean()))
        )

    # --- 6. 일조율 ---
    if "일조율(%)" in df.columns:
        df["일조율(%)"] = (
            df.groupby("지점명")["일조율(%)"]
            .transform(lambda x: x.fillna(x.mean()))
        )

    # --- 7. 합계 일사량 ---
    if "합계 일사량(MJ/m2)" in df.columns and "합계 일조시간(hr)" in df.columns:
        def fill_solar(group):
            x = group["합계 일조시간(hr)"]
            y = group["합계 일사량(MJ/m2)"]
            if y.isna().all():
                return y
            valid = x.dropna().size > 1 and y.dropna().size > 1
            coef = np.corrcoef(x.dropna(), y.dropna())[0, 1] if valid else 0
            if coef > 0.7:
                mean_ratio = (y / x).median()
                return y.fillna(x * mean_ratio)
            else:
                return y.fillna(y.mean())
        df["합계 일사량(MJ/m2)"] = df.groupby("지점명", group_keys=False).apply(fill_solar)

    # --- 8. 평균지면온도 ---
    if "평균지면온도(°C)" in df.columns:
        df["평균지면온도(°C)"] = (
            df.groupby("지점명")["평균지면온도(°C)"]
            .transform(lambda x: x.interpolate(method="linear", limit_direction="both"))
        )

    # --- ✨ 모든 수치형 컬럼 반올림 (소수점 1자리) ---
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].round(1)

    return df


# =====================================
# 3️⃣ 연도별 / 요소별 일괄 처리
# =====================================
years = [2020, 2021, 2022, 2023, 2024]
elements = [
    "평균기온", "월합강수량", "평균풍속", "평균운량",
    "합계일조시간", "일조율", "합계일사량", "평균지면온도"
]

for year in years:
    year_folder = os.path.join(base_dir, str(year))
    output_year_folder = os.path.join(output_base, str(year))
    os.makedirs(output_year_folder, exist_ok=True)

    for element in elements:
        filename = f"{year}_{element}.csv"
        filepath = os.path.join(year_folder, filename)

        if not os.path.exists(filepath):
            print(f"⚠️ {filename} 없음 — 건너뜀")
            continue

        # CSV 읽기
        df = pd.read_csv(filepath, encoding="utf-8")

        # 결측치 보정
        df_filled = fill_missing_weather(df)

        # 저장 경로
        output_path = os.path.join(output_year_folder, f"결측치보정_{year}_{element}.csv")
        df_filled.to_csv(output_path, index=False, encoding="utf-8-sig")

        # 진행 상황 출력
        print(f"✅ {year}_{element} 결측치 보정 + 반올림 완료 → {output_path}")
