#!/usr/bin/env python3
"""Modern schematic of selected Augustan adoptions, not inherited public office.
Historical loci: Suet.Aug.64--65;Tib.15.2;Dio54.18.1--2;Vell.2.103--104.
"""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'path'})
fig,ax=plt.subplots(figsize=(118/25.4,94/25.4));fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.02)
ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
def box(x,y,text,w=.222,h=.17):
 ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.006',edgecolor='#40515a',facecolor='#f5f4ef',linewidth=.7,zorder=3))
 ax.text(x,y,text,ha='center',va='center',fontsize=7,linespacing=1.35,zorder=4)
def arrow(x1,y1,x2,y2):ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=7,linestyle=(0,(4,3)),linewidth=.8,color='#40515a',zorder=1))
box(.5,.88,'АВГУСТ',w=.30,h=.10)
points=[(.125,'Гай Цезарь\n17 г. до н. э.'),(.375,'Луций Цезарь\n17 г. до н. э.'),(.625,'Тиберий\n4 г. н. э.'),(.875,'Агриппа\nПостум\n4 г. н. э.')]
for x,label in points:arrow(.5,.825,x,.615);box(x,.525,label)
arrow(.625,.435,.625,.285);box(.625,.195,'Германик\n4 г. н. э.',w=.25)
ax.text(.035,.23,'Пунктир — усыновление.\nДаты относятся к отдельным актам.\nСхема не изображает одновременный\nсостав семьи или передачу власти.',fontsize=6.5,ha='left',va='center',linespacing=1.5)
svg=ROOT/'assets/augustan_adoptions.svg';png=ROOT/'assets/augustan_adoptions.png'
fig.savefig(svg);fig.savefig(png,dpi=400);plt.close(fig)
record={'type':'Modern authorial reconstruction, 2026, created with AI assistance','scope':'Selected adoptions in the house of Augustus; not biological genealogy or automatic transmission of office','sources':['Suet.Aug.64.1;65.1','Suet.Tib.15.2','Dio54.18.1--2','Vell.2.103--104'],'editions':'Suetonius/Rolfe1913;Dio/Cary1917;Velleius/Shipley1924, electronic LacusCurtius reproductions; loci also checked in chapter14','rights':'Original project graphic; no external image used; DejaVu font outlines used under its embedding permission','files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [svg,png]]}
(ROOT/'assets/provenance/adoption_scheme.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Created',png.name,svg.name)
