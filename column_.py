import pandas as pd

# 기준 파일 (지점 컬럼이 있는 파일)
source_file = r"C:/Users/UserK/Documents/GitHub/climate_project/data/2024/2024_합계일조시간.csv"
source = pd.read_csv(source_file)

# 컬럼을 추가할 특정 파일
target_file = r"C:/Users/UserK/Documents/GitHub/climate_project/data/2024/2024_합계일사량.csv"
target = pd.read_csv(target_file)

# 지점 컬럼이 없으면 추가
if '지점' not in target.columns:
    # merge로 지점 컬럼 추가
    target = target.merge(
        source[['지점명', '일시', '지점']],
        on=['지점명', '일시'],
        how='left'
    )
    
    # 컬럼 순서 재정렬: 지점, 지점명, 일시, 나머지 컬럼
    cols = ['지점', '지점명', '일시'] + [c for c in target.columns if c not in ['지점', '지점명', '일시']]
    target = target[cols]
    
    # 저장
    target.to_csv(target_file, index=False)
    print(f"[DONE] '{target_file}'에 지점 컬럼 추가 완료.")
else:
    print(f"[SKIP] '{target_file}' 이미 지점 컬럼 존재.")
