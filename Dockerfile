FROM python:3.11-slim

# Устанавливаем системные зависимости, необходимые для psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]