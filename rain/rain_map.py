#rain_map.py

from base_map import BaseMap
import folium
import pandas as pd

class RainMap(BaseMap):
    def __init__(self, csv_file, location_csv="data/좌표.csv"):
        super().__init__(csv_file, location_csv)

    def draw_markers(self, df, data_type="🌧️ 일강수량"):
        m = self.create_map()

        if df.empty:
            folium.Marker(
                [36.5, 127.8],
                popup="⚠️ 선택한 날짜의 데이터가 없습니다.",
                icon=folium.Icon(color="gray")
            ).add_to(m)
            return m

        df = df.drop_duplicates(subset=["지역", "연도", "월", "일"], keep="last")

        value_col = [c for c in df.columns if "강수" in c]
        value_col = value_col[0] if value_col else "값"

        for _, row in df.iterrows():
            if pd.notna(row["위도"]) and pd.notna(row["경도"]):
                val = row.get(value_col, "N/A")
                popup_html = f"<div style='white-space:nowrap;'>🌧️ {row['지역']} | 일강수량: {val} mm</div>"

                folium.CircleMarker(
                    [row["위도"], row["경도"]],
                    radius=7,
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.8,
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(m)

        return m
