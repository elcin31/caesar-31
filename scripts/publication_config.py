"""Shared, explicit release paths and a conservative completion gate.

Interim exports never overwrite the preserved v0.1 in dist/. A final release
also needs research/final_review_status.json: chapter records 01..16 with
historical/scientific/style=pass; seven full_review_passes (historical, sources,
historiography, argument, style, editorial, technical)=pass; and an empty
unresolved_critical_issues list. This is a workflow record, not user approval.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PASSES = ('historical', 'sources', 'historiography', 'argument', 'style', 'editorial', 'technical')


def add_release_arguments(parser):
    parser.add_argument('--version', default='0.2', help='Research release version (default: 0.2)')
    parser.add_argument('--output-dir', type=Path, help='Output directory; default dist/vVERSION or dist/final')
    parser.add_argument('--final', action='store_true', help='Use final filenames only after the full completion gate passes')


def source_inputs():
    candidates = [ROOT / 'manuscript/introduction.md',
                  *sorted((ROOT / 'manuscript/chapters').glob('*.md')),
                  ROOT / 'manuscript/conclusion.md', ROOT / 'manuscript/appendices.md',
                  ROOT / 'manuscript/bibliography.md']
    return [p for p in candidates if p.is_file() and p.stat().st_size]


def relative(path):
    path = path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def final_completion_gate():
    """Fail closed; word count alone cannot certify a completed monograph."""
    chapters = sorted((ROOT / 'manuscript/chapters').glob('*.md'))
    numbers = [int(p.name.split('-', 1)[0]) for p in chapters if re.match(r'^\d+-', p.name)]
    errors = []
    if sorted(numbers) != list(range(1, 17)) or len(chapters) != 16:
        errors.append('expected exactly chapters 01–16')
    conclusion = ROOT / 'manuscript/conclusion.md'
    if not conclusion.is_file() or not conclusion.stat().st_size:
        errors.append('a non-empty manuscript/conclusion.md is required')
    body_files = [ROOT / 'manuscript/introduction.md', *chapters]
    if conclusion.is_file():
        body_files.append(conclusion)
    total = 0
    for path in body_files:
        if not path.is_file():
            errors.append('missing ' + relative(path))
            continue
        body = re.sub(r'^\[\^[^]]+\]:.*(?:\n(?:[ \t]+.*|[ \t]*$))*', '', path.read_text(encoding='utf-8'), flags=re.M)
        total += len(re.findall(r'[А-Яа-яЁё]+(?:[–-][А-Яа-яЁё]+)*', body))
    below_target = total < 45000
    status_file = ROOT / 'research/final_review_status.json'
    if not status_file.is_file():
        errors.append('research/final_review_status.json has not recorded the completed reviews')
    else:
        status = json.loads(status_file.read_text(encoding='utf-8'))
        if below_target:
            exception = status.get('word_count_exception', {})
            if not (exception.get('editorial_justification') and len(exception['editorial_justification'].strip()) >= 80):
                errors.append(f'Russian body word count {total} is below target45000; a substantive editorial justification is required, without padding or new user approval')
        for n in range(1, 17):
            for check in ('historical', 'scientific', 'style'):
                if status.get('chapters', {}).get(f'{n:02}', {}).get(check) != 'pass':
                    errors.append(f'chapter {n:02} {check} review is incomplete')
        for check in REVIEW_PASSES:
            if status.get('full_review_passes', {}).get(check) != 'pass':
                errors.append(f'full {check} pass is incomplete')
        if status.get('unresolved_critical_issues') != []:
            errors.append('critical findings have not been explicitly cleared')
        recorded_sources = status.get('manuscript_sha256', {})
        for path in body_files:
            if path.is_file() and recorded_sources.get(relative(path)) != digest(path):
                errors.append('missing or stale final review hash: ' + relative(path))
    for name in ('Bibliography.md', 'Research_Methodology.md', 'Editorial_Report.md'):
        p = ROOT / name
        if not p.is_file() or not p.stat().st_size:
            errors.append('missing final report: ' + name)
    if errors:
        raise SystemExit('Final release blocked:\n- ' + '\n- '.join(errors))
    return {'status': 'pass', 'russian_body_words': total, 'chapters': 16,
            'review_record': relative(status_file), 'review_record_sha256': digest(status_file)}


@dataclass(frozen=True)
class Release:
    version: str
    output_dir: Path
    final: bool = False

    @property
    def stem(self):
        return 'Caesar_Augustus' if self.final else f'Caesar_Augustus_v{self.version}'

    @property
    def archive_name(self):
        if self.version == '1.1' and not self.final:
            return 'Caesar_Augustus_v1.1.zip'
        return 'Caesar_Augustus_FINAL.zip' if self.final else f'Caesar_Augustus_Research_v{self.version}.zip'

    @property
    def label(self):
        if self.version == '1.1' and not self.final:
            return 'Иллюстрированная научно-редакторская версия 1.1'
        return 'Завершённая исследовательская версия' if self.final else f'Исследовательская версия {self.version}'


def release_from_args(args):
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', args.version):
        raise SystemExit('--version must have a numeric form such as 0.2 or 1.0.1')
    output_dir = args.output_dir or ROOT / 'dist' / ('final' if args.final else f'v{args.version}')
    output_dir = (ROOT / output_dir).resolve() if not output_dir.is_absolute() else output_dir.resolve()
    if output_dir == ROOT / 'dist':
        raise SystemExit('Use a versioned output directory; original dist/ v0.1 files are preserved.')
    if args.final:
        final_completion_gate()
    return Release(args.version, output_dir, args.final)
