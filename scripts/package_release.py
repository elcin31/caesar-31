#!/usr/bin/env python3
"""Package an actually checked release; final filenames require completion."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from publication_config import ROOT, add_release_arguments, release_from_args, relative

TOP = {'README.md', 'AGENTS.md', 'PROJECT_STATUS.md', 'NEXT_ACTION.md', 'references.bib', '.gitignore',
       'Bibliography.md', 'Research_Methodology.md', 'Editorial_Report.md', 'requirements.txt'}
DIRS = {'.agents', 'research', 'sources', 'manuscript', 'assets', 'scripts'}
NO_REDISTRIBUTION = {'paper-deep-research', 'paper-reviewer-check'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def selected(path, dist):
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if path.is_symlink():
        return False
    if parts[0] not in TOP | DIRS and not path.is_relative_to(dist):
        return False
    if '__pycache__' in parts or path.suffix == '.pyc':
        return False
    # This public-domain geographic source is required by the offline map builder.
    if path.suffix == '.zip' and rel.as_posix() != 'assets/maps/data/natural_earth_50m_land.zip':
        return False
    if parts[0] == '.agents' and len(parts) > 2 and parts[2] in NO_REDISTRIBUTION:
        return False
    if rel.as_posix().startswith('research/source_notes/evidence/') and path.suffix == '.txt':
        return False
    if path.is_relative_to(dist) and path.name in {'package_manifest.json', 'archive.sha256', 'reference.docx', 'pdf-header.tex'}:
        return False
    return True


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    parser = argparse.ArgumentParser()
    add_release_arguments(parser)
    parser.add_argument('--reader-bundle', action='store_true', help='Package reading editions and their editorial/validation records; source assets remain in the repository')
    args = parser.parse_args()
    release = release_from_args(args)
    dist = release.output_dir
    require(dist.is_relative_to(ROOT), 'A packaged release must be built within this project directory.')
    audit = json.loads((ROOT / 'research/project_audit.json').read_text(encoding='utf-8'))
    validation = json.loads((dist / 'validation.json').read_text(encoding='utf-8'))
    manifest_path = dist / 'build_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    require(audit['status'] == 'pass', 'Run and fix audit_project.py first')
    for item in audit['files']:
        require(digest((ROOT / item['path']).read_bytes()) == item['sha256'], 'Stale source audit: ' + item['path'])
    require(manifest.get('release') == release.version and manifest.get('final') == release.final, 'Build release metadata differs from package request')
    require(validation.get('build_manifest_sha256') == digest(manifest_path.read_bytes()), 'Export validation is stale: run verify_exports.py again')
    require(validation['epubcheck']['status'] == 'pass', 'This release requires actual EPUBCheck validation')
    for group in ('inputs', 'resources', 'outputs'):
        for item in manifest[group]:
            path = ROOT / item['path']
            require(path.is_file() and digest(path.read_bytes()) == item['sha256'], 'File changed since verified build: ' + item['path'])
    for suffix in ('docx', 'epub', 'pdf'):
        require((dist / f'{release.stem}.{suffix}').is_file(), 'Missing checked ' + suffix.upper() + ' edition')
        require(suffix in validation, 'No validation record for ' + suffix.upper())
    if args.reader_bundle:
        require(release.version == '1.1' and not release.final, 'Reader bundle is configured for edition 1.1')
        art_validation = json.loads((dist / 'illustration_validation.json').read_text())
        require(art_validation.get('status') == 'pass' and art_validation.get('new_illustrations') == 34,
                'Verify all 34 illustrations before packaging')
        candidates = [dist / f'{release.stem}.{suffix}' for suffix in ('docx', 'epub', 'pdf')]
        candidates += [dist / name for name in ('validation.json', 'illustration_validation.json', 'build_manifest.json',
                                               'visual_proof.json', 'illustration_pages.json', 'epubcheck.log')]
        candidates += [ROOT / name for name in ('README.md', 'Bibliography.md', 'Research_Methodology.md', 'Editorial_Report.md',
                                                'research/editorial_v11.md', 'research/illustration_plan_v11.json',
                                                'research/illustration_reviews_v11.json', 'assets/illustrations/v1.1/register.json')]
        files = sorted(candidates, key=lambda p: p.relative_to(ROOT).as_posix())
    else:
        files = sorted((p for p in ROOT.rglob('*') if p.is_file() and selected(p, dist)), key=lambda p: p.relative_to(ROOT).as_posix())
    listing = [{'path': relative(p), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in files]
    inventory = {'release': release.version, 'final': release.final, 'build_manifest_sha256': digest(manifest_path.read_bytes()),
                 'validation_sha256': digest((dist / 'validation.json').read_bytes()), 'files': listing, 'exclusions': [
        '.git; full external evidence snapshots; temporary caches; external validators and fonts; other release directories',
        '.agents/skills/paper-deep-research and paper-reviewer-check: no general redistribution license; see installation reports'
    ]}
    if args.reader_bundle:
        inventory['bundle_kind'] = 'Reading editions and editorial records; complete editable sources and image files are in elcin31/caesar-31, not duplicated in this ZIP.'
    out = dist / release.archive_name
    aliases = {}
    if release.final:
        for suffix in ('docx', 'epub', 'pdf'):
            aliases[f'Caesar_Augustus.{suffix}'] = dist / f'{release.stem}.{suffix}'
        for name in ('Bibliography.md', 'Research_Methodology.md', 'Editorial_Report.md'):
            aliases[name] = ROOT / name
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo('caesar-augustus/' + relative(path), (2026, 11, 5, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
        for name, path in aliases.items():
            archive.writestr(name, path.read_bytes())
        archive.writestr('caesar-augustus/PACKAGE_MANIFEST.json', json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(out) as archive:
        require(archive.testzip() is None, 'Archive integrity failed')
        for item in listing:
            require(digest(archive.read('caesar-augustus/' + item['path'])) == item['sha256'], 'Archive hash mismatch: ' + item['path'])
        require(args.reader_bundle or 'caesar-augustus/PROJECT_STATUS.md' in archive.namelist(), 'Missing project status')
        require(not any('/.git/' in name or any('/skills/' + skill + '/' in name for skill in NO_REDISTRIBUTION) for name in archive.namelist()), 'Archive contains excluded files')
        for name, path in aliases.items():
            require(digest(archive.read(name)) == digest(path.read_bytes()), 'Final alias mismatch: ' + name)
    inventory['archive'] = {'path': relative(out), 'bytes': out.stat().st_size, 'sha256': digest(out.read_bytes()), 'crc': 'pass', 'file_hashes': 'pass'}
    (dist / 'package_manifest.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (dist / 'archive.sha256').write_text(inventory['archive']['sha256'] + '  ' + release.archive_name + '\n', encoding='utf-8')
    print(json.dumps({'archive': inventory['archive'], 'files': len(listing)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
