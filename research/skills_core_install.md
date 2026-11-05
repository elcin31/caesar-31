# Установка основных навыков: 2026-11-04

Установлены локально только восемь запрошенных навыков. Все репозитории и пути существовали на дату проверки. GitHub-клоны со staging-копиями находятся вне проекта. Сторонние установщики и скрипты не запускались. `$skill-installer` в доступном каталоге инструментов отсутствовал, применено ручное копирование по инструкциям README.

| Локальное имя | Репозиторий / путь | Commit | Лицензия |
|---|---|---|---|
| unslop-academic-writing | https://github.com/KalarisLabs/research-agent-skills / `skills/unslop-academic-writing` | `fa023d6d166562a8de118f59bb73647c0e444b8c` | MIT |
| citation-verification | https://github.com/KalarisLabs/research-agent-skills / `skills/citation-verification` | `fa023d6d166562a8de118f59bb73647c0e444b8c` | MIT |
| humanizer | https://github.com/hannsxpeter/humanizer / `.` | `e8f1248a7d4919689c1f942e356ed95b102d9f07` | MIT |
| academic-humanizer | https://github.com/ashgreat/humanizer / `.` | `952c8a138e29eb2cbe637b8ae8e9f6c6e2f6d627` | MIT |
| historian | https://github.com/wonsukchoi/domain-experts / `roles/historian` | `859db64cd745861e528dffc1936e9dbaf0b50ee2` | MIT |
| history-research-guide | https://github.com/wentorai/research-plugins / `skills/domains/humanities/history-research-guide` | `bf44b3cd617fa94c8a1b254c5d1987142ca3d631` | MIT |
| paper-deep-research | https://github.com/duck011002/codex-custom-skills / `skills/paper-deep-research` | `6fa6a497e601bd54039ff109ac89272b3a82b585` | UNSPECIFIED; README explicitly permits copy-install; no general redistribution license |
| paper-reviewer-check | https://github.com/duck011002/codex-custom-skills / `skills/paper-reviewer-check` | `6fa6a497e601bd54039ff109ac89272b3a82b585` | UNSPECIFIED; README explicitly permits copy-install; no general redistribution license |

## Проверка и ограничения

- Прочитаны все восемь `SKILL.md` и инструкции установки соответствующих README. Скопированы целые выбранные подкаталоги с `references`, `scripts`, `agents`, если они присутствовали; корневые библиотеки целиком не устанавливались.
- MIT-лицензии сохранены; уведомления Kalaris `THIRD_PARTY_NOTICES.md` также сохранены. В выбранных Kalaris навыках оригинальное авторство Kalaris Labs; дополнительные библиотеки и копирование всего каталога LICENSES не нужны.
- `duck011002/codex-custom-skills` не содержит LICENSE. Его README прямо предлагает копирование выбранных каталогов в `.agents/skills`; это обосновывает локальную установку, но не общую лицензию распространения. Две копии не следует включать в публичный дистрибутив без отдельного разрешения; SHA и ссылки позволяют воспроизвести установку.
- `humanizer` (hannsxpeter) сохранён под оригинальным именем. `humanizer` (ashgreat) установлен как `academic-humanizer`; изменено только поле `name` в YAML. Неизменённый исходный текст лежит рядом в `SOURCE_SKILL.md`. Повторяющихся имён навыков нет.
- Метаданные compatibility/allowed-tools у ashgreat ориентированы на Claude/OpenCode; сами Markdown-инструкции читаются Codex вручную, инструментальные имена адаптируются к доступным средствам. Нельзя утверждать, что устанавливался отдельный MCP-сервис или новый плагин.
- Исторические примеры historian, связанные с США, National Register и oral history, для античного Рима неприменимы. Используются общие правила внешней/внутренней критики, независимости свидетельств, периодизации и отделения фактов от интерпретации.
- У `paper-deep-research` нет обязательной зависимости от dzhng/deep-research: при его отсутствии прямо допускаются веб-поиск, локальные PDF и BibTeX. Внешний агент, Firecrawl и ключи API не устанавливались.
- `paper-reviewer-check` не имеет программных зависимостей; экспериментальные и acceptance-oriented пункты адаптируются к научной исторической монографии.
- `unslop-academic-writing` и `citation-verification`: Python 3.9+, только стандартная библиотека. Скрипты разобраны AST: сторонних импортов, subprocess, eval/exec и команд оболочки нет. Полный запуск отложен до отдельной проверки исходников. Первый скрипт читает локальный текст/ZIP DOCX; второй обращается к Crossref/OpenAlex/arXiv и пишет JSON по явно заданному пути.
- Русскую прозу нельзя оценивать англоязычными порогами slop_check или detect_ai. В slop_check подсчёт слов явно ограничен `[A-Za-z]`; автоматический индекс для русской рукописи методологически непригоден. Редакторские принципы применяются вручную, без оптимизации под AI-детекторы.
- DOI-проверка не заменяет сверку книг и античных локаторов. Ссылки на первоисточники проверяются вручную по выбранному изданию.

## Активация в текущем сеансе

Codex обнаружит `.agents/skills/<name>/SKILL.md` при следующем обновлении каталога. В текущем сеансе навыки уже доступны как локальные инструкции: читать соответствующий `SKILL.md` и необходимые references, явно сообщив пользователю об использовании. Нельзя обещать динамическую регистрацию в интерфейсе без перезапуска.

Постоянно применяются `historian`, `history-research-guide`, `paper-deep-research`, `citation-verification`, `unslop-academic-writing`. `humanizer`, `academic-humanizer`, `paper-reviewer-check` применяются по этапам отдельно; не следует одновременно механически суммировать их стилистические предписания.

При конфликте user instruction > skill. Например, запрет ashgreat на любые em dash не переносится механически на русское именное сказуемое; требование точности, термины и необходимые смысловые оговорки сохраняются. Требование hannsxpeter о чат-формате отчёта редактора относится к отчёту, а не к книжной рукописи.

Полные SHA-256 файлов: `research/skills_core_manifest.json`. Ни один сторонний скрипт в ходе установки не выполнялся.
