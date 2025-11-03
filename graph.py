import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

# ===== 한글 폰트 설정 =====
font_path = "C:/Windows/Fonts/malgun.ttf"
font_manager.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
matplotlib.use("Agg")

# ===== 파일 경로 =====
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"
weather = pd.read_csv(f"{base_path}\\2020~2024.csv", encoding="utf-8")
fixed = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")
variable = pd.read_csv(f"{base_path}\\예측발전량_PR가변_수정.csv", encoding="utf-8")

# ===== 병합 =====
fixed = pd.merge(fixed, weather, on=["지점명", "일시"], how="left")
variable = pd.merge(variable, weather, on=["지점명", "일시"], how="left")

# ===== 컬럼 이름 자동 탐색 (KeyError 방지) =====
def find_col(df, keyword):
    """keyword가 포함된 실제 컬럼 이름 반환"""
    matches = [c for c in df.columns if keyword in c]
    if len(matches) == 0:
        raise KeyError(f"'{keyword}' 포함된 컬럼을 찾을 수 없습니다. 실제 컬럼: {list(df.columns)}")
    return matches[0]

col_irr = find_col(fixed, "합계 일사량")
col_rain = find_col(fixed, "일강수량")

# ===== 그래프 생성 함수 =====
def make_scatter(df, xcol, ycol, xlabel, ylabel, title, filename, color):
    plt.figure(figsize=(8, 6))
    plt.scatter(df[xcol], df[ycol], alpha=0.5, color=color, edgecolors='none')
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    plt.title(title, fontsize=15, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"{base_path}\\{filename}", dpi=300, bbox_inches="tight")
    plt.close()

# ===== 그래프 4종 생성 =====
# 1️⃣ 일사량 vs 예측 발전량 (PR 고정)
make_scatter(
    fixed, col_irr, "예측발전량_PR고정(kWh)",
    "합계 일사량 (MJ/m²)", "예측 발전량 (PR=0.75)",
    "일사량과 예측 발전량의 관계 (PR=0.75)",
    "그래프_PR고정_일사량.png", "#FFA500"
)

# 2️⃣ 일사량 vs 예측 발전량 (PR 가변)
make_scatter(
    variable, col_irr, "예측발전량_PR가변(kWh)",
    "합계 일사량 (MJ/m²)", "예측 발전량 (기온 기반 PR)",
    "일사량과 예측 발전량의 관계 (기온 기반 PR)",
    "그래프_PR가변_일사량.png", "#FF6347"
)

# 3️⃣ 강수량 vs 예측 발전량 (PR 고정)
make_scatter(
    fixed, col_rain, "예측발전량_PR고정(kWh)",
    "일강수량 (mm)", "예측 발전량 (PR=0.75)",
    "강수량과 예측 발전량의 관계 (PR=0.75)",
    "그래프_PR고정_강수량.png", "#4682B4"
)

# 4️⃣ 강수량 vs 예측 발전량 (PR 가변)
make_scatter(
    variable, col_rain, "예측발전량_PR가변(kWh)",
    "일강수량 (mm)", "예측 발전량 (기온 기반 PR)",
    "강수량과 예측 발전량의 관계 (기온 기반 PR)",
    "그래프_PR가변_강수량.png", "#2E8B57"
)

print("✅ 발표용 그래프 4종 생성 완료!")
print("📂 저장 위치:", base_path)
