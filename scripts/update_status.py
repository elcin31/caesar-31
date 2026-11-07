#!/usr/bin/env python3
"""Render a resumable research status from explicit editorial states and real files."""
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'planned': 'не начата', 'researching': 'исследование', 'draft': 'написана, проверка не завершена', 'reviewed': 'внутренняя проверка пройдена'}


def count(path):
    text = path.read_text()
    body = '\n'.join(s for s in text.splitlines() if not re.match(r'^\[\^[^]]+\]:', s))
    return len(re.findall(r'[А-Яа-яЁё]+(?:[–-][А-Яа-яЁё]+)*', body))


def main():
    progress = json.loads((ROOT / 'research/progress.json').read_text())
    version = progress['version']
    final = progress.get('final', False)
    completed = progress.get('completion_state') == 'final_verified'
    release_dir = ROOT / 'dist' / ('final' if final else f'v{version}')
    rows = []
    total = count(ROOT / 'manuscript/introduction.md')
    reviewed = 0
    for number, chapter in sorted(progress['chapters'].items()):
        paths = list((ROOT / 'manuscript/chapters').glob(number + '-*.md'))
        words = sum(count(p) for p in paths)
        total += words
        state = chapter['status']
        reviewed += state == 'reviewed'
        rows.append(f"| {int(number)} | {chapter['title']} | {LABELS[state]} | {words} |")
    conclusion = ROOT / 'manuscript/conclusion.md'
    conclusion_words = count(conclusion) if conclusion.exists() else 0
    total += conclusion_words
    drafts = []
    for path in sorted((ROOT / 'research/drafts').glob('*.md')):
        number = path.name.split('-', 1)[0]
        if number == '17' and conclusion.exists():
            continue
        if not list((ROOT / 'manuscript/chapters').glob(number + '-*.md')):
            drafts.append((path, count(path)))
    draft_table = '\n'.join(f'| {p.name} | {n} | ещё не включён в основную рукопись |' for p,n in drafts)
    bibliography = len(re.findall(r'^@\w+\s*\{', (ROOT / 'references.bib').read_text(), re.M))
    validation_file = release_dir / 'validation.json'
    if validation_file.exists():
        v = json.loads(validation_file.read_text())
        location = release_dir.relative_to(ROOT)
        exports = f"Версия v{version}: DOCX/EPUB/PDF фактически собраны; PDF {v.get('pdf', {}).get('pages', '?')} страниц; EPUBCheck: {v.get('epubcheck', {}).get('status', 'не выполнен')}. Подробности и SHA-256 — в {location}/validation.json и build_manifest.json."
        manifest_file = validation_file.parent / 'build_manifest.json'
        if manifest_file.exists():
            manifest = json.loads(manifest_file.read_text())
            current_files = {str(p.relative_to(ROOT)) for p in [ROOT/'manuscript/introduction.md', *sorted((ROOT/'manuscript/chapters').glob('*.md')), ROOT/'manuscript/conclusion.md', ROOT/'manuscript/appendices.md', ROOT/'manuscript/bibliography.md'] if p.exists()}
            old_files = {x['path'] for x in manifest['inputs']}
            stale = current_files != old_files or any(not (ROOT/x['path']).exists() or hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest() != x['sha256'] for x in manifest['inputs'])
            if stale:
                exports += ' Эта сборка относится к прежней контрольной точке: текущая рукопись уже расширена и требует новой сборки после завершения части. Наличие прежних файлов не означает экспорта новых глав.'
            if completed and stale:
                raise SystemExit('Final status cannot describe stale manuscript exports')
        if completed and (reviewed != 16 or not conclusion_words or v.get('epubcheck', {}).get('status') != 'pass'):
            raise SystemExit('Final status requires 16 reviewed chapters, conclusion, and EPUBCheck pass')
        package = release_dir / 'package_manifest.json'
        if package.exists():
            data = json.loads(package.read_text())
            archive = ROOT / data['archive']['path']
            if archive.is_file() and hashlib.sha256(archive.read_bytes()).hexdigest() == data['archive']['sha256']:
                exports += f" Архив {data['archive']['path']} фактически создан, CRC и контрольные суммы его файлов проверены; SHA-256 опубликована в archive.sha256."
    else:
        if completed:
            raise SystemExit('Final status requires actual export validation')
        exports = f'Читательские файлы v{version} ещё не собраны; предыдущие версии сохранены в dist.'
    completion_note = ('Полная исследовательская версия завершена и прошла внутренние проверки. Внешняя профессиональная рецензия не проводилась.'
                       if completed else 'Монография в работе; незавершённая версия не является FINAL.')
    workflow_note = ('Основные исследовательские и издательские этапы завершены. Дальнейшие изменения выпускать отдельной версией по конкретным замечаниям или новым проверенным материалам; перед правкой сохранять источники и контрольную точку. Работа после завершения сессии не обещается.'
                     if completed else 'После каждого законченного исследовательского цикла обновить реестры, выполнить внутреннюю проверку, сохранить отдельный Git-коммит и перейти к следующей главе. Не повторять завершённый материал и не запрашивать согласование обычного этапа. Работа после завершения текущей сессии не обещается.')
    repository_note = f"Канонический репозиторий: https://github.com/{progress['repository']}; ветка {progress.get('branch', 'main')}. Состояние миграции: {progress.get('migration_status', 'см. research/migration/')}." if progress.get('repository') else 'Удалённый репозиторий ещё не подключён.'
    text = f'''# Состояние CAESAR & AUGUSTUS — v{version}

Обновлено: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. {completion_note}

{repository_note}

Основной текст: **{total} русских слов**, включая введение и {conclusion_words} слов заключения, без примечаний, приложений и библиографии. Внутреннюю проверку прошли **{reviewed}/16 глав**. Библиографическая база: **{bibliography} записей**, включая программу чтения; запись не означает полного изучения работы.

| Глава | Содержание | Состояние | Русских слов |
|---|---|---|---:|
''' + '\n'.join(rows) + f'''

## Сохранённые черновики последующих глав

Эти тексты сохраняются для защиты от прерывания, проходят отдельную проверку и включаются в книгу по порядку. Они не входят в заявленный выше объём основной рукописи и не считаются завершёнными главами.

| Файл в research/drafts/ | Русских слов | Статус |
|---|---:|---|
{draft_table if drafts else '| — | 0 | сохранённых невключённых черновиков пока нет |'}

Суммарный объём сохранённых невключённых черновиков: {sum(n for _,n in drafts)} слов. Временный файл в /tmp не считается достаточным способом сохранения законченного текста.

Введение сохранено и точечно актуализировано после нового чтения. Развёрнутый план и гипотезы — research/conception.md. Исходный статус v0.1 сохранён в research/status_v01.md; первоначальный коммит и исходные читательские файлы сохранены.

## Последняя контрольная точка

Последний содержательный коммит, записанный при обновлении: `{progress['last_content_checkpoint']}`. Текущий HEAD и последующие служебные фиксации проверять командой `git log -1`; хеш коммита, содержащего этот файл, внутри самого себя не фиксируется. Удалённую контрольную точку и результаты сверки проверять по research/migration/; наличие локального коммита само по себе не доказывает успешный push.

## Научный аппарат и проверка

Примечания — Chicago Notes and Bibliography; античные книги/разделы сверяются с конкретными электронными изданиями, современные страницы — только с непосредственно доступными фрагментами. Реестры: sources/primary_sources.md, sources/secondary_sources.md, research/claim_ledger.md. Центральная база согласована с главами; отдельные additions/claims/review-фрагменты сохранены как история проверки.

Установлены17 исследовательских навыков, имена уникальны; проверки файлов — research/project_audit.json. Внутренние проверки с ИИ не заменяют внешней профессиональной рецензии. Влияние современных исследований раскрывается в аргументации и заметках; META/частичное чтение не выдаётся за полную книгу.

## Экспорт

{exports} Историческая обложка проекта сохранена. Тестирование Word и Apple Books непосредственно в Linux не проводится; проверяются контейнеры, XML, ссылки, русские метаданные, ресурсы, EPUBCheck и PDF.

## Неустранённые вопросы

''' + '\n'.join('- ' + s for s in progress['unresolved']) + f'''

## Ближайшее действие

{progress['next_action']}

{workflow_note}
'''
    (ROOT / 'PROJECT_STATUS.md').write_text(text)
    (ROOT / 'NEXT_ACTION.md').write_text('# Следующее действие\n\n' + progress['next_action'] + '\n\nПоследняя записанная содержательная контрольная точка: `' + progress['last_content_checkpoint'] + '`. До правки читать PROJECT_STATUS.md, AGENTS.md, источниковые заметки и review_log.md. Не начинать исследование заново и не повторять завершённые главы.\n')
    print(f'v{version}: {reviewed}/16 reviewed; {total} Russian body words; {bibliography} bibliography records')


if __name__ == '__main__':
    main()
