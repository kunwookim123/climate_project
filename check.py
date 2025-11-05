import pandas as pd
import os
import json
import numpy as np

# ====== 기본 설정 ======
base_path = r"C:\Users\UserK\Documents\GitHub\climate_project\data"
output_path = os.path.join(base_path, "비교지도_슬라이드_최종.html")

# ====== CSV 데이터 로드 ======
weather = pd.read_csv(f"{base_path}\\2020~2024.csv", encoding="utf-8")
pred = pd.read_csv(f"{base_path}\\예측발전량_PR고정_수정.csv", encoding="utf-8")
coords = pd.read_csv(f"{base_path}\\좌표.csv", encoding="utf-8")

# ====== 날짜 컬럼 변환 ======
weather["일시"] = pd.to_datetime(weather["일시"], errors="coerce")
pred["일시"] = pd.to_datetime(pred["일시"], errors="coerce")

# ====== 병합 ======
merged = pd.merge(pred, weather, on=["지점명", "일시"], how="left")
merged = pd.merge(merged, coords, on="지점명", how="left")

# ====== 날짜 지정 ======
rainy_dates = {
    "2020-07-13": "장마철",
    "2021-07-03": "장마철",
    "2022-07-09": "장마철",
    "2023-07-18": "장마철",
    "2024-06-29": "장마철",
}
non_rainy_dates = {
    "2020-02-11": "비장마철",
    "2021-03-20": "비장마철",
    "2022-09-03": "비장마철",
    "2023-11-27": "비장마철",
    "2024-10-14": "비장마철",
}

# ====== 슬라이드 데이터 생성 ======
slides = []

for d, label in {**rainy_dates, **non_rainy_dates}.items():
    d_parsed = pd.to_datetime(d)
    df = merged[merged["일시"].dt.date == d_parsed.date()].copy()
    if df.empty:
        print(f"⚠️ {d} 날짜 데이터 없음")
        continue

    rain_data = df[["지점명", "위도", "경도", "일강수량(mm)"]].dropna()
    power_data = df[["지점명", "위도", "경도", "예측발전량_PR고정(kWh)"]].dropna()

    slides.append({
        "date": d,
        "label": label,
        "rain": rain_data.to_dict(orient="records"),
        "power": power_data.to_dict(orient="records")
    })

# ====== HTML 생성 ======
html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>강수량 & 예측 발전량 비교 슬라이드</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
<style>
body {{
    margin: 0;
    background-color: white;
}}
#container {{
    display: flex;
    height: 100vh;
}}
.map {{
    width: 50%;
    height: 100%;
}}
h2 {{
    position: absolute;
    top: 10px;
    width: 100%;
    text-align: center;
    font-family: 'Malgun Gothic', sans-serif;
    font-size: 22px;
    color: black;
    z-index: 1000;
}}
.legend {{
    position: absolute;
    bottom: 20px;
    left: 20px;
    background: rgba(255,255,255,0.85);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
    line-height: 1.4;
    box-shadow: 0 0 5px rgba(0,0,0,0.2);
    font-family: 'Malgun Gothic', sans-serif;
    z-index: 1000;
}}
</style>
</head>
<body>

<h2 id="title"></h2>
<div id="container">
    <div id="mapLeft" class="map"></div>
    <div id="mapRight" class="map"></div>
</div>
<div class="legend">
    <b>🟦 일강수량(mm)</b><br>
    진할수록 강수량 많음<br><br>
    <b>🟧 예측 발전량(kWh)</b><br>
    진할수록 발전량 많음
</div>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.sync/L.Map.Sync.js"></script>

<script>
const slides = {json.dumps(slides, ensure_ascii=False, indent=2)};
let current = 0;

const mapLeft = L.map('mapLeft', {{
    center: [35.8, 128.0],
    zoom: 7,
    zoomControl: false
}});
const mapRight = L.map('mapRight', {{
    center: [35.8, 128.0],
    zoom: 7,
    zoomControl: false
}});

L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(mapLeft);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(mapRight);

mapLeft.sync(mapRight);
mapRight.sync(mapLeft);

let leftMarkers = [];
let rightMarkers = [];

function clearMarkers() {{
    leftMarkers.forEach(m => mapLeft.removeLayer(m));
    rightMarkers.forEach(m => mapRight.removeLayer(m));
    leftMarkers = [];
    rightMarkers = [];
}}

// 색상 및 크기 비선형(log) 조정 → 작은 값도 보이게
function getAdjustedValue(v, max) {{
    return Math.pow(Math.log1p(v) / Math.log1p(max), 0.8);
}}

// 색상: 기존 스타일 유지
function getRainColor(v, max) {{
    const ratio = getAdjustedValue(v, max);
    const r = Math.floor(30 + 30 * ratio);
    const g = Math.floor(90 + 70 * (1 - ratio));
    const b = Math.floor(160 + 50 * (1 - ratio));
    return `rgb(${{r}}, ${{g}}, ${{b}})`; // 파란계열
}}

function getPowerColor(v, max) {{
    const ratio = getAdjustedValue(v, max);
    const r = Math.floor(255 * ratio);
    const g = Math.floor(150 * (1 - ratio) + 80);
    const b = Math.floor(50 * (1 - ratio));
    return `rgb(${{r}}, ${{g}}, ${{b}})`; // 주황계열
}}

function showSlide(index) {{
    if (index < 0) index = slides.length - 1;
    if (index >= slides.length) index = 0;
    current = index;
    const s = slides[index];
    document.getElementById("title").innerText = `📅 ${{s.date}} — ${{s.label}}`;

    clearMarkers();

    const maxRain = Math.max(...s.rain.map(d => d["일강수량(mm)"]));
    const maxPower = Math.max(...s.power.map(d => d["예측발전량_PR고정(kWh)"]));
    const maxRadius = 18;

    // 🌧 왼쪽 지도 (일강수량)
    s.rain.forEach(d => {{
        const ratio = getAdjustedValue(d["일강수량(mm)"], maxRain);
        const radius = Math.max(5, ratio * maxRadius);
        const color = getRainColor(d["일강수량(mm)"], maxRain);
        const marker = L.circleMarker([d["위도"], d["경도"]], {{
            radius: radius,
            fillColor: color,
            fillOpacity: 0.8,
            stroke: false
        }}).bindTooltip(
            `📍 ${{d["지점명"]}}<br>🌧 일강수량: ${{d["일강수량(mm)"].toFixed(1)}} mm`,
            {{ direction: 'top' }}
        );
        marker.addTo(mapLeft);
        leftMarkers.push(marker);
    }});

    // ⚡ 오른쪽 지도 (예측 발전량)
    s.power.forEach(d => {{
        const ratio = getAdjustedValue(d["예측발전량_PR고정(kWh)"], maxPower);
        const radius = Math.max(5, ratio * maxRadius);
        const color = getPowerColor(d["예측발전량_PR고정(kWh)"], maxPower);
        const marker = L.circleMarker([d["위도"], d["경도"]], {{
            radius: radius,
            fillColor: color,
            fillOpacity: 0.8,
            stroke: false
        }}).bindTooltip(
            `📍 ${{d["지점명"]}}<br>⚡ 예측 발전량: ${{d["예측발전량_PR고정(kWh)"].toFixed(2)}} kWh`,
            {{ direction: 'top' }}
        );
        marker.addTo(mapRight);
        rightMarkers.push(marker);
    }});
}}

document.addEventListener("keydown", (e) => {{
    if (e.code === "ArrowRight" || e.code === "Space") showSlide(current + 1);
    else if (e.code === "ArrowLeft") showSlide(current - 1);
}});

showSlide(0);
</script>
</body>
</html>
"""

# ====== 저장 ======
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 슬라이드 HTML 생성 완료!\n📂 {output_path}")
