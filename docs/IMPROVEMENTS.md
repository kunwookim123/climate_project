# 프로젝트 개선 사항 및 추가 기능 제안

현재 프로젝트의 부족한 부분과 추가로 개발하면 좋을 기능들을 정리했습니다.

---

## 🚨 중요도: 높음 (즉시 개선 필요)

### 1. 의존성 관리 파일 누락

**문제점:**
- `requirements.txt` 파일이 없어서 필요한 패키지를 알 수 없음
- 다른 환경에서 프로젝트 설치 불가능

**해결 방안:**
```bash
# requirements.txt 생성
pandas>=1.5.0
numpy>=1.21.0
plotly>=5.0.0
folium>=0.14.0
geopandas>=0.12.0
kaleido>=0.2.1  # plotly 이미지 저장용
```

**우선순위:** ⭐⭐⭐⭐⭐

---

### 2. 데이터 파일 누락 처리

**문제점:**
- `data/좌표.csv` 등 필수 파일이 없으면 스크립트가 바로 에러
- 사용자에게 어떤 파일이 필요한지 명확하지 않음

**해결 방안:**
```python
# src/utils/check_data_files.py 생성
"""
필수 데이터 파일 존재 여부를 확인하는 유틸리티
"""
import os

REQUIRED_FILES = [
    "data/좌표.csv",
    "data/2020~2024.csv",
    "data/예측발전량_PR고정_수정.csv",
]

def check_required_files():
    """필수 파일 존재 여부 확인"""
    missing = []
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print("⚠️ 다음 파일들이 필요합니다:")
        for f in missing:
            print(f"  - {f}")
        return False
    return True
```

**우선순위:** ⭐⭐⭐⭐⭐

---

### 3. 에러 핸들링 부족

**문제점:**
- 파일을 읽다가 에러가 나면 프로그램이 그냥 중단됨
- 사용자에게 명확한 에러 메시지 제공 안 됨

**해결 방안:**
```python
# 모든 스크립트에 try-except 추가
try:
    df = pd.read_csv(file_path, encoding="utf-8")
except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
    print("💡 data/ 폴더에 파일이 있는지 확인해주세요.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"❌ 파일이 비어있습니다: {file_path}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 예상치 못한 오류: {e}")
    sys.exit(1)
```

**우선순위:** ⭐⭐⭐⭐

---

### 4. 설정 파일 하드코딩

**문제점:**
- 장마철 날짜, 색상 설정 등이 코드에 직접 작성되어 있음
- 수정하려면 코드를 직접 편집해야 함

**해결 방안:**
```yaml
# config.yaml 생성
monsoon:
  rainy_days:
    2020: "2020-07-13"
    2021: "2021-07-03"
    2022: "2022-07-09"
    2023: "2023-07-18"
    2024: "2024-06-29"

  rainy_periods:
    2020: ["2020-06-24", "2020-08-16"]
    2021: ["2021-07-03", "2021-07-26"]
    # ...

colors:
  regions:
    경기도: "#FFD700"
    강원특별자치도: "#58228B"
    # ...

  scales:
    rain: [[0, "#9ecae1"], [0.4, "#3182bd"], [1, "#08306b"]]
    power: [[0, "#fed976"], [0.5, "#fd8d3c"], [1, "#bd0026"]]

paths:
  data_dir: "data"
  output_dir: "outputs"
```

**우선순위:** ⭐⭐⭐⭐

---

## 🔧 중요도: 중간 (개발 효율성 향상)

### 5. 테스트 코드 부재

**문제점:**
- 단위 테스트가 전혀 없음
- 코드 수정 시 기존 기능이 깨지는지 확인 불가

**해결 방안:**
```python
# tests/test_base_map.py 생성
import pytest
from src.core.base_map import BaseMap

def test_load_location_data():
    """좌표 데이터 로딩 테스트"""
    base_map = BaseMap("data/2020_평균기온.csv")
    assert len(base_map.location_data) > 0
    assert "서울" in base_map.location_data

def test_auto_convert():
    """CSV 자동 변환 테스트"""
    # 테스트 로직
    pass

def test_filter_data():
    """날짜 필터링 테스트"""
    # 테스트 로직
    pass
```

```bash
# 테스트 실행
pytest tests/
```

**우선순위:** ⭐⭐⭐⭐

---

### 6. 로깅 시스템 부재

**문제점:**
- `print()` 문만 사용해서 디버깅 어려움
- 실행 로그를 파일로 저장할 수 없음

**해결 방안:**
```python
# src/utils/logger.py 생성
import logging
from datetime import datetime

def setup_logger(name, log_file=None):
    """로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (선택적)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# 사용 예시
logger = setup_logger(__name__, 'logs/analysis.log')
logger.info("데이터 로딩 시작")
logger.error("파일을 찾을 수 없습니다")
```

**우선순위:** ⭐⭐⭐

---

### 7. 데이터 검증 로직 부족

**문제점:**
- 데이터 품질 확인 없이 바로 분석 시작
- 이상치, 결측치, 중복 데이터 자동 감지 안 됨

**해결 방안:**
```python
# src/utils/data_validator.py 생성
"""
데이터 품질 검증 유틸리티
"""
import pandas as pd

class DataValidator:
    """데이터 검증 클래스"""

    def __init__(self, df):
        self.df = df
        self.report = []

    def check_missing_values(self):
        """결측치 확인"""
        missing = self.df.isnull().sum()
        if missing.any():
            self.report.append(f"⚠️ 결측치 발견: {missing[missing > 0].to_dict()}")

    def check_duplicates(self):
        """중복 데이터 확인"""
        dupes = self.df.duplicated().sum()
        if dupes > 0:
            self.report.append(f"⚠️ 중복 데이터 {dupes}개 발견")

    def check_outliers(self, column, method='iqr'):
        """이상치 확인"""
        if method == 'iqr':
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            outliers = self.df[
                (self.df[column] < Q1 - 1.5 * IQR) |
                (self.df[column] > Q3 + 1.5 * IQR)
            ]
            if len(outliers) > 0:
                self.report.append(f"⚠️ {column} 이상치 {len(outliers)}개 발견")

    def check_date_range(self, date_column, expected_start, expected_end):
        """날짜 범위 확인"""
        dates = pd.to_datetime(self.df[date_column])
        if dates.min() < pd.to_datetime(expected_start):
            self.report.append(f"⚠️ 예상보다 이른 날짜 발견: {dates.min()}")
        if dates.max() > pd.to_datetime(expected_end):
            self.report.append(f"⚠️ 예상보다 늦은 날짜 발견: {dates.max()}")

    def generate_report(self):
        """검증 리포트 생성"""
        if not self.report:
            return "✅ 모든 검증 통과"
        return "\n".join(self.report)
```

**우선순위:** ⭐⭐⭐

---

### 8. 진행 상황 표시 부재

**문제점:**
- 대용량 데이터 처리 시 진행 상황을 알 수 없음
- 프로그램이 멈춘 건지 실행 중인지 불분명

**해결 방안:**
```python
# requirements.txt에 추가
tqdm>=4.65.0

# 사용 예시
from tqdm import tqdm

for year in tqdm(range(2020, 2025), desc="연도별 처리"):
    # 처리 로직
    pass

# 또는
for _, row in tqdm(df.iterrows(), total=len(df), desc="데이터 처리 중"):
    # 처리 로직
    pass
```

**우선순위:** ⭐⭐⭐

---

## 💡 중요도: 낮음 (추가 기능)

### 9. 웹 대시보드

**제안:**
- Streamlit 또는 Dash로 인터랙티브 웹 대시보드 구축
- 사용자가 날짜, 지역 선택해서 실시간 시각화

**구현 예시:**
```python
# app_dashboard.py
import streamlit as st
import pandas as pd
from src.core.base_map import BaseMap

st.title("☀️ 기후 & 태양광 발전량 분석 대시보드")

# 사이드바
year = st.sidebar.selectbox("연도 선택", [2020, 2021, 2022, 2023, 2024])
month = st.sidebar.slider("월 선택", 1, 12, 6)

# 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("data/2020~2024.csv")

df = load_data()

# 지도 표시
st.subheader(f"{year}년 {month}월 강수량 분포")
# 지도 생성 로직
```

**실행:**
```bash
streamlit run app_dashboard.py
```

**우선순위:** ⭐⭐

---

### 10. 데이터베이스 연동

**제안:**
- CSV 대신 SQLite 또는 PostgreSQL 사용
- 데이터 쿼리 성능 향상

**구현 예시:**
```python
# src/database/db_manager.py
import sqlite3
import pandas as pd

class DatabaseManager:
    """데이터베이스 관리 클래스"""

    def __init__(self, db_path="data/climate.db"):
        self.conn = sqlite3.connect(db_path)

    def import_csv_to_db(self, csv_path, table_name):
        """CSV를 데이터베이스로 임포트"""
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, self.conn, if_exists='replace', index=False)

    def query(self, sql):
        """SQL 쿼리 실행"""
        return pd.read_sql_query(sql, self.conn)

    def get_data_by_date_range(self, start_date, end_date):
        """날짜 범위로 데이터 조회"""
        sql = f"""
            SELECT * FROM weather
            WHERE 일시 BETWEEN '{start_date}' AND '{end_date}'
        """
        return self.query(sql)
```

**우선순위:** ⭐⭐

---

### 11. REST API 서버

**제안:**
- FastAPI로 분석 결과를 API로 제공
- 다른 애플리케이션에서 데이터 조회 가능

**구현 예시:**
```python
# api/main.py
from fastapi import FastAPI, Query
from datetime import date
import pandas as pd

app = FastAPI(title="기후 데이터 API")

@app.get("/")
def read_root():
    return {"message": "기후 & 발전량 분석 API"}

@app.get("/weather/{region}")
def get_weather(
    region: str,
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    """특정 지역의 날씨 데이터 조회"""
    # 데이터 조회 로직
    return {"region": region, "data": []}

@app.get("/power/prediction")
def get_power_prediction(date: date, region: str = None):
    """발전량 예측 조회"""
    # 예측 로직
    return {"date": date, "prediction": 0}

# 실행: uvicorn api.main:app --reload
```

**우선순위:** ⭐

---

### 12. 머신러닝 예측 모델

**제안:**
- 기상 데이터를 기반으로 발전량 예측 모델 학습
- scikit-learn, XGBoost, 또는 TensorFlow 사용

**구현 예시:**
```python
# src/ml/power_predictor.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib

class PowerPredictor:
    """발전량 예측 모델"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_features(self, df):
        """피처 엔지니어링"""
        features = [
            '일강수량(mm)',
            '합계일사량(MJ/m2)',
            '평균기온(℃)',
            '일조율(%)'
        ]
        return df[features], df['예측발전량_PR고정(kWh)']

    def train(self, df):
        """모델 학습"""
        X, y = self.prepare_features(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        print(f"모델 정확도 (R²): {score:.4f}")
        return score

    def predict(self, weather_data):
        """발전량 예측"""
        return self.model.predict(weather_data)

    def save_model(self, path="models/power_predictor.pkl"):
        """모델 저장"""
        joblib.dump(self.model, path)

    def load_model(self, path="models/power_predictor.pkl"):
        """모델 로드"""
        self.model = joblib.load(path)
```

**우선순위:** ⭐

---

### 13. 자동화된 리포트 생성

**제안:**
- 월간/분기별 자동 분석 리포트 생성
- PDF 또는 HTML 형식으로 저장

**구현 예시:**
```python
# src/reports/report_generator.py
from datetime import datetime
from jinja2 import Template
import pdfkit

class ReportGenerator:
    """자동 리포트 생성기"""

    def generate_monthly_report(self, year, month):
        """월간 리포트 생성"""
        # 데이터 분석
        stats = self.calculate_monthly_stats(year, month)

        # HTML 템플릿
        template = Template("""
        <html>
        <head><title>{{ year }}년 {{ month }}월 분석 리포트</title></head>
        <body>
            <h1>기후 & 발전량 분석 리포트</h1>
            <h2>{{ year }}년 {{ month }}월</h2>

            <h3>주요 통계</h3>
            <ul>
                <li>평균 강수량: {{ stats.avg_rainfall }}mm</li>
                <li>평균 발전량: {{ stats.avg_power }}kWh</li>
                <li>발전량 감소율: {{ stats.reduction }}%</li>
            </ul>

            <h3>그래프</h3>
            <img src="graphs/{{ year }}_{{ month }}.png">
        </body>
        </html>
        """)

        html = template.render(year=year, month=month, stats=stats)

        # PDF로 저장
        output_path = f"reports/{year}_{month:02d}_report.pdf"
        pdfkit.from_string(html, output_path)
        print(f"✅ 리포트 생성 완료: {output_path}")
```

**우선순위:** ⭐

---

### 14. CI/CD 파이프라인

**제안:**
- GitHub Actions로 자동 테스트 및 배포 설정

**구현 예시:**
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest tests/ --cov=src/

    - name: Check code style
      run: |
        pip install flake8
        flake8 src/ --max-line-length=120
```

**우선순위:** ⭐

---

## 📊 우선순위 요약

### 즉시 해야 할 것 (이번 주)
1. ⭐⭐⭐⭐⭐ `requirements.txt` 생성
2. ⭐⭐⭐⭐⭐ 필수 데이터 파일 체크 기능
3. ⭐⭐⭐⭐ 에러 핸들링 강화
4. ⭐⭐⭐⭐ 설정 파일 분리 (`config.yaml`)

### 다음 단계 (이번 달)
5. ⭐⭐⭐⭐ 테스트 코드 작성
6. ⭐⭐⭐ 로깅 시스템 구축
7. ⭐⭐⭐ 데이터 검증 로직
8. ⭐⭐⭐ 진행 상황 표시

### 추후 고려 (필요시)
9. ⭐⭐ 웹 대시보드
10. ⭐⭐ 데이터베이스 연동
11. ⭐ REST API 서버
12. ⭐ ML 예측 모델
13. ⭐ 자동 리포트 생성
14. ⭐ CI/CD 파이프라인

---

## 🎯 추천 개선 순서

```
Week 1: 기본 인프라
├── requirements.txt 생성
├── 데이터 파일 체크 추가
└── 에러 핸들링 강화

Week 2: 코드 품질
├── config.yaml 분리
├── 로깅 시스템 구축
└── 데이터 검증 로직

Week 3-4: 테스트 & 문서화
├── 단위 테스트 작성
├── API 문서 작성
└── 사용자 가이드 작성

Week 5+: 추가 기능
├── 웹 대시보드 (선택)
├── DB 연동 (선택)
└── ML 모델 (선택)
```

---

이 문서를 참고하여 프로젝트를 단계적으로 개선해나가세요! 🚀
