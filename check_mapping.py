import fiona

path = "data/bnd_sido_00_2024_2Q/bnd_sido_00_2024_2Q.shp"

with fiona.open(path) as src:
    print("필드명 목록:", src.schema["properties"])
    first = next(iter(src))
    print("\n첫 번째 레코드 속성:", first["properties"])
