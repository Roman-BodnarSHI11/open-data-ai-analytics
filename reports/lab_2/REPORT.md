# Звіт: Лабораторна робота 2

[Репозиторій проєкту](https://github.com/Roman-BodnarSHI11/open-data-ai-analytics)

---

## Тема

Побудова CI/CD-конвеєра із використанням GitHub Actions

---

## Що було практично засвоєно

- **Принципи CI/CD:** зрозумів різницю між Continuous Integration (автоматична перевірка коду при кожній зміні) та Continuous Delivery (автоматична публікація артефактів після успішного CI).
- **Синтаксис GitHub Actions:** навчився писати YAML-файли workflow — описувати тригери (`on`), джоби (`jobs`), кроки (`steps`), використовувати готові action-и з Marketplace.
- **Matrix strategy:** засвоїв запуск одного й того самого набору кроків паралельно для кількох модулів через `strategy.matrix`, що значно скорочує час виконання пайплайну.
- **Path-based filtering:** зрозумів як за допомогою `dorny/paths-filter` запускати лише ті джоби, файли яких дійсно змінились при push/PR, — це дозволяє не запускати зайві перевірки.
- **GitHub-hosted runners:** навчився запускати пайплайн на хмарних раннерах GitHub (`ubuntu-latest`) із кешуванням pip-залежностей через `actions/setup-python` з опцією `cache: "pip"`.
- **Self-hosted runners:** налаштував власний локальний раннер на MacBook (macOS ARM64), зрозумів принцип реєстрації раннера, систему лейблів та підключення його до репозиторію.
- **Artifacts (CD):** навчився зберігати результати CI (pytest-звіти, логи, графіки) як артефакти через `actions/upload-artifact`, які доступні для завантаження після кожного запуску.
- **Ізоляція середовища:** зрозумів важливість використання virtual environment (`python -m venv`) на self-hosted раннері, щоб уникати конфліктів із системно встановленими пакетами.

---

## Що було зроблено

### 1. CI-пайплайн на GitHub-hosted runner (`ci.yml`)

Створив workflow-файл `.github/workflows/ci.yml`, який:

- **Тригери:** запускається автоматично при `push` та `pull_request` до гілки `main`, а також вручну через `workflow_dispatch` з вибором конкретного модуля або `all`.
- **Джоб `detect-changes`:** використовує `dorny/paths-filter@v3` для визначення яких модулів торкнулись зміни у коді. При ручному запуску — бере вибраний модуль напряму. Результатом є JSON-масив модулів для наступного джобу.
- **Джоб `run-modules` (matrix):** для кожного модуля паралельно запускає:
  1. Checkout репозиторію
  2. Встановлення Python 3.11 із кешем pip (`actions/setup-python@v5`)
  3. Встановлення залежностей із `src/requirements.txt`
  4. Запуск `pytest` із збереженням логу
  5. Збір додаткових артефактів (для `visualization` — копіювання графіків із `reports/figures`)
  6. Публікацію артефактів через `actions/upload-artifact@v4`

Модуль `data_research` не має тестів — для нього виводиться заглушка-повідомлення замість падіння пайплайну.

### 2. CI-пайплайн на self-hosted runner (`ci-selfhosted.yml`)

Створив окремий workflow-файл `.github/workflows/ci-selfhosted.yml`:

- **Тригер:** лише `workflow_dispatch` — ручний запуск із вибором модуля.
- **Раннер:** `[self-hosted, macOS, ARM64]` — мій MacBook Pro (Apple Silicon).
- **Джоб `resolve-modules`** виконується на `ubuntu-latest` (хмара), будує JSON-масив модулів.
- **Джоб `run-on-self-hosted` (matrix):** виконується локально та:
  1. Перевіряє версію Python (`python3 --version`)
  2. Створює ізольоване virtual environment (`.venv`) для уникнення конфліктів із системними пакетами
  3. Встановлює залежності через `.venv/bin/pip`
  4. Запускає `.venv/bin/pytest` зі збереженням звіту та логу
  5. Публікує артефакти

### 3. Реєстрація self-hosted runner

Встановив та налаштував локальний GitHub Actions runner:

```bash
mkdir actions-runner && cd actions-runner
curl -o actions-runner-osx-arm64-2.332.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.332.0/actions-runner-osx-arm64-2.332.0.tar.gz
tar xzf ./actions-runner-osx-arm64-2.332.0.tar.gz
./config.sh --url https://github.com/Roman-BodnarSHI11/open-data-ai-analytics --token <TOKEN>
./run.sh
```

Раннер зареєструвався з лейблами: `self-hosted`, `macOS`, `ARM64`.

---

## Проблеми та їх вирішення

### Проблема 1: Джоб зависав у черзі на self-hosted runner

**Причина:** у workflow був вказаний лейбл `macos-latest`, тоді як реальний раннер зареєстрований з лейблом `macOS`. GitHub Actions шукає раннер, що має **всі** вказані лейбли, і не знаходив збіг.

**Рішення:** замінив `runs-on: [self-hosted, macos-latest]` на `runs-on: [self-hosted, macOS, ARM64]`.

### Проблема 2: Помилка встановлення `numpy` на self-hosted runner

**Причина:** на системному Python MacBook була встановлена стара версія numpy без RECORD-файлу (встановлена поза pip), тому pip не міг її видалити для оновлення:

```
error: uninstall-no-record-file
× Cannot uninstall numpy None
╰─> The package's contents are unknown: no RECORD file was found for numpy.
```

**Рішення:** замінив `actions/setup-python` + системний pip на створення окремого virtual environment (`.venv`). Всі команди (`pip`, `pytest`) тепер виконуються через `.venv/bin/`, що повністю ізолює CI від системних пакетів.

### Проблема 3: Повільне встановлення Python на self-hosted runner

**Причина:** `actions/setup-python` при кожному запуску намагався завантажити Python 3.11 з інтернету, оскільки ця версія відсутня на машині (є лише 3.12 через Homebrew).

**Рішення:** видалив `actions/setup-python` та перейшов на вже встановлений `python3` (3.12), що миттєво доступний без завантажень.

---

## Структура артефактів CI

Після кожного успішного запуску пайплайну у вкладці **Actions → Artifacts** доступні:

| Артефакт | Вміст |
|---|---|
| `artifacts-data_load` | `pytest-report.xml`, `pytest.log` |
| `artifacts-data_quality_analysis` | `pytest-report.xml`, `pytest.log` |
| `artifacts-visualization` | `pytest-report.xml`, `pytest.log`, графіки з `reports/figures/` |
| `selfhosted-artifacts-*` | аналогічно, але з self-hosted раннера |

---

## Вивід команди `git log --oneline --graph --all`

```
* 3a13e58 chore(ci): add virtual environment creation and update dependency installation commands in CI workflow
* 9148a66 chore(ci): enhance Python verification and streamline dependency installation in CI workflow
* ebfc1e5 chore(ci): refactor virtual environment setup and streamline dependency installation in CI workflow
* 0d17b1a chore(ci): update Python setup and dependency installation in CI workflow
* af7efd4 chore(ci): update self-hosted runner configuration to support macOS and ARM64
* 6f2ff64 chore: set up pytest configuration and add initial test files for data loading, quality analysis, and visualization
* 48040e1 chore(ci): remove pyproject.toml from CI workflow paths and add requirements.txt
* 72dc621 feat(ci): enhance module resolution and execution in CI workflows
* 9b46c51 fix(ci): improve conditional logic for module execution in CI workflow
* e20b534 fix(ci): delete path matching
* 83b4249 chore: update .gitignore to include .DS_Store
* fed8f73 ci: self-host runner
* bb65eef ci: cloud runner
* 34d32b9 refactor: project structure
| * c6c20e6 chore: set up pytest configuration and add initial test files for data loading, quality analysis, and visualization
| * 5c0f0d6 chore(ci): remove pyproject.toml from CI workflow paths and add requirements.txt
| * 2b107e9 feat(ci): enhance module resolution and execution in CI workflows
| * 4b13143 fix(ci): improve conditional logic for module execution in CI workflow
| * 126fbd7 fix(ci): delete path matching
| * e8034d7 chore: update .gitignore to include .DS_Store
| * ee1bd49 ci: self-host runner
| * dcd3fde ci: cloud runner
| * 4d9339c refactor: project structure
|/  
* 4abae9c docs: add changelog and report for lab_1
* 667e46f Update title in README.md
* f96800f feat: add data visualization
| * dda103f feat: add data visualization
|/  
* 10f5637 docs: change readme file
| * a319005 docs: change readme file
|/  
* d9de624 docs: change readme (#4)
| * 64c592c docs: change readme
|/  
* 4dcfeff feat: add data and model analysis (#3)
* 98bb0c9 feat: add exploratory data analysis (#2)
| * 4457602 feat: add data and model analysis
|/  
| * e1608fe feat: add exploratory data analysis
|/  
*   c0d6b46 Merge pull request #1 from Roman-BodnarSHI11/feature/data_load
|\  
| * a588cbc add script to load data
|/  
* 038e599 initial commit
```
