"""
Репозитории для доступа к данным

Импорт:
    from src.repositories import (
        SupportMeasuresRepository,
        InvestmentObjectsRepository,
        BaseRepository
    )
"""
from src.repositories.base import BaseRepository, InMemoryRepository
from src.repositories.support_measures import (
    SupportMeasuresRepository,
    SupportMeasureModel
)
from src.repositories.investment_objects import (
    InvestmentObjectsRepository,
    InvestmentObjectModel
)

__all__ = [
    # Базовые классы
    "BaseRepository",
    "InMemoryRepository",
    
    # Репозитории
    "SupportMeasuresRepository",
    "InvestmentObjectsRepository",
    
    # Модели
    "SupportMeasureModel",
    "InvestmentObjectModel",
]
