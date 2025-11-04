import os
from glob import glob
import json

# ✅ PNG 파일들이 들어있는 폴더 경로
folder = r"C:\Users\UserK\Documents\GitHub\climate_project\data\발표용_장마비교지도_HTML"

if not os.path.isdir(folder):
    raise SystemExit("❌ 폴더를 찾을 수 없습니다. 경로를 다시 확인하세요.")

# ✅ PNG 파일 불러오기
pngs = sorted(glob(os.path.join(folder, "*.png")))
non_rain = sorted([p for p in pngs if "비장마" in os.path.basename(p)])
rain = sorted([p for p in pngs if "장마" in os.path.basename(p)])
ordered = non_rain + rain

if not ordered:
    raise SystemExit("❌ '비장마' 또는 '장마' PNG 파일을 찾지 못했습니다.")

# ✅ 이미지 태그 자동 생성
img_tags = []
titles = []
for i, full in enumerate(ordered):
    fname = os.path.basename(full)
    img_tags.append(f'<img src="{fname}" class="slide" id="slide{i}">')
    titles.append(os.path.splitext(fname)[0].split("_")[-1])

# ✅ HTML 본문 생성
html_body = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><title>강수량·예측 발전량 슬라이드</title>
<style>
  html,body{{height:100%;margin:0;background:#fff}}
  body{{display:flex;align-items:center;justify-content:center;font-family:'Malgun Gothic',sans-serif}}
  .container{{position:relative;width:100%;height:100%;overflow:hidden}}
  img.slide{{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;display:none;background:white}}
  .active{{display:block}}
  #title{{position:fixed;top:12px;width:100%;text-align:center;color:#222;font-size:22px;z-index:999;font-weight:bold}}
  #progress{{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);color:#333;font-size:14px;z-index:999}}
</style></head><body>
<div class="container">
  <div id="title">2020~2024 강수량·예측 발전량 비교</div>
  {''.join(img_tags)}
  <div id="progress"></div>
</div>
<script>
let current = 0;
const slides = document.getElementsByClassName('slide');
const titles = {json.dumps(titles, ensure_ascii=False)};

function showSlide(n) {{
  if(slides.length===0) return;
  if(n<0) n=slides.length-1;
  if(n>=slides.length) n=0;
  for(let i=0;i<slides.length;i++) slides[i].classList.remove('active');
  slides[n].classList.add('active');
  document.getElementById('title').innerText = titles[n];
  document.getElementById('progress').innerText = (n+1) + '/' + slides.length;
  current = n;
}}

function nextSlide(){{ showSlide(current+1); }}
function prevSlide(){{ showSlide(current-1); }}

document.addEventListener('keydown', function(e) {{
  if(e.key==='ArrowRight' || e.key===' ') nextSlide();
  if(e.key==='ArrowLeft') prevSlide();
}});

showSlide(0);
</script>
</body></html>
"""

# ✅ HTML 저장
output = os.path.join(folder, "발표용_장마비교_이미지슬라이드.html")
with open(output, "w", encoding="utf-8") as f:
    f.write(html_body)

print("✅ 생성 완료:", output)
print("📸 슬라이드 수:", len(ordered))
