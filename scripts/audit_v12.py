#!/usr/bin/env python3
"""Reproducible v1.2 structural checks, counts and preservation checks, not peer review."""
from pathlib import Path
import collections, hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='217f3e5'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def count(src):
    src=re.sub(r'<!-- v1\.1:ART-\d+:start -->.*?<!-- v1\.1:ART-\d+:end -->','',src,flags=re.S)
    body='\n'.join(x for x in src.splitlines() if not re.match(r'^\[\^[^]]+\]:',x))
    return len(re.findall(r'[А-Яа-яЁё]+(?:[–-][А-Яа-яЁё]+)*',body)),body

def main():
    paths=[ROOT/'manuscript/introduction.md',*sorted((ROOT/'manuscript/chapters').glob('*.md')),ROOT/'manuscript/conclusion.md']
    rows=[];errors=[];all_ids=[]
    for p in paths:
        rel=str(p.relative_to(ROOT));src=p.read_text();n,body=count(src);before=git('show',f'{BASE}:{rel}').decode();bn,_=count(before)
        defs=re.findall(r'^\[\^([^]]+)\]:',src,re.M);refs=re.findall(r'\[\^([^]]+)\]',body)
        issue={'undefined':sorted(set(refs)-set(defs)),'unused':sorted(set(defs)-set(refs)),'duplicate':[k for k,v in collections.Counter(defs).items() if v>1]}
        if any(issue.values()):errors.append({rel:issue})
        all_ids+=defs
        pattern=r'<!-- v1\.1:ART-\d+:start -->.*?<!-- v1\.1:ART-\d+:end -->'
        same=re.findall(pattern,src,re.S)==re.findall(pattern,before,re.S)
        if not same:errors.append({'illustration_blocks_changed':rel})
        rows.append({'path':rel,'baseline_words':bn,'current_words':n,'added_words':n-bn,'footnotes':len(defs),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'illustration_blocks_unchanged':same})
    preserved=[]
    for rel in git('ls-tree','-r','--name-only',BASE,'--','dist/final','dist/v1.1','assets').decode().splitlines():
        data=(ROOT/rel).read_bytes();ok=hashlib.sha256(data).hexdigest()==hashlib.sha256(git('show',f'{BASE}:{rel}')).hexdigest()
        if not ok:errors.append({'protected_file_changed':rel})
        preserved.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'unchanged':ok})
    books='\n'.join(p.read_text() for p in paths)+(ROOT/'manuscript/appendices.md').read_text()
    art=re.findall(r'<!-- v1\.1:(ART-\d+):start -->',books)
    if len(art)!=34 or len(set(art))!=34:errors.append({'illustration_count':len(art),'unique':len(set(art))})
    if len(list((ROOT/'manuscript/chapters').glob('*.md')))!=16:errors.append('chapter_count')
    if len(all_ids)!=len(set(all_ids)):errors.append('cross_file_duplicate_notes')
    report={'baseline_commit':git('rev-parse',BASE).decode().strip(),'method':'Russian letter tokens, headings included, notes and ART captions excluded; same as audit_project.py','files':rows,'baseline_words':sum(r['baseline_words'] for r in rows),'current_words':sum(r['current_words'] for r in rows),'illustrations':{'referenced':len(art),'unique':len(set(art))},'protected_files':preserved,'errors':errors,'structural_status':'pass' if not errors else 'fail','scope':'Structural verification only; no historical truth, export check or external review certified.'}
    out=ROOT/'research/v1.2/structural_audit.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['protected_files','files']},ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
