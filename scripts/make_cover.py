#!/usr/bin/env python3
"""Original typographic cover; no historical object or portrait is represented."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont
from xml.sax.saxutils import escape
ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--edition',default='ИССЛЕДОВАТЕЛЬСКОЕ ИЗДАНИЕ')
args=parser.parse_args()
W,H=1600,2400
BG='#142027'; GOLD='#cbb787'; IVORY='#f0eadc'
regular='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
lines=[
 ('CAESAR & AUGUSTUS',800,360,41,GOLD,False),
 ('ЮЛИЙ ЦЕЗАРЬ',800,700,99,IVORY,True),
 ('И ОКТАВИАН',800,845,89,IVORY,True),
 ('АВГУСТ',800,990,113,IVORY,True),
 ('Две политические биографии',800,1320,52,IVORY,False),
 ('и рождение Римской империи',800,1400,52,IVORY,False),
 ('От кризиса Республики',800,1660,48,GOLD,False),
 ('к установлению принципата',800,1737,48,GOLD,False),
 (args.edition,800,2070,32,GOLD,False),
 ('2026',800,2140,35,GOLD,False),
]
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
d.rectangle((95,95,W-95,H-95),outline=GOLD,width=3)
d.rectangle((112,112,W-112,H-112),outline=GOLD,width=1)
d.line((590,1190,1010,1190),fill=GOLD,width=3)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="1600" height="2400" fill="{BG}"/>',f'<rect x="95" y="95" width="1410" height="2210" fill="none" stroke="{GOLD}" stroke-width="3"/>',f'<rect x="112" y="112" width="1376" height="2176" fill="none" stroke="{GOLD}"/>',f'<path d="M590 1190H1010" stroke="{GOLD}" stroke-width="3"/>']
for text,x,y,size,color,is_bold in lines:
 f=ImageFont.truetype(bold if is_bold else regular,size)
 d.text((x,y),text,font=f,fill=color,anchor='mm')
 weight='bold' if is_bold else 'normal'
 svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Serif" font-weight="{weight}" font-size="{size}" text-anchor="middle" dominant-baseline="middle">{escape(text)}</text>')
svg.append('</svg>')
im.save(ROOT/'assets/cover.png',optimize=True)
(ROOT/'assets/cover.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
