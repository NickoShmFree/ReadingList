# ===== Builder =====
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем uv 
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости через uv (кешируются в слое Docker)
RUN uv pip install --system --no-cache -r pyproject.toml

# ===== Final =====
FROM python:3.12-slim AS final

# Создаем non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser -m -s /bin/bash appuser

WORKDIR /app

# Копируем только зависимости из builder
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