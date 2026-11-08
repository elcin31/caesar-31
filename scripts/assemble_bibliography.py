#!/usr/bin/env python3
"""Consolidate verified local records and render a consistent reading bibliography.

This formats metadata; evidence of reading remains in sources/ and research/.
It does not verify any historical assertion or retrieve external works.
"""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]

def parse(text):
    records=[]
    starts=list(re.finditer(r'^@(\w+)\s*\{([^,]+),',text,re.M))
    for i,m in enumerate(starts):
        block=text[m.start():starts[i+1].start() if i+1<len(starts) else len(text)]
        # All project records use braced fields, with at most nested title braces.
        fields={k.lower():re.sub(r'[{}]','',v).strip() for k,v in re.findall(r'(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}',block)}
        if 'title' not in fields or 'author' not in fields:raise ValueError('Incomplete record '+m[2])
        records.append({'key':m[2].strip(),'type':m[1].lower(),'fields':fields,'raw':block[:block.rfind('}')+1].strip()})
    return records

def people(value,inverted=True):
    out=[]
    for i,name in enumerate(value.split(' and ')):
        bits=[x.strip() for x in name.split(',',1)]
        out.append(name if len(bits)==1 else (bits[0]+', '+bits[1] if inverted and i==0 else bits[1]+' '+bits[0]))
    return ' and '.join(out)

def format_record(r):
    f=r['fields'];author=people(f['author']).rstrip('.');title=f['title'].replace('--','–').rstrip('.');year=f.get('year','б. г.').replace('--','–').rstrip('.');p=f.get('pages','').replace('--','–')
    if r['type']=='article':
        s=f'{author}. “{title}.” *{f["journal"]}* {f.get("volume", "")}'
        if f.get('number'):s+=', no. '+f['number']
        s+=f' ({year})'+(': '+p if p else '')+'.'
    elif r['type']=='incollection':
        s=f'{author}. “{title}.” In *{f["booktitle"]}*'
        if f.get('editor'):s+=', edited by '+people(f['editor'],False)
        if p:s+=', '+p
        s+='.'
        if f.get('publisher'):s+=' '+(f.get('address','')+': ' if f.get('address') else '')+f['publisher']+', '+year+'.'
    else:
        s=f'{author}. *{title}*.'
        if f.get('translator'):s+=' Перевод '+people(f['translator'],False)+'.'
        if f.get('volume'):s+=' Т. '+f['volume']+'.'
        if f.get('editor'):s+=' Редактор '+people(f['editor'],False)+'.'
        if f.get('publisher'):s+=' '+(f.get('address','')+': ' if f.get('address') else '')+f['publisher']+', '+year+'.'
        elif f.get('series'):s+=' '+f['series']+', '+year+'.'
        else:s+=' '+year+'.'
    link=('https://doi.org/'+f['doi']) if f.get('doi') else f.get('url')
    return s+(' '+link+'.' if link else '')

def access(r):
    f=r['fields'];notes=f.get('note','')+' '+f.get('addendum','')
    if re.search(r'PARTIAL|selected|выбран',notes,re.I):return 'PARTIAL'
    if re.search(r'FULL',notes):return 'FULL (ограничено указанным объектом чтения)'
    if re.search(r'META',notes):return 'META'
    return 'см. журнал чтения'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--merge',nargs='*',type=Path);a=ap.parse_args()
    ref=ROOT/'references.bib';raw=ref.read_text();records=parse(raw);keys={r['key'] for r in records}
    for filename in a.merge or []:
        for r in parse((ROOT/filename).read_text()):
            if r['key'] not in keys:raw+='\n\n'+r['raw']+'\n';keys.add(r['key'])
    ref.write_text(raw.rstrip()+'\n');records=parse(raw)
    if len(records)!=len(keys):raise ValueError('Duplicate bibliography keys')
    ancient={'Caesar','Suetonius','Suetonius Tranquillus','Plutarch','Appian','Dio','Cicero','Augustus','Velleius Paterculus','Nicolaus of Damascus','Polybius','Sallust','Gellius','Tacitus','Horace','Vergil'}
    def primary(r):return r['fields']['author'].split(',')[0] in ancient
    groups=[('Античные источники: использованные электронные издания',[r for r in records if primary(r)]),('Современные исследования: непосредственно использованные тексты и фрагменты',[r for r in records if not primary(r) and access(r)!='META']),('Проверенная программа дальнейшего чтения',[r for r in records if not primary(r) and access(r)=='META'])]
    text='# Библиография\n\nАнтичные произведения цитируются по устойчивым книгам и разделам. Ниже описаны конкретные использованные электронные воспроизведения и их печатная основа; даты прямых проверок, изученные места и ограничения приведены в реестрах sources/ и исследовательских заметках. Для современных работ полный библиографический диапазон не означает чтения всех страниц. Недоступные книги и публикации отделены как программа дальнейшего чтения. Авторская пагинация Cooley2019 отличается от журнальной.\n'
    for title,items in groups:
        text+='\n## '+title+'\n\n'+'\n\n'.join(format_record(r) for r in sorted(items,key=lambda x:x['fields']['author'].casefold()))+'\n'
    (ROOT/'manuscript/bibliography.md').write_text(text)
    inventory=[{'key':r['key'],'title':r['fields']['title'],'author':r['fields']['author'],'year':r['fields'].get('year'),'doi':r['fields'].get('doi'),'url':r['fields'].get('url'),'kind':'primary' if primary(r) else 'secondary','access':access(r),'reading_note':r['fields'].get('note',''),'addendum':r['fields'].get('addendum','')} for r in records]
    (ROOT/'sources/verification_registry.json').write_text(json.dumps({'records':inventory,'note':'Metadata verification and actual reading are separate; page and claim checks are documented in chapter dossiers.'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'records':len(records),'groups':{title:len(items) for title,items in groups}},ensure_ascii=False))
if __name__=='__main__':main()
