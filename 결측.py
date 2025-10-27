# fill_missing_weather_data.py
import pandas as pd
import glob
import os
# :흰색_확인_표시: 데이터 폴더 경로 (필요 시 수정)
data_dir = r"C:\Users\UserK\Documents\GitHub\climate_project\data"
# :흰색_확인_표시: 2020~2024 CSV 파일 자동 탐색
files = sorted(glob.glob(os.path.join(data_dir, "2020~2024.csv")))
print(f"총 {len(files)}개 파일을 자동 보정 및 반올림 처리합니다...\n")
for f in files:
    print(f":앞쪽_화살표: {os.path.basename(f)} 처리 중...")
    # CSV 읽기
    df = pd.read_csv(f, encoding="utf-8-sig")
    # :흰색_확인_표시: 수치형 변환 (빈칸 → NaN)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    # :흰색_확인_표시: 수치형 컬럼만 추출
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    # :흰색_확인_표시: 1단계: 지역별 평균으로 NaN 보정
    for col in numeric_cols:
        df[col] = df.groupby("지점명")[col].transform(lambda x: x.fillna(x.mean()))
    # :흰색_확인_표시: 2단계: 선형 보간 (시간 순서대로)
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear", limit_direction="both")
    # :흰색_확인_표시: 3단계: 전체 평균으로 잔여 NaN 보정
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    # :흰색_확인_표시: 4단계: 물리적으로 불가능한 값 자동 수정
    if "합계 일사량(MJ/m2)" in df.columns:
        df.loc[df["합계 일사량(MJ/m2)"] < 0, "합계 일사량(MJ/m2)"] = df["합계 일사량(MJ/m2)"].mean()
    if "일강수량(mm)" in df.columns:
        df.loc[df["일강수량(mm)"] < 0, "일강수량(mm)"] = 0  # 음수 강수는 존재 X
    # :흰색_확인_표시: 5단계: 반올림 처리 -------------------------
    for col in numeric_cols:
        if col == "합계 일사량(MJ/m2)":
            # 소수점 셋째자리 반올림 → 둘째자리까지 표시
            df[col] = df[col].round(2)
        else:
            # 나머지는 소수점 둘째자리 반올림 → 첫째자리까지 표시
            df[col] = df[col].round(1)
    # ------------------------------------------------
    # :흰색_확인_표시: 저장
    output_path = f.replace(".csv", "_filled.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f" - NaN 보정 및 반올림 완료 → {os.path.basename(output_path)} 저장 완료\n")
print(":흰색_확인_표시: 모든 파일 보정 + 반올림 완료")