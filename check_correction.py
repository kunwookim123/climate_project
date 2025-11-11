import pandas as pd

# 원본 파일 이름과 저장할 파일 이름
input_file = 'data/2020~2024_보정.csv'
output_file = 'data/2020~2024_수정본.csv'

print(f"'{input_file}' 파일을 읽는 중입니다...")

try:
    # CSV 파일 읽기 (한글 인코딩 문제에 대비해 'utf-8' 시도)
    df = pd.read_csv(input_file, encoding='utf-8')
except UnicodeDecodeError:
    # 'utf-8' 실패 시 'cp949' (Windows 기본 한글 인코딩) 시도
    print("UTF-8 디코딩 실패. 'cp949' 인코딩으로 다시 시도합니다.")
    df = pd.read_csv(input_file, encoding='cp949')
except FileNotFoundError:
    print(f"오류: '{input_file}' 파일을 찾을 수 없습니다. 스크립트와 같은 폴더에 파일이 있는지 확인하세요.")
    exit()
except Exception as e:
    print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    exit()

print("데이터 처리 중...")

# 1. '일강수량(mm)' 컬럼 처리
#    - 먼저 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
#    - 소수점 첫째 자리까지 반올림
precip_col = '일강수량(mm)'
if precip_col in df.columns:
    df[precip_col] = pd.to_numeric(df[precip_col], errors='coerce')
    df[precip_col] = df[precip_col].round(1)
else:
    print(f"경고: '{precip_col}' 컬럼을 찾을 수 없습니다.")

# 2. '합계 일사량(MJ/m2)' 컬럼 처리
#    - 먼저 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
#    - 소수점 둘째 자리까지 반올림
insolation_col = '합계 일사량(MJ/m2)'
if insolation_col in df.columns:
    df[insolation_col] = pd.to_numeric(df[insolation_col], errors='coerce')
    df[insolation_col] = df[insolation_col].round(2)
else:
    print(f"경고: '{insolation_col}' 컬럼을 찾을 수 없습니다.")

# 3. 수정된 데이터프레임을 새 CSV 파일로 저장
#    - 'utf-8-sig'는 Excel에서 한글이 깨지지 않게 하기 위해 BOM을 추가합니다.
#    - index=False는 불필요한 인덱스 컬럼이 저장되지 않게 합니다.
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n작업 완료! 수정된 데이터가 '{output_file}' 파일로 저장되었습니다.")