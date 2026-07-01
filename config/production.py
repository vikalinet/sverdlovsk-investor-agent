"""
Конфигурация для продакшена (production)
"""
from config.base import BaseSettingsModel
from pydantic import Field, field_validator
from typing import List
import os


class ProductionSettings(BaseSettingsModel):
    """Настройки для продакшена"""
    
    # Приложение
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    APP_NAME: str = "Investor Agent"
    
    # Логирование - только важные сообщения
    LOG_LEVEL: str = "WARNING"
    LOG_ECHO_SQL: bool = False
    
    # База данных - PostgreSQL для продакшена
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/investor_agent"
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Web
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 5000
    WEB_WORKERS: int = 4  # Несколько воркеров для производительности
    WEB_CORS_ORIGINS: List[str] = Field(
        default=["https://investor-agent.ru", "https://www.investor-agent.ru"]
    )
    
    # Кэширование - Redis для продакшена
    CACHE_TYPE: str = "redis"
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT: int = 600  # 10 минут
    
    # Безопасность - строгая
    RATE_LIMIT_PER_MINUTE: int = 60  # Строгий лимит
    API_KEY_REQUIRED: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_CORS: bool = True
    
    # Поиск
    SEARCH_PROVIDER: str = Field(default="yandex")  # Реальный поисковый провайдер
    SEARCH_MAX_RESULTS: int = 20
    SEARCH_TIMEOUT: int = 15
    
    # MCP серверы
    MCP_ENABLE_SSL: bool = True
    MCP_TIMEOUT: int = 30
    
    # Пути
    LOG_FILE: str = "logs/prod/agent.log"
    DOCUMENTS_DIR: str = "output/prod/documents"
    TEMPLATES_DIR: str = "templates/documents"
    
    # Флаги для продакшена
    AUTO_RELOAD: bool = False
    SHOW_SQL_QUERIES: bool = False
    ENABLE_PROFILING: bool = False
    
    # ============================================================
    # Валидаторы для продакшена
    # ============================================================
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Проверка что SECRET_KEY установлен в продакшене"""
        if not v or v == "dev-secret-key-not-for-production-change-in-prod":
            # Проверяем переменную окружения
            secret = os.getenv("SECRET_KEY")
            if not secret or len(secret) < 32:
                raise ValueError(
                    "SECRET_KEY должен быть установлен в переменных окружения "
                    "и иметь длину не менее 32 символов"
                )
            return secret
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Проверка что используется PostgreSQL в продакшене"""
        if not v.startswith("postgresql"):
            # Проверяем переменную окружения
            db_url = os.getenv("DATABASE_URL")
            if db_url and db_url.startswith("postgresql"):
                return db_url
            # Если нет - используем значение по умолчанию но с предупреждением
            import warnings
            warnings.warn(
                "Рекомендуется использовать PostgreSQL в продакшене. "
                "Установите DATABASE_URL в переменных окружения."
            )
        return v
    
    @field_validator("WEB_CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Проверка что CORS origins не wildcard в продакшене"""
        if "*" in v:
            raise ValueError(
                "В продакшене запрещено использовать '*' в CORS_ORIGINS. "
                "Укажите конкретные домены."
            )
        return v
