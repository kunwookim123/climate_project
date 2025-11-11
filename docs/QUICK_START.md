# 빠른 시작 가이드

> 처음 프로젝트를 접하는 사람을 위한 단계별 실행 가이드

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [환경 설정](#2-환경-설정)
3. [데이터 확인](#3-데이터-확인)
4. [분석 실행](#4-분석-실행)
5. [결과 확인](#5-결과-확인)
6. [문제 해결](#6-문제-해결)

---

## 1. 프로젝트 개요

### 무엇을 분석하는가?

```
입력 데이터:
├─ 기상 데이터 (2020-2024, 97개 지역)
│  └─ 일강수량, 일사량, 기온, 일조시간 등
└─ 태양광 발전량 예측 데이터
   ├─ PR고정: 발전량 = 일사량 × 상수
   └─ PR가변: 발전량 = f(일사량, 기온)

분석 목표:
└─ 기상 요인(특히 강수량)이 태양광 발전량에 미치는 영향
```

### 현재 상태

```
✅ 구현됨:
  - 강수량-발전량 산점도
  - 장마철/비장마철 비교 지도
  - 지역별 발전량 지도
  - 인터랙티브 슬라이드

⚠️  개선 필요:
  - 계절 효과 혼재 문제
  - 인과관계 해석 오류
  - PR고정 데이터의 한계
```

**📖 자세한 내용**: [ANALYSIS_ISSUES_AND_SOLUTIONS.md](./ANALYSIS_ISSUES_AND_SOLUTIONS.md)

---

## 2. 환경 설정

### 2.1 필수 요구사항

```bash
# Python 버전
Python 3.8 이상

# 운영체제
macOS, Linux, Windows 모두 지원
```

### 2.2 패키지 설치

```bash
# 프로젝트 루트로 이동
cd /Users/yundonghee/Desktop/project/project1

# 필수 패키지 설치
pip install --break-system-packages pandas plotly numpy folium kaleido geopandas

# 또는 (가상환경 사용 시)
pip install pandas plotly numpy folium kaleido geopandas
```

**설치되는 패키지**:
- `pandas`: 데이터 처리
- `plotly`: 인터랙티브 그래프
- `numpy`: 수치 연산
- `folium`: 지도 시각화
- `kaleido`: 이미지 저장
- `geopandas`: 지리 데이터 처리

### 2.3 설치 확인

```bash
# 패키지 정상 설치 확인
python -c "import pandas, plotly, folium, geopandas; print('✅ 모든 패키지 정상')"
```

**예상 출력**:
```
✅ 모든 패키지 정상
```

---

## 3. 데이터 확인

### 3.1 필수 데이터 파일

```bash
# 데이터 파일 존재 확인
ls -lh data/2020~2024.csv
ls -lh data/예측발전량_PR고정_수정.csv
ls -lh data/예측발전량_PR가변_수정.csv
ls -lh data/좌표.csv
```

**예상 출력**:
```
-rw-r--r--  1 user  staff   8.6M  2020~2024.csv
-rw-r--r--  1 user  staff   3.2M  예측발전량_PR고정_수정.csv
-rw-r--r--  1 user  staff   3.5M  예측발전량_PR가변_수정.csv
-rw-r--r--  1 user  staff    12K  좌표.csv
```

### 3.2 데이터 미리보기

```bash
# 기상 데이터 첫 5줄 확인
python -c "
import pandas as pd
df = pd.read_csv('data/2020~2024.csv', encoding='utf-8-sig', nrows=5)
print(df)
"
```

### 3.3 데이터 통계

```bash
# 전체 데이터 통계
python -c "
import pandas as pd

weather = pd.read_csv('data/2020~2024.csv', encoding='utf-8-sig')
power = pd.read_csv('data/예측발전량_PR고정_수정.csv', encoding='utf-8-sig')

print(f'기상 데이터: {len(weather):,}건')
print(f'발전량 데이터: {len(power):,}건')
print(f'기간: {weather[\"일시\"].min()} ~ {weather[\"일시\"].max()}')
print(f'지역 수: {weather[\"지점명\"].nunique()}개')
"
```

**예상 출력**:
```
기상 데이터: 174,829건
발전량 데이터: 174,829건
기간: 2020-01-01 ~ 2024-12-31
지역 수: 97개
```

---

## 4. 분석 실행

### 4.1 강수량 영향 분석

```bash
# 강수량-발전량 관계 분석
python -m src.analysis.rainfall_analysis
```

**생성되는 파일**:
```
outputs/graphs/
├── 1_강수량_예측발전량_산점도.html
├── 2_강수량구간_평균발전량_감소율.html
└── 강수량_영향분석_슬라이드.html
```

**실행 시간**: 약 30초

---

### 4.2 장마철/비장마철 비교 지도

```bash
# 비교 지도 생성 (10개 이미지)
python -m src.visualization.create_comparison_maps
```

**생성되는 파일**:
```
outputs/slides/
├── 장마_2020_07_13.png
├── 비장마_2020_02_11.png
├── 장마_2021_07_03.png
├── 비장마_2021_03_20.png
... (총 10개)
```

**실행 시간**: 약 1분

---

### 4.3 지역별 발전량 지도

```bash
# 권역별 색상 구분 지도
python -m src.visualization.create_region_map
```

**생성되는 파일**:
```
outputs/
└── 예측발전량_지도_권역색상.html
```

**실행 시간**: 약 20초

---

### 4.4 분석 슬라이드

```bash
# 키보드 네비게이션 슬라이드
python -m src.visualization.create_slides
```

**생성되는 파일**:
```
outputs/graphs/
└── 강수량_영향분석_슬라이드.html
```

**실행 시간**: 약 15초

---

### 4.5 모든 분석 한번에 실행

```bash
# 순차적으로 모든 분석 실행
python -m src.analysis.rainfall_analysis && \
python -m src.visualization.create_comparison_maps && \
python -m src.visualization.create_region_map && \
python -m src.visualization.create_slides

echo "✅ 모든 분석 완료!"
```

**총 실행 시간**: 약 2-3분

---

## 5. 결과 확인

### 5.1 브라우저에서 열기

```bash
# macOS
open outputs/graphs/강수량_영향분석_슬라이드.html
open outputs/예측발전량_지도_권역색상.html

# Linux
xdg-open outputs/graphs/강수량_영향분석_슬라이드.html

# Windows
start outputs/graphs/강수량_영향분석_슬라이드.html
```

### 5.2 결과 파일 목록

```bash
# 생성된 모든 결과 확인
find outputs -type f -name "*.html" -o -name "*.png" | sort
```

### 5.3 결과 해석

#### 📊 산점도 (`1_강수량_예측발전량_산점도.html`)

```
보는 방법:
1. 점들의 분포 확인
2. 강수량이 증가할수록 발전량 변화 관찰
3. 계절별 색상 구분 확인

⚠️  주의:
- 계절 효과가 혼재되어 있음
- 일사량 차이를 고려하지 않음
```

#### 🗺️ 비교 지도 (`장마_*.png`, `비장마_*.png`)

```
보는 방법:
1. 왼쪽: 강수량 (파란색 = 많음)
2. 오른쪽: 발전량 (빨강 = 많음)
3. 지역별 패턴 비교

해석:
- 장마철: 남부 강수 집중 → 발전량 감소
- 비장마철: 강수 적음 → 발전량 높음
```

#### 🎯 지역별 지도 (`예측발전량_지도_권역색상.html`)

```
사용 방법:
1. 지도 확대/축소 가능
2. 마커 클릭 → 상세 정보
3. 권역별 색상으로 구분

활용:
- 지역별 발전 패턴 비교
- 고발전/저발전 지역 파악
```

---

## 6. 문제 해결

### 6.1 패키지 설치 오류

**증상**:
```
error: externally-managed-environment
```

**해결**:
```bash
# macOS/Linux
pip install --break-system-packages [패키지명]

# 또는 가상환경 사용
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install [패키지명]
```

---

### 6.2 모듈을 찾을 수 없음

**증상**:
```
ModuleNotFoundError: No module named 'plotly'
```

**해결**:
```bash
# 패키지 설치 확인
pip list | grep plotly

# 없으면 설치
pip install --break-system-packages plotly
```

---

### 6.3 파일을 찾을 수 없음

**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/2020~2024.csv'
```

**해결**:
```bash
# 현재 위치 확인
pwd

# 프로젝트 루트로 이동
cd /Users/yundonghee/Desktop/project/project1

# 데이터 파일 확인
ls -l data/
```

**주의**: 반드시 **프로젝트 루트**에서 실행해야 합니다!

---

### 6.4 한글 깨짐

**증상**:
- CSV 파일의 한글이 깨져 보임

**해결**:
```python
# UTF-8 BOM 인코딩 사용
df = pd.read_csv('파일.csv', encoding='utf-8-sig')
```

프로젝트 코드에는 이미 적용되어 있습니다.

---

### 6.5 Kaleido 오류

**증상**:
```
ValueError: Image export requires kaleido package
```

**해결**:
```bash
pip install --break-system-packages kaleido
```

---

## 📚 추가 리소스

### 프로젝트 구조

```
project1/
├── src/                    # 소스 코드
│   ├── core/              # 핵심 맵 클래스
│   ├── analysis/          # 분석 스크립트
│   ├── visualization/     # 시각화 스크립트
│   └── utils/             # 유틸리티
├── data/                   # 데이터 파일
├── outputs/                # 결과물
│   ├── graphs/            # HTML 그래프
│   └── slides/            # PNG 이미지
├── docs/                   # 문서
│   ├── QUICK_START.md     # 이 문서
│   └── ANALYSIS_ISSUES_AND_SOLUTIONS.md
└── README.md              # 프로젝트 가이드
```

### 관련 문서

- **ANALYSIS_ISSUES_AND_SOLUTIONS.md**: 분석 문제점 및 개선 방안
- **README.md**: 프로젝트 개요 및 전체 구조

### 문의

문제가 발생하면:
1. [문제 해결](#6-문제-해결) 섹션 확인
2. 프로젝트 README 참고
3. 에러 메시지 전체를 복사해서 검색

---

## ✅ 체크리스트

실행 전 확인:

- [ ] Python 3.8 이상 설치됨
- [ ] 필수 패키지 설치됨 (`pandas`, `plotly`, `folium` 등)
- [ ] 프로젝트 루트 디렉토리에 있음
- [ ] `data/` 폴더에 필수 데이터 파일 존재
- [ ] `outputs/` 폴더 쓰기 권한 있음

실행 후 확인:

- [ ] `outputs/graphs/` 폴더에 HTML 파일 생성됨
- [ ] `outputs/slides/` 폴더에 PNG 파일 생성됨
- [ ] 브라우저에서 HTML 파일이 정상적으로 열림
- [ ] 인터랙티브 기능(줌, 클릭 등) 작동

---

**최종 수정**: 2025-11-11
**버전**: 1.0
