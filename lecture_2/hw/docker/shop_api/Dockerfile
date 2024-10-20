FROM python:3.12 AS base

# Установка переменных окружения
ARG PYTHONFAULTHANDLER=1
ARG PYTHONUNBUFFERED=1
ARG PYTHONHASHSEED=random
ARG PIP_NO_CACHE_DIR=on
ARG PIP_DISABLE_PIP_VERSION_CHECK=on
ARG PIP_DEFAULT_TIMEOUT=500

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y gcc && \
    python -m pip install --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*  # Очистка временных файлов

# Установка рабочего каталога
WORKDIR /app
COPY ./src/requirements.txt ./

# Установка зависимостей
RUN pip install -r requirements.txt

# Копируем код приложения
COPY ./src/ ./

# Переменные окружения для виртуального окружения
ENV VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

FROM base as dev

# Запускаем команду для поддержания контейнера в работе
CMD ["bash", "-c", "while true; do sleep 1; done"]

FROM base as local

# Запуск приложения
CMD ["uvicorn", "shop_api.main:app", "--port", "8080", "--host", "0.0.0.0"]
