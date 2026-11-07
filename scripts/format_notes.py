#!/usr/bin/env python3
"""Normalize footnote typography and DOI links without changing numeric loci.
Original drafts remain untouched. Every edited note retains exactly the same
sequence of numeric expressions; note labels and embedded references are protected.
"""
from pathlib import Path
import hashlib,json,re
from publication_config import ROOT,source_inputs

def format_text(text):
    text=re.sub(r'\bDOI\s*:\s*(10\.\d{4,9}/[^\s;,\)\]]+)',lambda m:'https://doi.org/'+m[1],text,flags=re.I)
    saved=[]
    def protect(m):saved.append(m[0]);return f'PROTECTEDTOKEN{len(saved)-1}END'
    text=re.sub(r'https?://[^\s)<>]+|`[^`]+`|\[\^[^]]+\]',protect,text)
    text=re.sub(r',(?=[A-Za-zА-Яа-яЁё«“*])',', ',text)
    text=re.sub(r'(?<=[A-Za-zА-Яа-яЁё]),(?=\d)',', ',text)
    text=re.sub(r'([)”»*]),(?=\d)',r'\1, ',text)
    text=re.sub(r';(?=\S)','; ',text)
    text=re.sub(r':(?=\S)',': ',text)
    text=re.sub(r'(\*[^*\n]+\*)(?=\d)',r'\1 ',text)
    text=re.sub(r'\b(Suet|Plut|Cic|Caes|Cass|Tac|Sall|Hirt)\.(?=[A-Za-z])',r'\1. ',text)
    text=re.sub(r'\b(Dio|BG|BC|RG|NA|Phil\.|Att\.|Fam\.|Iul\.|Aug\.|Caes\.|Brut\.|Ant\.|Cat\.|Leg\.|Ann\.|Vell\.|Polyb\.|Tib\.)(?=\d)',r'\1 ',text)
    text=re.sub(r'(?<=[А-Яа-яЁё])(?=\d{4}\b)',' ',text)
    for i,value in enumerate(saved):text=text.replace(f'PROTECTEDTOKEN{i}END',value)
    return text

def main():
 changes=[]
 for path in source_inputs():
  old=path.read_text();new=[]
  for line in old.splitlines():
   m=re.match(r'^(\[\^[^]]+\]:)(.*)$',line)
   if not m:new.append(line);continue
   note=format_text(m[2]);before=re.findall(r'\d+(?:[.–-]\d+)*',m[2]);after=re.findall(r'\d+(?:[.–-]\d+)*',note)
   if before!=after:raise ValueError('Numeric citation changed: '+str(path)+' '+m[1])
   value=m[1]+note
   if value!=line:changes.append({'file':str(path.relative_to(ROOT)),'note':m[1],'numeric_sequence_unchanged':True})
   new.append(value)
  path.write_text('\n'.join(new)+'\n')
 (ROOT/'research/note_typography_changes.json').write_text(json.dumps({'scope':'Footnote punctuation/abbreviation spacing and canonical DOI links; numeric citation streams and note IDs preserved','changes':changes},ensure_ascii=False,indent=2)+'\n')
 print('Edited notes:',len(changes))
if __name__=='__main__':main()
