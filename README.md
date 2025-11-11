# 기후 데이터 및 태양광 발전량 분석 프로젝트

한국의 기상 데이터(2020-2024)와 태양광 예측 발전량 간의 관계를 분석하고 시각화하는 프로젝트입니다.

## 프로젝트 개요

본 프로젝트는 2020년부터 2024년까지 5년간의 기상 데이터(강수량, 일사량, 온도, 풍속 등)와 태양광 발전 예측량을 결합하여 다음을 분석합니다:

- **강수량이 태양광 발전량에 미치는 영향**
- **장마철과 비장마철의 발전량 비교**
- **지역별 발전량 패턴 및 클러스터링**
- **기상 조건에 따른 발전 효율 변화**

모든 분석 결과는 인터랙티브 HTML 차트와 지도로 시각화됩니다.

## 주요 기능

### 1. 강수량 영향 분석
- 강수량 구간별 평균 발전량 분석
- 산점도 및 회귀 분석 그래프
- 강수량 증가에 따른 발전량 감소율 계산

### 2. 지도 시각화
- **비교 지도**: 장마철 vs 비장마철 발전량 비교
- **지역 지도**: 권역별 발전량 클러스터링 및 색상 구분
- **인터랙티브 맵**: Folium 기반 마커 및 팝업

### 3. 슬라이드 생성
- 키보드 내비게이션 지원 (Space/화살표)
- 연도별 장마철/비장마철 지도 자동 삽입
- Plotly 그래프 임베딩

## 프로젝트 구조

```
project1/
├── src/                          # 소스 코드
│   ├── core/                     # 핵심 클래스 (상속 구조)
│   │   ├── base_map.py          # BaseMap: CSV 로딩, 좌표 매핑, 지도 생성
│   │   ├── solar_map.py         # SolarMap: 일사량/온도 지도
│   │   └── rain_map.py          # RainMap: 강수량 지도
│   ├── visualization/           # 시각화 스크립트
│   │   ├── create_comparison_maps.py    # 장마철/비장마철 비교 지도
│   │   ├── create_region_map.py         # 권역별 발전량 지도
│   │   └── create_slides.py             # 키보드 내비게이션 슬라이드
│   ├── analysis/                # 분석 스크립트
│   │   ├── rainfall_analysis.py         # 강수량 영향 분석
│   │   └── check_rainfall_bins.py       # 강수량 구간 검증
│   └── utils/                   # 유틸리티
│       ├── fill_missing_data.py         # 결측치 보간
│       ├── fix_coordinates.py           # 좌표 오류 수정
│       └── check_columns.py             # 컬럼명 확인
├── data/                        # 데이터 파일 (git 제외)
│   ├── 2020~2024.csv           # 통합 기상 데이터
│   ├── 예측발전량_PR고정_수정.csv
│   ├── 예측발전량_PR가변_수정.csv
│   ├── 좌표.csv                # 지역 좌표 (필수)
│   └── skorea_provinces_geo.json
├── outputs/                     # 생성된 결과물
│   ├── graphs/                 # HTML 그래프
│   └── slides/                 # PNG 지도 이미지
└── old/                        # 레거시 코드 (deprecated)
```

## 설치 및 실행

### 1. 환경 설정

#### Python 가상환경 활성화
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 필요한 라이브러리
```bash
pip install pandas numpy plotly folium geopandas shapely
```

### 2. 데이터 준비

다음 파일들이 `data/` 디렉토리에 필요합니다:
- `2020~2024.csv`: 기상청 기상 데이터 (필수 컬럼: 지점명, 일시, 일강수량(mm))
- `예측발전량_PR고정_수정.csv`: 태양광 발전량 예측 데이터 (필수 컬럼: 지점명, 일시, 예측발전량_PR고정(kWh))
- `좌표.csv`: **필수** - 지역별 위도/경도 (컬럼: 지점명, 위도, 경도)

### 3. 스크립트 실행

**중요**: 모든 스크립트는 프로젝트 루트에서 모듈로 실행해야 합니다.

#### 강수량 영향 분석
```bash
python -m src.analysis.rainfall_analysis
```
**출력**:
- `outputs/graphs/강수량_영향분석_슬라이드.html`
- 산점도, 구간별 평균, 회귀 분석 그래프

#### 장마철 비교 지도 생성
```bash
python -m src.visualization.create_comparison_maps
```
**출력**:
- `outputs/slides/장마_2020_07_13.png` (각 연도별)
- `outputs/slides/비장마_2020_02_11.png` (각 연도별)

#### 권역별 발전량 지도
```bash
python -m src.visualization.create_region_map
```
**출력**:
- `outputs/예측발전량_지도_권역색상.html`
- 권역별 클러스터링 및 인터랙티브 맵

#### 분석 슬라이드 생성
```bash
python -m src.visualization.create_slides
```
**출력**:
- 키보드로 탐색 가능한 HTML 슬라이드
- 임베딩된 Plotly 그래프

### 4. 유틸리티

#### 결측치 보간
```bash
python -m src.utils.fill_missing_data
```
순서: 지역 평균 → 선형 보간 → 전체 평균 → 물리적 제약 (음수 강수량 → 0)

#### 좌표 오류 수정
```bash
python -m src.utils.fix_coordinates
```
위도/경도 뒤바뀜 감지, 퍼지 매칭으로 지역명 보정

#### 컬럼명 확인
```bash
python -m src.utils.check_columns
```

## 핵심 아키텍처

### 1. 클래스 상속 구조

```python
BaseMap (base_map.py)
├── CSV 로딩 및 표준 형식 변환
├── 좌표 매핑 (data/좌표.csv)
├── 값 컬럼 자동 감지 (일사/강수/온도)
└── Folium 지도 생성

SolarMap (solar_map.py) extends BaseMap
└── draw_markers() 오버라이드 (주황/빨강 색상)

RainMap (rain_map.py) extends BaseMap
└── draw_markers() 오버라이드 (파랑 색상)
```

**표준 데이터 형식**: `연도, 월, 일, 지역, 위도, 경도, 값`

### 2. 경로 관리

모든 스크립트는 **상대 경로**를 프로젝트 루트 기준으로 자동 해결합니다:

```python
# 자동 경로 해결 (모든 모듈에 적용)
if not os.path.isabs(data_dir):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(root_dir, data_dir)
```

### 3. 데이터 병합 패턴

대부분의 분석은 기상 데이터와 발전량 데이터를 병합합니다:

```python
merged = pd.merge(
    weather[["지점명", "일시", "일강수량(mm)"]],
    power[["지점명", "일시", "예측발전량_PR고정(kWh)"]],
    on=["지점명", "일시"],
    how="inner"
)
```

## ⚠️ 현재 분석의 한계점

**중요**: 현재 분석에는 다음과 같은 신뢰성 문제가 있습니다:

1. **예측발전량 = 일사량 × 상수**
   - PR고정 데이터는 일사량만으로 계산됨 (상관계수 +1.000)
   - 강수량은 발전량에 직접 영향을 주지 않음
   - 실제로는 강수량 → 일사량 감소 → 발전량 감소 (간접 효과)

2. **계절 효과 혼재**
   - 여름철에 비가 많이 오지만 일사량도 높음
   - 강수량과 계절이 혼재되어 인과관계 왜곡
   - 같은 일사량 조건에서는 강수량 영향이 거의 없음 (-0.5%)

3. **일사량 통제 부족**
   - 현재 분석은 일사량 차이를 고려하지 않음
   - 올바른 분석: 일사량을 통제하거나 경로 분석 필요

**📖 자세한 내용 및 개선 방안**: [docs/ANALYSIS_ISSUES_AND_SOLUTIONS.md](./docs/ANALYSIS_ISSUES_AND_SOLUTIONS.md)

---

## 📚 문서

처음 이 프로젝트를 시작한다면:

1. **[빠른 시작 가이드](./docs/QUICK_START.md)** ⭐
   - 환경 설정부터 실행까지 단계별 가이드
   - 문제 해결 방법
   - 결과 해석 방법

2. **[분석 문제점 및 개선 방안](./docs/ANALYSIS_ISSUES_AND_SOLUTIONS.md)**
   - 현재 분석의 신뢰성 문제
   - 왜 문제인지 구체적 설명
   - 개선 방안 3가지 제시
   - 구현 우선순위

---

## 주요 분석 결과

**⚠️ 주의**: 아래 결과는 계절 효과가 혼재되어 있어 신뢰성이 낮습니다. 개선된 분석 방법은 [문서](./docs/ANALYSIS_ISSUES_AND_SOLUTIONS.md)를 참고하세요.

### 1. 강수량과 발전량의 관계 (원본 분석)

- **0~1mm**: 발전량 최대 (기준점)
- **1~10mm**: 약 13% 증가 ⚠️ (여름철 일사량이 높기 때문)
- **10~50mm**: 약 9% 증가 ⚠️ (계절 효과)
- **50mm 이상**: 32% 감소 ✅ (폭우로 일사량 급감)

### 2. 장마철 영향 (신뢰성 높음)

- 장마철 평균 일사량: 비장마철 대비 **약 35% 감소**
- 장마철 평균 발전량: 비장마철 대비 **약 35% 감소**
- 지역별 편차 존재 (남부 지방이 더 큰 영향)

### 3. 지역 패턴

- 제주도: 연중 안정적인 발전량
- 강원도: 계절 편차 큼
- 남부 지방: 장마철 영향 큼

## 하드코딩된 데이터

### 장마철 기준일

`src/visualization/create_comparison_maps.py`에 정의:

```python
RAINY_DAYS_FIXED = {
    2020: "2020-07-13",
    2021: "2021-07-03",
    2022: "2022-07-09",
    2023: "2023-07-18",
    2024: "2024-06-29"
}

RAINY_PERIODS = {
    2020: ("2020-06-24", "2020-08-16"),
    2021: ("2021-06-25", "2021-08-14"),
    # ...
}
```

다른 기간 분석 시 이 딕셔너리를 수정하세요.

### 권역 색상

`src/visualization/create_region_map.py`에 정의:

```python
region_colors = {
    "경기도": "#FFD700",          # 금색
    "강원특별자치도": "#58228B",  # 보라
    "충청북도": "#32CD32",        # 연두
    "충청남도": "#00CED1",        # 청록
    # ...
}
```

## 중요 규칙

1. **한글 컬럼명 사용**: 모든 데이터는 한글 헤더 사용 (일강수량(mm), 예측발전량_PR고정(kWh))
2. **인코딩**: CSV 읽기/쓰기 시 항상 `encoding="utf-8"` 또는 `"utf-8-sig"` 사용
3. **모듈 실행**: 반드시 프로젝트 루트에서 `python -m src.module.script` 형태로 실행
4. **출력 위치**:
   - 그래프: `outputs/graphs/`
   - 슬라이드 이미지: `outputs/slides/`

## 시각화 특징

### Plotly 차트
- 한글 폰트: `font=dict(family="Malgun Gothic")`
- 인터랙티브 hover 툴팁 (이모지 아이콘 포함)
- 색상 스케일: 파랑 (강수량), 주황-빨강 (발전량)

### 슬라이드
- 키보드 내비게이션: Space/ArrowRight (다음), ArrowLeft (이전)
- Plotly 차트 iframe 임베딩
- 토글 표시/숨김 기능

### Folium 지도
- 원형 마커 크기: 데이터 값에 비례
- HTML 팝업: 포맷된 데이터 표시
- 밀집 지역 클러스터링

## 기술 스택

- **데이터 처리**: pandas, numpy
- **시각화**: plotly, folium
- **지리 데이터**: geopandas, shapely
- **웹**: HTML5, JavaScript (키보드 이벤트)

## 라이선스

본 프로젝트는 교육 및 연구 목적으로 작성되었습니다.

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
