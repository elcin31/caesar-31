#!/usr/bin/env python3
"""Structural checks plus optional EPUBCheck. This does not replace visual proofing."""
from pathlib import Path, PurePosixPath
import argparse, json, re, subprocess, zipfile, urllib.parse, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; STEM='Caesar_Augustus_v0.1'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','dc':'http://purl.org/dc/elements/1.1/','opf':'http://www.idpf.org/2007/opf','x':'http://www.w3.org/1999/xhtml'}

def require(condition,message):
    if not condition: raise AssertionError(message)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--epubcheck-jar',type=Path); a=ap.parse_args()
    result={}
    def normalized(s):
        s=re.sub(r'(?<=[А-Яа-яЁё])-\s*\n\s*(?=[а-яё])','',s)
        return re.sub(r'\s+', ' ', s).strip()
    manifest=json.loads((DIST/'build_manifest.json').read_text())
    require(len(manifest['inputs'])>=1,'Manuscript inputs missing')
    headings=[]
    image_sources=set()
    expected_notes=0
    def count_notes(value):
        if isinstance(value,dict):
            return int(value.get('t')=='Note')+sum(count_notes(v) for v in value.values())
        if isinstance(value,list): return sum(count_notes(v) for v in value)
        return 0
    for item in manifest['inputs']:
        source=(ROOT/item['path']).read_text(encoding='utf-8')
        top=re.search(r'^# +(.+)$',source,re.M)
        if top: headings.append(re.sub(r'\s*\{[^}]*\}\s*$', '', top.group(1)).replace('*',''))
        image_sources.update(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',source))
        ast=subprocess.run(['pandoc',str(ROOT/item['path']),'--from=markdown+footnotes+smart+autolink_bare_uris','--to=json'],capture_output=True,text=True,check=True)
        expected_notes+=count_notes(json.loads(ast.stdout))
    import hashlib
    for item in manifest['inputs']:
        p=ROOT/item['path']; require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Source changed since build: {p}')
    for item in manifest['outputs']:
        p=ROOT/item['path']; require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Output changed since build: {p}')
    for item in manifest.get('resources',[]):
        p=ROOT/item['path']; require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Resource changed since build: {p}')
    docx=DIST/f'{STEM}.docx'
    with zipfile.ZipFile(docx) as z:
        require(z.testzip() is None,'DOCX CRC failed')
        doc=ET.fromstring(z.read('word/document.xml'))
        notes=ET.fromstring(z.read('word/footnotes.xml'))
        refs=doc.findall('.//w:footnoteReference',NS)
        ids={n.get(f'{{{NS["w"]}}}id') for n in notes}
        require(all(n.get(f'{{{NS["w"]}}}id') in ids for n in refs),'DOCX unresolved footnote')
        require(len(refs)==expected_notes,'DOCX footnote count differs from parsed Markdown')
        media=[n for n in z.namelist() if n.startswith('word/media/')]
        require(len(media)>=len(image_sources),'DOCX missing manuscript image resources')
        text=' '.join(e.text or '' for e in doc.findall('.//w:t',NS))
        require(all(normalized(h) in normalized(text) for h in headings),'DOCX missing a source heading')
        require('Цезарь' in text and 'Август' in text,'DOCX missing Cyrillic title')
        require('TOC' in z.read('word/document.xml').decode(),'DOCX TOC field missing')
        result['docx']={'crc':'pass','footnote_references':len(refs),'footnote_resolution':'pass','toc_field':'pass','cyrillic':'pass','image_resources':len(media)}
    epub=DIST/f'{STEM}.epub'
    with zipfile.ZipFile(epub) as z:
        require(z.testzip() is None,'EPUB CRC failed')
        first=z.infolist()[0]; require(first.filename=='mimetype' and first.compress_type==zipfile.ZIP_STORED,'EPUB mimetype not first/uncompressed')
        require(z.read('mimetype')==b'application/epub+zip','EPUB mimetype wrong')
        container=ET.fromstring(z.read('META-INF/container.xml'))
        opf_name=next(e.get('full-path') for e in container.iter() if e.tag.endswith('rootfile'))
        opf=ET.fromstring(z.read(opf_name))
        require(opf.get('version')=='3.0','EPUB not version 3')
        language=opf.find('.//dc:language',NS).text
        require(language.lower().startswith('ru'),'EPUB not Russian')
        require(any('nav' in e.get('properties','').split() for e in opf.findall('.//opf:item',NS)),'EPUB navigation missing')
        images=[e for e in opf.findall('.//opf:item',NS) if e.get('media-type','').startswith('image/')]
        require(len(images)>=len(image_sources)+1,'EPUB missing manuscript images or cover')
        pages={n:ET.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.xhtml')}
        footrefs=0; backlinks=0
        combined=' '.join(' '.join(tree.itertext()) for tree in pages.values())
        require(all(normalized(h) in normalized(combined) for h in headings),'EPUB missing a source heading')
        import posixpath
        for n,tree in pages.items():
            for el in tree.iter():
                href=el.get('href') or el.get('src')
                if not href or urllib.parse.urlsplit(href).scheme: continue
                bits=urllib.parse.urlsplit(href)
                target=posixpath.normpath(posixpath.join(posixpath.dirname(n),urllib.parse.unquote(bits.path))) if bits.path else n
                require(target in z.namelist(),f'Broken EPUB resource: {n} -> {href}')
                if bits.fragment and target in pages:
                    require(any(e.get('id')==urllib.parse.unquote(bits.fragment) for e in pages[target].iter()),f'Broken EPUB anchor: {n} -> {href}')
                if el.get('{http://www.idpf.org/2007/ops}type')=='noteref': footrefs+=1
                if 'footnote-back' in el.get('class','').split(): backlinks+=1
        require(footrefs==len(refs),'EPUB and DOCX footnote counts differ')
        require(backlinks==footrefs,'EPUB missing footnote return links')
        result['epub']={'crc':'pass','version':'3.0','language':language,'xhtml_files':len(pages),'internal_links':'pass','footnote_references':footrefs,'footnote_backlinks':backlinks,'image_resources':len(images)}
    pdf=DIST/f'{STEM}.pdf'
    if pdf.exists():
        info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True).stdout
        text=subprocess.run(['pdftotext',str(pdf),'-'],capture_output=True,text=True,check=True).stdout
        require('Цезарь' in text and 'Август' in text,'PDF missing Cyrillic text')
        require(all(normalized(h) in normalized(text) for h in headings),'PDF missing a source heading')
        count=int(re.search(r'Pages:\s+(\d+)',info).group(1))
        require(count>0,'PDF has no pages')
        font_report=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True).stdout
        (DIST/'pdf_fonts.txt').write_text(font_report,encoding='utf-8')
        font_rows=font_report.splitlines()[2:]
        require(bool(font_rows),'PDF contains no inspectable fonts')
        # Fixed table columns: name/type/encoding vary in spacing; embedding is a yes/no token.
        require(all(re.search(r'\byes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',row) for row in font_rows),'PDF has a font that is not embedded')
        bbox=subprocess.run(['pdftotext','-bbox',str(pdf),'-'],capture_output=True,text=True,check=True).stdout
        bounds=ET.fromstring(bbox);outside=[]
        for page_number,page in enumerate(bounds.findall('.//x:page',NS),1):
            width=float(page.get('width'));height=float(page.get('height'))
            for word in page.findall('.//x:word',NS):
                if float(word.get('xMin'))<10 or float(word.get('xMax'))>width-10 or float(word.get('yMin'))<8 or float(word.get('yMax'))>height-8:
                    outside.append({'page':page_number,'text':word.text,'bounds':word.attrib})
        (DIST/'pdf_page_bounds.json').write_text(json.dumps(outside,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        require(not outside,f'PDF text reaches page edge: {outside[:3]}')
        result['pdf']={'pages':count,'cyrillic_extraction':'pass','text_characters':len(text),'embedded_fonts':'pass','font_count':len(font_rows),'page_bounds':'pass'}
    jar=a.epubcheck_jar
    if jar:
        r=subprocess.run(['java','-jar',str(jar),str(epub)],capture_output=True,text=True)
        (DIST/'epubcheck.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
        require(r.returncode==0,'EPUBCheck failed; see dist/epubcheck.log')
        result['epubcheck']={'status':'pass','log':'dist/epubcheck.log'}
    else: result['epubcheck']={'status':'not_run','reason':'Pass --epubcheck-jar /path/to/epubcheck.jar'}
    result['source_heading_count']=len(headings)
    result['expected_note_occurrences']=expected_notes
    result['manuscript_image_sources']=sorted(image_sources)
    result['visual_proofreading']='Separate PDF page inspection and reader testing required; structural checks do not certify Apple Books rendering.'
    (DIST/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
