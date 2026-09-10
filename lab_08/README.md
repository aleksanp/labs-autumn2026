# Лабораторная работа № 8

## Краткое описание

В ходе работы необходимо поднять контейнеры с помощью docker-compose.
После запуска будут доступны:
- ML сервис (FastAPI) http://localhost:8308
  - /health
  - /predict
  - /metrics
  - /docs
- Prometheus будет доступен на http://localhost:8309
- Grafana будет доступна на http://localhost:8310

Далее необходимо настроить визуализацию.


## Архитектура

  ```
  Клиент / тестовые запросы
          |
          v
  ML API сервис (FastAPI)
    /predict
    /health
    /metrics
          |
          v
  Prometheus собирает метрики
          |
          v
  Grafana строит дашборды
  ```


## Настройка контейнеров 
`~/labs/lab_08/monitoring/docker-compose.yml`

### Параметры контейнера ML сервиса (FastAPI)

```yaml
  ml-api:
    # Этап указывает build, что образ для контейнера нужно собрать из исходников, а не использовать готовый образ из реестра
    build:
      # Задаёт путь к директории, которая будет использоваться как контекст сборки. 
      # Здесь .. означает родительскую папку относительно текущего местоположения файла docker-compose.yml
      context: ..
      # Имя файла Dockerfile, который находится в контексте (..) и содержит инструкции по сборке образа
      dockerfile: Dockerfile
    # Явно задаёт имя контейнера. Docker присвоил бы имя автоматически (например, project_prometheus_1).
    # Фиксированное имя удобно, если вы хотите обращаться к контейнеру по этому имени из других контейнеров (в той же сети) - http://ml-api:3000
    container_name: ml-api
    # Пробрасывает порт контейнера 8308 (внутренний, задаётся в Dockerfile) на порт хоста 8308 (внешний)
    ports:
      - "8308:8308"
    # Политика перезапуска контейнера. unless-stopped – перезапускать при падении, кроме случаев, 
    # когда контейнер был явно остановлен пользователем.
    restart: unless-stopped
```

### Параметры контейнера Prometheus
```yaml
  prometheus:
    # Docker-образ, который будет использован для создания контейнера. prom/prometheus — официальный образ Prometheus от разработчиков.
    # Docker скачает этот образ из Docker Hub, если его нет локально.
    image: prom/prometheus:latest
    container_name: prometheus
    # Docker передаёт этот аргумент в точку входа образа Prometheus (аргументы запуска). 
    # В итоге контейнер стартует так /bin/prometheus --config.file=/etc/prometheus/prometheus.yml.
    # По умолчанию образ уже ищет конфиг по пути /etc/prometheus/prometheus.yml, поэтому эта строка технически избыточна, но добавлена для наглядности.
    # Конфиг тот же самый, который мы монтируем через volumes.
    command:  
      - "--config.file=/etc/prometheus/prometheus.yml"
    # Монтирование файла с хоста внутрь контейнера: файл ~/labs/lab_08/monitoring/prometheus.yml.
    # Будет доступен по пути /etc/prometheus/prometheus.yml.
    # Без этого тома использовался бы конфиг, вшитый в образ (или пришлось бы собирать свой образ).
    volumes: 
      - ./prometheus.yml:/etc/prometheus/prometheus.yml 
    ports:
      - "8309:9090"
    # Гарантирует порядок запуска контейнеров
    depends_on:
      - ml-api
    restart: unless-stopped
```

### Параметры контейнера Grafana

```yaml
grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      # Слева (8310) — порт на вашем хост-компьютере, справа (3000) — порт внутри контейнера.
      - "8310:3000"
    # Переменные окружения. Здесь задается пароль для администратора по умолчанию.
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    # Монтирование тома. Слева (grafana_data) — имя именованного тома Docker, который физически хранится на вашем диске (где именно — можно узнать через docker volume inspect grafana_data). Справа (/var/lib/grafana) — папка внутри контейнера, где Grafana хранит свои дашборды, настройки источников данных и БД SQLite. Благодаря этому том вы не потеряете настройки при перезапуске или обновлении контейнера.
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped
```


## Настройки Prometheus

Параметры prometheus (`~/labs/lab_08/monitoring/prometheus.yml`):
```yaml
global:
  # Prometheus будет опрашивать сервис раз в 30 секунд
  scrape_interval: 30s
scrape_configs:
  - job_name: ml-service
    # Путь, где FastAPI отдаёт метрики
    metrics_path: /metrics
    static_configs:
      # Prometheus из Docker обращается к ML сервису (в той же сети)
      - targets: ["ml-api:8308"]
```
---


## Запуск

Поднять контейнеры
```bash
cd ~/labs/lab_08/monitoring
docker compose up -d
```

Проверка
```bash
docker ps
```

Должны быть запущены

|...| IMAGE |...| NAMES |
|-|-|-|-|
|...|grafana/grafana:latest|...| prometheus|
|...|prom/prometheus:latest|...| grafana|

Остановить (внутри папки monitoring)
```bash
docker compose down
```

## Работа с ML сервисом

Проверить метрики в терминале
```bash
curl http://localhost:8308/metrics
```

Ответ примерно такой:
```
...
ml_model_loaded 1.0 ...
ml_http_requests_total{endpoint="/metrics",status="200"} 1.0 ...
ml_prediction_duration_seconds_bucket{le="0.005"} 0.0 ...
ml_prediction_value_bucket{le="1000.0"} 0.0 ...
...
```

Пример запроса
```bash
curl -X POST http://localhost:8308/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Классификатор перевозок": "Тип 1",
    "Тип заказа": "Тип 1",
    "Ранг отправки": "конт. поезд",
    "Операция": "Тип 1",
    "Тип услуги": "Решение ЭС",
    "Наименование плановой услуги предоставления": "Услуга предоставления на плече",
    "Связка": "Тип 1",
    "Тип клиента": "Экспедитор",
    "ДФЭ": 1.0,
    "month": 1,
    "dayofweek": 1,
    "hour": 1
  }'
```

Пример успешного ответа:
```
{
    "prediction":81450.73574339398,
    "duration_ms":30.94484587199986
}
```


## Работа в Prometheus

Prometheus будет доступен на http://localhost:8309

Проверка - перейти Status -> Targets health.
Отобразится:
- Задача `ml-service`
- состояние state - `UP`
- Endpoint - `http://host.docker.internal:8308/metrics`
- Labels - `instance="host.docker.internal:8308"`, `job="ml-service"`

Если состояние UP, значит Prometheus успешно собирает метрики с FastAPI-сервиса.

Проверка через запрос: 
query -> Enter expression -> ввести `up{job="ml-service"}` -> Execute -> ответ должен быть 0 или 1 (справа) 


## Работа в Grafana

Grafana будет доступна на http://localhost:8310

Логин Grafana по умолчанию admin. Пароль мы задали в конфиге admin.

### Подключение
1. Слева выбери раздел Connections или Configuration.
2. Найди Data Sources.
3. Нажми Add new data source.
4. Выбери Prometheus.
5. В поле URL укажи:
http://prometheus:9090
Grafana и Prometheus находятся в одной Docker-сети, поэтому Grafana должна обращаться к Prometheus по имени сервиса.
6. Нажми Save & test. Должно появиться сообщение вроде Successfully queried the Prometheus API.

### Создание дашборда в Grafana
1. Нажми Dashboards.
2. Нажми Create dashboard (перейдёт в New dashboard)
3. Нажми Add new element (может быть уже открыт).
4. Нажать на Panel. Дать название Title или оставить текущее.
5. Нажать Configure visualization.
6. Выбери источник данных Data source - Prometheus.
7. Добавим визуализацию доступности сервиса. Нажать All visualisation и выбрать Stats. Настроить запрос можно сделать через builder или напрямую через promql
  - в Metric выбрать `up` и задать Label filters `job = "ml-service"` (builder)
  - или поменять Builder на Code и ввести `up{job="ml-service"}` (promql)
  - Запустить `run queries`
  - название панели введите Service Up


## Самостоятельная работа:
1. Добавьте в Grafana дашборды:

    1.1 Добавьте визуализацию загружена ли модель. Вернуться в New dashboard. Повторить аналогично, но в Metric выбрать `ml_model_loaded`
    1.2. Добавьте визуализацию количества запросов в секунду. 
      - Time series
      - воспроизвести в builder функцию `sum by(status) (rate(ml_http_requests_total{endpoint!="/metrics", job="ml-service"}[1m]))`
    Эта панель показывает RPS по статусам ответа
    1.3. Добавьте визуализацию количества запросов к /predict.
      - Histogram
      - воспроизвести в builder функцию `ml_prediction_value_bucket{job="ml-service"}`
    1.4. Перейдите в jupyter notebook и выполните задания.

