import shutil

src1 = "/mnt/data/2020~2024_보정.csv"
src2 = "/mnt/data/결측보정_리포트.csv"
dst_dir = "C:/Users/UserK/Documents/GitHub/climate_project/data"  # 원하는 경로로 수정

for src in [src1, src2]:
    shutil.copy(src, dst_dir)

print("✅ 파일이 data 폴더에 복사되었습니다!")
