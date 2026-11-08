#!/usr/bin/env python3
"""Verify the pushed tree and stream-download only the four new 1.1 deliverables."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPO = 'elcin31/caesar-31'


def command(args):
    return subprocess.check_output(args, cwd=ROOT)


def api(path):
    return json.loads(command(['gh', 'api', 'repos/' + REPO + '/' + path]))


def main():
    if command(['git', 'status', '--porcelain', '--untracked-files=no']).strip():
        raise SystemExit('Commit tracked changes before remote verification')
    head = command(['git', 'rev-parse', 'HEAD']).decode().strip()
    assert api('branches/main')['commit']['sha'] == head, 'Remote main differs'
    commit = api('git/commits/' + head)
    tree = api('git/trees/' + commit['tree']['sha'] + '?recursive=1')
    assert not tree.get('truncated'), 'Truncated remote tree'
    local = {}
    for line in command(['git', 'ls-tree', '-rz', 'HEAD']).split(b'\0'):
        if line:
            meta, path = line.split(b'\t', 1)
            mode, kind, sha = meta.decode().split()
            if kind == 'blob':
                local[path.decode()] = (mode, sha)
    remote = {x['path']: (x['mode'], x['sha']) for x in tree['tree'] if x['type'] == 'blob'}
    assert local == remote, 'Remote/local Git tree differs'

    def download(suffix):
        path = f'dist/v1.1/Caesar_Augustus_v1.1.{suffix}'
        url = f'https://raw.githubusercontent.com/{REPO}/{head}/' + urllib.parse.quote(path)
        digest = hashlib.sha256()
        size = 0
        with urllib.request.urlopen(url, timeout=60) as response:
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
        expected = ROOT / path
        assert size == expected.stat().st_size, 'Download size differs: ' + path
        assert digest.hexdigest() == hashlib.sha256(expected.read_bytes()).hexdigest(), 'Download hash differs: ' + path
        return {'path': path, 'bytes': size, 'sha256': digest.hexdigest()}

    with ThreadPoolExecutor(max_workers=2) as pool:
        downloads = list(pool.map(download, ('docx', 'epub', 'pdf', 'zip')))
    report = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'status': 'pass',
              'repository': REPO, 'branch': 'main', 'commit': head, 'tree_sha': commit['tree']['sha'],
              'all_git_files_match': True, 'file_count': len(local), 'actual_downloads': downloads,
              'qualification': 'Checks only the new 1.1 deliverables. This immutable checkpoint is recorded by a later documentation commit.'}
    (ROOT / 'research/github_v11_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
