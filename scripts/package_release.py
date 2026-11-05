#!/usr/bin/env python3
"""Package the reviewed local release with a verifiable inventory and rights exclusions."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
NAME = 'Caesar_Augustus_Research_v0.1.zip'
TOP = {'README.md', 'AGENTS.md', 'PROJECT_STATUS.md', 'references.bib', '.gitignore'}
DIRS = {'.agents', 'research', 'sources', 'manuscript', 'assets', 'scripts', 'dist'}
NO_REDISTRIBUTION = {'paper-deep-research', 'paper-reviewer-check'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def selected(path):
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if parts[0] not in TOP | DIRS: return False
    if '__pycache__' in parts or path.suffix in {'.pyc', '.zip'}: return False
    if parts[0] == '.agents' and len(parts) > 2 and parts[2] in NO_REDISTRIBUTION: return False
    if rel.as_posix().startswith('research/source_notes/evidence/') and path.suffix == '.txt': return False
    if parts[0] == 'dist' and path.name in {'package_manifest.json', 'archive.sha256', 'reference.docx', 'pdf-header.tex'}: return False
    return True


def main():
    audit = json.loads((ROOT / 'research/project_audit.json').read_text())
    validation = json.loads((DIST / 'validation.json').read_text())
    assert audit['status'] == 'pass', 'Run and fix audit_project.py first'
    for item in audit['files']:
        assert digest((ROOT / item['path']).read_bytes()) == item['sha256'], 'Stale source audit: ' + item['path']
    assert validation['epubcheck']['status'] == 'pass', 'This release requires actual EPUBCheck validation'
    for suffix in ['docx', 'epub', 'pdf']:
        assert (DIST / f'Caesar_Augustus_v0.1.{suffix}').is_file()
    files = sorted((p for p in ROOT.rglob('*') if p.is_file() and selected(p)), key=lambda p: p.relative_to(ROOT).as_posix())
    listing = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in files]
    inventory = {'release': '0.1', 'files': listing, 'exclusions': [
        '.git; full external evidence snapshots; temporary caches; external validators and fonts',
        '.agents/skills/paper-deep-research and paper-reviewer-check: no general redistribution license; see installation reports'
    ]}
    out = DIST / NAME
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in files:
            info = zipfile.ZipInfo('caesar-augustus/' + path.relative_to(ROOT).as_posix(), (2026, 11, 5, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes())
        z.writestr('caesar-augustus/PACKAGE_MANIFEST.json', json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None, 'Archive integrity failed'
        for item in listing:
            assert digest(z.read('caesar-augustus/' + item['path'])) == item['sha256'], item['path']
        assert 'caesar-augustus/PROJECT_STATUS.md' in z.namelist()
        assert not any('/.git/' in n or any('/skills/' + s + '/' in n for s in NO_REDISTRIBUTION) for n in z.namelist())
    inventory['archive'] = {'path': 'dist/' + NAME, 'bytes': out.stat().st_size, 'sha256': digest(out.read_bytes()), 'crc': 'pass', 'file_hashes': 'pass'}
    (DIST / 'package_manifest.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
    (DIST / 'archive.sha256').write_text(inventory['archive']['sha256'] + '  ' + NAME + '\n')
    print(json.dumps({'archive': inventory['archive'], 'files': len(listing)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
