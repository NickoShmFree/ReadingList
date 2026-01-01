# ===== Builder =====
FROM python:3.12-slim AS builder

WORKDIR /app

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry и зависимости
RUN pip install --no-cache-dir --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

# ===== Final =====
FROM python:3.12-slim AS final

# Установка curl (опционально для healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser -m -s /bin/bash appuser

WORKDIR /app

# Копируем зависимости из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем исходный код
COPY src/ ./src/
COPY alembic_files/ ./alembic_files/

# Права доступа
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Команда запуска
CMD ["sh", "-c", "cd /app && alembic -c alembic_files/alembic.ini upgrade head && cd /app/src && exec gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 2 --access-logfile - --error-logfile -"]