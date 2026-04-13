# Перелік місць доставки

This project analyzes delivery location data to optimize logistics while applying DevOps practices (Git, CI/CD via GitHub/GitLab Actions, Docker, Kubernetes) learned in the "Development Environment and Components in Data Modeling and Analysis" course .

## Мета

Build an automated, containerized data analysis pipeline using modern DevOps tools to extract actionable logistical insights.

## Questions & hypotheses

1. Which locations on the list have the highest order density and are the most profitable?

2. How do delivery efficiency metrics (time and cost) vary by region or city?

3. Are there noticeable trends in demand for certain delivery locations over time?

## Dataset

[Перелік місць доставки](https://data.gov.ua/dataset/ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb)

---

## Контейнерна архітектура (Docker)

Сервіси описані в [`compose.yaml`](compose.yaml). Мережа `analytics` (bridge) з’єднує усі контейнери. Постійні дані зберігаються в іменованих томах:

| Том | Призначення |
|-----|-------------|
| `postgres_data` | Файли PostgreSQL |
| `pipeline_data` | Спільний каталог CSV (`/data/raw`) для завантаження та аналізу |
| `pipeline_reports` | Звіти якості, дослідження та PNG-графіки (`/reports`) |

**Обмін даними:** CSV і графіки — через спільний том; метадані імпорту та табличні дані — у PostgreSQL (таблиці на кожен CSV + службова `pipeline_meta`).

### Сервіси

| Сервіс | Dockerfile | Роль |
|--------|-------------|------|
| `db` | образ `postgres:16-alpine` | База даних |
| `data_load` | [`docker/data_load/Dockerfile`](docker/data_load/Dockerfile) | Завантаження з CKAN (за бажанням), копія демо-CSV, імпорт CSV у БД |
| `data_quality_analysis` | [`docker/data_quality_analysis/Dockerfile`](docker/data_quality_analysis/Dockerfile) | JSON-звіт якості у `/reports/quality/` |
| `data_research` | [`docker/data_research/Dockerfile`](docker/data_research/Dockerfile) | Зведений Markdown з вибірок БД у `/reports/research/` |
| `visualization` | [`docker/visualization/Dockerfile`](docker/visualization/Dockerfile) | Побудова графіків у `/reports/figures/` |
| `web` | [`docker/web/Dockerfile`](docker/web/Dockerfile) | Веб-інтерфейс (Flask) на порту **8080** |

### Запуск (Docker Workspace / локально)

Потрібні [Docker Engine](https://docs.docker.com/engine/install/) та [Docker Compose V2](https://docs.docker.com/compose/).

```bash
docker compose up --build
```

Після успішного проходження одноразових job-контейнерів працює лише `web` (і `db`). Відкрийте в браузері:

**http://localhost:8080**

Там відображаються таблиці в `public`, журнал імпорту (`pipeline_meta`) та посилання на файли з `/reports`.

Зупинка:

```bash
docker compose down
```

Повне очищення томів (видалить БД і згенеровані артефакти):

```bash
docker compose down -v
```

### Змінні середовища

| Змінна | Опис |
|--------|------|
| `SKIP_DOWNLOAD` | Якщо `1` / `true` — не викликати CKAN, лише CSV з тому (`data_load`) |
| `PIPELINE_DATA_DIR` | Каталог пошуку CSV (у compose: `/data/raw`) |
| `REPORTS_DIR` | Корінь звітів (у compose: `/reports`) |
| `DATABASE_URL` | Рядок підключення SQLAlchemy, напр. `postgresql+psycopg2://analytics:analytics@db:5432/analytics` |
| `FIGURES_DIR` | Каталог для PNG (у compose: `/reports/figures`) |

### Локальна розробка (без Docker)

```bash
cd src
pip install -r requirements.txt
export PYTHONPATH=.
python -m data_load.pipeline   # потрібен доступний PostgreSQL
```

---

## Структура модулів (Python)

- `data_load` — завантаження та [`db_import`](src/data_load/db_import.py) (CSV → PostgreSQL).
- `data_quality_analysis` — аналіз якості ([`pipeline.py`](src/data_quality_analysis/pipeline.py)).
- `data_research` — звіти з БД ([`pipeline.py`](src/data_research/pipeline.py)).
- `visualization` — графіки Matplotlib/Seaborn.
- `web` — Flask-додаток ([`app.py`](src/web/app.py)).
