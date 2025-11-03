import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium import Choropleth, LayerControl

base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"

# --- 데이터 로드 ---
coords = pd.read_csv(f"{base_path}\\좌표.csv", encoding="utf-8")
fixed = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")
variable = pd.read_csv(f"{base_path}\\예측발전량_PR가변_수정.csv", encoding="utf-8")

# 평균값 계산
fixed_mean = fixed.groupby("지점명")["예측발전량_PR고정(kWh)"].mean().reset_index()
variable_mean = variable.groupby("지점명")["예측발전량_PR가변(kWh)"].mean().reset_index()

# 병합
merged = coords.merge(fixed_mean, on="지점명", how="left").merge(variable_mean, on="지점명", how="left")

# --- 행정구역 GeoJSON 로드 ---
gdf_provinces = gpd.read_file(f"{base_path}\\skorea_provinces_geo.json", encoding="utf-8")

# 영어 → 한글 변환
name_map = {
    "Seoul": "서울특별시", "Busan": "부산광역시", "Daegu": "대구광역시",
    "Incheon": "인천광역시", "Gwangju": "광주광역시", "Daejeon": "대전광역시",
    "Ulsan": "울산광역시", "Gyeonggi-do": "경기도", "Gangwon-do": "강원도",
    "Chungcheongbuk-do": "충청북도", "Chungcheongnam-do": "충청남도",
    "Jeollabuk-do": "전라북도", "Jeollanam-do": "전라남도",
    "Gyeongsangbuk-do": "경상북도", "Gyeongsangnam-do": "경상남도",
    "Jeju-do": "제주특별자치도", "Sejong": "세종특별자치시"
}
gdf_provinces["NAME_1"] = gdf_provinces["NAME_1"].map(name_map)

# --- 좌표를 GeoDataFrame으로 변환 ---
gdf_points = gpd.GeoDataFrame(
    merged,
    geometry=gpd.points_from_xy(merged["경도"], merged["위도"]),
    crs="EPSG:4326"
)

# --- 각 지점이 속한 도 이름 매핑 ---
joined = gpd.sjoin(gdf_points, gdf_provinces[['geometry', 'NAME_1']], how="left", predicate="within")
joined = joined.rename(columns={"NAME_1": "도"})

# --- 도별 평균 발전량 계산 ---
prov_mean = joined.groupby("도")[["예측발전량_PR고정(kWh)", "예측발전량_PR가변(kWh)"]].mean().reset_index()

# GeoDataFrame에 합치기
gdf_provinces = gdf_provinces.merge(prov_mean, left_on="NAME_1", right_on="도", how="left")

# --- 지도 생성 ---
center_lat, center_lon = merged["위도"].mean(), merged["경도"].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="CartoDB positron")

# --- Choropleth (도별 색상 지도) ---
for col, label in [("예측발전량_PR고정(kWh)", "PR 고정"), ("예측발전량_PR가변(kWh)", "PR 가변")]:
    choropleth = Choropleth(
        geo_data=gdf_provinces,
        data=gdf_provinces,
        columns=["NAME_1", col],
        key_on="feature.properties.NAME_1",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"도별 평균 예측발전량 ({label}) [kWh]",
        name=f"{label} 지도"
    )
    choropleth.add_to(m)

# --- 지점별 마커 추가 ---
for _, row in joined.iterrows():
    popup_text = (
        f"<b>지점명:</b> {row['지점명']}<br>"
        f"<b>도:</b> {row['도']}<br>"
        f"<b>예측발전량(PR 고정):</b> {row['예측발전량_PR고정(kWh)']:.2f} kWh<br>"
        f"<b>예측발전량(PR 가변):</b> {row['예측발전량_PR가변(kWh)']:.2f} kWh"
    )
    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=5,
        color="black",
        fill=True,
        fill_opacity=0.8,
        fill_color="blue",
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# --- 지도 제어기 추가 (레이어 전환용) ---
LayerControl(collapsed=False).add_to(m)

# --- 저장 ---
output_path = f"{base_path}\\도별_평균_예측발전량_지도.html"
m.save(output_path)
print("✅ 지도 저장 완료:", output_path)
