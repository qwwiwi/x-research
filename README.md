# x-research

Скилл для Claude Code: поиск по X (Twitter) из терминала через xAI Grok Live Search.

Скрипт `x_search.py` вызывает встроенный инструмент `x_search` в xAI Responses API. Grok сам ищет по X на стороне сервера и возвращает сводный ответ со ссылками на исходные посты. Без cookies, без скрейпинга, без MCP.

## Что делает

- Отвечает на вопрос по теме: «что обсуждают про AI-агентов за две недели».
- Ограничивает поиск списком аккаунтов (`--handles`) и окном дат (`--from`, `--to`).
- Исключает аккаунты (`--exclude`), умеет разбирать картинки и видео в постах (`--images`, `--videos`).
- Отдаёт сырой JSON (`--json`) для сборки отчётов.
- Содержит пример вотчлиста публичных AI-аккаунтов и сценарий еженедельного радара.

## Что нужно

- Python 3.9+ (только стандартная библиотека).
- Ключ xAI API: [console.x.ai](https://console.x.ai). Запросы расходуют квоту твоего аккаунта xAI.

## Установка

Через skills CLI:

```bash
npx skills add https://github.com/qwwiwi/x-research --skill x-research
```

Вручную:

```bash
git clone https://github.com/qwwiwi/x-research
mkdir -p ~/.claude/skills
cp -R x-research/skills/x-research ~/.claude/skills/x-research
```

Ключ:

```bash
export XAI_API_KEY="..."     # или файл ~/.config/x-research/xai.key (путь меняется через XAI_KEY_FILE)
```

## Как пользоваться

Попроси агента: «посмотри, что пишут в X про Claude Code skills за последнюю неделю». Либо запусти сам:

```bash
SK=~/.claude/skills/x-research/scripts/x_search.py

python3 $SK "что нового по AI agents за последние две недели"
python3 $SK "Claude Code skills and subagents" --handles karpathy,simonw,bcherny --from 2026-06-03
python3 $SK "AI agent funding rounds" --json
```

Флаги: `--handles a,b,c`, `--exclude a,b`, `--from YYYY-MM-DD`, `--to YYYY-MM-DD`, `--model`, `--images`, `--videos`, `--json`.

Модель по умолчанию – `grok-4.20-reasoning`. Она настраивается флагом `--model` или переменной `XAI_MODEL`: если xAI переименует модель, подставь актуальный id.

## Пример

```bash
python3 $SK "Claude Code subagents: главные приёмы" --handles bcherny,trq212,steipete --from 2026-06-01
```

На выходе – сводка обсуждения и блок «Источники (X)» со ссылками на посты.

## Вотчлист

`skills/x-research/references/watchlist.md` – пример списка публичных аккаунтов. Замени на авторов своей ниши. xAI ограничивает число аккаунтов в одном запросе, поэтому обходи список пачками по 10–15.

## Ограничения

- Сложный запрос идёт 60–120 секунд (таймаут 200 секунд).
- Grok пересказывает обсуждение в X – это «что говорят», а не проверенные факты. Проверяй перед публикацией.
- Нужен ключ xAI; лимиты и стоимость зависят от твоего аккаунта.

## Лицензия

MIT.
