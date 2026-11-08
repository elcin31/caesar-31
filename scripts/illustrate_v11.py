#!/usr/bin/env python3
"""Integrate only real, visually reviewed v1.1 plates and render honest progress."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    plan = json.loads((ROOT / 'research/illustration_plan_v11.json').read_text())
    reviews = json.loads((ROOT / 'research/illustration_reviews_v11.json').read_text())
    records = []
    for item in plan:
        item = dict(item)
        path = ROOT / item['file']
        item['generated'] = path.is_file()
        item['visual_review'] = reviews.get(item['id'], {}).get('decision') == 'accept'
        item['integrated'] = False
        if item['generated']:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                item['dimensions'] = list(image.size)
                if min(image.size) < 1000:
                    raise ValueError('Insufficient resolution: ' + item['id'])
            item['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            item['bytes'] = path.stat().st_size
            item['jpeg_quality'] = 94 if int(item['id'].split('-')[1]) <= 13 else 92
        if item['generated'] and item['visual_review']:
            source = ROOT / item['manuscript']
            text = source.read_text()
            start = '<!-- v1.1:' + item['id'] + ':start -->'
            end = '<!-- v1.1:' + item['id'] + ':end -->'
            text = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n*', '', text, flags=re.S)
            heading = '## ' + item['section']
            section = text.index(heading)
            beginning = text.index('\n\n', section) + 2
            following = text.find('\n\n', beginning)
            if following < 0:
                following = len(text)
            section_end = text.find('\n## ', beginning)
            section_text = text[section:section_end if section_end >= 0 else len(text)]
            item['supporting_note_ids'] = sorted(set(re.findall(r'\[\^([^]]+)\]', section_text)))
            block = (f'\n\n{start}\n\n![Ил. {int(item["id"].split("-")[1])}. '
                     f'{item["caption"]}]({item["file"]}){{width=100%}}\n\n{end}\n\n')
            source.write_text(text[:following] + block + text[following:].lstrip('\n'))
            item['integrated'] = True
            item['status'] = 'accepted_and_integrated'
            item['review'] = reviews[item['id']]
        records.append(item)
    totals = {key: sum(bool(item[key]) for item in records)
              for key in ('generated', 'visual_review', 'integrated')}
    register = {
        'version': '1.1', 'updated_utc': datetime.now(timezone.utc).isoformat(),
        'required': 34, **totals,
        'type': 'Современные художественные реконструкции, созданные с применением ИИ.',
        'rights': 'Оригинальные генерации по заданиям проекта; не музейные изображения и не '
                  'копии работ названного художника. Использование по условиям сервиса генерации; '
                  'исключительные авторские права и статус CC0 не заявляются.',
        'originals': 'Исходные PNG сохранены генератором в /workspace/generated_images; '
                     'книжные JPEG имеют исходное разрешение, качество 92–94 и цветовую субдискретизацию 4:4:4.',
        'records': records,
    }
    (ROOT / 'assets/illustrations/v1.1/register.json').write_text(json.dumps(register, ensure_ascii=False, indent=2) + '\n')
    progress_path = ROOT / 'research/progress.json'
    progress = json.loads(progress_path.read_text())
    progress.update(version='1.1', final=False, completion_state='illustrating', illustrations=totals)
    pending = [item['id'] for item in records if not item['integrated']]
    progress['next_action'] = (
        'Действует прямая директива пользователя о создании иллюстрированной версии 1.1. '
        f'Из 34 изображений фактически создано {totals["generated"]}, визуально принято '
        f'{totals["visual_review"]}, встроено {totals["integrated"]}. '
        + ('Продолжить с ' + ', '.join(pending[:6]) + '; индивидуальные задания — research/illustration_plan_v11.json. '
           if pending else 'Все 34 иллюстрации встроены; выполнить сборку и проверки версии 1.1. ')
        + 'После каждой партии обновить reviews/register, статус, commit и push. '
        'Завершить целевую научно-редакторскую правку, собрать DOCX/EPUB/PDF/ZIP 1.1 и '
        'доказать наличие всех новых изображений во всех трёх форматах. '
        'Файлы dist/final выпуска 1.0 не перезаписывать. Внешняя рецензия не блокирует '
        'эту утверждённую пользователем редакцию; новые исторические утверждения требуют источников.'
    )
    progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n')
    subprocess.run(['python', 'scripts/update_status.py'], cwd=ROOT, check=True)
    print(json.dumps(totals, ensure_ascii=False))


if __name__ == '__main__':
    main()
