"""
Конфигурация для тестирования (testing)
"""
from config.base import BaseSettingsModel
from pydantic import Field
from typing import List


class TestingSettings(BaseSettingsModel):
    """Настройки для тестирования"""
    
    # Приложение
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    APP_NAME: str = "Investor Agent (Test)"
    
    # Логирование - минимальное для тестов
    LOG_LEVEL: str = "ERROR"
    LOG_ECHO_SQL: bool = False
    
    # База данных - SQLite in-memory для скорости
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 1
    DATABASE_MAX_OVERFLOW: int = 0
    
    # Web
    WEB_HOST: str = "127.0.0.1"
    WEB_PORT: int = 5001  # Отличный от dev порт
    WEB_WORKERS: int = 1
    WEB_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    TESTING: bool = True  # Флаг для Flask
    
    # Кэширование - отключено для тестов
    CACHE_TYPE: str = "simple"
    CACHE_DEFAULT_TIMEOUT: int = 0  # Без кэширования
    
    # Безопасность - упрощённая для тестов
    RATE_LIMIT_PER_MINUTE: int = 10000  # Очень высокий лимит
    ENABLE_RATE_LIMITING: bool = False
    SECRET_KEY: str = "test-secret-key-for-testing-only"
    
    # Поиск - только mock
    SEARCH_PROVIDER: str = "mock"
    SEARCH_MAX_RESULTS: int = 3
    SEARCH_TIMEOUT: int = 5
    
    # MCP серверы - mock
    MCP_SUPPORT_MEASURES_URL: str = ""
    MCP_INVESTMENT_OBJECTS_URL: str = ""
    MCP_BUSINESS_REGISTRY_URL: str = ""
    
    # Пути - временные
    LOG_FILE: str = "logs/test/agent.log"
    DOCUMENTS_DIR: str = "output/test/documents"
    TEMPLATES_DIR: str = "templates/documents"
    
    # Флаги для тестирования
    AUTO_RELOAD: bool = False
    SHOW_SQL_QUERIES: bool = False
    ENABLE_PROFILING: bool = False
    MOCK_EXTERNAL_APIS: bool = True
    
    # Тестовые данные
    TEST_INDUSTRY: str = "металлургия"
    TEST_MIN_INVESTMENT: float = 10_000_000
