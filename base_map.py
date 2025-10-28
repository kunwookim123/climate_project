# base_map.py

import folium
import pandas as pd
import os
import re

class BaseMap:
    def __init__(self, data_path: str, location_csv: str = "data/좌표.csv"):
        """CSV나 리스트 데이터를 로드"""
        self.data_path = data_path
        self.location_csv = location_csv
        self.location_data = self.load_location_data(location_csv)
        self.df = self.load_data(data_path)

    def load_location_data(self, location_csv):
        """지점좌표 CSV 파일에서 지역명-위도/경도 정보를 불러옴"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        abs_path = os.path.join(data_dir, os.path.basename(location_csv))

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"좌표 파일이 존재하지 않습니다: {abs_path}")

        loc_df = pd.read_csv(abs_path, encoding="utf-8-sig")
        loc_dict = {row["지역명"]: [row["위도"], row["경도"]] for _, row in loc_df.iterrows()}
        return loc_dict

    def load_data(self, data_path):
        """CSV 또는 리스트 형태 데이터 읽기 및 자동 구조 변환"""
        if isinstance(data_path, str) and not os.path.isabs(data_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, data_path)

        if isinstance(data_path, str) and data_path.endswith(".csv"):
            df = pd.read_csv(data_path, encoding="utf-8-sig")
            df = self.auto_convert(df)
            return df
        elif isinstance(data_path, list):
            return pd.DataFrame(data_path, columns=["연도", "월", "일", "지역", "위도", "경도", "값"])
        else:
            raise ValueError("지원하지 않는 데이터 형식입니다.")

    def auto_convert(self, df):
        """CSV 구조 자동 변환"""
        cols = df.columns

        if "일시" in cols:
            try:
                df["연도"] = df["일시"].str[:4].astype(int)
                df["월"] = df["일시"].str[5:7].astype(int)
                df["일"] = df["일시"].str[8:10].astype(int)
            except Exception:
                df["연도"], df["월"], df["일"] = None, None, 1

        if "지점명" in cols:
            df.rename(columns={"지점명": "지역"}, inplace=True)

        # 좌표 자동 매핑
        df["위도"] = df["지역"].map(lambda x: self.location_data.get(x, [None, None])[0])
        df["경도"] = df["지역"].map(lambda x: self.location_data.get(x, [None, None])[1])

        # 값 자동 식별
        for key in ["일사", "강수", "온도"]:
            col = [c for c in cols if key in c]
            if col:
                df.rename(columns={col[0]: "값"}, inplace=True)
                break

        df = df.dropna(subset=["위도", "경도"])
        return df

    def filter_data(self, year, month, day):
        return self.df[
            (self.df["연도"].astype(int) == year)
            & (self.df["월"].astype(int) == month)
            & (self.df["일"].astype(int) == day)
        ]

    def create_map(self, lat=36.5, lon=127.8, zoom=7):
        """기본 지도 생성"""
        return folium.Map(location=[lat, lon], zoom_start=zoom, control_scale=True)
