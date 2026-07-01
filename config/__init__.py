"""
Конфигурация проекта

Использование:
    from config import settings
    
    # Доступ к настройкам
    debug = settings.DEBUG
    db_url = settings.DATABASE_URL
"""
import os
from pathlib import Path

# Определяем текущее окружение
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# Импортируем соответствующую конфигурацию
if ENVIRONMENT == "production":
    from config.production import ProductionSettings as Settings
elif ENVIRONMENT == "testing":
    from config.testing import TestingSettings as Settings
else:
    from config.development import DevelopmentSettings as Settings

# Создаём экземпляр настроек
settings = Settings()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Экспортируем для обратной совместимости
REGION = {
    "name": settings.REGION_NAME,
    "code": settings.REGION_CODE,
    "capital": settings.REGION_CAPITAL
}

__all__ = ["settings", "BASE_DIR", "REGION", "ENVIRONMENT"]
