import pandas as pd
from difflib import get_close_matches

# === 파일 경로 ===
DATA_FILE = "data/2020~2024.csv"
COORD_FILE = "data/위도,경도.csv"

# === 1️⃣ 데이터 불러오기 ===
data = pd.read_csv(DATA_FILE)
coords = pd.read_csv(COORD_FILE)

print("🔍 원본 데이터 로드 완료")
print("데이터 지점 수:", data["지점명"].nunique())
print("좌표 데이터 지점 수:", coords["지점명"].nunique())

# === 2️⃣ 위경도 유효성 검사 ===
invalid = coords[
    (coords["위도"] < 33) | (coords["위도"] > 39) |
    (coords["경도"] < 124) | (coords["경도"] > 132)
]

if len(invalid) > 0:
    print(f"⚠️ 위경도 값이 비정상인 지점 {len(invalid)}개 발견")
    print(invalid)
else:
    print("✅ 모든 위경도 값이 정상 범위입니다.")

# === 3️⃣ 위경도 뒤바뀐 값 자동 교정 ===
swapped = coords[coords["위도"] > coords["경도"]]
if len(swapped) > 0:
    coords.loc[swapped.index, ["위도", "경도"]] = coords.loc[swapped.index, ["경도", "위도"]].values
    print(f"🔄 위경도가 뒤바뀐 지점 {len(swapped)}개 자동 수정 완료.")
else:
    print("✅ 위경도 뒤바뀐 지점 없음.")

# === 4️⃣ 이름 유사도 기반 병합 ===
merged = pd.merge(data, coords, on="지점명", how="left")

missing = merged[merged["위도"].isna()]["지점명"].unique()
print(f"\n좌표 누락 지점 {len(missing)}개")

for name in missing:
    match = get_close_matches(name, coords["지점명"], n=1, cutoff=0.6)
    if match:
        lat = coords.loc[coords["지점명"] == match[0], "위도"].values[0]
        lon = coords.loc[coords["지점명"] == match[0], "경도"].values[0]
        merged.loc[merged["지점명"] == name, ["위도", "경도"]] = [lat, lon]
        print(f"→ '{name}' 지역을 '{match[0]}' 좌표로 대체함.")
    else:
        print(f"⚠ '{name}' 지역은 자동 매칭 실패 (수동 입력 필요)")

# === 5️⃣ 결과 저장 ===
merged.to_csv("data/2020~2024_fixed.csv", index=False, encoding="utf-8-sig")
coords.to_csv("data/위도,경도_교정.csv", index=False, encoding="utf-8-sig")

print("\n✅ 교정 완료!")
print("📁 수정된 위경도 파일: data/위도,경도_교정.csv")
print("📁 병합된 결과 파일: data/2020~2024_fixed.csv")
