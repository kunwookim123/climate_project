import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os

def generate_monthly_graph_with_long_term_avg_change():
    # -----------------------------------------------------------------
    # 1단계: 데이터 불러오기 및 월별 집계
    # -----------------------------------------------------------------
    try:
        # 🚨 파일 경로에 'data/' 적용
        weather_df = pd.read_csv('data/2020~2024.csv')
        gen_df = pd.read_csv('data/예측발전량_PR고정_수정.csv')
    except FileNotFoundError:
        print("🚨 오류: 파일을 찾을 수 없습니다. 파일 이름을 확인하세요. (경로: data/파일명)")
        return

    df = pd.merge(
        weather_df[['지점명', '일시']],
        gen_df[['지점명', '일시', '예측발전량_PR고정(kWh)']],
        on=['지점명', '일시']
    )
    df['일시'] = pd.to_datetime(df['일시'])
    
    # 월별 집계
    df['year'] = df['일시'].dt.year
    df['month'] = df['일시'].dt.month
    df['period_str'] = df['일시'].dt.strftime('%Y. %m')
    
    monthly_df = df.groupby(['year', 'month', 'period_str']).agg(
        총_발전량=('예측발전량_PR고정(kWh)', 'sum')
    ).reset_index()

    # -----------------------------------------------------------------
    # 2단계: 동월 장기 평균 계산 및 변화율 적용
    # -----------------------------------------------------------------
    
    # (A) '월'별 장기 평균 총 발전량 계산 (2020~2024년 전체 데이터 기준)
    monthly_avg_base = monthly_df.groupby('month')['총_발전량'].mean().reset_index()
    monthly_avg_base.rename(columns={'총_발전량': '동월_장기_평균_발전량'}, inplace=True)
    
    # (B) 월별 데이터에 장기 평균 값 병합
    monthly_df = pd.merge(monthly_df, monthly_avg_base, on='month')
    
    # (C) 동월 장기 평균 대비 변화율 계산 (플러스/마이너스)
    monthly_df['동월 평균 대비 변화율 (%)'] = (
        (monthly_df['총_발전량'] / monthly_df['동월_장기_평균_발전량']) - 1
    ) * 100

    # -----------------------------------------------------------------
    # 3단계: Plotly를 이용한 대화형 그래프 생성
    # -----------------------------------------------------------------
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # --- 색상 변수 설정 ---
    COLOR_GEN = '#1f77b4'  # 파란색 (발전량)
    COLOR_CHANGE = '#ff7f0e'  # 주황색 (변화율)

    # Y1: 총 발전량 (꺾은선)
    fig.add_trace(
        go.Scatter(x=monthly_df['period_str'], y=monthly_df['총_발전량'], 
                   name='월 총 발전량 (kWh)', mode='lines+markers', 
                   line=dict(color=COLOR_GEN, width=3),
                   hovertemplate = '<b>%{x}</b><br>총 발전량: %{y:,.0f} kWh<extra></extra>'),
        secondary_y=False,
    )

    # Y2: 동월 평균 대비 변화율 (%) (막대 그래프)
    fig.add_trace(
        go.Bar(x=monthly_df['period_str'], y=monthly_df['동월 평균 대비 변화율 (%)'], 
               name='동월 평균 대비 변화율 (%)', 
               marker=dict(color=COLOR_CHANGE, opacity=0.7),
               hovertemplate = '<b>%{x}</b><br>변화율: %{y:.2f} %<extra></extra>'),
        secondary_y=True,
    )

    # 기준선 (0% 라인) 추가: 해당 월의 장기 평균 성능을 시각적으로 강조
    fig.add_hline(y=0, line_dash="dash", secondary_y=True, line_color="gray", annotation_text="동월 장기 평균 (0%)")


    # --- 레이아웃 설정 ---
    fig.update_layout(
        template='plotly_white',
        title_text='<b>월별 총 발전량 및 동월 장기 평균 대비 변화율 추이 (2020~2024)</b>',
        title_font_size=20,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=100, l=50, r=50) 
    )

    # X축 설정: 6개월 단위로 레이블 표시
    tick_labels_6m = monthly_df['period_str'].iloc[::6]
    fig.update_xaxes(
        tickangle=45, 
        title_text="연도 및 월",
        tickvals=tick_labels_6m, 
        ticktext=tick_labels_6m, 
    )
    
    # Y축 설정
    fig.update_yaxes(title_text="<b>월 총 발전량 (kWh)</b>", secondary_y=False, title_font=dict(color=COLOR_GEN))
    fig.update_yaxes(title_text="<b>동월 평균 대비 변화율 (%)</b>", secondary_y=True, title_font=dict(color=COLOR_CHANGE))

    # -----------------------------------------------------------------
    # 4단계: HTML 파일로 저장
    # -----------------------------------------------------------------
    html_filename = 'interactive_pv_monthly_long_term_avg.html'
    fig.write_html(html_filename, auto_open=True)
    
    print(f"\n✅ 동월 평균 대비 변화율이 적용된 월별 HTML 파일 생성 완료! '{html_filename}'이 웹 브라우저에서 열립니다.")

# 함수 실행
generate_monthly_graph_with_long_term_avg_change()
