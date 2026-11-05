#!/usr/bin/env python3
"""Local structural audit; does not certify historical truth or completeness of reading."""
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    files = [ROOT / 'manuscript/introduction.md', *sorted((ROOT / 'manuscript/chapters').glob('*.md'))]
    report = {'method': 'Russian letter tokens in body; headings included; footnotes excluded', 'files': [], 'errors': []}
    all_ids = []
    banned = ['следует отметить', 'нельзя не подчеркнуть', 'не только', 'важную роль в этом процессе сыграл', 'данное событие стало поворотным моментом']
    for path in files:
        src = path.read_text()
        defs = re.findall(r'^\[\^([^]]+)\]:', src, re.M)
        body = '\n'.join(line for line in src.splitlines() if not re.match(r'^\[\^[^]]+\]:', line))
        refs = re.findall(r'\[\^([^]]+)\]', body)
        missing = sorted(set(refs) - set(defs))
        unused = sorted(set(defs) - set(refs))
        duplicates = [k for k, n in collections.Counter(defs).items() if n > 1]
        hits = [x for x in banned if x in body.lower()]
        hidden = sorted({f'U+{ord(c):04X}' for c in src if c in '\u200b\u200c\u200d\u2060\ufeff'})
        item = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'russian_body_words': len(re.findall(r'[А-Яа-яЁё]+(?:[–-][А-Яа-яЁё]+)*', body)),
                'whitespace_body_words': len(body.split()), 'footnote_definitions': len(defs),
                'footnote_occurrences': len(refs), 'undefined': missing, 'unused': unused,
                'duplicate_definitions': duplicates, 'banned_phrase_hits': hits, 'hidden_characters': hidden}
        report['files'].append(item)
        if missing or unused or duplicates or hits or hidden: report['errors'].append(item['path'])
        all_ids.extend(defs)
    report['cross_file_duplicate_footnotes'] = [k for k,n in collections.Counter(all_ids).items() if n > 1]
    if report['cross_file_duplicate_footnotes']: report['errors'].append('duplicate footnote namespaces')
    bib = (ROOT / 'references.bib').read_text()
    keys = re.findall(r'^@\w+\s*\{\s*([^,]+),', bib, re.M)
    report['bibliographic_entries'] = len(keys)
    report['duplicate_bibliographic_keys'] = [k for k,n in collections.Counter(keys).items() if n > 1]
    if report['duplicate_bibliographic_keys']: report['errors'].append('duplicate bib keys')
    skills = []
    for path in sorted((ROOT / '.agents/skills').glob('*/SKILL.md')):
        match = re.search(r'^name:\s*[\'"]?([^\n\'"]+)', path.read_text(), re.M)
        if match: skills.append(match.group(1).strip())
        else: report['errors'].append('skill missing name: ' + str(path.relative_to(ROOT)))
    report['installed_skill_names'] = skills
    report['duplicate_skill_names'] = [k for k,n in collections.Counter(skills).items() if n > 1]
    if report['duplicate_skill_names']: report['errors'].append('duplicate skill discovery names')
    checked = 0
    mismatches = []
    distribution_exclusions = []
    for manifest_name in ['skills_core_manifest.json', 'skills_toolkits_manifest.json']:
        for skill in json.loads((ROOT / 'research' / manifest_name).read_text()):
            skill_dir = ROOT / '.agents/skills' / skill['name']
            if not skill_dir.exists() and skill['name'] in {'paper-deep-research', 'paper-reviewer-check'}:
                distribution_exclusions.append(skill['name'])
                continue
            listed = skill['files']
            entries = listed.items() if isinstance(listed, dict) else ((x['path'], x['sha256']) for x in listed)
            for relative, expected in entries:
                path = ROOT / '.agents/skills' / skill['name'] / relative
                checked += 1
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                    mismatches.append(str(path.relative_to(ROOT)))
    report['installed_skill_files_hash_checked'] = checked
    report['installed_skill_file_mismatches'] = mismatches
    report['documented_distribution_exclusions_absent'] = distribution_exclusions
    if mismatches: report['errors'].append('skill installation hash mismatch')
    report['total_russian_body_words'] = sum(x['russian_body_words'] for x in report['files'])
    report['total_footnote_occurrences'] = sum(x['footnote_occurrences'] for x in report['files'])
    report['status'] = 'pass' if not report['errors'] else 'fail'
    out = ROOT / 'research/project_audit.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not report['errors'] else 1)


if __name__ == '__main__':
    main()
