import pandas as pd

# 파일 경로 (상대경로)
in_path  = "data/2022_1.csv"
out_path = "data/2022_1_sorted.csv"

# 1) 로드 및 컬럼 이름 정리
df = pd.read_csv(in_path)
df.columns = df.columns.str.strip()  # 열 이름 앞뒤 공백 제거

# 2) 날짜 컬럼 찾기 (일자, date 등 후보)
date_col_candidates = [c for c in df.columns if c.lower().replace(" ", "") in ("일자","date","날짜","일시","datetime")]
if len(date_col_candidates) == 0:
    # 좀 더 느슨하게 검색
    date_col_candidates = [c for c in df.columns if "일" in c and "자" in c or "date" in c.lower() or "time" in c.lower()]
if len(date_col_candidates) == 0:
    raise RuntimeError("일자(날짜) 컬럼을 찾을 수 없습니다. 컬럼명을 확인해주세요: " + ", ".join(df.columns))

date_col = date_col_candidates[0]  # 우선 첫 후보 사용

# 3) 정렬 전 간단 확인
print("정렬 전 - 상위 3개 일자(원본 문자열):")
print(df[date_col].head(3).to_list())

# 4) 안전하게 datetime 변환 (다양한 포맷 허용)
# 백업 컬럼을 만들어 원본 문자열 보존
df['_date_original_str_'] = df[date_col].astype(str)

# 시도 1: 표준 포맷 우선 (예: "YYYY-MM-DD" 또는 "YYYY-MM-DD HH:MM:SS")
df['_date_parsed_'] = pd.to_datetime(df[date_col], errors='coerce', infer_datetime_format=True)

# 시도 2: 아직 NaT인 경우, 여러 포맷 시도 (예: "YYYY/MM/DD", "YYYY.MM.DD", "YYYYMMDD")
mask_nat = df['_date_parsed_'].isna()
if mask_nat.any():
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d", "%Y-%m-%d %H:%M"]
    for fmt in formats:
        try:
            parsed = pd.to_datetime(df.loc[mask_nat, date_col], format=fmt, errors='coerce')
            df.loc[mask_nat, '_date_parsed_'] = parsed
            mask_nat = df['_date_parsed_'].isna()
            if not mask_nat.any():
                break
        except Exception:
            pass

# 시도 3: 아직 NaT가 있으면 마지막으로 파이썬 파서에 맡김 (어쩔 수 없음)
mask_nat = df['_date_parsed_'].isna()
if mask_nat.any():
    df.loc[mask_nat, '_date_parsed_'] = pd.to_datetime(df.loc[mask_nat, date_col].astype(str), errors='coerce')

# 5) 정렬 - 일자(파싱된) 기준으로 오름차순. NaT는 맨 뒤로
df_sorted = df.sort_values(by='_date_parsed_', ascending=True, na_position='last').reset_index(drop=True)

# 6) 원래 날짜 컬럼은 원본 문자열로 복원(형식 유지)
df_sorted[date_col] = df_sorted['_date_original_str_']

# 7) 임시 컬럼 삭제
df_sorted = df_sorted.drop(columns=['_date_original_str_', '_date_parsed_'])

# 8) 저장
df_sorted.to_csv(out_path, index=False, encoding='utf-8-sig')

# 9) 결과 확인 출력
print("\n정렬 후 - 상위 5개 일자:")
print(df_sorted[date_col].head(5).to_list())
print("\n정렬 후 - 하위 5개 일자:")
print(df_sorted[date_col].tail(5).to_list())
print(f"\n✅ 완료: '{out_path}'에 저장되었습니다. (원본 파일은 변경되지 않음)")
