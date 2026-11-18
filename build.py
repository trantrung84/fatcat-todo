#!/usr/bin/env python3
"""Build www/index.html from src/index.src.html, inlining fonts (base64 woff2) and cat sprites (base64 webp)."""
import base64, io, json, os
from PIL import Image
ROOT=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(ROOT,"src")
LAT="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
VI="U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB"
def b64(p): return base64.b64encode(open(p,"rb").read()).decode()
css=[]
for fam,file,w in [("Baloo 2","baloo-2",800),("Nunito","nunito",600),("Nunito","nunito",700),("Nunito","nunito",800)]:
    for sub,rng in [("vietnamese",VI),("latin",LAT)]:
        f=os.path.join(SRC,"fonts",f"{file}-{sub}-{w}-normal.woff2")
        css.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(data:font/woff2;base64,{b64(f)}) format('woff2');unicode-range:{rng}}}")
spr={}
for fn in sorted(os.listdir(os.path.join(SRC,"sprites"))):
    if not fn.endswith(".png"): continue
    im=Image.open(os.path.join(SRC,"sprites",fn)).convert("RGBA")
    buf=io.BytesIO(); im.save(buf,"WEBP",quality=88,method=6)
    spr[fn[:-4]]="data:image/webp;base64,"+base64.b64encode(buf.getvalue()).decode()
html=open(os.path.join(SRC,"index.src.html"),encoding="utf-8").read()
html=html.replace("/*__FONTS__*/","\n".join(css)).replace("/*__SPRITES__*/{}",json.dumps(spr))
os.makedirs(os.path.join(ROOT,"www"),exist_ok=True)
open(os.path.join(ROOT,"www","index.html"),"w",encoding="utf-8").write(html)
print("www/index.html",len(html)//1024,"KB")
