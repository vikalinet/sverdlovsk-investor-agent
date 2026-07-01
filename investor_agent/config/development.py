"""
Конфигурация для разработки (development)
"""
from config.base import BaseSettingsModel
from pydantic import Field
from typing import List


class DevelopmentSettings(BaseSettingsModel):
    """Настройки для разработки"""
    
    # Приложение
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Investor Agent (Dev)"
    
    # Логирование - более подробное
    LOG_LEVEL: str = "DEBUG"
    LOG_ECHO_SQL: bool = True
    
    # База данных - SQLite для простоты
    DATABASE_URL: str = "sqlite+aiosqlite:///data/dev.db"
    DATABASE_ECHO: bool = True
    
    # Web
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 5000
    WEB_WORKERS: int = 1  # Один воркер для отладки
    WEB_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite
        "http://127.0.0.1:5173"
    ]
    
    # Кэширование - простой in-memory
    CACHE_TYPE: str = "simple"
    CACHE_DEFAULT_TIMEOUT: int = 60  # 1 минута для быстрой отладки
    
    # Безопасность - упрощённая для разработки
    RATE_LIMIT_PER_MINUTE: int = 1000  # Высокий лимит
    SECRET_KEY: str = "dev-secret-key-not-for-production-change-in-prod"
    
    # Поиск - mock provider
    SEARCH_PROVIDER: str = "mock"
    SEARCH_MAX_RESULTS: int = 5  # Меньше результатов для скорости
    
    # Пути
    LOG_FILE: str = "logs/dev/agent.log"
    DOCUMENTS_DIR: str = "output/dev/documents"
    TEMPLATES_DIR: str = "templates/documents"
    
    # Флаги для разработки
    AUTO_RELOAD: bool = True
    SHOW_SQL_QUERIES: bool = True
    ENABLE_PROFILING: bool = False
