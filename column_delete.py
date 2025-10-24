import pandas as pd

# CSV 파일 읽기
file_path = r"C:/Users/UserK/Documents/GitHub/climate_project/data/2024/2024_합계일조시간.csv"
df = pd.read_csv(file_path)

# 필요 없는 컬럼 삭제
df.drop(columns=['월'], inplace=True)

# 저장
df.to_csv(file_path, index=False)