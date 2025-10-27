import pandas as pd
import folium

class SolarMap:
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        
        # ✅ '일시'를 datetime으로 변환하고 년/월/일 컬럼 생성
        if '일시' in self.data.columns:
            self.data['일시'] = pd.to_datetime(self.data['일시'])
            self.data['년'] = self.data['일시'].dt.year
            self.data['월'] = self.data['일시'].dt.month
            self.data['일'] = self.data['일시'].dt.day

    def filter_data(self, year, month, day):
        return self.data[
            (self.data["년"] == year) &
            (self.data["월"] == month) &
            (self.data["일"] == day)
        ]

    def draw_markers(self, filtered, data_type="☀️ 합계일사량"):
        m = folium.Map(location=[36.5, 127.8], zoom_start=7)
        value_col = "합계 일사량(MJ/m2)" if data_type == "☀️ 합계일사량" else "평균 지면온도(°C)"

        for _, row in filtered.iterrows():
            if pd.notna(row["위도"]) and pd.notna(row["경도"]):
                value = row[value_col]
                folium.CircleMarker(
                    location=[row["위도"], row["경도"]],
                    radius=7,
                    color="orange",
                    fill=True,
                    fill_color="orange",
                    fill_opacity=0.7,
                    popup=f"{row['지점명']}<br>{value_col}: {value}"
                ).add_to(m)
        return m
