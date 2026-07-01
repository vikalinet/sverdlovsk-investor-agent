"""
Базовая конфигурация для всех окружений
Использует pydantic-settings для валидации и загрузки из .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional
from pathlib import Path
import os


class BaseSettingsModel(BaseSettings):
    """Базовая модель настроек"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Игнорировать неизвестные переменные
    )
    
    # ============================================================
    # Приложение
    # ============================================================
    APP_NAME: str = Field(default="Investor Agent", max_length=100)
    ENVIRONMENT: str = Field(default="development", pattern="^(development|production|testing)$")
    DEBUG: bool = Field(default=False)
    VERSION: str = Field(default="1.0.0")
    
    # ============================================================
    # Регион
    # ============================================================
    REGION_NAME: str = Field(default="Свердловская область", max_length=200)
    REGION_CODE: str = Field(default="66", max_length=10)
    REGION_CAPITAL: str = Field(default="Екатеринбург", max_length=100)
    
    # Приоритетные отрасли
    PRIORITY_INDUSTRIES: List[str] = Field(
        default=[
            "металлургия",
            "машиностроение",
            "химическая промышленность",
            "IT и цифровые технологии",
            "логистика и транспорт",
            "сельское хозяйство",
            "туризм"
        ]
    )
    
    # ============================================================
    # База данных
    # ============================================================
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///data/main.db")
    DATABASE_ECHO: bool = Field(default=False)  # Логирование SQL запросов
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    
    # ============================================================
    # Поиск API
    # ============================================================
    SEARCH_API_KEY: str = Field(default="")
    SEARCH_PROVIDER: str = Field(default="mock", pattern="^(mock|yandex|google)$")
    SEARCH_MAX_RESULTS: int = Field(default=10, ge=1, le=100)
    SEARCH_TIMEOUT: int = Field(default=30, ge=5, le=120)
    
    # Регионы для сравнения
    COMPARE_REGIONS: List[str] = Field(
        default=[
            "Московская область",
            "Ленинградская область",
            "Татарстан",
            "Башкортостан",
            "Челябинская область",
            "Пермский край"
        ]
    )
    
    # ============================================================
    # MCP серверы
    # ============================================================
    MCP_SUPPORT_MEASURES_URL: str = Field(default="")
    MCP_INVESTMENT_OBJECTS_URL: str = Field(default="")
    MCP_BUSINESS_REGISTRY_URL: str = Field(default="")
    
    # ============================================================
    # Документы
    # ============================================================
    DOCUMENTS_DIR: str = Field(default="output/documents")
    TEMPLATES_DIR: str = Field(default="templates/documents")
    SUPPORTED_FORMATS: List[str] = Field(default=["docx", "pdf"])
    
    # ============================================================
    # Логирование
    # ============================================================
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FILE: str = Field(default="logs/agent.log")
    LOG_FORMAT: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    LOG_ROTATION: str = Field(default="10 MB")
    LOG_RETENTION: str = Field(default="30 days")
    LOG_COMPRESSION: str = Field(default="zip")
    
    # ============================================================
    # Web сервер
    # ============================================================
    WEB_HOST: str = Field(default="0.0.0.0")
    WEB_PORT: int = Field(default=5000, ge=1, le=65535)
    WEB_WORKERS: int = Field(default=4, ge=1, le=16)
    WEB_CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])
    WEB_CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    WEB_CORS_HEADERS: List[str] = Field(default=["Content-Type", "Authorization", "X-API-Key"])
    
    # ============================================================
    # Безопасность
    # ============================================================
    API_KEY_HEADER: str = Field(default="X-API-Key")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    SECRET_KEY: Optional[str] = Field(default=None, min_length=32)
    
    # ============================================================
    # Кэширование (опционально)
    # ============================================================
    CACHE_TYPE: str = Field(default="simple", pattern="^(simple|redis|memcached)$")
    CACHE_DEFAULT_TIMEOUT: int = Field(default=300, ge=0, le=3600)
    REDIS_URL: Optional[str] = Field(default=None)
    
    # ============================================================
    # Аналитика
    # ============================================================
    MIN_INVESTMENT_AMOUNT: float = Field(default=10_000_000, gt=0)
    MAX_PAYBACK_PERIOD: int = Field(default=5, ge=1, le=20)
    
    # ============================================================
    # Валидаторы
    # ============================================================
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def generate_secret_key(cls, v: Optional[str], info) -> Optional[str]:
        """Генерация секретного ключа если не указан"""
        if v is None or v.strip() == "":
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    @field_validator("LOG_FILE", "DOCUMENTS_DIR", "TEMPLATES_DIR")
    @classmethod
    def resolve_paths(cls, v: str) -> str:
        """Преобразование относительных путей в абсолютные"""
        if not os.path.isabs(v):
            base_dir = Path(__file__).resolve().parent.parent
            return str(base_dir / v)
        return v
    
    # ============================================================
    # Методы
    # ============================================================
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"
    
    def get_database_config(self) -> dict:
        """Конфигурация для SQLAlchemy"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DATABASE_ECHO,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
        }
    
    def get_logging_config(self) -> dict:
        """Конфигурация для логирования"""
        return {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
            "file": self.LOG_FILE,
            "rotation": self.LOG_ROTATION,
            "retention": self.LOG_RETENTION,
            "compression": self.LOG_COMPRESSION,
        }
    
    def get_web_config(self) -> dict:
        """Конфигурация для веб-сервера"""
        return {
            "host": self.WEB_HOST,
            "port": self.WEB_PORT,
            "workers": self.WEB_WORKERS,
            "cors_origins": self.WEB_CORS_ORIGINS,
            "cors_methods": self.WEB_CORS_METHODS,
            "cors_headers": self.WEB_CORS_HEADERS,
        }
    
    def get_search_config(self) -> dict:
        """Конфигурация для поиска"""
        return {
            "api_key": self.SEARCH_API_KEY,
            "provider": self.SEARCH_PROVIDER,
            "max_results": self.SEARCH_MAX_RESULTS,
            "timeout": self.SEARCH_TIMEOUT,
            "regions_to_compare": self.COMPARE_REGIONS,
        }
    
    def get_mcp_config(self) -> dict:
        """Конфигурация для MCP серверов"""
        return {
            "support_measures": self.MCP_SUPPORT_MEASURES_URL,
            "investment_objects": self.MCP_INVESTMENT_OBJECTS_URL,
            "business_registry": self.MCP_BUSINESS_REGISTRY_URL,
        }
