#!/usr/bin/env python3
"""Recheck a preserved release without rewriting its files or original reports.

Run verify_github_release.py separately before changing tracked files. This
script checks local bytes and runs the existing audits/validators in a temporary
copy; it does not build, edit, or certify the historical argument afresh.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--epubcheck-jar', type=Path)
    args = parser.parse_args()
    output = (ROOT / args.output_dir).resolve()
    require(output.is_relative_to(ROOT / 'research/recovery'),
            'Use a report directory within research/recovery/')
    release = ROOT / 'dist/final'
    protected = [p for directory in (release, ROOT / 'manuscript')
                 for p in directory.rglob('*') if p.is_file()]
    require(not any(output == p.parent or p.is_relative_to(output) for p in protected),
            'Recovery reports must be separate from preserved files')
    before = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in protected}
    report = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'repository': 'elcin31/caesar-31',
        'baseline_commit': git('rev-parse', 'HEAD').decode().strip(),
        'release': '1.0',
        'method': 'SHA-256 manifests, historical Git blobs, archive CRC and every '
                  'packaged file; existing audits and export validator in a temporary copy.',
    }
    build = load(release / 'build_manifest.json')
    for group in ('inputs', 'resources', 'outputs'):
        for item in build[group]:
            require(digest((ROOT / item['path']).read_bytes()) == item['sha256'],
                    'Changed build file: ' + item['path'])
    report['build_manifest_checks'] = {group: len(build[group])
                                       for group in ('inputs', 'resources', 'outputs')}

    original = load(ROOT / 'research/github_final_verification.json')
    require(original['status'] == 'pass', 'Original remote verification did not pass')
    subprocess.run(['git', 'merge-base', '--is-ancestor', original['commit'],
                    report['baseline_commit']], cwd=ROOT, check=True)
    for item in original['actual_download_sha256_checks']:
        data = git('show', original['commit'] + ':' + item['path'])
        require(digest(data) == item['sha256'], 'Historical report mismatch: ' + item['path'])
    report['original_remote_report'] = {
        'commit': original['commit'],
        'historical_file_hashes_checked': len(original['actual_download_sha256_checks']),
        'status': 'pass',
    }

    package = load(release / 'package_manifest.json')
    archive = ROOT / package['archive']['path']
    require(digest(archive.read_bytes()) == package['archive']['sha256'], 'Archive SHA-256 mismatch')
    checksum, name = (release / 'archive.sha256').read_text().strip().split(maxsplit=1)
    require(name == archive.name and checksum == package['archive']['sha256'],
            'Archive checksum file mismatch')
    require(digest((release / 'build_manifest.json').read_bytes()) == package['build_manifest_sha256'],
            'Package build manifest mismatch')
    require(digest((release / 'validation.json').read_bytes()) == package['validation_sha256'],
            'Package validation report mismatch')
    differences = []
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        require(bundle.testzip() is None, 'Archive CRC mismatch')
        require(len(names) == len(set(names)), 'Duplicate archive members')
        for name in names:
            parts = PurePosixPath(name).parts
            require(not name.startswith('/') and '..' not in parts and '.git' not in parts
                    and not any(p == '.env' or p.startswith('.env.') for p in parts),
                    'Unsafe archive member: ' + name)
            require(not any('/skills/' + skill + '/' in name
                            for skill in ('paper-deep-research', 'paper-reviewer-check')),
                    'Excluded skill in archive: ' + name)
            require(not (name.startswith('caesar-augustus/research/source_notes/evidence/')
                         and name.endswith('.txt')), 'Excluded evidence snapshot: ' + name)
        embedded = json.loads(bundle.read('caesar-augustus/PACKAGE_MANIFEST.json'))
        require(embedded == {k: v for k, v in package.items() if k != 'archive'},
                'Embedded and external package manifests differ')
        expected_members = {'caesar-augustus/PACKAGE_MANIFEST.json'}
        for item in package['files']:
            member = 'caesar-augustus/' + item['path']
            expected_members.add(member)
            data = bundle.read(member)
            require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                    'Packaged file mismatch: ' + item['path'])
            current = ROOT / item['path']
            if not current.is_file() or digest(current.read_bytes()) != item['sha256']:
                differences.append(item['path'])
        aliases = {f'Caesar_Augustus.{suffix}': release / f'Caesar_Augustus.{suffix}'
                   for suffix in ('docx', 'epub', 'pdf')}
        aliases.update({name: ROOT / name for name in
                        ('Bibliography.md', 'Research_Methodology.md', 'Editorial_Report.md')})
        for name, path in aliases.items():
            expected_members.add(name)
            require(digest(bundle.read(name)) == digest(path.read_bytes()), 'Alias mismatch: ' + name)
        require(set(names) == expected_members, 'Unexpected or missing archive members')
    report['archive'] = {
        'path': archive.relative_to(ROOT).as_posix(), 'sha256': package['archive']['sha256'],
        'crc': 'pass', 'packaged_files_checked': len(package['files']),
        'aliases_checked': len(aliases), 'members': len(names),
        'snapshot_differences_from_current_checkout': differences,
        'qualification': 'The archive is the original publication snapshot. Later '
                         'repository documentation is not silently substituted into it.',
    }

    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='caesar-recovery-') as temporary:
        scratch = Path(temporary)
        for name in ('scripts', 'manuscript', 'assets', '.agents'):
            shutil.copytree(ROOT / name, scratch / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (scratch / 'research').mkdir()
        for name in ('skills_core_manifest.json', 'skills_toolkits_manifest.json',
                     'final_review_status.json'):
            shutil.copy2(ROOT / 'research' / name, scratch / 'research' / name)
        for name in ('references.bib', 'Bibliography.md', 'Research_Methodology.md', 'Editorial_Report.md'):
            shutil.copy2(ROOT / name, scratch / name)
        shutil.copytree(release, scratch / 'dist/final', ignore=shutil.ignore_patterns('*.zip'))
        commands = [
            [sys.executable, 'scripts/audit_project.py'],
            [sys.executable, 'scripts/full_manuscript_audit.py'],
            [sys.executable, 'scripts/verify_exports.py', '--version', '1.0', '--final'],
        ]
        if args.epubcheck_jar:
            commands[-1] += ['--epubcheck-jar', str(args.epubcheck_jar.resolve())]
            report['epubcheck_jar_sha256'] = digest(args.epubcheck_jar.read_bytes())
        for command in commands:
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            require(result.returncode == 0, 'Verification failed: ' + ' '.join(command[1:])
                    + '\n' + result.stdout + '\n' + result.stderr)
        for source in ('research/project_audit.json', 'research/full_manuscript_audit.json',
                       'dist/final/validation.json', 'dist/final/pdf_fonts.txt',
                       'dist/final/pdf_page_bounds.json'):
            shutil.copy2(scratch / source, output / Path(source).name)
        if args.epubcheck_jar:
            log = (scratch / 'dist/final/epubcheck.log').read_text(encoding='utf-8')
            (output / 'epubcheck.log').write_text(log.rstrip() + '\n', encoding='utf-8')
        validation = load(output / 'validation.json')
        report['export_validation'] = validation
        report['project_audit_status'] = load(output / 'project_audit.json')['status']
        report['manuscript_audit_status'] = load(output / 'full_manuscript_audit.json')['structural_status']

    require(all(digest((ROOT / path).read_bytes()) == sha for path, sha in before.items()),
            'A preserved manuscript/release file changed during verification')
    report['preserved_file_sha256'] = before
    report['preserved_files_unchanged'] = True
    report['verified_utc'] = datetime.now(timezone.utc).isoformat()
    report['status'] = 'pass'
    report['qualification'] = ('Technical recovery only; no new historical reading, external peer review, '
                               'fresh visual proofing, or direct Word/Apple Books test. EPUBCheck '
                               'was rerun only if recorded as pass in export_validation.')
    (output / 'local.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in
                      ('preserved_file_sha256', 'export_validation')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
