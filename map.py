import pandas as pd
import geopandas as gpd
import folium
from folium import plugins
from shapely.geometry import Point

# ===== 기본 경로 =====
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"

# ===== 파일 불러오기 =====
coords = pd.read_csv(f"{base_path}\\좌표.csv", encoding="utf-8")
fixed = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")
variable = pd.read_csv(f"{base_path}\\예측발전량_PR가변_수정.csv", encoding="utf-8")

# ===== 평균 예측 발전량 계산 =====
fixed_mean = fixed.groupby("지점명")["예측발전량_PR고정(kWh)"].mean().reset_index()
variable_mean = variable.groupby("지점명")["예측발전량_PR가변(kWh)"].mean().reset_index()

merged = coords.merge(fixed_mean, on="지점명", how="left").merge(variable_mean, on="지점명", how="left")

# ===== GeoJSON 파일 불러오기 =====
geo_path = f"{base_path}\\skorea_provinces_geo.json"
gdf_provinces = gpd.read_file(geo_path, encoding="utf-8")

# ===== 영어 → 한글 도 이름 변환 =====
name_map = {
    "Seoul": "서울특별시", "Busan": "부산광역시", "Daegu": "대구광역시", "Incheon": "인천광역시",
    "Gwangju": "광주광역시", "Daejeon": "대전광역시", "Ulsan": "울산광역시",
    "Gyeonggi-do": "경기도", "Gangwon-do": "강원특별자치도",
    "Chungcheongbuk-do": "충청북도", "Chungcheongnam-do": "충청남도",
    "Jeollabuk-do": "전라북도", "Jeollanam-do": "전라남도",
    "Gyeongsangbuk-do": "경상북도", "Gyeongsangnam-do": "경상남도",
    "Jeju-do": "제주특별자치도", "Sejong": "세종특별자치시"
}
gdf_provinces["NAME_1"] = gdf_provinces["NAME_1"].map(name_map)

# ===== 지점 좌표를 GeoDataFrame으로 변환 =====
gdf_points = gpd.GeoDataFrame(
    merged,
    geometry=gpd.points_from_xy(merged["경도"], merged["위도"]),
    crs="EPSG:4326"
)

# ===== 도 단위 매핑 =====
joined = gpd.sjoin(gdf_points, gdf_provinces[['geometry', 'NAME_1']], how="left", predicate="within")
joined = joined.rename(columns={"NAME_1": "도"})

# ===== 권역 기준 색상 통합 =====
region_group = {
    # 수도권
    "서울특별시": "경기도",
    "인천광역시": "경기도",
    # 충청권
    "대전광역시": "충청남도",
    "세종특별자치시": "충청남도",
    # 영남권
    "부산광역시": "경상남도",
    "울산광역시": "경상남도",
    "대구광역시": "경상북도",
    # 호남권
    "광주광역시": "전라남도",
}

joined["권역"] = joined["도"].replace(region_group)

# ===== 🎨 권역별 색상 (PPT용, 명확한 대비) =====
region_colors = {
    "경기도": "#FFD700",      # 금색
    "강원특별자치도": "#58228B",  # 보라
    "충청북도": "#D100B2",      # 선명한 진분홍
    "충청남도": "#1E90FF",      # 파랑
    "전라북도": "#32CD32",      # 연초록
    "전라남도": "#008000",      # 녹색
    "경상북도": "#8B0000",      # 진한 빨강
    "경상남도": "#FF4500",      # 주황빨강
    "제주특별자치도": "#708090"   # 회색
}

# ===== 지도 생성 =====
m = folium.Map(location=[merged["위도"].mean(), merged["경도"].mean()],
               zoom_start=7, tiles="OpenStreetMap")

# ===== 마커 표시 =====
for _, row in joined.iterrows():
    region_color = region_colors.get(row["권역"], "gray")
    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=7,
        color=region_color,
        fill=True,
        fill_color=region_color,
        fill_opacity=0.9,
        popup=folium.Popup(
            f"<b>지점명:</b> {row['지점명']}<br>"
            f"<b>도:</b> {row['도']}<br>"
            f"<b>권역(색상 기준):</b> {row['권역']}<br>"
            f"<b>예측 발전량(PR 고정):</b> {row['예측발전량_PR고정(kWh)']:.2f} kWh<br>"
            f"<b>예측 발전량(PR 가변):</b> {row['예측발전량_PR가변(kWh)']:.2f} kWh",
            max_width=300
        )
    ).add_to(m)

# ===== 클러스터 기능 추가 =====
plugins.MarkerCluster().add_to(m)

# ===== 저장 =====
output_path = f"{base_path}\\예측발전량_지도_권역색상.html"
m.save(output_path)
print("✅ 지도 저장 완료:", output_path)
