"""
Репозиторий для инвестиционных объектов

Использование:
    from src.repositories.investment_objects import InvestmentObjectsRepository
    
    repo = InvestmentObjectsRepository()
    objects = await repo.find_by_location("Екатеринбург")
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

from src.repositories.base import BaseRepository


class InvestmentObjectModel(BaseModel):
    """Модель инвестиционного объекта"""
    id: str = Field(..., max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., pattern="^(площадка|бизнес|объект|парк)$")
    location: str = Field(..., max_length=300)
    address: Optional[str] = Field(None, max_length=500)
    area: Optional[float] = Field(None, gt=0)  # Площадь в м²
    price: Optional[float] = Field(None, ge=0)  # Цена/инвестиции
    description: str = Field(default="", max_length=2000)
    infrastructure: List[str] = Field(default=[])
    industry: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", pattern="^(active|reserved|sold|inactive)$")
    contacts: Optional[str] = Field(None)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(None)
    
    class Config:
        from_attributes = True


class InvestmentObjectsRepository(BaseRepository[InvestmentObjectModel]):
    """
    Репозиторий для инвестиционных объектов
    
    Источники данных:
    - MCP сервер (приоритет)
    - Локальная база данных
    - In-memory хранилище (fallback)
    """
    
    def __init__(self, database_module=None):
        super().__init__()
        self._database = database_module
        self._storage: Dict[str, InvestmentObjectModel] = {}
        self._initialize_default_objects()
        logger.info("InvestmentObjectsRepository инициализирован")
    
    def _initialize_default_objects(self) -> None:
        """Инициализация объектами по умолчанию"""
        default_objects = [
            {
                "id": "INV-SVE-001",
                "name": "Индустриальный парк 'Титановая долина'",
                "type": "парк",
                "location": "Верхняя Салда",
                "address": "Свердловская обл., г. Верхняя Салда",
                "area": 50000,
                "price": 500_000_000,
                "description": "Готовая инфраструктура для производств полного цикла",
                "infrastructure": [
                    "Электроснабжение",
                    "Газоснабжение",
                    "Водоснабжение",
                    "Ж/д подъезд",
                    "Автодороги"
                ],
                "industry": "металлургия",
                "status": "active",
                "contacts": "info@titan-valley.ru"
            },
            {
                "id": "INV-SVE-002",
                "name": "Технопарк 'Екатеринбург'",
                "type": "парк",
                "location": "Екатеринбург",
                "address": "г. Екатеринбург, ул. Инновационная, 1",
                "area": 20000,
                "price": 200_000_000,
                "description": "Технопарк для IT и высокотехнологичных компаний",
                "infrastructure": [
                    "Оптоволоконная связь",
                    "Коворкинг",
                    "Конференц-залы",
                    "Лаборатории"
                ],
                "industry": "IT и цифровые технологии",
                "status": "active",
                "contacts": "info@technopark-ekb.ru"
            },
            {
                "id": "INV-SVE-003",
                "name": "Логистический комплекс 'Кольцово'",
                "type": "объект",
                "location": "Кольцово",
                "address": "Свердловская обл., пос. Кольцово",
                "area": 15000,
                "price": 150_000_000,
                "description": "Современный логистический комплекс рядом с аэропортом",
                "infrastructure": [
                    "Складские помещения",
                    "Погрузочная техника",
                    "Таможенный терминал",
                    "Офисные помещения"
                ],
                "industry": "логистика и транспорт",
                "status": "active",
                "contacts": "logistics@koltsovo.ru"
            }
        ]
        
        for obj_data in default_objects:
            obj = InvestmentObjectModel(**obj_data)
            self._storage[obj.id] = obj
            logger.debug(f"Добавлен объект: {obj.id}")
    
    async def get_by_id(self, id: str) -> Optional[InvestmentObjectModel]:
        """Получение объекта по ID"""
        # Проверка кэша
        cached = self._cache_get(f"object:{id}")
        if cached:
            logger.debug(f"Найдено в кэше: {id}")
            return cached
        
        # Поиск в хранилище
        if id in self._storage:
            obj = self._storage[id]
            self._cache_set(f"object:{id}", obj)
            return obj
        
        logger.warning(f"Объект не найден: {id}")
        return None
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[InvestmentObjectModel]:
        """Получение всех объектов с пагинацией"""
        objects = [obj for obj in self._storage.values() if obj.status == "active"]
        return objects[offset:offset + limit]
    
    async def find_by(
        self,
        filters: Dict[str, Any],
        limit: int = 100
    ) -> List[InvestmentObjectModel]:
        """
        Поиск объектов по фильтрам
        
        Поддерживаемые фильтры:
        - type: Тип объекта
        - location: Локация
        - industry: Отрасль
        - min_price: Минимальная цена
        - max_price: Максимальная цена
        - min_area: Минимальная площадь
        - max_area: Максимальная площадь
        - infrastructure: Элемент инфраструктуры
        """
        results = []
        
        for obj in self._storage.values():
            if obj.status != "active":
                continue
            
            match = True
            
            # Фильтр по типу
            if "type" in filters and filters["type"]:
                if obj.type != filters["type"]:
                    match = False
            
            # Фильтр по локации
            if "location" in filters and filters["location"]:
                if filters["location"].lower() not in obj.location.lower():
                    match = False
            
            # Фильтр по отрасли
            if "industry" in filters and filters["industry"]:
                if obj.industry and filters["industry"].lower() not in obj.industry.lower():
                    match = False
            
            # Фильтр по цене
            if "min_price" in filters and filters["min_price"]:
                if obj.price and obj.price < filters["min_price"]:
                    match = False
            
            if "max_price" in filters and filters["max_price"]:
                if obj.price and obj.price > filters["max_price"]:
                    match = False
            
            # Фильтр по площади
            if "min_area" in filters and filters["min_area"]:
                if obj.area and obj.area < filters["min_area"]:
                    match = False
            
            # Фильтр по инфраструктуре
            if "infrastructure" in filters and filters["infrastructure"]:
                infra_item = filters["infrastructure"].lower()
                if not any(infra_item in item.lower() for item in obj.infrastructure):
                    match = False
            
            if match:
                results.append(obj)
                if len(results) >= limit:
                    break
        
        logger.info(f"Найдено {len(results)} инвестиционных объектов")
        return results
    
    async def find_by_location(
        self,
        location: str,
        limit: int = 100
    ) -> List[InvestmentObjectModel]:
        """Поиск объектов по локации"""
        return await self.find_by({"location": location}, limit=limit)
    
    async def find_by_industry(
        self,
        industry: str,
        limit: int = 100
    ) -> List[InvestmentObjectModel]:
        """Поиск объектов по отрасли"""
        return await self.find_by({"industry": industry}, limit=limit)
    
    async def find_by_price_range(
        self,
        min_price: float,
        max_price: float,
        limit: int = 100
    ) -> List[InvestmentObjectModel]:
        """Поиск объектов по диапазону цены"""
        return await self.find_by({
            "min_price": min_price,
            "max_price": max_price
        }, limit=limit)
    
    async def create(self, entity) -> InvestmentObjectModel:
        """Создание инвестиционного объекта"""
        if isinstance(entity, dict):
            obj = InvestmentObjectModel(**entity)
        else:
            obj = entity
        
        self._storage[obj.id] = obj
        self._cache_invalidate(f"object:{obj.id}")
        logger.info(f"Создан инвестиционный объект: {obj.id}")
        return obj
    
    async def update(
        self,
        id: str,
        data: Dict[str, Any]
    ) -> Optional[InvestmentObjectModel]:
        """Обновление объекта"""
        if id not in self._storage:
            logger.warning(f"Объект не найден для обновления: {id}")
            return None
        
        obj = self._storage[id]
        update_data = obj.model_dump()
        update_data.update(data)
        update_data["updated_at"] = datetime.now().isoformat()
        
        updated_obj = InvestmentObjectModel(**update_data)
        self._storage[id] = updated_obj
        self._cache_invalidate(f"object:{id}")
        
        logger.info(f"Обновлён инвестиционный объект: {id}")
        return updated_obj
    
    async def delete(self, id: str) -> bool:
        """Удаление объекта (мягкое)"""
        if id in self._storage:
            # Мягкое удаление - изменение статуса
            await self.update(id, {"status": "inactive"})
            logger.info(f"Деактивирован объект: {id}")
            return True
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Подсчёт количества объектов"""
        if not filters:
            return len([o for o in self._storage.values() if o.status == "active"])
        
        matching = await self.find_by(filters, limit=1000)
        return len(matching)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики по объектам"""
        objects = list(self._storage.values())
        active_objects = [o for o in objects if o.status == "active"]
        
        return {
            "total": len(objects),
            "active": len(active_objects),
            "by_type": {
                "парк": len([o for o in active_objects if o.type == "парк"]),
                "площадка": len([o for o in active_objects if o.type == "площадка"]),
                "объект": len([o for o in active_objects if o.type == "объект"]),
                "бизнес": len([o for o in active_objects if o.type == "бизнес"]),
            },
            "by_industry": self._group_by_industry(active_objects),
            "total_investment": sum(o.price or 0 for o in active_objects),
            "avg_price": sum(o.price or 0 for o in active_objects) / max(len(active_objects), 1),
            "total_area": sum(o.area or 0 for o in active_objects),
        }
    
    def _group_by_industry(self, objects: List[InvestmentObjectModel]) -> Dict[str, int]:
        """Группировка по отраслям"""
        result = {}
        for obj in objects:
            industry = obj.industry or "Другое"
            result[industry] = result.get(industry, 0) + 1
        return result
