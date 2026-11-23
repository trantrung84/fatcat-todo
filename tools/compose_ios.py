import asyncio,base64,re
from playwright.async_api import async_playwright
html=open('/home/claude/fatcat-todo/www/index.html',encoding='utf-8').read()
fonts="\n".join(re.findall(r"@font-face\{[^}]*\}",html))
b64=lambda p:"data:image/png;base64,"+base64.b64encode(open(p,'rb').read()).decode()
R="/home/claude/storeraw/";import sys
OUT="/home/claude/fatcat-todo/store/ios/"
import os;os.makedirs(OUT,exist_ok=True)
W,H,Z,PHW,TAG=[(1320,2868,1320/1080,900,"iphone"),(2064,2752,2064/1080,450,"ipad"),(1398,2034,1398/1080,480,"duo")][int(sys.argv[1])]
SPR="/home/claude/fatcat-todo/src/sprites/";WP="/home/claude/fatcat-todo/android/app/src/main/res/drawable-nodpi/"
slides=[("1-home.png","Plan gently with Mochi","Today & Someday to-dos that never nag","#FFE3D8"),
("2-calendar.png","Your month at a glance","A little cat face shows how each day went","#FDEBD3"),
("3-quickadd.png","Add tasks in a tap","Focus mode keeps you on track","#E9E3F7"),
("4-alldone.png","Celebrate finished days","Confetti, purrs and a very happy cat","#DFF3E8"),
("5-luxe.png","10 cozy color themes","Including Luxe: black, white & gold","#EFE7D2"),
(None,"Home-screen widgets","See today's tasks without opening the app","#DCEBFA")]
CSS=f"""{fonts}
body{{margin:0}}.s{{width:1080px;height:{H/Z}px;zoom:{Z};position:relative;overflow:hidden;font-family:'Baloo 2',sans-serif;color:#4A2C24;display:flex;flex-direction:column;align-items:center}}
.t{{font-size:92px;font-weight:800;line-height:1;margin-top:120px;text-align:center;padding:0 60px}}
.st{{font-family:'Nunito',sans-serif;font-weight:700;font-size:44px;color:#7E5D52;margin-top:22px;text-align:center;padding:0 80px}}
.ph{{margin-top:{110 if TAG=="iphone" else 60}px;width:{PHW}px;border-radius:70px;border:16px solid #2B211E;box-shadow:0 40px 90px rgba(70,35,20,.28);overflow:hidden;background:#fff}}
.ph img{{display:block;width:100%}}.dot{{position:absolute;border-radius:50%;opacity:.45}}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={"width":W,"height":H})
        for i,(img,ti,st,bg) in enumerate(slides,1):
            if img: inner=f'<div class="ph"><img src="{b64(R+img)}"></div>'
            else:
                inner=f'''<div style="margin-top:80px;width:880px;height:{1750 if TAG=="iphone" else 1050}px;border-radius:60px;background:linear-gradient(160deg,#F9C9B6,#C7B8F0 55%,#9FC9F2);position:relative;box-shadow:0 40px 90px rgba(70,35,20,.22)">
                 <img src="{b64(WP+'widget_preview_large.png')}" style="position:absolute;left:60px;top:90px;width:760px">
                 <img src="{b64(WP+'widget_preview_small.png')}" style="position:absolute;left:60px;top:560px;width:380px">
                 <div style="position:absolute;left:470px;top:560px;width:350px;height:380px;border-radius:44px;background:rgba(255,255,255,.35)"></div>
                 <div style="position:absolute;bottom:60px;left:70px;right:70px;height:150px;border-radius:50px;background:rgba(255,255,255,.4)"></div></div>'''
            deco=f'<img src="{b64(SPR+"check.png")}" style="position:absolute;right:40px;bottom:30px;width:300px">' if i==6 else ""
            page=f'<html><head><style>{CSS}</style></head><body><div class="s" style="background:{bg}"><div class="dot" style="width:420px;height:420px;background:#fff;left:-140px;top:-120px"></div><div class="dot" style="width:300px;height:300px;background:#fff;right:-90px;top:420px"></div><div class="t">{ti}</div><div class="st">{st}</div>{inner}{deco}</div></body></html>'
            await pg.set_content(page);await pg.wait_for_timeout(300);await pg.screenshot(path=f"{OUT}{TAG}-{i}.png")
        await b.close()
asyncio.run(main())
