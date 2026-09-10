import logging
import os
import time
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("ml-service")

cat_cols = [
    "Классификатор перевозок",
    "Тип заказа",
    "Ранг отправки",
    "Операция",
    "Тип услуги",
    "Наименование плановой услуги предоставления",
    "Связка",
    "Тип клиента"
]

num_cols = [
    "ДФЭ",
    "month",
    "dayofweek",
    "hour",
]

required_cols = cat_cols + num_cols

MODEL_PATH = os.getenv("MODEL_PATH", "model/model.joblib")
SCALER_PATH = os.getenv("SCALER_PATH", "model/scaler.joblib")
FEATURE_COLUMNS_PATH = os.getenv("FEATURE_COLUMNS_PATH", "model/feature_columns.joblib")

model = None
scaler = None
feature_columns = None

MODEL_LOADED = Gauge(
    "ml_model_loaded",
    "1 if model artifacts are loaded, 0 otherwise"
)

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

    MODEL_LOADED.set(1)

    logger.info("Model loaded: %s", MODEL_PATH)
    logger.info("Scaler loaded: %s", SCALER_PATH)
    logger.info("Feature columns loaded: %s", FEATURE_COLUMNS_PATH)

except Exception as exc:
    MODEL_LOADED.set(0)
    logger.error("Cannot load model artifacts: %s", exc)

app = FastAPI(title="Linear Regression API without Pipeline")

REQUESTS = Counter(
    "ml_http_requests_total",
    "Total HTTP requests",
    ["endpoint", "status"]
)

PREDICTION_DURATION = Histogram(
    "ml_prediction_duration_seconds",
    "Prediction duration in seconds"
)

PREDICTION_VALUE = Histogram(
    "ml_prediction_value",
    "Prediction value distribution",
    buckets=(
        0,
        1_000,
        5_000,
        10_000,
        50_000,
        100_000,
        200_000,
    )
)

ERRORS = Counter(
    "ml_prediction_errors_total",
    "Total prediction errors",
    ["reason"]
)


def prepare_features(payload: dict) -> pd.DataFrame:
    """
    Готовит один входной JSON к прогнозу.

    Делает то же самое, что делалось при обучении:
    1. проверяет обязательные поля;
    2. приводит категориальные признаки к строкам;
    3. приводит числовые признаки к числам;
    4. делает get_dummies;
    5. выравнивает колонки по обучающему набору;
    6. масштабирует числовые признаки.
    """

    if model is None or scaler is None or feature_columns is None:
        raise RuntimeError("Model artifacts are not loaded")

    missing_cols = [
        col for col in required_cols
        if col not in payload
    ]

    if missing_cols:
        raise ValueError(f"Missing required fields: {missing_cols}")

    row = {
        col: payload[col]
        for col in required_cols
    }

    df = pd.DataFrame([row])
    df[cat_cols] = df[cat_cols].astype(str)

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="raise")
        
    df = pd.get_dummies(df, columns=cat_cols, dtype=np.uint8)

    # Обязательный шаг:
    # оставляем ровно те же колонки и в том же порядке,
    # которые были при обучении модели.
    df = df.reindex(
        columns=feature_columns,
        fill_value=0
    )

    # Масштабируем числовые признаки тем же scaler,
    # который был обучен на train.
    df[num_cols] = scaler.transform(df[num_cols].astype(float))

    return df


@app.get("/")
def root():
    REQUESTS.labels(endpoint="/", status="200").inc()

    return {
        "service": "linear-regression-api",
        "pipeline_used": False,
        "endpoints": [
            "/health",
            "/predict",
            "/metrics"
        ]
    }


@app.get("/health")
def health():
    if model is None or scaler is None or feature_columns is None:
        REQUESTS.labels(endpoint="/health", status="503").inc()

        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "model_loaded": False
            }
        )

    REQUESTS.labels(endpoint="/health", status="200").inc()

    return {
        "status": "ok",
        "model_loaded": True
    }


@app.get("/metrics")
def metrics():
    REQUESTS.labels(endpoint="/metrics", status="200").inc()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/predict")
def predict(payload: dict):
    start = time.perf_counter()

    try:
        if model is None or scaler is None or feature_columns is None:
            raise HTTPException(
                status_code=503,
                detail="Model artifacts are not loaded"
            )

        features = prepare_features(payload)

        prediction = float(model.predict(features)[0])

        duration = time.perf_counter() - start

        PREDICTION_DURATION.observe(duration)
        PREDICTION_VALUE.observe(prediction)
        REQUESTS.labels(endpoint="/predict", status="200").inc()

        logger.info(
            "predict ok prediction=%.2f duration_ms=%.1f",
            prediction,
            duration * 1000
        )

        return {
            "prediction": prediction,
            "duration_ms": duration * 1000
        }

    except HTTPException as exc:
        duration = time.perf_counter() - start

        PREDICTION_DURATION.observe(duration)
        ERRORS.labels(reason="http_error").inc()
        REQUESTS.labels(
            endpoint="/predict",
            status=str(exc.status_code)
        ).inc()

        logger.warning(
            "predict failed status=%s detail=%s",
            exc.status_code,
            exc.detail
        )

        raise

    except ValueError as exc:
        duration = time.perf_counter() - start

        PREDICTION_DURATION.observe(duration)
        ERRORS.labels(reason="validation_error").inc()
        REQUESTS.labels(endpoint="/predict", status="422").inc()

        logger.warning("validation error: %s", exc)

        return JSONResponse(
            status_code=422,
            content={
                "error": str(exc)
            }
        )

    except Exception as exc:
        duration = time.perf_counter() - start

        PREDICTION_DURATION.observe(duration)
        ERRORS.labels(reason="prediction_error").inc()
        REQUESTS.labels(endpoint="/predict", status="500").inc()

        logger.exception("predict failed error=%s", exc)

        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc)
            }
        )