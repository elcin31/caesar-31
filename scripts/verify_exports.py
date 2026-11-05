#!/usr/bin/env python3
"""Structural checks plus optional EPUBCheck. This does not replace visual proofing."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, posixpath, re, subprocess, zipfile, urllib.parse, xml.etree.ElementTree as ET
from publication_config import ROOT, add_release_arguments, release_from_args, relative
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','dc':'http://purl.org/dc/elements/1.1/','opf':'http://www.idpf.org/2007/opf','x':'http://www.w3.org/1999/xhtml'}

def require(condition,message):
    if not condition: raise AssertionError(message)

def main():
    ap=argparse.ArgumentParser(); add_release_arguments(ap)
    ap.add_argument('--epubcheck-jar',type=Path); a=ap.parse_args()
    release=release_from_args(a); DIST=release.output_dir; STEM=release.stem
    result={'release':release.version,'final':release.final,'output_dir':relative(DIST)}
    def normalized(s):
        s=re.sub(r'(?<=[А-Яа-яЁё])-\s*\n\s*(?=[а-яё])','',s)
        return re.sub(r'\s+', ' ', s).strip()
    manifest=json.loads((DIST/'build_manifest.json').read_text())
    require(manifest.get('release')==release.version and manifest.get('final')==release.final,'Build belongs to a different release')
    result['build_manifest_sha256']=hashlib.sha256((DIST/'build_manifest.json').read_bytes()).hexdigest()
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
    for item in manifest['inputs']:
        p=ROOT/item['path']; require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Source changed since build: {p}')
    for item in manifest['outputs']:
        p=ROOT/item['path']; require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Output changed since build: {p}')
    for item in manifest.get('resources',[]):
        p=ROOT/item['path']; require(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Resource changed since build: {p}')
    docx=DIST/f'{STEM}.docx'
    with zipfile.ZipFile(docx) as z:
        require(z.testzip() is None,'DOCX CRC failed')
        xml_parts=[name for name in z.namelist() if name.endswith(('.xml','.rels'))]
        for name in xml_parts: ET.fromstring(z.read(name))
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
        require('Содержание' in text,'DOCX Russian TOC heading missing')
        require('ru-RU' in z.read('word/styles.xml').decode(),'DOCX Russian language metadata missing')
        result['docx']={'crc':'pass','xml_parts_parsed':len(xml_parts),'footnote_references':len(refs),'footnote_resolution':'pass','toc_field':'pass','toc_heading':'Содержание','language':'ru-RU','cyrillic':'pass','image_resources':len(media)}
    epub=DIST/f'{STEM}.epub'
    with zipfile.ZipFile(epub) as z:
        require(z.testzip() is None,'EPUB CRC failed')
        xml_parts=[name for name in z.namelist() if name.endswith(('.xml','.xhtml','.opf','.ncx'))]
        for name in xml_parts: ET.fromstring(z.read(name))
        first=z.infolist()[0]; require(first.filename=='mimetype' and first.compress_type==zipfile.ZIP_STORED,'EPUB mimetype not first/uncompressed')
        require(z.read('mimetype')==b'application/epub+zip','EPUB mimetype wrong')
        container=ET.fromstring(z.read('META-INF/container.xml'))
        opf_name=next(e.get('full-path') for e in container.iter() if e.tag.endswith('rootfile'))
        opf=ET.fromstring(z.read(opf_name))
        require(opf.get('version')=='3.0','EPUB not version 3')
        language=opf.find('.//dc:language',NS).text
        require(language.lower().startswith('ru'),'EPUB not Russian')
        description=opf.find('.//dc:description',NS)
        require(description is not None and release.label in (description.text or ''),'EPUB description has a stale release version')
        require(any('nav' in e.get('properties','').split() for e in opf.findall('.//opf:item',NS)),'EPUB navigation missing')
        for item in opf.findall('.//opf:item',NS):
            target=posixpath.normpath(posixpath.join(posixpath.dirname(opf_name),urllib.parse.unquote(item.get('href'))))
            require(target in z.namelist(),'EPUB manifest resource missing: '+target)
        images=[e for e in opf.findall('.//opf:item',NS) if e.get('media-type','').startswith('image/')]
        require(len(images)>=len(image_sources)+1,'EPUB missing manuscript images or cover')
        pages={n:ET.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.xhtml')}
        epub_type='{http://www.idpf.org/2007/ops}type'
        nav_item=next(e for e in opf.findall('.//opf:item',NS) if 'nav' in e.get('properties','').split())
        nav_path=posixpath.normpath(posixpath.join(posixpath.dirname(opf_name),nav_item.get('href')))
        nav=pages[nav_path]
        labels={'titlepage':'Титульный лист','cover':'Обложка','toc':'Содержание'}
        for section in nav.findall('.//x:nav',NS):
            expected_title='Содержание' if section.get(epub_type)=='toc' else 'Навигация'
            require(section.get('title')==expected_title,'EPUB generated navigation title is not Russian')
        landmarks={a.get(epub_type):''.join(a.itertext()).strip() for section in nav.findall('.//x:nav',NS) if section.get(epub_type)=='landmarks' for a in section.findall('.//x:a',NS)}
        require(all(landmarks.get(k)==v for k,v in labels.items()),'EPUB landmarks are not fully localized: '+str(landmarks))
        toc_title=nav.find('.//x:h1[@id="toc-title"]',NS)
        require(toc_title is not None and ''.join(toc_title.itertext()).strip()=='Содержание','EPUB TOC heading is not Russian')
        for reference in opf.findall('.//opf:guide/opf:reference',NS):
            kind=reference.get('type')
            if kind in labels: require(reference.get('title')==labels[kind],'EPUB OPF guide contains an unlocalized label')
        for filename,label in [('nav.xhtml','Содержание'),('title_page.xhtml','Титульный лист'),('cover.xhtml','Обложка')]:
            page=next((page for name,page in pages.items() if name.endswith('/'+filename)),None)
            require(page is not None,'EPUB generated page missing: '+filename)
            require(page.find('x:head/x:title',NS).text==label,'EPUB generated document title is not Russian: '+filename)
        forbidden={'Title Page','Cover','Table of Contents','Contents','Footnotes','Endnotes'}
        require(not any((el.text or '').strip() in forbidden for el in nav.iter()),'EPUB generated navigation retains English labels')
        for ncx_name in [n for n in z.namelist() if n.endswith('.ncx')]:
            ncx=ET.fromstring(z.read(ncx_name))
            for point in ncx.findall('.//{http://www.daisy.org/z3986/2005/ncx/}navPoint'):
                content=point.find('{http://www.daisy.org/z3986/2005/ncx/}content')
                target=content.get('src','').split('#')[0].rsplit('/',1)[-1] if content is not None else ''
                expected_label={'title_page.xhtml':labels['titlepage'],'cover.xhtml':labels['cover'],'nav.xhtml':labels['toc']}.get(target)
                if expected_label:
                    text_node=point.find('{http://www.daisy.org/z3986/2005/ncx/}navLabel/{http://www.daisy.org/z3986/2005/ncx/}text')
                    require(text_node is not None and text_node.text==expected_label,'NCX generated navigation label is not Russian')
        footrefs=0; backlinks=0
        combined=' '.join(' '.join(tree.itertext()) for tree in pages.values())
        require(all(normalized(h) in normalized(combined) for h in headings),'EPUB missing a source heading')
        for n,tree in pages.items():
            require(tree.get('lang')=='ru-RU' and tree.get('{http://www.w3.org/XML/1998/namespace}lang')=='ru-RU','EPUB XHTML Russian language missing: '+n)
            for el in tree.iter():
                href=el.get('href') or el.get('src') or el.get('{http://www.w3.org/1999/xlink}href')
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
        cover_item=next(e for e in images if 'cover-image' in e.get('properties','').split())
        cover_path=posixpath.normpath(posixpath.join(posixpath.dirname(opf_name),cover_item.get('href')))
        require(z.read(cover_path)==(ROOT/'assets/cover.png').read_bytes(),'EPUB does not preserve the original cover resource')
        result['epub']={'crc':'pass','xml_parts_parsed':len(xml_parts),'manifest_resources':'pass','version':'3.0','language':language,'xhtml_languages':'ru-RU','localized_navigation':'pass','landmark_labels':landmarks,'opf_guide_labels':'pass','ncx_generated_labels':'pass','cover_preserved':'pass','xhtml_files':len(pages),'internal_links':'pass','footnote_references':footrefs,'footnote_backlinks':backlinks,'image_resources':len(images)}
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
        require(r.returncode==0,'EPUBCheck failed; see '+relative(DIST/'epubcheck.log'))
        result['epubcheck']={'status':'pass','log':relative(DIST/'epubcheck.log')}
    else: result['epubcheck']={'status':'not_run','reason':'Pass --epubcheck-jar /path/to/epubcheck.jar'}
    result['source_heading_count']=len(headings)
    result['expected_note_occurrences']=expected_notes
    result['manuscript_image_sources']=sorted(image_sources)
    result['visual_proofreading']='Separate PDF page inspection and reader testing required; structural checks do not certify Apple Books rendering.'
    (DIST/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
