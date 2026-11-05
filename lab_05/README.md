# Лабораторная работа № 5. Версионирование кода и данных

## Краткое описание

В ходе работы настраиваем версионирование трёх артефактов ML-проекта — **кода**, **данных** и **схемы базы данных**. Лабораторная работа состоит из двух частей:

| Часть | Студенческий ноутбук | Что делаем | Инструменты |
|-------|----------------------|------------|-------------|
| **1. Git + DVC** | `dvc_exercises.ipynb` | Версионируем датасеты: Git хранит код и метаданные, DVC — сами данные в хранилище. Публикуем эксперименты в GitLab CE и откатываемся к прошлым версиям | Git, DVC, GitLab CE, SQLite |
| **2. Liquibase** | `liquibase_exercises.ipynb` | Версионируем схему PostgreSQL: описываем изменения как миграции (changeset'ы), накатываем и откатываем их | Liquibase, PostgreSQL, Docker |

> Используются данные из БД лабораторной №2

## Подготовка

> При вводе команд `sudo` потребуется пароль от системы.

### 1. Устанавливаем Docker

```bash
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl tree
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
```

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# Ввести пароль и согласиться 'Y'
```

```bash
# Запускаем docker
sudo systemctl start docker
```

```bash
# Проверяем, что всё успешно установлено
sudo docker run hello-world
# Увидим "Hello from Docker! ..."
```

### 2. Устанавливаем Git

```bash
sudo apt install git
```

### 3. Запускаем окружение лабораторной (GitLab, PostgreSQL, Liquibase)

```bash
# Переходим в папку с лабой
cd ~/labs/lab_05

# Перезапускаем докер и разворачиваем окружение
sudo systemctl restart docker && docker compose up -d
```

Поднимается три сервиса:

- **GitLab CE** — `http://localhost:8081`, логин `root`, пароль `EducationLab!`. Первый запуск занимает до 3–5 минут (логин/пароль из `docker-compose.yaml`).
- **PostgreSQL 13** — `localhost:5432`, пользователь `postgres` (часть 2).
- **Liquibase** — не запускается постоянно, поднимается по требованию из ноутбука: `docker compose run --rm liquibase <команда>`.

Конфигурация окружения: `docker-compose.yaml` — рабочий файл, `description.docker-compose.yaml` — тот же файл с подробными комментариями для изучения.

### 4. Запускаем Jupyter

```bash
cd ~/labs
uv run jupyter notebook
```

В браузере открываем папку `lab_05`, выбираем ядро **`Python 3.11 (labs)`** и начинаем с `dvc_exercises.ipynb`.

## Ход работы

### Часть 1. Git + DVC — [`dvc_exercises.ipynb`](dvc_exercises.ipynb)

1. Открываем GitLab (`http://localhost:8081`, `root` / `EducationLab!`) и создаём проект **`mlops-logistics-lab05`** (blank project, public, без README).
2. Загружаем 12000 строк из БД лабораторной №2 и готовим первую версию датасетов: `data/train.csv`, `data/validation.csv`.
3. Инициализируем `git` и `dvc`, добавляем датасеты под контроль DVC, настраиваем локальное хранилище `storage/` и делаем `dvc push`.
4. Публикуем коммит **«first experiment»** в GitLab.
5. **Самостоятельная работа (7 задач):** загружаем всю таблицу, готовим вторую, более крупную версию датасетов, версионируем её (`dvc add` → `git add` → `dvc push`) и публикуем **«second experiment»**.
6. Проверяем версионирование: `git checkout <hash>` + `dvc checkout` откатывают данные к первому эксперименту, затем возвращают обратно — и мы видим, как меняется размер файлов в `data/`.

### Часть 2. Liquibase — [`liquibase_exercises.ipynb`](liquibase_exercises.ipynb)

1. Создаём папку `liquibase_project/`, файл подключения `liquibase.properties` и первую миграцию `changelog.sql` (создание таблицы `route_table`).
2. Проверяем `liquibase status`, накатываем `liquibase update`, смотрим таблицу и учётную таблицу `databasechangelog`.
3. Добавляем вторую миграцию `add_column.sql` (колонка + инструкция `--rollback`), накатываем и откатываем последним changeset'ом `rollback-count`.
4. **Самостоятельная работа (5 задач):** создаём две миграции — две колонки (`new_add_columns.sql`) и одна запись (`add_row.sql`), накатываем их и откатываемся к указанной дате командой `rollback-to-date`; смотрим, что произошло с новыми колонками и с записью.

> Все команды Liquibase выполняются через контейнер: `!docker compose run --rm liquibase ...`.

## Файлы лаборатории

| Файл | Назначение |
|------|-----------|
| `dvc_exercises.ipynb` | Часть 1 |
| `liquibase_exercises.ipynb` | Часть 2 |
| `docker-compose.yaml` | Конфигурация окружения (GitLab, PostgreSQL, Liquibase) |
| `description.docker-compose.yaml` | То же с подробными комментариями |

## Частые проблемы

- **GitLab долго не открывается.** Первый запуск контейнера занимает время: посмотрите `docker compose logs gitlab`.
- **Ошибка при `git commit`: «Please tell me who you are».** Задайте имя и почту: `git config --global user.name "..."` и `git config --global user.email "..."` (подсказка есть в ноутбуке).
- **`git push` не находит репозиторий / отвечает 401.** Название проекта в GitLab должно быть в точности `mlops-logistics-lab05`; проверьте логин/пароль и порт (8081).
- **Файл `../lab_02/...` не найден.** Ноутбук должен запуститься из папки `lab_05`, а база лабораторной №2 — быть уже создана.
- **`dvc add`: файл уже отслеживается Git.** CSV-файлы не должны попадать в Git — `git rm --cached data/...`, проблема в том, что файл добавили в Git вручную.
- **Заново запускаете лабораторную.** Удалите созданные артефакты: папки `.git/`, `.dvc/`, `data/`, `storage/`, `liquibase_project/`, проект `mlops-logistics-lab05` в GitLab и содержимое PostgreSQL (или `docker compose down -v`), затем начните ноутбуки заново.
- **Занимает много места кэш DVC.** Кэш находится в `~/.dvc/cache`; освободить место: `dvc gc`.
