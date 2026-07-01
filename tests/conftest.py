"""
pytest фикстуры для тестирования

Использование:
    def test_example(sample_industry, mock_search_api):
        # Тест с использованием фикстур
"""
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Generator, Dict, Any
import asyncio

# Импорты для фикстур
from config import settings, ENVIRONMENT
from src.agent import InvestorAgent
from src.repositories import SupportMeasuresRepository, InvestmentObjectsRepository
from src.dependencies import get_container, reset_container


# ============================================================
# Конфигурация pytest
# ============================================================

def pytest_configure(config):
    """Настройка pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )


# ============================================================
# Фикстуры окружения
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def set_testing_environment():
    """Установка testing окружения для всех тестов"""
    import os
    os.environ["ENVIRONMENT"] = "testing"
    yield
    os.environ.pop("ENVIRONMENT", None)


# ============================================================
# Фикстуры данных
# ============================================================

@pytest.fixture
def sample_industry() -> str:
    """Пример отрасли для тестов"""
    return "металлургия"


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Пример данных проекта"""
    return {
        "applicant_name": "ООО 'Тест'",
        "inn": "6601000001",
        "ogrn": "1026600000001",
        "address": "г. Екатеринбург, ул. Тестовая, 1",
        "contact_phone": "+7 (343) 000-00-00",
        "contact_email": "test@example.com",
        "project_name": "Тестовый проект",
        "industry": "металлургия",
        "description": "Тестовое описание проекта",
        "investment_amount": 100_000_000,
        "grant_amount": 30_000_000,
        "jobs_created": 50,
        "implementation_period": 12,
        "justification": "Тестовое обоснование",
        "expected_results": "Тестовые результаты"
    }


@pytest.fixture
def sample_filters() -> Dict[str, Any]:
    """Пример фильтров для поиска"""
    return {
        "industry": "металлургия",
        "type": "grant",
        "min_amount": 5_000_000
    }


# ============================================================
# Фикстуры для моков
# ============================================================

@pytest.fixture
def mock_search_api() -> AsyncMock:
    """Mock для Search API"""
    mock = AsyncMock()
    mock.search.return_value = [
        MagicMock(
            title="Тестовая практика",
            snippet="Описание тестовой практики",
            url="http://example.com/test"
        )
    ]
    return mock


@pytest.fixture
def mock_agent() -> AsyncMock:
    """Mock для InvestorAgent"""
    mock = AsyncMock(spec=InvestorAgent)
    mock.find_best_practices.return_value = []
    mock.find_investment_opportunities.return_value = []
    mock.find_support_measures.return_value = []
    return mock


@pytest.fixture
def mock_database_session() -> AsyncMock:
    """Mock для сессии базы данных"""
    return AsyncMock()


# ============================================================
# Фикстуры для репозиториев
# ============================================================

@pytest.fixture
def support_measures_repo() -> SupportMeasuresRepository:
    """Репозиторий мер поддержки для тестов"""
    return SupportMeasuresRepository()


@pytest.fixture
def investment_objects_repo() -> InvestmentObjectsRepository:
    """Репозиторий инвестобъектов для тестов"""
    return InvestmentObjectsRepository()


@pytest_asyncio.fixture
async def populated_support_repo() -> SupportMeasuresRepository:
    """Репозиторий с тестовыми данными"""
    repo = SupportMeasuresRepository()
    
    # Добавление тестовых мер
    await repo.create({
        "id": "TEST-GRANT-001",
        "name": "Тестовый грант",
        "type": "grant",
        "max_amount": 10_000_000,
        "industry": "металлургия",
        "is_active": True
    })
    
    await repo.create({
        "id": "TEST-SUBSIDY-001",
        "name": "Тестовая субсидия",
        "type": "subsidy",
        "max_amount": 5_000_000,
        "industry": "сельское хозяйство",
        "is_active": True
    })
    
    return repo


@pytest_asyncio.fixture
async def populated_objects_repo() -> InvestmentObjectsRepository:
    """Репозиторий с тестовыми объектами"""
    repo = InvestmentObjectsRepository()
    
    # Добавление тестовых объектов
    await repo.create({
        "id": "TEST-OBJ-001",
        "name": "Тестовый объект",
        "type": "площадка",
        "location": "Екатеринбург",
        "price": 50_000_000,
        "area": 1000,
        "industry": "металлургия",
        "status": "active"
    })
    
    return repo


# ============================================================
# Фикстуры для DI контейнера
# ============================================================

@pytest_asyncio.fixture
async def agent_session() -> Generator[InvestorAgent, None, None]:
    """Сессия агента для тестов"""
    from src.dependencies import get_agent_session
    
    async with get_agent_session() as agent:
        yield agent


@pytest_asyncio.fixture(autouse=True)
async def reset_di_container():
    """Автоматический сброс DI контейнера между тестами"""
    yield
    reset_container()


# ============================================================
# Фикстуры для Flask API
# ============================================================

@pytest.fixture
def flask_app():
    """Flask приложение для тестов"""
    from web.app import app
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    yield app


@pytest.fixture
def test_client(flask_app):
    """Test client для Flask"""
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def api_headers() -> Dict[str, str]:
    """Заголовки для API запросов"""
    return {
        'Content-Type': 'application/json',
        'X-API-Key': 'demo-api-key-12345'
    }


# ============================================================
# Фикстуры для временных файлов
# ============================================================

@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Временная директория для выходных файлов"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_logs_dir(tmp_path) -> Path:
    """Временная директория для логов"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


# ============================================================
# Утилиты для тестов
# ============================================================

@pytest.fixture
def async_runner():
    """Утилита для запуска асинхронных функций в тестах"""
    def run(coro):
        return asyncio.run(coro)
    return run


def create_test_api_key(permissions=None):
    """Создание тестового API ключа"""
    from web.middleware.auth import create_api_key
    
    return create_api_key(
        owner="test_user",
        permissions=permissions or ["read", "write"],
        expires_days=365
    )
