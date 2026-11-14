# Лабораторная работа № 6. Конвейер машинного обучения: Airflow + DVC + MLflow

## Краткое описание

В ходе работы настраиваем конвейер машинного обучения на **Apache Airflow**: извлечение данных из SQLite-базы лабораторной № 2, запуск **DVC**-пайплайна (split → train → validate), версионирование экспериментов в **Git** (GitLab из лабораторной № 5) и логирование обучений в **MLflow**. Студенческая работа ведётся в одном ноутбуке и состоит из трёх частей:

| Часть | Что делаем | Инструменты |
|-------|------------|-------------|
| **1. Основы Airflow** | Создаём первый DAG: задача выгружает 5000 строк из базы лабы № 2 в CSV и запускается из UI Airflow | Airflow, PythonOperator |
| **2. Airflow + DVC** | Присоединяем DVC-пайплайн к DAG из пяти задач (download → dvc repro → dvc add → git commit → git tag), переобучаем модель, меняя параметры в `params.yaml`, публикуем коммиты в GitLab | Airflow, DVC, Git, GitLab CE |
| **3. Airflow + MLflow** | DAG обучает модель и логирует запуск в MLflow: параметры, метрики, модель; разбираем эксперимент в UI | Airflow, MLflow |

> Используются данные (SQLite-база) из лабораторной № 2 и GitLab из лабораторной № 5.

## Что нужно до начала работы

- Выполнена **лабораторная № 2**: её база `lab_02/data/db/data_lab02_prepared.db` — источник данных.
- Выполнена **лабораторная № 5**: 
  - развёрнут GitLab CE (`http://localhost:8081`, логин `root`, пароль `EducationLab!`).
  - Установлен Docker


## Ограничение ресурсов (важно)

Airflow и GitLab — самые «тяжёлые» сервисы курса: вместе занимают ~6–7 ГБ RAM.
В WSL2 память ограничена — следите за свободной памятью (`free -h`). Если не
хватает, GitLab можно временно остановить (`cd ~/labs/lab_05 && docker compose stop`):
он нужен только в момент создания проекта и `git push`.

## Подготовка

### 1. Поднимаем GitLab (из лабы № 5)

```bash
# Если GitLab останавливали или удаляли в 5-й лабораторной
cd ~/labs/lab_05
docker compose up gitlab -d
```

Ждём 1–2 минуты. Заходим на `http://localhost:8081` (`root` / `EducationLab!`)
и создаём новый пустой проект **`mlops-logistics-lab06`**:
*Create new project* → Pick a group or namespace: `root` → снимаем галку
*Project Configuration* (без README и остальных файлов) → *Create project*.

### 2. Создаём файл `.env`

```bash
# Переходим в папку с лабораторной
cd ~/labs/lab_06

# UID/GID вашего пользователя (иначе Airflow не сможет работать с локальными папками)
printf "AIRFLOW_UID=%s\nAIRFLOW_GID=%s\n" "$(id -u)" "$(id -g)" > .env
# Пользователь UI Airflow
echo "_AIRFLOW_WWW_USER_USERNAME=airflow" >> .env
echo "_AIRFLOW_WWW_USER_PASSWORD=airflow" >> .env

# Проверяем
cat .env
```

### 3. Собираем и запускаем окружение

```bash
# Сборка образа Airflow (apache/airflow + dvc, mlflow, scikit-learn) — 10–15 минут!
docker compose build --no-cache

# Инициализация: миграция БД и создание администратора
docker compose up airflow-init
# Ждём строку "airflow-init-1 exited with code 0"

# Запускаем все сервисы в фоновом режиме
docker compose up -d

# Проверяем, что все контейнеры запущены
docker compose ps
```

Поднимаются четыре сервиса (конфиг — `docker-compose.yaml`):

- **Airflow 3.3.1** — PostgreSQL 16 + API-сервер + планировщик + dag-processor;
  UI на `http://localhost:8080`, логин `airflow`, пароль `airflow`.
- **MLflow** — UI на `http://localhost:5000` (эксперименты и запуски моделей).

### 4. Запускаем Jupyter

```bash
cd ~/labs
uv run jupyter notebook
```

В браузере открываем папку `lab_06`, выбираем ядро **`Python 3.11 (labs)`**
и начинаем с `airflow_exercises.ipynb`.


## Файлы лаборатории

| Файл | Назначение |
|------|-----------|
| `airflow_exercises.ipynb` | Студенческий ноутбук (все три части, с задачами) |
| `airflow_solutions.ipynb` | Референтная версия с готовыми решениями |
| `docker-compose.yaml` | Конфигурация окружения (Airflow 3.3.1, PostgreSQL 16, MLflow) |
| `Dockerfile` | Образ Airflow: база `apache/airflow:3.3.1` + библиотеки из `requirements.txt` |
| `requirements.txt` | Добавленные в образ библиотеки (dvc, mlflow, scikit-learn, pandas, joblib) |


## Сброс окружения

```bash
cd ~/labs/lab_06
# Останавливаем контейнеры и удаляем том с метаданными Airflow (PostgreSQL)
docker compose down -v
# Удаляем артефакты, созданные ноутбуком
rm -rf dags logs config plugins ml_projects .env
```
