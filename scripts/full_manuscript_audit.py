#!/usr/bin/env python3
"""Whole-source editorial diagnostics, complementary to historical reading."""
from pathlib import Path
import collections,hashlib,json,re
from publication_config import ROOT,source_inputs
from update_status import count
files=source_inputs();chapters=sorted((ROOT/'manuscript/chapters').glob('*.md'))
headings=[];ids=[];uses=[];paragraphs=collections.defaultdict(list);mixed=[];markers=[];zero=[]
for p in files:
 t=p.read_text();defs=re.findall(r'^\[\^([^]]+)\]:',t,re.M);body=re.sub(r'^\[\^[^]]+\]:.*$', '',t,flags=re.M)
 ids.extend(defs);uses.extend(re.findall(r'\[\^([^]]+)\]',body))
 headings.extend({'file':str(p.relative_to(ROOT)),'heading':h} for h in re.findall(r'^# (.*)$',t,re.M))
 for i,line in enumerate(body.splitlines(),1):
  for m in re.finditer(r'(?:[А-Яа-яЁё]+[A-Za-z]+[А-Яа-яЁё]*|[A-Za-z]+[А-Яа-яЁё]+)',line):mixed.append({'file':str(p.relative_to(ROOT)),'line':i,'token':m.group(0)})
  if re.search(r'\b(?:TODO|TBD|CITATION NEEDED|FIXME)\b',line):markers.append({'file':str(p.relative_to(ROOT)),'line':i})
  if re.search(r'(?<!\d)0\s*г\.',line):zero.append({'file':str(p.relative_to(ROOT)),'line':i})
 for paragraph in body.split('\n\n'):
  normalized=re.sub(r'\[\^[^]]+\]','',paragraph);normalized=re.sub(r'\s+',' ',normalized).strip()
  if len(re.findall(r'\w+',normalized))>=35:paragraphs[normalized].append(str(p.relative_to(ROOT)))
prose=[ROOT/'manuscript/introduction.md',*chapters,ROOT/'manuscript/conclusion.md']
result={'method':'Source-level diagnostic; not an automated fact check or external peer review','source_files':len(files),'chapter_numbers':[int(p.name.split('-')[0]) for p in chapters],'russian_body_words':sum(count(p) for p in prose),'source_headings':headings,'footnote_definitions':len(ids),'footnote_calls':len(uses),'undefined_notes':sorted(set(uses)-set(ids)),'unused_notes':sorted(set(ids)-set(uses)),'duplicate_note_ids':[k for k,n in collections.Counter(ids).items() if n>1],'verbatim_duplicate_long_paragraphs':[{'files':v,'text_start':k[:180]} for k,v in paragraphs.items() if len(v)>1],'mixed_script_tokens':mixed,'unfinished_markers':markers,'zero_year_candidates':zero,'manuscript_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
result['structural_status']='pass' if result['chapter_numbers']==list(range(1,17)) and not any(result[k] for k in ['undefined_notes','unused_notes','duplicate_note_ids','unfinished_markers','zero_year_candidates']) else 'review'
(ROOT/'research/full_manuscript_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['source_headings','manuscript_sha256']},ensure_ascii=False,indent=2))
