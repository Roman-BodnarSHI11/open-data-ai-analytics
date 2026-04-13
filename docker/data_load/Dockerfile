FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY data/raw/sample_delivery.csv /opt/seed/sample_delivery.csv
COPY src /app/src

RUN mkdir -p /data/raw

# Демо-CSV у спільний том + завантаження з CKAN (якщо мережа доступна) та імпорт у БД
ENTRYPOINT ["sh", "-c", "mkdir -p /data/raw && cp /opt/seed/sample_delivery.csv /data/raw/ && exec python -m data_load.pipeline"]
