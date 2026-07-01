"""
Репозиторий для мер государственной поддержки

Использование:
    from src.repositories.support_measures import SupportMeasuresRepository
    
    repo = SupportMeasuresRepository()
    measures = await repo.find_by_industry("металлургия")
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

from src.repositories.base import BaseRepository, InMemoryRepository


class SupportMeasureModel(BaseModel):
    """Модель меры поддержки"""
    id: str = Field(..., max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., pattern="^(grant|subsidy|fund|tax_break|other)$")
    max_amount: float = Field(default=0, ge=0)
    min_amount: float = Field(default=0, ge=0)
    description: str = Field(default="", max_length=2000)
    eligibility: Optional[str] = Field(None, max_length=1000)
    documents_required: List[str] = Field(default=[])
    deadline: Optional[str] = Field(None)
    contact_info: Optional[str] = Field(None)
    industry: Optional[str] = Field(None, max_length=100)
    business_size: List[str] = Field(default=["small", "medium", "large"])
    region: str = Field(default="Свердловская область")
    is_active: bool = Field(default=True)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(None)
    
    class Config:
        from_attributes = True


class SupportMeasuresRepository(BaseRepository[SupportMeasureModel]):
    """
    Репозиторий для мер поддержки
    
    Источники данных:
    - MCP сервер (приоритет)
    - Локальная база данных
    - In-memory хранилище (fallback)
    """
    
    def __init__(self, database_module=None):
        super().__init__()
        self._database = database_module
        self._storage: Dict[str, SupportMeasureModel] = {}
        self._initialize_default_measures()
        logger.info("SupportMeasuresRepository инициализирован")
    
    def _initialize_default_measures(self) -> None:
        """Инициализация мерами по умолчанию"""
        default_measures = [
            {
                "id": "GRANT-IND-001",
                "name": "Грант на развитие промышленного производства",
                "type": "grant",
                "max_amount": 30_000_000,
                "min_amount": 5_000_000,
                "description": "Грант на модернизацию производства и закупку оборудования",
                "eligibility": "Промышленные предприятия, создающие от 50 рабочих мест",
                "documents_required": [
                    "Заявка на грант",
                    "Бизнес-план",
                    "Финансовая модель",
                    "Документы о создании рабочих мест"
                ],
                "deadline": "2024-12-31",
                "contact_info": "Министерство инвестиций Свердловской области",
                "industry": "промышленность",
                "business_size": ["medium", "large"],
                "is_active": True
            },
            {
                "id": "SUBSIDY-AGRO-001",
                "name": "Субсидия на развитие сельского хозяйства",
                "type": "subsidy",
                "max_amount": 10_000_000,
                "min_amount": 1_000_000,
                "description": "Компенсация затрат на покупку техники и удобрений",
                "eligibility": "Сельскохозяйственные производители",
                "documents_required": [
                    "Заявление на субсидию",
                    "Расчёт необходимых средств",
                    "Документы на технику"
                ],
                "deadline": "2024-06-30",
                "contact_info": "Министерство АПК Свердловской области",
                "industry": "сельское хозяйство",
                "business_size": ["small", "medium"],
                "is_active": True
            },
            {
                "id": "FUND-IT-001",
                "name": "Фонд поддержки IT-стартапов",
                "type": "fund",
                "max_amount": 50_000_000,
                "min_amount": 5_000_000,
                "description": "Венчурное финансирование IT-проектов",
                "eligibility": "IT-стартапы с работающим прототипом",
                "documents_required": [
                    "Инвестиционная заявка",
                    "Due Diligence пакет",
                    "Презентация продукта"
                ],
                "deadline": None,
                "contact_info": "Фонд развития IT",
                "industry": "IT и цифровые технологии",
                "business_size": ["small"],
                "is_active": True
            }
        ]
        
        for measure_data in default_measures:
            measure = SupportMeasureModel(**measure_data)
            self._storage[measure.id] = measure
            logger.debug(f"Добавлена мера: {measure.id}")
    
    async def get_by_id(self, id: str) -> Optional[SupportMeasureModel]:
        """Получение меры по ID"""
        # Проверка кэша
        cached = self._cache_get(f"measure:{id}")
        if cached:
            logger.debug(f"Найдено в кэше: {id}")
            return cached
        
        # Поиск в хранилище
        if id in self._storage:
            measure = self._storage[id]
            self._cache_set(f"measure:{id}", measure)
            return measure
        
        logger.warning(f"Мера не найдена: {id}")
        return None
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[SupportMeasureModel]:
        """Получение всех мер с пагинацией"""
        measures = list(self._storage.values())
        return measures[offset:offset + limit]
    
    async def find_by(
        self,
        filters: Dict[str, Any],
        limit: int = 100
    ) -> List[SupportMeasureModel]:
        """
        Поиск мер по фильтрам
        
        Поддерживаемые фильтры:
        - industry: Отрасль
        - type: Тип меры (grant, subsidy, fund)
        - business_size: Размер бизнеса
        - is_active: Активность
        - max_amount: Максимальная сумма
        """
        results = []
        
        for measure in self._storage.values():
            if not measure.is_active:
                continue
            
            match = True
            
            # Фильтр по отрасли
            if "industry" in filters and filters["industry"]:
                if measure.industry and filters["industry"].lower() not in measure.industry.lower():
                    match = False
            
            # Фильтр по типу
            if "type" in filters and filters["type"]:
                if measure.type != filters["type"]:
                    match = False
            
            # Фильтр по размеру бизнеса
            if "business_size" in filters and filters["business_size"]:
                if filters["business_size"] not in measure.business_size:
                    match = False
            
            # Фильтр по сумме
            if "min_amount" in filters and filters["min_amount"]:
                if measure.max_amount < filters["min_amount"]:
                    match = False
            
            if match:
                results.append(measure)
                if len(results) >= limit:
                    break
        
        logger.info(f"Найдено {len(results)} мер поддержки")
        return results
    
    async def find_by_industry(
        self,
        industry: str,
        limit: int = 100
    ) -> List[SupportMeasureModel]:
        """Поиск мер по отрасли"""
        return await self.find_by({"industry": industry}, limit=limit)
    
    async def find_by_type(
        self,
        measure_type: str,
        limit: int = 100
    ) -> List[SupportMeasureModel]:
        """Поиск мер по типу"""
        return await self.find_by({"type": measure_type}, limit=limit)
    
    async def create(self, entity) -> SupportMeasureModel:
        """Создание меры поддержки"""
        if isinstance(entity, dict):
            measure = SupportMeasureModel(**entity)
        else:
            measure = entity
        
        self._storage[measure.id] = measure
        self._cache_invalidate(f"measure:{measure.id}")
        logger.info(f"Создана мера поддержки: {measure.id}")
        return measure
    
    async def update(
        self,
        id: str,
        data: Dict[str, Any]
    ) -> Optional[SupportMeasureModel]:
        """Обновление меры поддержки"""
        if id not in self._storage:
            logger.warning(f"Мера не найдена для обновления: {id}")
            return None
        
        measure = self._storage[id]
        update_data = measure.model_dump()
        update_data.update(data)
        update_data["updated_at"] = datetime.now().isoformat()
        
        updated_measure = SupportMeasureModel(**update_data)
        self._storage[id] = updated_measure
        self._cache_invalidate(f"measure:{id}")
        
        logger.info(f"Обновлена мера поддержки: {id}")
        return updated_measure
    
    async def delete(self, id: str) -> bool:
        """Удаление меры поддержки (мягкое)"""
        if id in self._storage:
            # Мягкое удаление - деактивация
            await self.update(id, {"is_active": False})
            logger.info(f"Деактивирована мера поддержки: {id}")
            return True
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Подсчёт количества мер"""
        if not filters:
            return len([m for m in self._storage.values() if m.is_active])
        
        matching = await self.find_by(filters, limit=1000)
        return len(matching)
    
    async def get_active_measures(self) -> List[SupportMeasureModel]:
        """Получение всех активных мер"""
        return [m for m in self._storage.values() if m.is_active]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики по мерам"""
        measures = list(self._storage.values())
        
        return {
            "total": len(measures),
            "active": len([m for m in measures if m.is_active]),
            "by_type": {
                "grant": len([m for m in measures if m.type == "grant" and m.is_active]),
                "subsidy": len([m for m in measures if m.type == "subsidy" and m.is_active]),
                "fund": len([m for m in measures if m.type == "fund" and m.is_active]),
            },
            "total_funding": sum(m.max_amount for m in measures if m.is_active),
            "avg_amount": sum(m.max_amount for m in measures if m.is_active) / max(len(measures), 1)
        }
