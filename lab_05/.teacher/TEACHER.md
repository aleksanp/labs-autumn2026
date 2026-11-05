# Лабораторная работа № 5 — описание для преподавателя

Файл объясняет, **что происходит в ноутбуках** лаборатории, как её вести и что проверять у студентов.

Студентам выдаются `dvc_exercises.ipynb` и `liquibase_exercises.ipynb`; преподаватель работает с референтными `dvc_solutions.ipynb` и `liquibase_solutions.ipynb`. Структура ячеек в парах **идентична** — различаются только ячейки с задачами (в solutions под пометкой `# YOUR CODE` написано решение, в exercises — плейсхолдер).

## Окружение

Все сервисы поднимаются одной командой из папки `lab_05`: `docker compose up -d`.

| Сервис | Образ | Назначение | Доступ |
|--------|-------|-----------|--------|
| gitlab | `gitlab/gitlab-ce:17.6.0-ce.0` | Remote для git-репозиториев ноутбуков | `http://localhost:8081`, `root` / `EducationLab!` |
| postgres | `postgres:13` | БД для части 2 | `localhost:5432`, `postgres` / `postgres` |
| liquibase | `liquibase:4.30.0` | Миграции схемы БД, запуск по требованию | `docker compose run --rm liquibase <команда>` |

Томы `gitlab_config`, `gitlab_logs`, `gitlab_data` сохраняют состояние GitLab между перезапусками; папка `./liquibase_project` монтируется в контейнер liquibase как рабочая директория changelog'ов. Поднимать окружение **нужно до** запуска ноутбуков: `dvc push`/`git push` и команды liquibase без него не выполнятся.

---

## Часть 1. Git + DVC

### Что происходит в `dvc_solutions.ipynb` (по этапам)

**1. Подготовка и теория.**
- `!uv add -q dvc` — устанавливает DVC в окружение uv; следующие ячейки — только проверки версий.
- `hostname -I` — IP машины, по которой студенты открывают GitLab из браузера.
- Студент **вручную** создаёт в GitLab проект `mlops-logistics-lab05` (blank, public, без README) — шаги описаны в markdown-ячейке. Следующая код-ячейка показывает, откуда берутся параметры remote, и формирует `git_remote_url` с встроенными логином и паролем (`EducationLab!` → URL-кодирование `EducationLab%21`).
  - *Что обсудить:* встраивание пароля в URL — учебное упрощение; в реальных проектах используют Personal Access Tokens или SSH-ключи.
- Далее — теоретические блоки: роль Git в ML-проекте и принцип работы DVC (Git — код и метаданные `.dvc`, кэш — данные, remote — «облако»).

**2. Первая версия данных.**
- Запрос `SELECT * FROM data_lab02_prepared LIMIT 12000` к SQLite-БД лабораторной №2 → `df`.
- Ручной split: `train_df = df[:11000]`, `val_df = df[11000:]` (11 000 / 1 000 строк) → `data/train.csv`, `data/validation.csv`.

**3. Инициализация версионирования.**
- `git init` + `git branch -M main` + `git remote add origin http://root:EducationLab%21@127.0.0.1:8081/root/mlops-logistics-lab05.git`.
- `dvc init` — создаётся папка `.dvc/` (`config` + `.gitignore`); `ls -la .dvc/` — показываем.
- `dvc add data/train.csv data/validation.csv` — для каждого CSV появляется файл `*.csv.dvc` (метаданные: md5-хэш, размер), сами CSV попадают в `.gitignore`. `cat data/validation.csv.dvc` — показываем содержимое метаданных.
- `git add data/*.csv.dvc` — в Git под готовятся **только метаданные**.
- `mkdir storage` + `dvc remote add -d storage "$(realpath storage)"` — remote DVC это локальная папка (аналог облака); `cat .dvc/config` — показываем, что появилось в конфиге.

**4. «first experiment».**
- `dvc push` — данные копируются в `storage/` в виде хеш-дерева; `tree storage/` — показываем.
- `git commit -m 'first experiment'` + `git push --set-upstream origin main`.
  - *Что будет видно в GitLab:* в репозитории только два файла — `data/train.csv.dvc` и `data/validation.csv.dvc` (CSV туда не попадают, они в `.gitignore`). Хороший момент показать это в браузере.
  - Перед коммитом — подсказка про `git config --global user.name/email` (в ноутбуке закомментирована; без неё `git commit` упадёт с «Please tell me who you are»).

**5. «second experiment» (самостоятельная часть; в solutions код заполнен).**
- Загружается **вся** таблица лабораторной №2 (без LIMIT) → `train_df = df[:-2000]`, `val_df = df[-2000:]`; датасеты примерно на порядок больше первых.
- Пересоздаются `data/train.csv` и `data/validation.csv`; `dvc add` — md5 в `.dvc`-файлах изменились; `git add` — метаданные в Git; `dvc push` — в `storage/` появляются хеши новой версии (старые не удаляются — обе версии данных доступны); `git commit -m 'second experiment'`; `git push`.

**6. Проверка версионирования (ключевой момент лабораторной).**
- `git log` — видны два коммита; хэши берутся из вывода.
- `git checkout <hash first experiment>` + `dvc checkout` → `data/*.csv` восстанавливаются в виде первого эксперимента: `print` показывает 11 000 / 1 000 строк.
- `git checkout <hash second experiment>` + `dvc checkout` → большие датасеты возвращаются.
- *Вывод для студентов:* пара команд `git checkout` + `dvc checkout` воссоздаёт данные любого исторического эксперимента; сами данные в Git не хранятся — только их метаданные.

### Задачи студентов в `dvc_exercises.ipynb`

| # | Задача (markdown-ячейка) | Что пишет студент |
|---|--------------------------|-------------------|
| 1 | Загрузить всю таблицу лабы №2 в `df` | `engine = create_engine(f'sqlite:///{DB_PATH}')` и `df = pd.read_sql_query(query, engine)` |
| 2 | Пересоздать `data/train.csv` и `data/validation.csv` | `train_df.to_csv('data/train.csv')`, `val_df.to_csv('data/validation.csv')` |
| 3 | Добавить данные в DVC | `!dvc add data/train.csv data/validation.csv` |
| 4 | Добавить метаданные в Git | `!git add data/train.csv.dvc data/validation.csv.dvc` |
| 5 | Отправить данные в хранилище | `!dvc push` |
| 6 | Откатиться к «first experiment» | `!git checkout <hash>` |
| 7 | Вернуться к «second experiment» | `!git checkout <hash>` |

Ячейки-«скрепы» после задач (не задачи): `git commit -m "second experiment"`, `git push`, `dvc checkout` и чтение CSV с `print` количества строк — это **встроенная самопроверка**: после отката к первому эксперименту студент видит 11 000 / 1 000 строк, после возврата к второму — полный размер таблицы.

### Критерии проверки (часть 1)

- [ ] Проект `mlops-logistics-lab05` создан в GitLab; в ветке `main` два коммита: `first experiment`, `second experiment`.
- [ ] В репозитории есть `data/*.csv.dvc` и **нет** `data/*.csv`.
- [ ] В `storage/` присутствуют обе версии данных (хеш-дерево, `dvc status`).
- [ ] Откат к первому эксперименту работает: после `git checkout` + `dvc checkout` в `data/train.csv` 11 000 строк; после возврата к второму — больше.
- [ ] Студент объясняет: что хранится в `.dvc`-файле (md5 + размер), почему CSV не в Git, чем `dvc checkout` отличается от `git checkout`.

### Типичные проблемы (часть 1)

| Симптом | Причина / решение |
|---------|-------------------|
| `git commit`: «Please tell me who you are» | не заданы `git config user.name/user.email` — подсказка в ноутбуке |
| `git push`: «repository not found» / 401 | неверное имя проекта в GitLab (нужно в точности `mlops-logistics-lab05`) или неверные логин/пароль/порт |
| `No such file or directory: '../lab_02/...'` | ядро Jupyter запущено не из папки `lab_05` или нет БД лабы №2 |
| `dvc add`: файл отслеживается Git | CSV случайно добавили в Git — `git rm --cached data/...` |
| `dvc push`: «No remote config» | пропущен шаг `dvc remote add -d storage ...` |
| `git checkout <hash>`: «pathspec did not match» | хэш скопирован не полностью или с лишними символами |
| Повторный запуск лабы | удалить `.git/`, `.dvc/`, `data/`, `storage/`, `liquibase_project/`, проект в GitLab и данные БД (или `docker compose down -v`) |

---

## Часть 2. Liquibase

### Что происходит в `liquibase_solutions.ipynb` (по этапам)

**1. Введение и теория.**
- Шапка «Лабораторная работа № 5, Часть 2», цель, план «Что мы будем делать» (4 пункта), таблица «Окружение и файлы».
- `!uv add -q psycopg2-binary` — драйвер PostgreSQL для запросов `pd.read_sql` в конце ноутбука.
- Теория: changelog (файл миграций: `.sql`/`.xml`/`.yaml`/`.json`), changeset (`--changeset <автор>:<id>`), учётная таблица `DATABASECHANGELOG`, команды `update` / `rollback` / `status` / `validate`.

**2. Проект и подключение (шаги 1–2 ноутбука).**
- `mkdir -p liquibase_project` — папка проекта; по `docker-compose.yaml` она смонтирована в контейнер liquibase как рабочая директория `/liquibase/changelog`.
- `liquibase.properties` — `url`, `username`, `password`; дальше любая команда получает `--defaultsFile=liquibase.properties` вместо повторения параметров подключения.

**3. Первая миграция (шаг 3).**
- `changelog.sql` — один changeset `user:student`: `CREATE TABLE route_table (start_station INT NOT NULL, finish_station INT, PRIMARY KEY (start_station))`.
- `liquibase status` → «1 changeset has not been applied to postgres» (ожидаемо, `update` ещё не запускали; при первом обращении Liquibase сам создаёт учётные таблицы).
- `liquibase update` → «Liquibase: Update has been successful». Проверки: `SELECT * FROM route_table` (пустая таблица, 2 колонки) и `SELECT * FROM databasechangelog` (одна строка changeseta).

**4. Вторая миграция и откат по счётчику (шаг 5).**
- `add_column.sql` — `ALTER TABLE route_table ADD COLUMN distance INT` **плюс инструкция `--rollback`** (`DROP COLUMN distance`).
- `liquibase update --changelog-file=add_column.sql` → 3 колонки; в `databasechangelog` вторая строка.
- `liquibase rollback-count --count=1 --changelog-file=add_column.sql` → колонка удалена, осталось 2; строка об этом changesete исчезла из `databasechangelog`.
- *Что обсудить:* без `--rollback` changeset нельзя откатить — Liquibase упадёт с ошибкой; изменения описываются декларативно, а не «в лоб».

**5. Самостоятельная часть (в solutions код заполнен; в exercises — 5 задач).**
- `new_add_columns.sql` — один changeset: `ADD COLUMN distance INT` + `ADD COLUMN region VARCHAR(255)` и **две** `--rollback DROP COLUMN` (в обратном порядке). `liquibase update` → 4 колонки.
- `add_row.sql` — один changeset: `INSERT INTO route_table (start_station, finish_station, distance, region) VALUES (100500, 200600, 100, 'RF')` + `--rollback DELETE ...`. `liquibase update` → в таблице 1 строка.
- `rollback-to-date --date=<дата> --changelog-file=new_add_columns.sql` — в референтном решении дата берётся программно: `date.today()` (любая дата, **раньше** даты наката миграций).

**Проверенный нюанс (проверено по исходникам Liquibase 4.30.0).** `rollback-to-date` откатывает только changeset'ы тех файлов, которые переданы в `--changelog-file` — здесь это лишь changeset колонок из `new_add_columns.sql`. **Запись из `add_row.sql` остаётся в таблице** (её changeset лежит в другом файле), её строка остаётся и в `databasechangelog`. Итоговое состояние после задачи 5: 2 колонки, 1 строка. Чтобы откатить и запись, добавляют во команду второй файл: `--changelog-file=add_row.sql` — хороший момент разобрать, как `--changelog-file` ограничивает область любого rollback-команды.

### Задачи студентов в `liquibase_exercises.ipynb`

| # | Задача (markdown-ячейка) | Что пишет студент |
|---|--------------------------|-------------------|
| 1 | Создать `new_add_columns.sql` (2 колонки + `--rollback`) | `write_text` с changeset'ом: два `ALTER TABLE route_table ADD COLUMN ...` и два `--rollback ... DROP COLUMN ...` (в обратном порядке) |
| 2 | Накатить миграцию | `!docker compose run --rm liquibase update --changelog-file=new_add_columns.sql --defaultsFile=liquibase.properties` |
| 3 | Создать `add_row.sql` (1 валидная запись + `--rollback`) | `write_text` с changeset'ом: `INSERT INTO route_table ... VALUES (...)` и `--rollback DELETE ...` |
| 4 | Накатить миграцию | `!docker compose run --rm liquibase update --changelog-file=add_row.sql --defaultsFile=liquibase.properties` |
| 5 | Откат к указанной дате | `!docker compose run --rm liquibase rollback-to-date --date=<YYYY-MM-DD> --changelog-file=new_add_columns.sql --defaultsFile=liquibase.properties` |

Ячейки-«скрепы» после задач (`SELECT * FROM route_table` с пометкой «Проверим результат») — это **встроенная самопроверка**: после задачи 2 — 4 колонки, после задачи 4 — 1 строка, после задачи 5 — 2 колонки (запись из `add_row.sql` при этом остаётся — см. нюанс выше; на неё указывает финальный вопрос в конце ноутбука).

### Критерии проверки (часть 2)

- [ ] `route_table` существует; в `databasechangelog` виден changeset создания таблицы.
- [ ] Самостоятельные миграции накатились: после задач 2 и 4 — 4 колонки и 1 строка.
- [ ] После `rollback-to-date` — 2 колонки; строка changeseta `new_add_columns.sql` удалена из `databasechangelog`.
- [ ] Студент объясняет: зачем нужна `--rollback`; что учитывает `rollback-to-date` (только файлы из `--changelog-file`) и почему запись из `add_row.sql` осталась (и как её откатить).

### Типичные проблемы (часть 2)

| Симптом | Причина / решение |
|---------|-------------------|
| Ошибка при `update`: ошибка SQL в changesete | опечатка в SQL — читать текст ошибки Liquibase |
| `Rollback failed`: changeset cannot be rolled back | в файле миграции нет `--rollback`-описания |
| `rollback-to-date`: «0 changesets rolled back» | дата не раньше даты наката миграций (дату указали на будущее) |
| `Connection refused` к postgres | контейнер не поднят / не готов: `docker compose ps`, `docker compose logs postgres` |
| Команда liquibase долго «висит» | первый раз поднимается контейнер; подождать |

---

## Сброс окружения для новой группы/зачёта

```bash
cd ~/labs/lab_05
docker compose down -v                          # контейнеры + именованные томы (GitLab, Postgres)
rm -rf .git .dvc data storage liquibase_project # артефакты ноутбуков
```

После `down -v` GitLab поднимается заново (снова 3–5 минут), проект `mlops-logistics-lab05` придётся создать заново.
