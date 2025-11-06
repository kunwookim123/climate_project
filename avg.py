import pandas as pd

def check_bin_averages():
    # -----------------------------------------------------------------
    # 1단계: 데이터 로드 및 전처리 (이전과 동일)
    # -----------------------------------------------------------------
    try:
        weather_df = pd.read_csv('data/2020~2024.csv')
        gen_df = pd.read_csv('data/예측발전량_PR고정_수정.csv')
    except FileNotFoundError:
        print("🚨 오류: 파일을 찾을 수 없습니다. 파일 이름을 확인하세요.")
        return

    df = pd.merge(
        weather_df[['지점명', '일시', '일강수량(mm)']],
        gen_df[['지점명', '일시', '예측발전량_PR고정(kWh)']],
        on=['지점명', '일시']
    )

    df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
    df['예측발전량_PR고정(kWh)'] = df['예측발전량_PR고정(kWh)'].fillna(0)

    # 💥 강수량 구간 및 이름 정의 (이전과 동일)
    bins = [0, 1, 5, 10, 20, 50, 100, 9999] 
    labels = ['0mm', '0-1mm', '1-5mm', '5-10mm', '10-20mm', '20-50mm', '50mm 이상']

    df['강수량 구간'] = pd.cut(
        df['일강수량(mm)'], 
        bins=bins, 
        labels=labels, 
        right=False, 
        include_lowest=True
    )

    # 구간별 평균 발전량 계산
    bin_summary = df.groupby('강수량 구간', observed=True)['예측발전량_PR고정(kWh)'].mean().reset_index()
    bin_summary.rename(columns={'예측발전량_PR고정(kWh)': '평균 일 발전량 (kWh)'}, inplace=True)
    
    # -----------------------------------------------------------------
    # 2단계: 핵심 구간 비교 결과 출력
    # -----------------------------------------------------------------
    
    print("---------------------------------------------------------")
    print("✅ 강수량 구간별 절대 평균 발전량 비교 (가장 높아야 할 0mm 기준)")
    print("---------------------------------------------------------")
    
    # 0mm 구간의 평균 발전량
    avg_0mm = bin_summary[bin_summary['강수량 구간'] == '0mm']['평균 일 발전량 (kWh)'].iloc[0]
    print(f"🥇 0mm 구간 평균 발전량 (기준): {avg_0mm:,.2f} kWh")

    # 1-5mm 구간의 평균 발전량
    avg_1_5mm = bin_summary[bin_summary['강수량 구간'] == '1-5mm']['평균 일 발전량 (kWh)'].iloc[0]
    print(f"💧 1-5mm 구간 평균 발전량: {avg_1_5mm:,.2f} kWh")

    # 5-10mm 구간의 평균 발전량
    avg_5_10mm = bin_summary[bin_summary['강수량 구간'] == '5-10mm']['평균 일 발전량 (kWh)'].iloc[0]
    print(f"🌧️ 5-10mm 구간 평균 발전량: {avg_5_10mm:,.2f} kWh")
    
    # 최종 비교
    if avg_0mm > avg_1_5mm and avg_0mm > avg_5_10mm:
        print("\n💡 분석: 0mm 구간의 평균 발전량이 다른 모든 구간보다 높습니다. 그래프의 '플러스 영역'은 전체 평균 대비 높은 것이며, 0mm 대비 효율이 좋은 것은 아닙니다.")
    else:
        print("\n❗️ 경고: 0mm 구간보다 강수량이 있는 구간의 평균이 더 높습니다. 데이터 오류 또는 이상치 확인이 필요합니다.")
    print("---------------------------------------------------------")


# 함수 실행
check_bin_averages()