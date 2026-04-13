FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app/src
ENV FLASK_APP=web.app

COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src

EXPOSE 8080

CMD ["flask", "--app", "web.app", "run", "--host=0.0.0.0", "--port=8080"]
