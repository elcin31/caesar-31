#!/usr/bin/env python3
"""Build all reading editions from the same Markdown sources. Run from any directory."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, uuid
from datetime import datetime, timezone
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from publication_config import ROOT, add_release_arguments, release_from_args, source_inputs, relative
from epub_localization import localize_epub

def run(args,env=None):
    return subprocess.run([str(x) for x in args],cwd=ROOT,check=True,text=True,capture_output=True,env=env)

def russian_tex_environment(dist):
    """Create an isolated format with Russian patterns, without changing system TeX."""
    support=ROOT/'scripts/tex-support'
    env=os.environ.copy()
    env.update(TEXMFHOME=str(support),TEXMFVAR=str(ROOT/'.cache/texmf-var'),TEXMFCONFIG=str(ROOT/'.cache/texmf-config'))
    inputs=sorted(p for p in support.rglob('*.tex'))+sorted(support.rglob('language.dat'))
    signature=hashlib.sha256((''.join(hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs)+run(['xelatex','--version']).stdout).encode()).hexdigest()
    stamp=ROOT/'.cache/russian-format.sha256'
    fmt=ROOT/'.cache/texmf-var/web2c/xetex/xelatex.fmt'
    if not fmt.exists() or not stamp.exists() or stamp.read_text().strip()!=signature:
        result=run(['fmtutil-user','--byfmt','xelatex'],env=env)
        (dist/'tex_format_setup.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        stamp.parent.mkdir(parents=True,exist_ok=True);stamp.write_text(signature+'\n')
    return env

def reference_docx(path,release):
    doc=Document()
    sec=doc.sections[0]
    sec.top_margin=Cm(2.2); sec.bottom_margin=Cm(2.2)
    sec.left_margin=Cm(2.7); sec.right_margin=Cm(2.2)
    sec.page_width=Cm(21); sec.page_height=Cm(29.7)
    for name in ['Normal','Body Text','First Paragraph','Footnote Text','Footnote Reference','Title','Subtitle','Heading 1','Heading 2','Heading 3','TOC 1','TOC 2']:
        try: style=doc.styles[name]
        except KeyError:
            from docx.enum.style import WD_STYLE_TYPE
            style=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH if name!='Footnote Reference' else WD_STYLE_TYPE.CHARACTER)
        style.font.name='DejaVu Serif'
        style._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'DejaVu Serif')
        style._element.get_or_add_rPr().rFonts.set(qn('w:cs'),'DejaVu Serif')
        style.font.size=Pt(11.5)
    for name in ['Normal','Body Text']:
        p=doc.styles[name].paragraph_format
        p.first_line_indent=Cm(.65); p.space_after=Pt(0); p.line_spacing=1.15
    doc.styles['Footnote Text'].font.size=Pt(9)
    doc.styles['Footnote Text'].paragraph_format.first_line_indent=Cm(0)
    doc.styles['Footnote Text'].paragraph_format.line_spacing=1
    doc.styles['Title'].font.size=Pt(28)
    doc.styles['Subtitle'].font.size=Pt(15)
    for n,size in [(1,20),(2,15),(3,12)]:
        st=doc.styles[f'Heading {n}']; st.font.size=Pt(size); st.font.bold=False
        st.paragraph_format.keep_with_next=True
        st.paragraph_format.first_line_indent=Cm(0)
        st.paragraph_format.space_before=Pt(20); st.paragraph_format.space_after=Pt(12)
    doc.styles['Heading 1'].paragraph_format.page_break_before=True
    sec.different_first_page_header_footer=True
    header=sec.header.paragraphs[0]
    header.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=header.add_run('Цезарь и Август · '+release.label); r.font.name='DejaVu Serif'; r.font.size=Pt(8)
    footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE')
    footer._p.append(fld)
    update=OxmlElement('w:updateFields'); update.set(qn('w:val'),'true'); doc.settings.element.append(update)
    lang=OxmlElement('w:themeFontLang'); lang.set(qn('w:val'),'ru-RU'); doc.settings.element.append(lang)
    doc.save(path)

def finish_docx(path):
    doc=Document(path)
    # A page break before TOC keeps the title block on its own page.
    for p in doc.paragraphs:
        if p.text.strip() in ('Содержание','Оглавление','Table of Contents','Contents'):
            p.paragraph_format.page_break_before=True
    for p in doc.paragraphs:
        if p.style.name in ('Title','Subtitle','Author','Date'):
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.save(path)

def main():
    ap=argparse.ArgumentParser(); add_release_arguments(ap)
    ap.add_argument('--no-pdf',action='store_true'); ap.add_argument('--inputs',nargs='+',type=Path)
    a=ap.parse_args()
    release=release_from_args(a); DIST=release.output_dir; STEM=release.stem
    DIST.mkdir(parents=True,exist_ok=True)
    inputs=[(ROOT/p).resolve() for p in a.inputs] if a.inputs else source_inputs()
    if a.final and inputs!=source_inputs(): raise SystemExit('A final build must use the complete canonical manuscript.')
    if not inputs: raise SystemExit('No non-empty manuscript files found.')
    reference=DIST/'reference.docx'; reference_docx(reference,release)
    identifier='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'caesar-augustus/research/'+('final' if a.final else release.version)))
    common=['pandoc',*inputs,'--from=markdown+footnotes+smart+autolink_bare_uris','--standalone','--metadata-file',ROOT/'manuscript/metadata.yaml','--toc','--toc-depth=2','-M','toc-title=Содержание','-M','lang=ru-RU','-M','date='+datetime.now(timezone.utc).date().isoformat(),'-M','description='+release.label+'. Академическая монография'+('.' if a.final else ' в процессе подготовки.'),'-M','identifier='+identifier,'--resource-path',f'{ROOT}:{ROOT/"manuscript"}:{ROOT/"assets"}']
    outputs=[]; logs=[]
    def build(extra,out,env=None):
        r=run(common+extra+['-o',out],env=env); logs.append(r.stderr)
        outputs.append(out)
    docx=DIST/f'{STEM}.docx'
    build(['--reference-doc',reference],docx); finish_docx(docx)
    epub=DIST/f'{STEM}.epub'
    build(['--to=epub3','--epub-cover-image',ROOT/'assets/cover.png','--css',ROOT/'assets/epub.css','--split-level=1'],epub)
    localized_labels=localize_epub(epub)
    if not a.no_pdf:
        tex_header=DIST/'pdf-header.tex'
        tex_header.write_text(r'''\usepackage{fancyhdr}
\usepackage{titlesec}
\titleformat{\chapter}{\normalfont\fontsize{18}{22}\selectfont\bfseries\raggedright}{}{0pt}{}
\titlespacing*{\chapter}{0pt}{12pt}{24pt}
\usepackage{float}
\floatplacement{figure}{H}
\babelhyphenation[russian]{Cor-re-spon-dence}
\makeatletter
\AtBeginDocument{\let\caesar@author\@author\def\@author{\normalsize\caesar@author}}
\makeatother
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small Цезарь и Август}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{16pt}
\renewcommand{\headrulewidth}{0.2pt}
\setlength{\emergencystretch}{3em}
''',encoding='utf-8')
        build(['--pdf-engine=xelatex','-V','documentclass=book','-V','classoption=oneside,openany','-V','papersize=a5','-V','geometry:inner=20mm,outer=17mm,top=21mm,bottom=22mm','-V','fontsize=10pt','-V','mainfont=DejaVu Serif','-V','sansfont=DejaVu Sans','-V','monofont=DejaVu Sans Mono','-V','linestretch=1.08','-V','colorlinks=true','-V','linkcolor=black','-V','urlcolor=black','--include-in-header',tex_header],DIST/f'{STEM}.pdf',env=russian_tex_environment(DIST))
    resources={ROOT/'manuscript/metadata.yaml',ROOT/'assets/epub.css',ROOT/'assets/cover.png',Path(__file__).resolve(),ROOT/'scripts/epub_localization.py',ROOT/'scripts/publication_config.py'}
    for p in inputs:
        resources.update(ROOT/image for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')))
    resources.update(p for p in (ROOT/'scripts/tex-support').rglob('*') if p.is_file())
    manifest={'release':release.version,'final':release.final,'stem':STEM,'output_dir':relative(DIST),'localized_epub_labels':localized_labels,'cover_preserved_sha256':hashlib.sha256((ROOT/'assets/cover.png').read_bytes()).hexdigest(),'built_utc':datetime.now(timezone.utc).isoformat(),'inputs':[{'path':relative(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs], 'resources':[{'path':relative(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(resources)], 'outputs':[{'path':relative(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs], 'versions':{'pandoc':run(['pandoc','--version']).stdout.splitlines()[0],'xelatex':run(['xelatex','--version']).stdout.splitlines()[0]},'warnings':'\n'.join(logs)}
    (DIST/'build_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DIST/'build.log').write_text('\n'.join(logs),encoding='utf-8')
    for p in outputs: print(f'{relative(p)} ({p.stat().st_size:,} bytes)')
if __name__=='__main__': main()
