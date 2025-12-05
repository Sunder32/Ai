# Структура проекта

Ниже — карта папок и кратко «зачем это». Проект состоит из двух стеков (FastAPI+Ollama и Django+React) и набора данных/скриптов рядом.

## Текущее расположение
- `.venv/` — локальное Python‑окружение.
- `server/` — FastAPI API под DeepSeek/Ollama (`main.py`, RAG/learning движки, подготовка датасета).
- `client/` — статический фронт под FastAPI API (простая страница чата/загрузок).
- `Modelfile`, `Modelfile.finetune`, `start_server.bat`, `start_with_tunnel.bat`, `install*.bat`, `setup_network.bat` — всё для запуска и обучения через Ollama.
- `dataset.jsonl`, `training_data.txt`, `uploads/`, `learning_data/`, `rag_index/`, `ollama_data/` — рабочие данные FastAPI‑стека (логи диалогов, загруженные файлы, индекс RAG, дамп Ollama).
- `frontend/` — React (CRA + Tailwind/Three/GSAP) фронт для конфигуратора ПК.
- `project/` — Django + DRF backend (аккаунты, компоненты ПК, рекомендации).
- `Ai/` — копия документации/скриптов старой ревизии.
- `Tasks/` — список задач/этапов.
- `config.yml`, `cloudflared.exe`, `get_my_ip.bat` и др. — утилиты и конфиги инфраструктуры.

## Предлагаемая группировка (чтобы не путаться)
Если будем наводить порядок, можно свернуть так:
```
apps/
  fastapi/           (бывш. server/ + Modelfile* + start_server.bat + start_with_tunnel.bat)
  fastapi-client/    (бывш. client/)
  django/            (бывш. project/ + manage.py + requirements.txt)
  react-configurator/(бывш. frontend/)
data/
  ollama/            (бывш. ollama_data/)
  rag/               (бывш. rag_index/)
  learning/          (бывш. learning_data/)
  uploads/           (бывш. uploads/)
  datasets/          (dataset.jsonl, training_data.txt)
infra/
  cloudflared/       (cloudflared.exe, install_cloudflared.bat, config.yml, setup_network.bat)
scripts/             (install.bat, get_my_ip.bat, прочие служебные .bat)
docs/                (README.md, ARCHITECTURE.md, Tasks/)
legacy/              (Ai/)
```
Переезд лучше делать отдельным коммитом, обновив пути в скриптах/конфигах.

## Быстрые шпаргалки по стекам
- FastAPI + Ollama: `start_server.bat` (поднимает API на 5050), UI — `client/index.html`. Модели/датасеты — в корне (Modelfile*, dataset.jsonl) и `rag_index/`, `learning_data/`, `uploads/`.
- Django + DRF: `cd project && python manage.py runserver` (env из `project/.env.example`), база SQLite внутри `project/`.
- React (конфигуратор): `cd frontend && npm start` (env из `frontend/.env.example`).

## Что сейчас стоит починить
- README и Tasks в корне вбитой кодировкой — лучше пересохранить в UTF‑8 и оставить ссылку на эту схему.
- Если оставляем только один стек, остальные можно убрать в `legacy/` или удалить, чтобы корень очистить.
