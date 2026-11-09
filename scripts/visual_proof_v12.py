#!/usr/bin/env python3
"""Prepare labeled PDF samples for actual human/AI viewing; does not certify review."""
from pathlib import Path
import re,json,subprocess,hashlib,tempfile
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'dist/v1.2';pdf=D/'Caesar_Augustus_v1.2.pdf'
pages=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True).split('\f');pages=pages[:-1] if not pages[-1].strip() else pages
normalize=lambda s:re.sub(r'\s+',' ',s)
starts={}
for n in range(1,17):
 hits=[i+1 for i,s in enumerate(pages) if re.search(r'Глава\s+'+str(n)+r'\.',s)]
 if not hits:raise ValueError('Chapter heading not found '+str(n))
 starts[str(n)]=max(hits)
art={}
for n in range(1,35):
 hits=[i+1 for i,s in enumerate(pages) if re.search(r'Ил\.\s*'+str(n)+r'\.',s)]
 if len(hits)!=1:raise ValueError('Caption occurrence '+str(n)+':'+str(hits))
 art[str(n)]=hits[0]
register=json.loads((ROOT/'assets/illustrations/v1.1/register.json').read_text())['records']
samples=[{'page':1,'purpose':'title'},{'page':2,'purpose':'contents'}]
for n in range(1,17):
 ids=[int(r['id'].split('-')[-1]) for r in register if r['chapter']==f'{n:02}']
 if len(ids)!=2:raise ValueError('Chapter plates '+str(n))
 stop=starts[str(n+1)]-1 if n<16 else next(i+1 for i,s in enumerate(pages) if i+1>starts['16'] and 'Заключение.' in s)-1
 for k in ids:
  if not starts[str(n)]<=art[str(k)]<=stop:raise ValueError('Misplaced illustration '+str(k))
 samples.extend([{'page':art[str(min(ids))],'purpose':f'ch{n:02} image'},{'page':stop,'purpose':f'ch{n:02} ending/notes'}])
samples.extend([{'page':art['1'],'purpose':'introduction image'},{'page':art['34'],'purpose':'appendix image'}])
for word,label in [('Заключение.','conclusion'),('Библиография','bibliography')]:
 hits=[i+1 for i,s in enumerate(pages) if word in s and i+1>starts['16']]
 samples.append({'page':min(hits),'purpose':label})
out=D/'visual_samples';out.mkdir(exist_ok=True)
sheets=[]
with tempfile.TemporaryDirectory(prefix='caesar-proof-') as t:
 for batch in range(0,len(samples),6):
  subset=samples[batch:batch+6];sheet=Image.new('RGB',(1080,1110),'#dddddd');draw=ImageDraw.Draw(sheet)
  for j,row in enumerate(subset):
   prefix=Path(t)/str(row['page']);subprocess.run(['pdftoppm','-f',str(row['page']),'-l',str(row['page']),'-scale-to','620','-singlefile','-png',str(pdf),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   im=Image.open(str(prefix)+'.png').convert('RGB');im.thumbnail((350,510))
   x=(j%3)*360+(360-im.width)//2;y=(j//3)*555+30;sheet.paste(im,(x,y));draw.text(((j%3)*360+8,(j//3)*555+8),f"PDF {row['page']} | {row['purpose']}",fill='black')
  path=out/f'sheet-{batch//6+1:02}.jpg';sheet.save(path,quality=90);sheets.append(str(path.relative_to(ROOT)))
plan={'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':len(pages),'chapter_starts':starts,'illustration_pages':art,'caption_distribution':'all34captions once; both chapter plates within chapter span','samples':samples,'contact_sheets':sheets,'status':'prepared_for_actual_viewing_not_yet_reviewed'}
(D/'illustration_pages.json').write_text(json.dumps(art,indent=2)+'\n');(D/'visual_inspection_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'samples':len(samples),'sheets':sheets,'starts':starts},ensure_ascii=False))
