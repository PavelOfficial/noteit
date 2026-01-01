# Используем официальный базовый образ Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (опционально, для компиляции некоторых пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY . .

# Создаем директорию для instance (база данных)
RUN mkdir -p instance

# Открываем порт 5000
EXPOSE 5000

# Задаем переменные окружения по умолчанию
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Запускаем приложение через gunicorn
# Используем 4 воркера и привязываемся к 0.0.0.0:5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]

