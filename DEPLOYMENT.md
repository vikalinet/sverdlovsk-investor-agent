# 🚀 Production Deployment Guide

## Содержание

1. [Docker развертывание](#docker-развертывание)
2. [Kubernetes развертывание](#kubernetes-развертывание)
3. [Environment переменные](#environment-переменные)
4. [Мониторинг и логирование](#мониторинг-и-логирование)
5. [Backup и восстановление](#backup-и-восстановление)

---

## Docker развертывание

### Быстрый старт

```bash
# Development окружение
docker-compose up -d

# Production окружение
docker-compose -f docker-compose.prod.yml up -d

# Просмотр логов
docker-compose logs -f api

# Остановка
docker-compose down
```

### Переменные окружения для production

Создайте `.env.production`:

```bash
# Application
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-super-secret-key-min-32-chars

# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/investor_agent

# Redis
REDIS_URL=redis://redis:6379/0
CACHE_TYPE=redis

# Web
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_WORKERS=4
WEB_CORS_ORIGINS=["https://investor-agent.ru"]

# Security
RATE_LIMIT_PER_MINUTE=60
API_KEY_REQUIRED=True

# Search
SEARCH_PROVIDER=yandex
SEARCH_API_KEY=your-search-api-key

# Logging
LOG_LEVEL=WARNING
```

### Production docker-compose

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  api:
    image: ghcr.io/nlp-core-team/investor-agent:latest
    ports:
      - "5000:5000"
    env_file: .env.production
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
    depends_on:
      - postgres
      - redis
    networks:
      - investor_network
    restart: always
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=investor_agent
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - investor_network
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - investor_network
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    networks:
      - investor_network
    restart: always

volumes:
  postgres_data:
  redis_data:

networks:
  investor_network:
    driver: bridge
```

### Nginx конфигурация

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream investor_agent {
        server api:5000;
        keepalive 32;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name investor-agent.ru;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name investor-agent.ru;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000" always;

        location / {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://investor_agent;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /api/health {
            proxy_pass http://investor_agent;
            access_log off;
        }
    }
}
```

---

## Kubernetes развертывание

### Deployment

**k8s/deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: investor-agent
  labels:
    app: investor-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: investor-agent
  template:
    metadata:
      labels:
        app: investor-agent
    spec:
      containers:
      - name: api
        image: ghcr.io/nlp-core-team/investor-agent:latest
        ports:
        - containerPort: 5000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: investor-agent-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: investor-agent-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: investor-agent-service
spec:
  selector:
    app: investor-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

---

## Environment переменные

### Обязательные для production

| Переменная | Описание | Пример |
|-----------|---------|--------|
| `ENVIRONMENT` | Окружение | `production` |
| `SECRET_KEY` | Секретный ключ (мин 32 символа) | `random-string` |
| `DATABASE_URL` | URL базы данных | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379/0` |
| `WEB_CORS_ORIGINS` | Разрешённые CORS домены | `["https://domain.ru"]` |

### Опциональные

| Переменная | Описание | Default |
|-----------|---------|---------|
| `SEARCH_PROVIDER` | Поисковый провайдер | `mock` |
| `SEARCH_API_KEY` | API ключ поиска | - |
| `RATE_LIMIT_PER_MINUTE` | Лимит запросов | `60` |
| `LOG_LEVEL` | Уровень логирования | `WARNING` |

---

## Мониторинг и логирование

### Prometheus метрики

Добавьте endpoint `/metrics` с использованием `prometheus-flask-exporter`:

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

@metrics.counter('api_requests_total', 'Total API requests',
                 labels={'endpoint': lambda: request.path})
@app.route('/api/endpoint')
def endpoint():
    ...
```

### Grafana дашборд

Импортируйте дашборд из `monitoring/grafana-dashboard.json`

### Логирование

Логи сохраняются в:
- `logs/agent.log` - логи агента
- `logs/web_api.log` - логи API

Для централизованного логирования используйте ELK stack или Loki.

---

## Backup и восстановление

### Backup базы данных

```bash
# PostgreSQL backup
pg_dump -U investor investor_agent > backup_$(date +%Y%m%d).sql

# Redis backup
redis-cli BGSAVE

# Документы
tar -czf documents_backup_$(date +%Y%m%d).tar.gz output/documents/
```

### Восстановление

```bash
# PostgreSQL restore
psql -U investor investor_agent < backup_20240101.sql

# Redis restore
# Копировать dump.rdb в data директорию

# Документы
tar -xzf documents_backup_20240101.tar.gz
```

### Автоматический backup (cron)

```bash
# /etc/cron.d/investor-agent-backup
0 2 * * * root /opt/investor-agent/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## Troubleshooting

### API не отвечает

```bash
# Проверка контейнеров
docker-compose ps

# Проверка логов
docker-compose logs api

# Проверка health
curl http://localhost:5000/api/health
```

### Проблемы с базой данных

```bash
# Подключение к PostgreSQL
docker-compose exec postgres psql -U investor -d investor_agent

# Проверка соединений
SELECT count(*) FROM pg_stat_activity;

# Перезапуск
docker-compose restart postgres
```

### Высокая нагрузка

```bash
# Увеличение реплик
docker-compose up -d --scale api=8

# Проверка ресурсов
docker stats
```

---

## Контакты поддержки

- Email: support@investor-agent.ru
- Telegram: @investor_agent_support
- GitHub Issues: https://github.com/NLP-Core-Team/investor-agent/issues
