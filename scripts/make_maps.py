#!/usr/bin/env python3
"""Render the three research maps from preserved official data (no network).

Python 3 + matplotlib only.  No political boundaries are inferred. Coordinates
are representative Pleiades points, never invented battlefield coordinates.
Natural Earth shapefile polygons are read here with Python's standard library.
Run from anywhere: python scripts/make_maps.py
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch
import matplotlib.patheffects as pe

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/maps'
DATA = OUT / 'data'
INK, SEA, LAND, COAST = '#202d36', '#edf3f5', '#f7f5ef', '#7b888d'
COLORS = {'a': '#254f70', 'b': '#a54828', 'c': '#24756b', 'r': '#444444'}
MARKERS = {'a': 'o', 'b': 's', 'c': '^', 'r': '*'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5,
                     'svg.fonttype': 'none', 'svg.hashsalt': 'caesar-augustus-maps-v1',
                     'axes.linewidth': .5, 'text.color': INK,
                     'xtick.color': '#53636c', 'ytick.color': '#53636c'})

# Each entry contains only a geographical anchor, a selected historical event,
# and its directly checked primary locus.  Dates are BCE throughout.
GAUL = [
 ('177528', 'Генава', '58', 'a', 'Caes. BG 1.6–8', 'Мост и начало кампании против гельветов.', False),
 ('177473', 'Бибракте', '58', 'a', 'Caes. BG 1.23–24', 'Ориентир кампании; поле сражения не локализовано этой точкой.', False),
 ('177657', 'Везонтион', '58', 'a', 'Caes. BG 1.38', 'Занятие города перед действиями против Ариовиста.', False),
 ('109321', 'Самаробрива', '54', 'b', 'Caes. BG 5.24; 5.53', 'Собрание галлов и зимняя дислокация; не поле битвы.', False),
 ('138207', 'Аварик', '52', 'c', 'Caes. BG 7.13; 7.27–28', 'Осада и взятие города.', False),
 ('138373', 'Герговия?', '52', 'c', 'Caes. BG 7.36', 'В Pleiades название Gergovia?; неопределённость сохранена.', True),
 ('177434', 'Алезия', '52', 'c', 'Caes. BG 7.68–69; 7.89', 'Осада; точка обозначает поселение, а не линии осадных сооружений.', False),
]
CIVIL = [
 ('246431', 'Илерда', '49', 'a', 'Caes. BC 1.38–41; 1.78–87', 'Район кампании, завершившейся капитуляцией.', False),
 ('481818', 'Диррахий', '48', 'a', 'Caes. BC 3.41–45; 3.62–72', 'Город-ориентир сражений; не точка прорыва укреплений.', False),
 ('541042', 'Фарсал', '48', 'a', 'Caes. BC 3.82–99', 'Город-ориентир Фарсальского сражения; положение поля битвы этим не устанавливается.', False),
 ('324827', 'Тапс', '46', 'a', 'Dio 43.7–8', 'Поселение-ориентир сражения.', False),
 ('256314', 'Мунда?', '45', 'a', 'Dio 43.35–38', 'Pleiades указывает Cerro de las Camorras?; локализация предположительна.', True),
 ('383715', 'Мутина', '43', 'b', 'App. BC 3.71–72', 'Бои у города; соседний Форум Галлорум отдельной точкой не обозначен.', False),
 ('501482', 'Филиппы', '42', 'b', 'App. BC 4.105–112; 4.128–131', 'Город-ориентир двух сражений.', False),
 ('462384', 'Навлох', '36', 'c', 'App. BC 5.116; 5.118–121', 'Береговой ориентир морского сражения; точное положение флотов не дано.', False),
 ('530772', 'Акций', '31', 'c', 'Dio 50.12; 50.31–35; 51.1.1', 'Мыс-ориентир морского сражения; не координаты боевого построения.', False),
 ('727070', 'Александрия', '30', 'c', 'Dio 51.9–10', 'Город-ориентир завершающих боёв в Египте.', False),
]
ADMIN = [
 ('246349', 'Испания: Тарракон', '27', 'a', 'Dio 53.12.5', 'Географический ориентир провинциального управления Августа.', False),
 ('246347', 'Нарбонская Галлия: Нарбон', '27', 'a', 'Dio 53.12.5; 53.12.7', 'В выбранном срезе у Августа; последующая передача народу не перенесена в 27 г.', False),
 ('658381', 'Сирия: Антиохия', '27', 'a', 'Dio 53.12.7', 'Географический ориентир; сопредельные области не закрашены.', False),
 ('727070', 'Египет: Александрия', '27', 'a', 'Dio 53.12.7; 51.17.1', 'Особый порядок: всаднический префект; общий цвет не делает Египет обычной легатской провинцией.', False),
 ('314921', 'Африка: Карфаген', '27', 'b', 'Dio 53.12.4', 'Выборочный ориентир провинций народа и сената.', False),
 ('599612', 'Азия: Эфес', '27', 'b', 'Dio 53.12.4', 'Выборочный ориентир провинций народа и сената.', False),
 ('491741', 'Македония: Фессалоника', '27', 'b', 'Dio 53.12.4', 'Выборочный ориентир; позднейшие изменения границ не изображены.', False),
 ('589796', 'Крит и Киренаика: Гортина', '27', 'b', 'Dio 53.12.4; 53.12.8', 'Один ориентир составной провинции; не вся её территория.', False),
 ('619103', 'Галатия, Аминта: Анкира', '27', 'c', 'Dio 49.32.3; 51.2.1; 53.26.3', 'Выборочный ориентир зависимого царства; провинция возникла после смерти Аминты в 25 г.', False),
 ('629035', 'Каппадокия, Архелай: Мазака', '27', 'c', 'Dio 49.32.3; 51.2.1', 'Выборочный ориентир зависимого царства; не утверждение о точном местонахождении царского двора.', False),
]

def place(pid):
    return json.loads((DATA / f'pleiades_{pid}.json').read_text())


def rings():
    """Read Polygon parts from the official Natural Earth .shp inside its ZIP."""
    with zipfile.ZipFile(DATA / 'natural_earth_50m_land.zip') as z:
        raw = z.read('ne_50m_land.shp')
    if struct.unpack('>i', raw[:4])[0] != 9994:
        raise ValueError('Unexpected shapefile header')
    pos = 100
    while pos < len(raw):
        _, words = struct.unpack_from('>2i', raw, pos)
        body = raw[pos + 8:pos + 8 + words * 2]
        pos += 8 + words * 2
        typ = struct.unpack_from('<i', body, 0)[0]
        if typ == 0:
            continue
        if typ != 5:
            raise ValueError(f'Expected polygon, found {typ}')
        bbox = struct.unpack_from('<4d', body, 4)
        nparts, npoints = struct.unpack_from('<2i', body, 36)
        starts = list(struct.unpack_from(f'<{nparts}i', body, 44)) + [npoints]
        points = list(struct.iter_unpack('<2d', body[44 + nparts*4:44 + nparts*4 + npoints*16]))
        yield bbox, [points[a:b] for a, b in zip(starts, starts[1:])]


def base(fig, box, extent, lat0):
    """Plate carrée with x scaled by cos(lat0); no modern borders."""
    ax = fig.add_axes(box)
    west, east, south, north = extent
    c = math.cos(math.radians(lat0))
    project = lambda lon, lat: (lon*c, lat)
    ax.set_facecolor(SEA)
    for bbox, parts in rings():
        if bbox[2] < west or bbox[0] > east or bbox[3] < south or bbox[1] > north:
            continue
        verts, codes = [], []
        for ring in parts:
            if len(ring) < 3:
                continue
            verts.extend(project(x, y) for x, y in ring)
            codes.extend([MplPath.MOVETO] + [MplPath.LINETO]*(len(ring)-2) + [MplPath.CLOSEPOLY])
        ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=LAND, edgecolor=COAST, lw=.4, zorder=1))
    ax.set(xlim=(west*c, east*c), ylim=(south,north), aspect='equal')
    step = 2 if east-west < 20 else 10
    xt = list(range(math.ceil(west/step)*step, int(east)+1, step))
    yt = list(range(math.ceil(south/2)*2, int(north)+1, 2 if north-south<12 else 5))
    ax.set_xticks([x*c for x in xt], [f'{abs(x)}°' + (' з.' if x<0 else ' в.' if x>0 else '') for x in xt], fontsize=6.5)
    ax.set_yticks(yt, [f'{y}°' for y in yt], fontsize=6.5)
    ax.tick_params(length=2, pad=2)
    ax.grid(color='#8c9ca3', alpha=.35, lw=.35, zorder=0)
    for sp in ax.spines.values(): sp.set_color('#687780')
    return ax, project


def marker(ax, xy, number, group, uncertain=False, size=115):
    col = COLORS[group]
    ax.scatter([xy[0]], [xy[1]], s=size, marker=MARKERS[group], c=['white' if uncertain else col],
               edgecolors=col, linewidths=.9, zorder=4)
    ax.annotate(str(number), xy, xytext=(0,-1.3 if group=='c' else 0), textcoords='offset points',
                ha='center', va='center', color=col if uncertain else 'white',
                weight='bold', fontsize=6.8, zorder=5)


def scale(ax, extent, project, km, lat0):
    west,east,south,north=extent
    lon=west+(east-west)*.05;lat=south+(north-south)*.08
    x,y=project(lon,lat)
    # A degree of latitude on this spherical model is R*pi/180 kilometres.
    length=km/(6371.0088*math.pi/180)
    ax.plot([x,x+length],[y,y], color=INK, lw=1.3, zorder=6)
    ax.text(x+length/2,y+(north-south)*.025,f'{km} км при {lat0}° с. ш.',ha='center',fontsize=6.2,
            path_effects=[pe.withStroke(linewidth=2,foreground=LAND)],zorder=7)


def title(fig, heading, subheading):
    fig.text(.07,.965,heading,fontsize=10.5,weight='bold',va='top')
    fig.text(.07,.920,subheading,fontsize=8,va='top')


def footer(fig, y, detail):
    fig.text(.07,y,detail,fontsize=6.7,va='top',linespacing=1.35)
    fig.text(.07,.025,'Основа: Natural Earth (PD) · Пункты: Pleiades (CC BY 3.0)',fontsize=6.4)


def save(fig, stem):
    for suffix in ['svg','png']:
        dest=OUT/f'{stem}.{suffix}'
        fig.savefig(dest,dpi=400,facecolor='white',metadata={'Date':None} if suffix=='svg' else {'Software':'CaesarAugustus / make_maps.py'})
        if suffix=='svg':ET.parse(dest)
    plt.close(fig)


def render_gaul():
    fig=plt.figure(figsize=(4.65,6.3))
    title(fig,'Галльская война: избранные пункты','58–52 гг. до н. э. · события показаны выборочно')
    extent=(-5,9,42.8,51.7)
    ax,p=base(fig,[.10,.37,.86,.50],extent,47)
    offsets={1:(12,-12),2:(-60,-17),3:(12,10),4:(8,12),5:(-68,15),6:(-72,-20),7:(-62,27)}
    for n,(pid,label,date,g,loc,note,unc) in enumerate(GAUL,1):
        xy=p(*place(pid)['reprPoint']);marker(ax,xy,n,g,unc)
        ax.annotate(f'{label}\n{date}',xy,xytext=offsets[n],textcoords='offset points',fontsize=7.6,
                    ha='left',va='center',arrowprops={'arrowstyle':'-','color':COLORS[g],'lw':.55},
                    path_effects=[pe.withStroke(linewidth=2,foreground='white')],zorder=7)
    scale(ax,extent,p,200,47)
    for x,g,t in [(.07,'a','58 г.'),(.36,'b','54 г.'),(.65,'c','52 г.')]:
        fig.text(x,.315,MARKERS[g].replace('o','●').replace('s','■').replace('^','▲')+' '+t,color=COLORS[g],fontsize=9,weight='bold')
    footer(fig,.262,'Точки обозначают поселения — ориентиры кампаний.\nБибракте не отмечает точное поле сражения;\nСамаробрива — собрание и зимняя дислокация.\nГерговия? — неопределённость записи Pleiades.\nБереговая линия современная; маршруты и границы\nполитических образований не реконструированы.')
    save(fig,'map_01_gaul_58_52')


def render_civil():
    fig=plt.figure(figsize=(4.65,6.1))
    title(fig,'Гражданские войны: районы сражений','49–30 гг. до н. э. · даты в легенде — до н. э.')
    extent=(-10,39,29,47)
    ax,p=base(fig,[.10,.465,.86,.405],extent,38)
    # Three nearby Balkan anchors receive leader lines to keep numbers legible.
    shift={2:(-1.8,1.5),3:(-.9,-1.3),9:(-3.0,-1.8)}
    for n,(pid,label,date,g,loc,note,unc) in enumerate(CIVIL,1):
        xy=p(*place(pid)['reprPoint']);target=(xy[0]+shift.get(n,(0,0))[0],xy[1]+shift.get(n,(0,0))[1])
        if n in shift:
            ax.plot([xy[0],target[0]],[xy[1],target[1]],color=COLORS[g],lw=.6,zorder=3)
            ax.scatter([xy[0]],[xy[1]],s=5,c=COLORS[g],zorder=4)
        marker(ax,target,n,g,unc,size=113)
    scale(ax,extent,p,500,38)
    for n,(_,label,date,g,*_) in enumerate(CIVIL,1):
        col=0 if n<=5 else 1; row=(n-1)%5
        fig.text(.07+col*.47,.411-row*.033,f'{n:>2}  {label} — {date}',fontsize=8.0,color=COLORS[g])
    footer(fig,.222,'● 49–45 гг.   ■ 43–42 гг.   ▲ 36–30 гг.\nПункты — географические ориентиры, а не точные\nкоординаты полей битв или положения флотов.\nМунда? — предположительная локализация Pleiades.\nБереговая линия современная; маршруты не показаны.')
    save(fig,'map_02_civil_wars_49_30')


def render_admin():
    fig=plt.figure(figsize=(4.65,6.1))
    title(fig,'Римский мир: управление и зависимые цари','27 г. до н. э. · выборочные географические ориентиры')
    extent=(-10,42,28,49)
    ax,p=base(fig,[.10,.50,.86,.365],extent,38)
    for n,(pid,label,date,g,loc,note,unc) in enumerate(ADMIN,1):
        marker(ax,p(*place(pid)['reprPoint']),n,g,unc,size=125)
    rome=p(*place('423025')['reprPoint'])
    ax.scatter([rome[0]],[rome[1]],marker='*',s=70,color=INK,zorder=4)
    ax.annotate('Рим',rome,xytext=(-21,8),textcoords='offset points',fontsize=7.8,
                path_effects=[pe.withStroke(linewidth=2,foreground='white')],zorder=5)
    scale(ax,extent,p,500,38)
    # Two columns leave space for the book's external figure caption on A5.
    labels=['1  Испания: Тарракон','2  Нарбонская Галлия',
            '3  Сирия: Антиохия','4  Египет: Александрия',
            '5  Африка: Карфаген','6  Азия: Эфес',
            '7  Македония: Фессалоника','8  Крит/Киренаика: Гортина',
            '9  Галатия: Анкира','10  Каппадокия: Мазака']
    for n,line in enumerate(labels):
        col=0 if n<5 else 1;row=n%5
        fig.text(.07+col*.47,.450-row*.036,line,fontsize=7.6,color=COLORS[ADMIN[n][3]])
    footer(fig,.235,'● Август   ■ народ и сенат   ▲ зависимые цари\nЦари: Аминта (9), Архелай (10). Египет: префект.\nСхема пунктов, а не территориальная карта. Точки\nне обозначают границы или всю площадь владений.\nПеречень выборочный; основа современная.\nСрез: Dio 53.12; позднейшие изменения не показаны.')
    save(fig,'map_03_administration_27')


def manifest():
    maps={}
    for stem,entries in [('map_01_gaul_58_52',GAUL),('map_02_civil_wars_49_30',CIVIL),('map_03_administration_27',ADMIN)]:
        objects=[]
        for number,(pid,label,date,group,locus,note,unc) in enumerate(entries,1):
            j=place(pid)
            objects.append({'map_number':number,'label_ru':label,'date_bce':date,'layer':group,
                'pleiades_id':pid,'source_url':j['uri'],'data_url':j['uri']+'/json',
                'title':j['title'],'coordinate_order':'longitude, latitude','coordinate_datum':'WGS84',
                'coordinate':j['reprPoint'],'coordinate_field':'reprPoint',
                'coordinate_role':'representative place point; not a battlefield or administrative boundary',
                'creators':j.get('creators',[]),'contributors':j.get('contributors',[]),
                'rights_as_received':j['rights'],'license':'CC BY 3.0',
                'license_url':'https://creativecommons.org/licenses/by/3.0/',
                'attribution':'; '.join(x.get('name','') for x in j.get('creators',[]))+' and contributors, Pleiades, '+j['title']+', '+j['uri'],
                'access_date':'2026-11-05','access_status':'FULL: individual JSON record inspected; not its full cited bibliography',
                'primary_locus_checked':locus,'interpretation_ru':note,'uncertain_location':unc,
                'transformations':'reprPoint selected; label translated to Russian; plotted on scaled longitude grid; civil-war numbers 2, 3, 9 offset with a leader line to the source coordinate'})
        maps[stem]={'objects':objects,'files':[stem+'.svg',stem+'.png']}
    j=place('423025')
    maps['map_03_administration_27']['reference_city']={'label_ru':'Рим','pleiades_id':'423025',
        'source_url':j['uri'],'data_url':j['uri']+'/json','coordinate':j['reprPoint'],
        'creators':j.get('creators',[]),'contributors':j.get('contributors',[]),
        'rights_as_received':j['rights'],'license':'CC BY 3.0','license_url':'https://creativecommons.org/licenses/by/3.0/',
        'access_date':'2026-11-05','coordinate_role':'reference city; star is not an administrative category'}
    files={str(p.relative_to(OUT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
           for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['maps_provenance.json','validation.json']}
    payload={'schema_version':1,'created_for':'Caesar & Augustus research monograph','access_date':'2026-11-05',
      'cartography':'Modern original project maps prepared with AI assistance; no generated historical artefact',
      'base_data':{'object':'Natural Earth ne_50m_land','version':zipfile.ZipFile(DATA/'natural_earth_50m_land.zip').read('ne_50m_land.VERSION.txt').decode().strip(),
        'source_url':'https://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-land/',
        'download_url':'https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_land.zip',
        'license':'Public Domain','license_url':'https://www.naturalearthdata.com/about/terms-of-use/',
        'attribution':'Made with Natural Earth. Tom Patterson, Nathaniel Vaughn Kelso and contributors.',
        'transformation':'Land polygons only; modern coastline retained; no modern country boundaries used.',
        'access_date':'2026-11-05'},
      'projection':{'name':'Equirectangular, spherical approximation','formula':'x=longitude*cos(standard_parallel); y=latitude',
        'standard_parallel_degrees':{'map_01':47,'map_02':38,'map_03':38},
        'coordinate_datum':'Pleiades WGS84 longitude/latitude; no datum shift',
        'scale_bar':'Approximate horizontal distance at the stated standard parallel; spherical radius 6371.0088 km'},
      'maps':maps,'file_checksums':files}
    (OUT/'maps_provenance.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    render_gaul();render_civil();render_admin();manifest()
    print('Rendered three SVG + PNG pairs and maps_provenance.json from preserved data.')

if __name__=='__main__':main()
