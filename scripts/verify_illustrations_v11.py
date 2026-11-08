#!/usr/bin/env python3
"""Prove that each accepted new plate is embedded in DOCX, EPUB and PDF."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile
from io import BytesIO
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist/v1.1'


def pixels(data):
    with Image.open(BytesIO(data)) as image:
        rgb = image.convert('RGB')
        return hashlib.sha256(str(rgb.size).encode() + rgb.tobytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    register_path = ROOT / 'assets/illustrations/v1.1/register.json'
    register = json.loads(register_path.read_text())
    records = register['records']
    require(len(records) == 34 and all(x['generated'] and x['visual_review'] and x['integrated'] for x in records),
            'All 34 plates must actually exist, pass visual review and be integrated')
    require({f'{n:02}' for n in range(1, 17)} <= {x['chapter'] for x in records}, 'A chapter is unillustrated')
    expected = {}
    for item in records:
        data = (ROOT / item['file']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Stale illustration register: ' + item['id'])
        require((ROOT / item['manuscript']).read_text().count('<!-- v1.1:' + item['id'] + ':start -->') == 1,
                'Missing or repeated manuscript plate: ' + item['id'])
        expected[item['id']] = pixels(data)
    require(len(set(expected.values())) == 34, 'Duplicate artwork in the 34-plate set')
    embedded = {}
    for suffix, prefix in [('docx', 'word/media/'), ('epub', 'EPUB/media/')]:
        with zipfile.ZipFile(DIST / f'Caesar_Augustus_v1.1.{suffix}') as archive:
            require(archive.testzip() is None, 'Broken ' + suffix + ' container')
            hashes = set()
            for name in archive.namelist():
                if name.startswith(prefix) and name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    hashes.add(pixels(archive.read(name)))
            embedded[suffix] = hashes
    with tempfile.TemporaryDirectory(prefix='caesar-pdf-plates-') as temporary:
        subprocess.run(['pdfimages', '-j', str(DIST / 'Caesar_Augustus_v1.1.pdf'), str(Path(temporary) / 'plate')], check=True)
        embedded['pdf'] = {pixels(p.read_bytes()) for p in Path(temporary).iterdir() if p.is_file()}
    evidence = []
    for item in records:
        formats = {kind: expected[item['id']] in hashes for kind, hashes in embedded.items()}
        require(all(formats.values()), 'Missing image in export: ' + item['id'] + ': ' + str(formats))
        evidence.append({'id': item['id'], 'file': item['file'], 'decoded_rgb_sha256': expected[item['id']], 'embedded': formats})
    baseline = json.loads((ROOT / 'research/recovery/2026-11-08/local.json').read_text())
    preserved = [path for path in baseline['preserved_file_sha256'] if path.startswith('dist/final/')]
    for path in preserved:
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == baseline['preserved_file_sha256'][path],
                'Version 1.0 release file changed: ' + path)
    result = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'status': 'pass', 'new_illustrations': 34,
              'chapter_coverage': list(range(1, 17)), 'method': 'Compare dimensions and decoded RGB pixels of every source JPEG against all embedded DOCX/EPUB resources and every PDF image extracted by Poppler pdfimages -j.',
              'register_sha256': hashlib.sha256(register_path.read_bytes()).hexdigest(),
              'formats_checked': ['docx', 'epub', 'pdf'], 'preserved_v10_files_checked': len(preserved), 'plates': evidence}
    (DIST / 'illustration_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'plates'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
