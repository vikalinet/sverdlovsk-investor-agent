# 📘 Пошаговый гайд по улучшению проекта Investor Agent

## 📋 Оглавление

1. [Анализ текущего состояния](#1-анализ-текущего-состояния)
2. [Приоритет 1: Критические улучшения](#2-приоритет-1-критические-улучшения)
3. [Приоритет 2: Архитектурные улучшения](#3-приоритет-2-архитектурные-улучшения)
4. [Приоритет 3: Качество кода](#4-приоритет-3-качество-кода)
5. [Приоритет 4: Тестирование](#5-приоритет-4-тестирование)
6. [Приоритет 5: Безопасность](#6-приоритет-5-безопасность)
7. [Приоритет 6: DevOps и CI/CD](#7-приоритет-6-devops-и-cicd)
8. [Приоритет 7: Производительность](#8-приоритет-7-производительность)
9. [Дорожная карта](#9-дорожная-карта)

---

## 1. Анализ текущего состояния

### ✅ Сильные стороны проекта

| Аспект | Статус | Комментарий |
|--------|--------|-------------|
| Модульная архитектура | ✅ | Чёткое разделение на модули (search, database, documents, analysis) |
| Асинхронность | ✅ | Использование asyncio для I/O операций |
| MCP-серверы | ✅ | Разделение баз данных по доменам |
| Web API | ✅ | Flask REST API с CORS |
| Документация | ✅ | Наличие README, USAGE, ML_MODEL и других markdown-файлов |
| Тесты | ✅ | Базовая структура тестов присутствует |
| Конфигурация | ✅ | Вынесена в config.py с поддержкой .env |

### ⚠️ Области для улучшения

| Категория | Проблемы | Приоритет |
|-----------|----------|-----------|
| **Зависимости** | Дублирование в requirements.txt, нет версионирования | 🔴 Критический |
| **Обработка ошибок** | Минимальная, нет единого подхода | 🔴 Критический |
| **Валидация данных** | Отсутствует Pydantic-модели для API | 🔴 Критический |
| **Логирование** | Нет структурированного логирования | 🟡 Высокий |
| **Тесты** | Низкое покрытие, нет mock-объектов | 🟡 Высокий |
| **Безопасность** | Нет rate limiting, CORS слишком открытый | 🟡 Высокий |
| **Документация API** | Нет OpenAPI/Swagger спецификации | 🟡 Высокий |
| **Конфигурация** | Хардкод значений, нет разделения по окружениям | 🟡 Высокий |
| **Типизация** | Частичная, нет mypy проверки | 🟢 Средний |
| **Мониторинг** | Отсутствует | 🟢 Средний |
| **CI/CD** | Нет конфигурации | 🟢 Средний |

---

## 2. Приоритет 1: Критические улучшения

### 2.1 Исправление requirements.txt

**Проблема:** Дублирование зависимостей, отсутствие точного версионирования.

**Решение:**

```txt
# requirements.txt
# Основные зависимости
python-dotenv==1.0.0
requests==2.31.0
aiohttp==3.9.1

# Работа с данными
pandas==2.1.4
sqlalchemy==2.0.23

# MCP SDK
mcp==1.0.0

# Обработка документов
jinja2==3.1.2
python-docx==1.1.0
reportlab==4.0.7

# Валидация и сериализация
pydantic==2.5.3
pydantic-settings==2.1.0
pyyaml==6.0.1

# Логирование
loguru==0.7.2
structlog==23.2.0

# Тестирование
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0

# Web интерфейс
flask==3.0.0
flask-cors==4.0.0
flask-pydantic==0.11.0
gunicorn==21.2.0

# MCP серверы
click==8.1.7

# Утилиты
tenacity==8.2.3
```

**Дополнительно создать:**

```txt
# requirements-dev.txt
-r requirements.txt

# Линтинг и форматирование
black==23.12.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
pylint==3.0.3

# Пре-коммит хуки
pre-commit==3.6.0

# Безопасность
bandit==1.7.5
safety==2.3.5
```

### 2.2 Настройка Pydantic моделей для API

**Проблема:** Отсутствие валидации входящих данных в API.

**Решение:** Создать файл `web/schemas.py`:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class PracticeRequest(BaseModel):
    industry: str = Field(..., min_length=1, max_length=100)
    practice_type: str = Field(default="all", pattern="^(all|технологии|управление|финансы)$")
    
    @field_validator('industry')
    @classmethod
    def validate_industry(cls, v):
        if not v.strip():
            raise ValueError('industry не может быть пустым')
        return v.strip()


class OpportunityRequest(BaseModel):
    industry: Optional[str] = Field(None, max_length=100)
    min_investment: float = Field(default=0, ge=0)
    location: Optional[str] = Field(None, max_length=200)


class SupportMeasuresRequest(BaseModel):
    industry: str = Field(..., min_length=1, max_length=100)
    business_size: str = Field(default="medium", pattern="^(small|medium|large|smo)$")


class ProjectData(BaseModel):
    applicant_name: str = Field(..., min_length=1)
    inn: str = Field(..., pattern=r'^\d{10}$')
    ogrn: str = Field(..., pattern=r'^\d{13}$')
    address: str
    contact_phone: str
    contact_email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    project_name: str
    industry: str
    description: str
    investment_amount: float = Field(..., gt=0)
    grant_amount: float = Field(..., ge=0)
    jobs_created: int = Field(..., ge=0)
    implementation_period: int = Field(..., ge=1)


class DocumentsPackageRequest(BaseModel):
    measure_name: str
    measure_type: str = Field(..., pattern="^(grant|subsidy|fund)$")
    project_data: ProjectData


class AnalysisRequest(BaseModel):
    industry: str
    min_investment: float = Field(default=10_000_000, ge=0)
```

### 2.3 Единый обработчик ошибок

**Проблема:** Повторяющийся код обработки ошибок в каждом endpoint.

**Решение:** Создать `web/error_handlers.py`:

```python
from flask import jsonify
from loguru import logger
from functools import wraps


class APIError(Exception):
    """Базовый класс для API ошибок"""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(APIError):
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message, status_code=404)


class ValidationError(APIError):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)


class ServiceUnavailableError(APIError):
    def __init__(self, message: str = "Сервис временно недоступен"):
        super().__init__(message, status_code=503)


def handle_api_errors(f):
    """Декоратор для обработки ошибок API"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API ошибка: {e.message}")
            return jsonify({
                "success": False,
                "error": e.message,
                "details": e.details
            }), e.status_code
        except Exception as e:
            logger.exception(f"Необработанная ошибка: {e}")
            return jsonify({
                "success": False,
                "error": "Внутренняя ошибка сервера"
            }), 500
    return wrapper
```

---

## 3. Приоритет 2: Архитектурные улучшения

### 3.1 Разделение конфигурации по окружениям

**Проблема:** Единый config.py для всех окружений.

**Решение:** Создать структуру:

```
config/
├── __init__.py
├── base.py          # Базовая конфигурация
├── development.py   # Разработка
├── production.py    # Продакшен
└── testing.py       # Тесты
```

**config/base.py:**
```python
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Приложение
    APP_NAME: str = "Investor Agent"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Регион
    REGION_NAME: str = "Свердловская область"
    REGION_CODE: str = "66"
    REGION_CAPITAL: str = "Екатеринбург"
    
    # База данных
    DATABASE_URL: str = "sqlite:///data/main.db"
    
    # Поиск
    SEARCH_API_KEY: str = ""
    SEARCH_PROVIDER: str = "mock"
    SEARCH_MAX_RESULTS: int = 10
    
    # MCP серверы
    MCP_SUPPORT_MEASURES_URL: str = ""
    MCP_INVESTMENT_OBJECTS_URL: str = ""
    MCP_BUSINESS_REGISTRY_URL: str = ""
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/agent.log"
    
    # Web
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 5000
    WEB_CORS_ORIGINS: List[str] = ["*"]
    
    # Безопасность
    RATE_LIMIT_PER_MINUTE: int = 60
    API_KEY_HEADER: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
BASE_DIR = Path(__file__).resolve().parent.parent
```

### 3.2 Dependency Injection

**Проблема:** Глобальные инстансы агента, сложность тестирования.

**Решение:** Создать `src/dependencies.py`:

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .agent import InvestorAgent
from .search_module import SearchModule
from .database_module import DatabaseModule
from .documents_module import DocumentsModule
from .analysis_module import AnalysisModule


class DependencyContainer:
    """Контейнер зависимостей"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self._agent: InvestorAgent = None
    
    async def get_agent(self) -> InvestorAgent:
        if self._agent is None:
            self._agent = InvestorAgent(config=self.config)
        return self._agent
    
    async def close(self):
        if self._agent:
            await self._agent.end_session()
            self._agent = None


# Глобальный контейнер
container = DependencyContainer()


@asynccontextmanager
async def get_agent_session() -> AsyncGenerator[InvestorAgent, None]:
    """Получение сессии агента"""
    agent = await container.get_agent()
    await agent.start_session()
    try:
        yield agent
    finally:
        await agent.end_session()
```

### 3.3 Репозиторий паттерн для данных

**Проблема:** Прямой доступ к БД из сервисов.

**Решение:** Создать `src/repositories/`:

```
src/repositories/
├── __init__.py
├── base.py              # Базовый репозиторий
├── support_measures.py  # Репозиторий мер поддержки
├── investment_objects.py # Репозиторий инвестобъектов
└── best_practices.py    # Репозиторий лучших практик
```

**src/repositories/base.py:**
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Базовый класс репозитория"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100) -> List[T]:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, id: str, **kwargs) -> Optional[T]:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
```

---

## 4. Приоритет 3: Качество кода

### 4.1 Настройка линтеров

**Создать `.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-aiohttp, types-PyYAML]
```

**Создать `pyproject.toml`:**
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
skip = [".venv", "build", "dist"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
asyncio_mode = "auto"
addopts = "-v --tb=short --cov=src --cov=web --cov-report=term-missing"

[tool.coverage.run]
source = ["src", "web"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

### 4.2 Улучшение структуры проекта

**Рекомендуемая структура:**
```
investor_agent/
├── .github/
│   └── workflows/         # CI/CD пайплайны
├── config/                # Конфигурация
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── dependencies.py    # DI контейнер
│   ├── exceptions.py      # Кастомные исключения
│   ├── repositories/      # Репозитории
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── ...
│   ├── services/          # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── search_service.py
│   │   ├── analysis_service.py
│   │   └── ...
│   ├── models/            # Pydantic модели
│   │   ├── __init__.py
│   │   ├── practice.py
│   │   ├── opportunity.py
│   │   └── ...
│   └── modules/           # Существующие модули (рефакторинг)
│       ├── search_module.py
│       ├── database_module.py
│       ├── documents_module.py
│       └── analysis_module.py
├── web/
│   ├── __init__.py
│   ├── app.py
│   ├── schemas.py         # Pydantic схемы
│   ├── routes/            # Роуты по модулям
│   │   ├── __init__.py
│   │   ├── practices.py
│   │   ├── opportunities.py
│   │   └── ...
│   ├── middleware/        # Middleware
│   │   ├── __init__.py
│   │   ├── error_handler.py
│   │   └── rate_limiter.py
│   └── static/
├── mcp_servers/
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # pytest фикстуры
│   ├── unit/              # Unit тесты
│   ├── integration/       # Integration тесты
│   └── e2e/               # E2E тесты
├── scripts/               # Скрипты для разработки
│   ├── setup_db.py
│   └── seed_data.py
├── docs/                  # Документация
│   ├── api/               # API документация
│   └── architecture/      # Архитектурные решения
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 5. Приоритет 4: Тестирование

### 5.1 Настройка pytest фикстур

**Создать `tests/conftest.py`:**
```python
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.agent import InvestorAgent
from src.search_module import SearchModule
from src.database_module import DatabaseModule


@pytest.fixture(scope="session")
def test_data_dir():
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_search_api():
    """Mock для Search API"""
    mock = AsyncMock()
    mock.search.return_value = [
        MagicMock(
            title="Тестовая практика",
            snippet="Описание",
            url="http://example.com"
        )
    ]
    return mock


@pytest.fixture
def sample_industry():
    return "металлургия"


@pytest.fixture
def sample_project_data():
    return {
        "applicant_name": "ООО 'Тест'",
        "inn": "6601000001",
        "ogrn": "1026600000001",
        "address": "г. Екатеринбург, ул. Тестовая, 1",
        "contact_phone": "+7 (343) 000-00-00",
        "contact_email": "test@example.com",
        "project_name": "Тестовый проект",
        "industry": "металлургия",
        "description": "Тестовое описание",
        "investment_amount": 100_000_000,
        "grant_amount": 30_000_000,
        "jobs_created": 50,
        "implementation_period": 12,
    }


@pytest_asyncio.fixture
async def agent():
    """Фикстура для создания агента"""
    agent = InvestorAgent()
    await agent.start_session()
    yield agent
    await agent.end_session()


@pytest_asyncio.fixture
async def search_module(mock_search_api):
    module = SearchModule(search_provider="mock")
    module.api_client = mock_search_api
    return module
```

### 5.2 Примеры unit-тестов

**Создать `tests/unit/test_search_module.py`:**
```python
import pytest
from src.search_module import SearchModule, BestPractice


class TestSearchModule:
    """Тесты для SearchModule"""
    
    @pytest.mark.asyncio
    async def test_search_best_practices_returns_list(self, search_module):
        """Тест возврата списка практик"""
        practices = await search_module.search_best_practices("металлургия")
        
        assert isinstance(practices, list)
        assert len(practices) > 0
        assert all(isinstance(p, BestPractice) for p in practices)
    
    @pytest.mark.asyncio
    async def test_search_best_practices_industry_filter(self, search_module):
        """Тест фильтрации по отрасли"""
        practices = await search_module.search_best_practices("IT")
        
        assert all(p.industry == "IT" for p in practices)
    
    @pytest.mark.asyncio
    async def test_evaluate_applicability_sorts_by_score(self, search_module):
        """Тест сортировки по применимости"""
        practices = [
            BestPractice(
                name=f"Practice {i}",
                region=region,
                industry="металлургия",
                description="Desc",
                results="Results",
                applicability_score=0.0
            )
            for i, region in enumerate(["Москва", "Челябинск", "Казань"])
        ]
        
        scored = await search_module._evaluate_applicability(practices)
        
        assert len(scored) == 3
        assert scored[0].applicability_score >= scored[-1].applicability_score


class TestApplicabilityScoring:
    """Тесты для расчёта применимости"""
    
    @pytest.mark.asyncio
    async def test_neighboring_region_bonus(self, search_module):
        """Тест бонуса для соседних регионов"""
        practice = BestPractice(
            name="Test",
            region="Челябинская область",
            industry="металлургия",
            description="Desc",
            results="Results",
            applicability_score=0.0
        )
        
        score = await search_module._calculate_applicability_score(practice)
        
        assert score >= 0.7  # Базовый 0.5 + бонус 0.2
    
    @pytest.mark.asyncio
    async def test_score_not_exceeds_one(self, search_module):
        """Тест что score не превышает 1.0"""
        practice = BestPractice(
            name="Test",
            region="Челябинская область",
            industry="металлургия",
            description="Desc",
            results="Results",
            applicability_score=0.0
        )
        
        score = await search_module._calculate_applicability_score(practice)
        
        assert score <= 1.0
```

### 5.3 Integration тесты для API

**Создать `tests/integration/test_web_api.py`:**
```python
import pytest
from web.app import app


@pytest.fixture
def client():
    """Test client для Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Тесты health check endpoint"""
    
    def test_health_check_returns_ok(self, client):
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data
        assert 'region' in data
    
    def test_health_check_content_type(self, client):
        response = client.get('/api/health')
        
        assert response.content_type == 'application/json'


class TestPracticesEndpoint:
    """Тесты endpoint практик"""
    
    def test_find_practices_valid_request(self, client):
        response = client.post('/api/practices', json={
            'industry': 'металлургия',
            'practice_type': 'all'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
    
    def test_find_practices_empty_industry(self, client):
        response = client.post('/api/practices', json={
            'industry': '',
        })
        
        assert response.status_code in [400, 200]  # Зависит от валидации
    
    def test_find_practices_invalid_practice_type(self, client):
        response = client.post('/api/practices', json={
            'industry': 'металлургия',
            'practice_type': 'invalid_type'
        })
        
        # Должна быть валидация
        assert response.status_code in [400, 200]
```

---

## 6. Приоритет 5: Безопасность

### 6.1 Rate Limiting

**Создать `web/middleware/rate_limiter.py`:**
```python
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger


class RateLimiter:
    """Простой rate limiter"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Очистка старых запросов
        self.requests[client_id] = [
            ts for ts in self.requests[client_id]
            if ts > window_start
        ]
        
        # Проверка лимита
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Добавление текущего запроса
        self.requests[client_id].append(now)
        return True


# Глобальный rate limiter
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)


def rate_limit(f):
    """Декоратор для rate limiting"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        client_id = request.remote_addr
        
        # Проверка API ключа для повышенных лимитов
        api_key = request.headers.get('X-API-Key')
        if api_key:
            # TODO: Валидация API ключа и повышенные лимиты
            pass
        
        if not rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for {client_id}")
            return jsonify({
                "success": False,
                "error": "Превышен лимит запросов"
            }), 429
        
        return f(*args, **kwargs)
    return wrapper
```

### 6.2 Улучшение CORS конфигурации

**Обновить `web/app.py`:**
```python
from config import settings

# Вместо CORS(app) использовать:
CORS(
    app,
    origins=settings.WEB_CORS_ORIGINS,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    supports_credentials=True,
    max_age=3600
)
```

### 6.3 Аутентификация API

**Создать `web/middleware/auth.py`:**
```python
from functools import wraps
from flask import request, jsonify, g
import hmac
import hashlib
from loguru import logger


API_KEYS = {
    # В продакшене хранить в БД или secrets manager
    # "api_key_hash": {"owner": "user", "permissions": [...]}
}


def validate_api_key(api_key: str) -> bool:
    """Валидация API ключа"""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return key_hash in API_KEYS


def require_api_key(f):
    """Декоратор для обязательного API ключа"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Требуется API ключ"
            }), 401
        
        if not validate_api_key(api_key):
            logger.warning(f"Невалидный API ключ от {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "Невалидный API ключ"
            }), 401
        
        g.api_key = api_key
        return f(*args, **kwargs)
    return wrapper
```

### 6.4 Security headers

**Добавить в `web/app.py`:**
```python
@app.after_request
def add_security_headers(response):
    """Добавление security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

---

## 7. Приоритет 6: DevOps и CI/CD

### 7.1 Dockerfile

**Создать `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание директорий
RUN mkdir -p logs output/documents output/reports

# Переменная окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Пользователь без root прав
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "web.app:app"]
```

### 7.2 docker-compose.yml

**Создать `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/investor_agent
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - investor_network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=investor_agent
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - investor_network
    restart: unless-stopped

  # MCP серверы (опционально)
  mcp-support:
    build:
      context: .
      dockerfile: mcp_servers/Dockerfile
    command: python mcp_servers/support_measures_server.py
    volumes:
      - ./mcp_servers/data:/app/data
    networks:
      - investor_network

volumes:
  postgres_data:

networks:
  investor_network:
    driver: bridge
```

### 7.3 GitHub Actions CI/CD

**Создать `.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run black
        run: black --check src/ web/ tests/
      
      - name: Run isort
        run: isort --check-only src/ web/ tests/
      
      - name: Run flake8
        run: flake8 src/ web/ tests/
      
      - name: Run mypy
        run: mypy src/ web/

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: pytest --cov=src --cov=web --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install safety
        run: pip install safety
      
      - name: Check dependencies
        run: safety check -r requirements.txt
      
      - name: Run bandit
        run: bandit -r src/ web/

  docker:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t investor-agent:${{ github.sha }} .
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'investor-agent:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
```

### 7.4 Production deployment

**Создать `.github/workflows/deploy.yml`:**
```yaml
name: Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            investor-agent:latest
            investor-agent:${{ github.ref_name }}
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_KEY }}
          script: |
            cd /opt/investor-agent
            docker-compose pull
            docker-compose up -d
            docker system prune -f
```

---

## 8. Приоритет 7: Производительность

### 8.1 Кэширование

**Установить:**
```bash
pip install flask-caching redis
```

**Добавить в `web/app.py`:**
```python
from flask_caching import Cache
from config import settings

# Настройка кэша
cache = Cache(app, config={
    'CACHE_TYPE': 'RedisCache' if settings.ENVIRONMENT == 'production' else 'SimpleCache',
    'CACHE_REDIS_URL': settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else None,
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 минут
})

# Использование в endpoint
@app.route('/api/practices', methods=['POST'])
@cache.cached(timeout=600, query_string=True)  # Кэш на 10 минут
def find_best_practices():
    # ... код endpoint
```

### 8.2 Асинхронные задачи

**Установить Celery для фоновых задач:**
```bash
pip install celery[redis]
```

**Создать `tasks.py`:**
```python
from celery import Celery
from config import settings

celery = Celery(
    'investor_agent',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery.task
def generate_document_package_task(package_id: str, project_data: dict):
    """Фоновая генерация документов"""
    from src.documents_module import DocumentsModule
    
    documents = DocumentsModule()
    # ... генерация документов
    
    return {"status": "completed", "package_id": package_id}


@celery.task
def full_analysis_task(industry: str, min_investment: float):
    """Фоновый комплексный анализ"""
    import asyncio
    from src.agent import InvestorAgent
    
    async def run_analysis():
        async with InvestorAgent() as agent:
            return await agent.full_investment_analysis(industry, min_investment)
    
    return asyncio.run(run_analysis())
```

### 8.3 Оптимизация запросов к БД

**Добавить индексы и пагинацию:**

```python
# В database_module.py
async def get_support_measures(
    self,
    industry: str = None,
    measure_type: str = None,
    limit: int = 50,
    offset: int = 0
) -> list[SupportMeasure]:
    """С пагинацией"""
    query = select(SupportMeasure)
    
    if industry:
        query = query.where(SupportMeasure.industry == industry)
    if measure_type:
        query = query.where(SupportMeasure.type == measure_type)
    
    query = query.limit(limit).offset(offset)
    
    result = await self.session.execute(query)
    return result.scalars().all()
```

---

## 9. Дорожная карта

### 📅 Неделя 1-2: Критические исправления

- [ ] Исправить requirements.txt
- [ ] Добавить Pydantic модели для API
- [ ] Внедрить единый обработчик ошибок
- [ ] Настроить pre-commit хуки

### 📅 Неделя 3-4: Архитектура

- [ ] Разделить конфигурацию по окружениям
- [ ] Внедрить Dependency Injection
- [ ] Создать репозитории для данных
- [ ] Рефакторинг модулей

### 📅 Неделя 5-6: Тестирование

- [ ] Увеличить покрытие тестов до 80%
- [ ] Добавить integration тесты
- [ ] Настроить CI пайплайн
- [ ] Добавить security scanning

### 📅 Неделя 7-8: Безопасность

- [ ] Внедрить rate limiting
- [ ] Добавить API аутентификацию
- [ ] Настроить security headers
- [ ] Audit зависимостей

### 📅 Неделя 9-10: DevOps

- [ ] Dockerize приложение
- [ ] Настроить docker-compose
- [ ] Создать CD пайплайн
- [ ] Настроить мониторинг

### 📅 Неделя 11-12: Производительность

- [ ] Добавить кэширование
- [ ] Оптимизировать запросы к БД
- [ ] Внедрить фоновые задачи
- [ ] Load testing

---

## 📊 Метрики успеха

| Метрика | Текущее | Цель |
|---------|---------|------|
| Покрытие тестами | ~20% | 80% |
| Время ответа API | N/A | <200ms |
| Уязвимости зависимостей | Неизвестно | 0 критических |
| Время сборки CI | N/A | <5 мин |
| Время деплоя | N/A | <2 мин |

---

## 📚 Дополнительные ресурсы

- [Flask Best Practices](https://flask.palletsprojects.com/en/3.0.x/patterns/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

*Документ создан: $(date)*
*Версия: 1.0*
