# Лабораборная работа № 6

## Краткое описание

В ходе работы необходимо настроить конвейер машинного обучения.

В результате выполнения лабораторной работы студент получает навык работы с Apache Airflow и
Kedro для организации воспроизводимого конвейера машинного обучения.

## Поднятие Git 

```bash
# Если останавливали или удаляли gitlab с 5 лабораторной работы
cd ../lab_05
docker compose down
docker compose up gitlab -d
```
Подождать 1-2 минуты, пока не запустится gitlab.
Зайти:
- user: "root"
- password: "EducationLab!"

Создать новый пустой проект:
- Create new project
- Задать имя `mlops-logistics-lab06` (без кавычек)
- В поле Pick a group or namespace выбрать root
- Убрать галочку в разделе Project Configuration (!)
- Нажать Create project


## Поднятие Airflow
```bash
# Перейдем в папку с лабораторной работой
cd ../lab_06
# Airflow использует несколько локальных папок для DAG, логов, плагинов и конфигурации. Создадим:

# Далее создайте файл .env
printf "AIRFLOW_UID=%s\nAIRFLOW_GID=%s\n" "$(id -u)" "$(id -g)" > .env
echo "_AIRFLOW_WWW_USER_USERNAME=airflow" >> .env
echo "_AIRFLOW_WWW_USER_PASSWORD=airflow" >> .env

# Посмотреть результат
cat .env
```
Сборка образа занимает около 10-15 минут!
```bash
# Сборка образа.
docker compose build --no-cache
# Инициализируем Airflow
docker compose up airflow-init
# Ожидаем "airflow-init-1 exited with code 0"
```

```bash
# Запустим Airflow в фоновом режиме
docker compose up -d
# Логин: airflow
# Пароль: airflow 
```
```bash
# Проверить IP
hostname -I
# В браузере подключиться по http://127.0.0.1:8080/dags или http://ip:8080/dags
# Аналогично MLflow: http://127.0.0.1:5000 или http://ip:5000 
```

## Запуск Jupyter
```bash
cd ~/labs
# Запускаем jupyter и переходим в airflow.ipynb
uv run jupyter notebook
```
