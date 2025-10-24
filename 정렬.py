import os
import pandas as pd

# 1️⃣ CSV 파일이 있는 폴더 경로
data_dir = r"C:/Users/UserK/Documents/GitHub/climate_project/data/2024"

# 2️⃣ 정렬 기준 컬럼 설정
sort_columns = ['지점', '지점명', '일시']   # 원하는 컬럼 순서로 정렬
ascending_order = [True, True, True]     # True = 오름차순, False = 내림차순

# 3️⃣ 폴더 내 CSV 파일 순회
for file_name in os.listdir(data_dir):
    if file_name.endswith(".csv"):
        file_path = os.path.join(data_dir, file_name)
        df = pd.read_csv(file_path)
        
        # 컬럼이 모두 존재할 때만 정렬
        if all(col in df.columns for col in sort_columns):
            df = df.sort_values(by=sort_columns, ascending=ascending_order)
            df.to_csv(file_path, index=False)
            print(f"[DONE] '{file_name}' 정렬 완료.")
        else:
            print(f"[SKIP] '{file_name}'에 정렬 기준 컬럼이 없음.")