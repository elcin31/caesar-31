#!/usr/bin/env python3
"""Verify canonical GitHub history/tree and download the actual final editions.

The saved report describes the immutable commit checked, not its own later
documentation commit. Original migration reports remain unchanged.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'elcin31/caesar-31'


def command(args):
    return subprocess.check_output(args, cwd=ROOT)


def api(path):
    return json.loads(command(['gh', 'api', 'repos/' + REPOSITORY + '/' + path]))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_tree():
    result = {}
    for line in command(['git', 'ls-tree', '-rz', 'HEAD']).split(b'\0'):
        if line:
            info, path = line.split(b'\t', 1)
            mode, kind, sha = info.decode().split()
            if kind == 'blob':
                result[path.decode()] = sha
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('research/github_final_verification.json'))
    args = parser.parse_args()
    if command(['git', 'status', '--porcelain', '--untracked-files=no']).strip():
        raise SystemExit('Commit tracked changes before verifying the release')
    head = command(['git', 'rev-parse', 'HEAD']).decode().strip()
    if api('branches/main')['commit']['sha'] != head:
        raise SystemExit('Remote main differs from local HEAD')
    commit = api('git/commits/' + head)
    tree = api('git/trees/' + commit['tree']['sha'] + '?recursive=1')
    if tree.get('truncated'):
        raise SystemExit('Remote tree is truncated')
    local = local_tree()
    remote = {item['path']: item['sha'] for item in tree['tree'] if item['type'] == 'blob'}
    if local != remote or command(['git', 'rev-parse', 'HEAD^{tree}']).decode().strip() != commit['tree']['sha']:
        raise SystemExit('Remote/local file tree differs')
    historical = ['7c6e8af', '7445478a155f144196495ee8c4422d8c24ae46c6', '3678eed']
    for ancestor in historical:
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, head], cwd=ROOT, check=True)
    selected = sorted(p for p in local if p.startswith('manuscript/'))
    selected += ['AGENTS.md', 'PROJECT_STATUS.md', 'NEXT_ACTION.md', 'references.bib', 'Bibliography.md',
                 'Research_Methodology.md', 'Editorial_Report.md', 'sources/primary_sources.md',
                 'sources/secondary_sources.md', 'assets/cover.png', 'assets/augustan_adoptions.png',
                 'dist/final/validation.json', 'dist/final/build_manifest.json',
                 'dist/final/package_manifest.json', 'dist/final/archive.sha256',
                 'dist/final/Caesar_Augustus.docx', 'dist/final/Caesar_Augustus.epub',
                 'dist/final/Caesar_Augustus.pdf', 'dist/final/Caesar_Augustus_FINAL.zip']

    def download_check(path):
        endpoint = 'repos/' + REPOSITORY + '/contents/' + quote(path, safe='/') + '?ref=' + head
        data = command(['gh', 'api', endpoint, '-H', 'Accept: application/vnd.github.raw+json'])
        expected = (ROOT / path).read_bytes()
        if digest(data) != digest(expected):
            raise ValueError('Actual downloaded bytes differ: ' + path)
        return {'path': path, 'bytes': len(data), 'sha256': digest(data), 'git_blob_sha1': local[path]}

    with ThreadPoolExecutor(max_workers=2) as pool:
        checks = list(pool.map(download_check, selected))
    result = {
        'verified_utc': datetime.now(timezone.utc).isoformat(), 'status': 'pass',
        'repository': REPOSITORY, 'branch': 'main', 'commit': head,
        'commit_url': 'https://github.com/' + REPOSITORY + '/commit/' + head,
        'tree_sha': commit['tree']['sha'], 'file_count': len(local),
        'all_remote_git_blobs_match': True, 'both_original_histories_preserved': True,
        'actual_download_sha256_checks': checks,
        'method': 'GitHub REST branch/commit/recursive tree and raw content downloads at immutable commit; all local committed blobs compared; final ZIP and three reading editions downloaded and SHA-256 checked.',
        'qualification': 'This report records the checked release commit; it is subsequently saved in a separate documentation commit to avoid self-referential hashes.'
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'actual_download_sha256_checks'}, ensure_ascii=False, indent=2))
    print('Actual downloaded files:', len(checks))


if __name__ == '__main__':
    main()
