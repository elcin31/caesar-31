#!/usr/bin/env python3
"""Compare actual DOI registry metadata with local bibliographic records.
Does not verify ancient loci, book pages, historical claims or full-text reading.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from difflib import SequenceMatcher
import hashlib,json,re,unicodedata,urllib.request,urllib.parse,urllib.error
from assemble_bibliography import ROOT,parse

def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def read(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CaesarAugustusResearch/0.3 (bibliographic verification)'})
 with urllib.request.urlopen(req,timeout=35) as r:return json.load(r)
def check(record):
 f=record['fields'];doi=f['doi'];item={'key':record['key'],'doi':doi,'expected_title':f['title'],'expected_author':f['author'],'expected_year':f.get('year')};errors=[]
 for registry,url in [('Crossref','https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')),('DataCite','https://api.datacite.org/dois/'+urllib.parse.quote(doi,safe=''))]:
  try:
   v=read(url)
   if registry=='Crossref':
    d=v['message'];title=d['title'][0];authors=[x.get('family',x.get('name','')) for x in d.get('author',[])];years=sorted(set(d[k]['date-parts'][0][0] for k in ['published-print','published-online','issued'] if d.get(k,{}).get('date-parts')));pages=d.get('page');updates=d.get('update-to',[])
   else:
    d=v['data']['attributes'];title=d['titles'][0]['title'];authors=[x.get('familyName') or x.get('name','').split(',')[0] for x in d.get('creators',[])];years=[d.get('publicationYear')];pages=None;updates=[]
   similarity=SequenceMatcher(None,norm(f['title']),norm(title)).ratio();surname=norm(f['author'].split(' and ')[0].split(',')[0]);author_match=bool(authors and surname==norm(authors[0]));year_match=int(f['year']) in years if f.get('year','').isdigit() else None
   item.update(registry=registry,registry_title=title,registry_authors=authors,registry_years=years,registry_page=pages,registry_updates=updates,title_similarity=round(similarity,4),author_match=author_match,year_match=year_match,status='match' if similarity>=.85 and author_match and year_match else 'manual_review');return item
  except Exception as e:errors.append({'registry':registry,'error':str(e)[:200]})
 item.update(status='registry_unavailable',errors=errors);return item

if __name__=='__main__':
 ref=ROOT/'references.bib';items=[r for r in parse(ref.read_text()) if r['fields'].get('doi')]
 with ThreadPoolExecutor(max_workers=1) as pool:results=list(pool.map(check,items))
 out=ROOT/'research/source_notes/evidence/doi_registry_verification_v03.json';out.write_text(json.dumps({'checked_utc':datetime.now(timezone.utc).isoformat(),'references_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'scope':'DOI identity/title/first-author/year, not page support or full-text reading','records':results},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'checked':len(results),'match':sum(x['status']=='match' for x in results),'review':[{k:v for k,v in x.items() if k in ['key','status','registry_title','registry_years','registry_authors','title_similarity','errors']} for x in results if x['status']!='match']},ensure_ascii=False,indent=2))
