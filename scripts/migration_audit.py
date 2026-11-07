#!/usr/bin/env python3
"""Inventory the existing workspace and verify the exact canonical GitHub tree.

Uses the configured gh identity without reading or logging credential values.
No repository creation, history rewrite, force push, or remote deletion occurs.
"""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import argparse,base64,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
REPO='elcin31/caesar-31'
OUT=ROOT/'research/migration'

def command(args):return subprocess.check_output(args,cwd=ROOT)
def api(path):return json.loads(command(['gh','api','repos/'+REPO+'/'+path]))
def sha256(data):return hashlib.sha256(data).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def write(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def git_tree(ref):
    result={}
    for line in command(['git','ls-tree','-rz',ref]).split(b'\0'):
        if not line:continue
        info,path=line.split(b'\t',1);mode,kind,sha=info.decode().split()
        if kind=='blob':result[path.decode()]=sha
    return result

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted(set(p.decode() for p in command(['git','ls-files','--cached','--others','--exclude-standard','-z']).split(b'\0') if p))
    ignore={'research/migration/source_snapshot.json','research/migration/remote_verification.json','research/migration/migration_report.md'}
    files=[];findings=[]
    patterns={
      'github_token':re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{25,}\b'),
      'aws_access_key':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
      'private_key_material':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]{20,}'),
    }
    for rel in paths:
        if rel in ignore:continue
        p=ROOT/rel
        if not p.is_file():continue
        if p.is_symlink():raise SystemExit('Resolve symlink before migration: '+rel)
        data=p.read_bytes()
        if p.name.startswith('.env') or p.name.lower() in {'credentials','id_rsa','id_ed25519'}:findings.append({'path':rel,'rule':'sensitive filename'})
        for name,pattern in patterns.items():
            if pattern.search(data):findings.append({'path':rel,'rule':name})
        if len(data)>=100*1024*1024:findings.append({'path':rel,'rule':'GitHub100MiB limit'})
        files.append({'path':rel,'bytes':len(data),'sha256':sha256(data),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
    sys.path.insert(0,str(ROOT/'scripts'))
    from update_status import count
    main=[ROOT/'manuscript/introduction.md',*sorted((ROOT/'manuscript/chapters').glob('*.md'))]
    drafts=[p for p in sorted((ROOT/'research/drafts').glob('*.md')) if not list((ROOT/'manuscript/chapters').glob(p.name.split('-')[0]+'-*.md'))]
    result={'prepared_utc':now(),'repository':REPO,'branch':'main','local_head_before_migration':command(['git','rev-parse','HEAD']).decode().strip(),'remote_head_before_migration':api('branches/main')['commit']['sha'],'files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files),'main_body_words':sum(count(p) for p in main),'all_saved_body_words_without_duplicate_drafts':sum(count(p) for p in main+drafts),'canonical_chapter_files':len(main)-1,'draft_files_not_integrated':len(drafts),'installed_skills':len(list((ROOT/'.agents/skills').glob('*/SKILL.md'))),'high_signal_secret_scan':{'findings':findings,'limitations':'Checks selected high-signal token/key patterns and sensitive filenames; not a universal forensic guarantee.'},'excluded':'Git internals, ignored caches, temporary files, full external working PDF/transcription snapshots; the manifest and subsequent migration verification reports are excluded from their own inventory.'}
    write('source_snapshot.json',result)
    if findings:raise SystemExit('Migration preflight findings; inspect report without exposing values.')
    print(json.dumps({k:v for k,v in result.items() if k not in {'files'}},ensure_ascii=False))

def verify():
    local_head=command(['git','rev-parse','HEAD']).decode().strip();remote_head=api('branches/main')['commit']['sha']
    if local_head!=remote_head:raise SystemExit('Remote main does not equal local HEAD')
    remote_commit=api('git/commits/'+remote_head);remote_tree=api('git/trees/'+remote_commit['tree']['sha']+'?recursive=1')
    if remote_tree.get('truncated'):raise SystemExit('GitHub recursive tree truncated')
    remote={x['path']:x['sha'] for x in remote_tree['tree'] if x['type']=='blob'};local=git_tree('HEAD')
    if local!=remote:raise SystemExit('Remote/local Git tree mismatch')
    if command(['git','rev-parse','HEAD^{tree}']).decode().strip()!=remote_commit['tree']['sha']:raise SystemExit('Root tree SHA mismatch')
    selected=[p for p in local if p.startswith(('manuscript/','research/drafts/'))]
    selected += [p for p in ['AGENTS.md','PROJECT_STATUS.md','NEXT_ACTION.md','references.bib','sources/primary_sources.md','sources/secondary_sources.md','research/source_notes/chapter04_sources.md','assets/cover.png','assets/genealogy.png','assets/images/met_248037.jpg','assets/images/met_248119.jpg','assets/maps/map_03_administration_27.png','dist/v0.2/Caesar_Augustus_v0.2.docx','dist/v0.2/Caesar_Augustus_v0.2.epub','dist/v0.2/Caesar_Augustus_v0.2.pdf','dist/v0.2/Caesar_Augustus_Research_v0.2.zip'] if p in local]
    def check(rel):
        value=api('git/blobs/'+local[rel]);data=base64.b64decode(value['content'])
        expected=(ROOT/rel).read_bytes()
        if sha256(data)!=sha256(expected):raise ValueError('Downloaded content differs: '+rel)
        return {'path':rel,'bytes':len(data),'sha256':sha256(data),'git_blob_sha1':local[rel]}
    with ThreadPoolExecutor(max_workers=4) as pool:checks=list(pool.map(check,selected))
    result={'verified_utc':now(),'repository':REPO,'branch':'main','commit':remote_head,'commit_url':'https://github.com/'+REPO+'/commit/'+remote_head,'tree_sha':remote_commit['tree']['sha'],'file_count':len(local),'every_remote_blob_matches_local_git_tree':True,'actual_blob_download_sha256_checks':checks,'status':'pass','method':'GitHub REST branch/commit/recursive tree compared with every local committed blob; selected source and binary blobs independently downloaded and SHA256-compared. No second working repository created.'}
    write('remote_verification.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='actual_blob_download_sha256_checks'},ensure_ascii=False));print('Actual downloaded file checks:',len(checks))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','verify']);args=p.parse_args()
    prepare() if args.mode=='prepare' else verify()
