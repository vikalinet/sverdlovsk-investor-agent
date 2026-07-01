# ============================================================
# Dockerfile для Investor Agent
# Multi-stage сборка для минимального размера образа
# ============================================================

# ============================================================
# Stage 1: Build
# ============================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
COPY requirements-dev.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================
# Stage 2: Production
# ============================================================
FROM python:3.11-slim as production

WORKDIR /app

# Метки образа
LABEL maintainer="NLP-Core-Team"
LABEL version="1.0.0"
LABEL description="AI-агент помощник инвестора в Свердловской области"

# Создание пользователя без root прав
RUN useradd --create-home --shell /bin/bash appuser

# Копирование зависимостей из builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Копирование кода проекта
COPY --chown=appuser:appuser . .

# Создание директорий
RUN mkdir -p logs output/documents output/reports data && \
    chown -R appuser:appuser /app

# Переключение на пользователя без root прав
USER appuser

# Добавление bin в PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1

# Переменные окружения
ENV ENVIRONMENT=production
ENV WEB_HOST=0.0.0.0
ENV WEB_PORT=5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; r = requests.get('http://localhost:5000/api/health', timeout=5); exit(0 if r.status_code == 200 else 1)" || exit 1

# Экспортируемый порт
EXPOSE 5000

# Запуск приложения через gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "web.app:app"]

# ============================================================
# Stage 3: Development
# ============================================================
FROM production as development

# Переключение на root для установки dev зависимостей
USER root

# Установка dev зависимостей
RUN pip install --no-cache-dir --user -r requirements-dev.txt

# Переключение обратно на appuser
USER appuser

# Переменная окружения для development
ENV ENVIRONMENT=development
ENV DEBUG=True
ENV WEB_WORKERS=1

# Запуск в development режиме
CMD ["python", "web/app.py"]
