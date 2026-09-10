FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

# Копируем только нужные файлы приложения
COPY service.py .
COPY model/model.joblib model/model.joblib
COPY model/scaler.joblib model/scaler.joblib
COPY model/feature_columns.joblib model/feature_columns.joblib

# Порт, на котором слушает uvicorn
EXPOSE 8000


CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8308"]