#!/usr/bin/env python3
"""Render a resumable research status from explicit editorial states and real files."""
from datetime import datetime, timezone
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'planned': 'не начата', 'researching': 'исследование', 'draft': 'написана, проверка не завершена', 'reviewed': 'внутренняя проверка пройдена'}


def count(path):
    text = path.read_text()
    body = '\n'.join(s for s in text.splitlines() if not re.match(r'^\[\^[^]]+\]:', s))
    return len(re.findall(r'[А-Яа-яЁё]+(?:[–-][А-Яа-яЁё]+)*', body))


def main():
    progress = json.loads((ROOT / 'research/progress.json').read_text())
    version = progress['version']
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
    bibliography = len(re.findall(r'^@\w+\s*\{', (ROOT / 'references.bib').read_text(), re.M))
    validation_file = ROOT / 'dist' / f'v{version}' / 'validation.json'
    if validation_file.exists():
        v = json.loads(validation_file.read_text())
        exports = f"Версия v{version}: DOCX/EPUB/PDF фактически собраны; PDF {v.get('pdf', {}).get('pages', '?')} страниц; EPUBCheck: {v.get('epubcheck', {}).get('status', 'не выполнен')}. Подробности и SHA-256 — в dist/v{version}/validation.json и build_manifest.json."
    else:
        exports = f'Читательские файлы v{version} ещё не собраны; предыдущие версии сохранены в dist.'
    text = f'''# Состояние CAESAR & AUGUSTUS — v{version}

Обновлено: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. Монография в работе; незавершённая версия не является FINAL.

Основной текст: **{total} русских слов**, включая введение и {conclusion_words} слов заключения, без примечаний, приложений и библиографии. Внутреннюю проверку прошли **{reviewed}/16 глав**. Библиографическая база: **{bibliography} записей**, включая программу чтения; запись не означает полного изучения работы.

| Глава | Содержание | Состояние | Русских слов |
|---|---|---|---:|
''' + '\n'.join(rows) + f'''

Введение сохранено и точечно актуализировано после нового чтения. Развёрнутый план и гипотезы — research/conception.md. Исходный статус v0.1 сохранён в research/status_v01.md; первоначальный коммит и исходные читательские файлы сохранены.

## Последняя контрольная точка

Последний содержательный коммит, записанный при обновлении: `{progress['last_content_checkpoint']}`. Текущий HEAD и последующие служебные фиксации проверять командой `git log -1`; хеш коммита, содержащего этот файл, внутри самого себя не фиксируется. Git только локальный, origin не создавался.

## Научный аппарат и проверка

Примечания — Chicago Notes and Bibliography; античные книги/разделы сверяются с конкретными электронными изданиями, современные страницы — только с непосредственно доступными фрагментами. Реестры: sources/primary_sources.md, sources/secondary_sources.md, research/claim_ledger.md. Новые главы временно имеют отдельные additions/claims/review-фрагменты до центральной интеграции.

Установлены17 исследовательских навыков, имена уникальны; проверки файлов — research/project_audit.json. Внутренние проверки с ИИ не заменяют внешней профессиональной рецензии. Влияние современных исследований раскрывается в аргументации и заметках; META/частичное чтение не выдаётся за полную книгу.

## Экспорт

{exports} Историческая обложка проекта сохранена. Тестирование Word и Apple Books непосредственно в Linux не проводится; проверяются контейнеры, XML, ссылки, русские метаданные, ресурсы, EPUBCheck и PDF.

## Неустранённые вопросы

''' + '\n'.join('- ' + s for s in progress['unresolved']) + f'''

## Ближайшее действие

{progress['next_action']}

После каждого законченного исследовательского цикла обновить реестры, выполнить внутреннюю проверку, сохранить отдельный Git-коммит и перейти к следующей главе. Не повторять завершённый материал и не запрашивать согласование обычного этапа. Работа после завершения текущей сессии не обещается.
'''
    (ROOT / 'PROJECT_STATUS.md').write_text(text)
    (ROOT / 'NEXT_ACTION.md').write_text('# Следующее действие\n\n' + progress['next_action'] + '\n\nПоследняя записанная содержательная контрольная точка: `' + progress['last_content_checkpoint'] + '`. До правки читать PROJECT_STATUS.md, AGENTS.md, источниковые заметки и review_log.md. Если черновики следующей главы находятся в /tmp, проверить их наличие; отсутствие временного файла не отменяет сохранённых источниковых заметок.\n')
    print(f'v{version}: {reviewed}/16 reviewed; {total} Russian body words; {bibliography} bibliography records')


if __name__ == '__main__':
    main()
