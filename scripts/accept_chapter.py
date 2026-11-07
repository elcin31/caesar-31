#!/usr/bin/env python3
"""Integrate an actually reviewed chapter, preserve its draft, commit and push.

Requires a report containing PASS and the exact reviewed draft SHA256. Only
editorial chapter anchors may differ at this step. This is not a substitute
for historical or literary review.
"""
from pathlib import Path
import argparse,base64,hashlib,json,re,shutil,subprocess,sys
from datetime import datetime,timezone
from editorial_cleanup import clean
ROOT=Path(__file__).resolve().parents[1]

def run(args):return subprocess.check_output(args,cwd=ROOT,text=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def append(path,text):path.write_text(path.read_text().rstrip()+'\n\n'+text.strip()+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('number',type=int);a=ap.parse_args();n=a.number
 if not 4<=n<=16:raise SystemExit('This continuation helper accepts chapters04--16 only')
 if run(['git','remote','get-url','origin']).strip()!='https://github.com/elcin31/caesar-31.git':raise SystemExit('Unexpected remote')
 if run(['git','branch','--show-current']).strip()!='main':raise SystemExit('Expected main')
 for prior in range(1,n):
  if len(list((ROOT/'manuscript/chapters').glob(f'{prior:02}-*.md')))!=1:raise SystemExit('Previous chapter missing')
 draft=next((ROOT/'research/drafts').glob(f'{n:02}-*.md'));target=ROOT/'manuscript/chapters'/draft.name
 if target.exists():raise SystemExit('Chapter already integrated; review existing state')
 report=ROOT/f'research/reviews/ch{n:02}_independent.md';report_text=report.read_text();draft_sha=sha(draft)
 if 'PASS' not in report_text or draft_sha not in report_text:raise SystemExit('Missing exact review checkpoint')
 content=draft.read_text();lines=content.splitlines()
 if not re.search(r'\{#ch\d+\}',lines[0]):lines[0]+=f' {{#ch{n:02}}}'
 accepted_text,editorial_changes=clean('\n'.join(lines)+'\n')
 target.write_text(accepted_text)
 claims=ROOT/f'research/claims_ch{n:02}.md'
 if not claims.is_file():raise SystemExit('Claim ledger fragment missing')
 append(ROOT/'research/claim_ledger.md',claims.read_text())
 before=run(['git','rev-parse','HEAD']).strip()
 record={'accepted_utc':datetime.now(timezone.utc).isoformat(),'chapter':n,'source_draft':str(draft.relative_to(ROOT)),'reviewed_draft_sha256':draft_sha,'manuscript':str(target.relative_to(ROOT)),'manuscript_sha256':sha(target),'independent_internal_report':str(report.relative_to(ROOT)),'review_report_sha256':sha(report),'prior_git_commit':before,'editorial_difference':'Stable chapter anchor added when absent; recorded stylistic edits without changes to dates/citations', 'editorial_changes':editorial_changes,'scope':'Internal research acceptance; no external professional peer review claimed'}
 out=ROOT/'research/acceptance'/f'ch{n:02}.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 note=ROOT/f'research/source_notes/chapter{n:02}.md'
 if not note.exists():note.write_text(f'# Глава{n}: принятие\n\nПолный исследовательский текст принят после независимой внутренней проверки. Источниковое досье: chapter{n:02}_sources.md; тезисы: ../claims_ch{n:02}.md; независимый отчёт: ../reviews/ch{n:02}_independent.md. Точные контрольные суммы и пределы принятия: ../acceptance/ch{n:02}.json. Последующая редактура должна сохранять подтверждённые источники и фиксировать конкретную причину изменения.\n')
 append(ROOT/'research/review_log.md',f'## Принятие главы{n}, {record["accepted_utc"][:10]}\n\nПринят полный текст {target.name}; независимый внутренний отчёт ch{n:02}_independent.md содержитPASS для точного драфта SHA256`{draft_sha}`. При переносе добавлен якорь и применены записанные стилистические правки без изменения дат и ссылок; исходный черновик сохранён. Источники/ограничения — в досье и отчёте; существенные тезисы внесены в общийledger. Это не внешнее профессиональное рецензирование. Отдельная последующая общая проверка книги остаётся обязательной.')
 progress=ROOT/'research/progress.json';v=json.loads(progress.read_text());v['chapters'][f'{n:02}']['status']='reviewed';v['last_content_checkpoint']=before
 v['next_action']=(f'Принять следующую главу{n+1}: проверить точный SHA её драфта по независимому отчёту, выполнить scripts/accept_chapter.py {n+1}; источник и claims уже сохранены. Затем продолжить по порядку до16, принять заключение и провести общий редакционно-источниковедческий проход перед сборкой. Не повторять готовое, сохранять commit/push и проверять GitHub.' if n<16 else 'Все16глав включены. Принять проверенное заключение из research/drafts/17-conclusion.md, проверить весь центральный аппарат, выполнить семь общих редакционных проходов, собрать и проверить DOCX/EPUB/PDF; FINAL только после закрытия всех проверок.')
 progress.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 run([sys.executable,'scripts/update_status.py']);run([sys.executable,'scripts/audit_project.py'])
 stage=[str(p.relative_to(ROOT)) for p in [target,claims,report,out,note,ROOT/'research/claim_ledger.md',ROOT/'research/review_log.md',progress,ROOT/'PROJECT_STATUS.md',ROOT/'NEXT_ACTION.md',ROOT/'research/project_audit.json']]
 run(['git','add',*stage]);print(run(['git','commit','-m',f'Integrate reviewed chapter {n:02} and update its scientific apparatus']).strip(),flush=True)
 run(['git','-c','credential.helper=!gh auth git-credential','push','origin','main'])
 head=run(['git','rev-parse','HEAD']).strip();remote=json.loads(run(['gh','api','repos/elcin31/caesar-31/branches/main']))['commit']['sha']
 if head!=remote:raise SystemExit('Push verification: different remote HEAD')
 item=json.loads(run(['gh','api',f'repos/elcin31/caesar-31/contents/manuscript/chapters/{target.name}?ref={head}']))
 data=base64.b64decode(item['content'])
 if hashlib.sha256(data).hexdigest()!=sha(target):raise SystemExit('Remote chapter content mismatch')
 print(f'Chapter{n:02}: accepted, committed and verified on GitHub at {head}',flush=True)
if __name__=='__main__':main()
