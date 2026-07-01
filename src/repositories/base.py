"""
Репозитории для работы с данными

Репозиторий - это паттерн, который абстрагирует доступ к данным
и предоставляет единый интерфейс для бизнес-логики.
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

T = TypeVar('T', bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """
    Базовый класс репозитория
    
    Паттерн: Repository
    Назначение: Абстракция доступа к данным
    
    Args:
        ABC: Абстрактный базовый класс
        Generic[T]: Дженерик для типа сущности
    """
    
    def __init__(self):
        self._cache: Dict[str, T] = {}
        self._cache_ttl: int = 300  # 5 минут
        logger.info(f"{self.__class__.__name__} инициализирован")
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Получение сущности по ID
        
        Args:
            id: Идентификатор сущности
        
        Returns:
            Optional[T]: Сущность или None
        """
        pass
    
    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        Получение всех сущностей с пагинацией
        
        Args:
            limit: Лимит записей
            offset: Смещение
        
        Returns:
            List[T]: Список сущностей
        """
        pass
    
    @abstractmethod
    async def find_by(
        self,
        filters: Dict[str, Any],
        limit: int = 100
    ) -> List[T]:
        """
        Поиск сущностей по фильтрам
        
        Args:
            filters: Словарь фильтров
            limit: Лимит записей
        
        Returns:
            List[T]: Список сущностей
        """
        pass
    
    @abstractmethod
    async def create(self, entity: Union[T, Dict[str, Any]]) -> T:
        """
        Создание сущности
        
        Args:
            entity: Сущность или данные для создания
        
        Returns:
            T: Созданная сущность
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        id: str,
        data: Dict[str, Any]
    ) -> Optional[T]:
        """
        Обновление сущности
        
        Args:
            id: Идентификатор сущности
            data: Данные для обновления
        
        Returns:
            Optional[T]: Обновлённая сущность или None
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Удаление сущности
        
        Args:
            id: Идентификатор сущности
        
        Returns:
            bool: True если успешно
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Подсчёт количества сущностей
        
        Args:
            filters: Опциональные фильтры
        
        Returns:
            int: Количество сущностей
        """
        pass
    
    # ============================================================
    # Вспомогательные методы
    # ============================================================
    
    def _cache_get(self, key: str) -> Optional[T]:
        """Получение из кэша"""
        return self._cache.get(key)
    
    def _cache_set(self, key: str, value: T) -> None:
        """Сохранение в кэш"""
        self._cache[key] = value
        logger.debug(f"Кэшировано: {key}")
    
    def _cache_invalidate(self, key: str) -> None:
        """Инвалидация кэша"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Кэш инвалидирован: {key}")
    
    def _cache_clear(self) -> None:
        """Очистка всего кэша"""
        self._cache.clear()
        logger.info("Кэш очищен")
    
    async def exists(self, id: str) -> bool:
        """Проверка существования сущности"""
        entity = await self.get_by_id(id)
        return entity is not None
    
    async def get_or_none(
        self,
        id: str,
        default: Optional[T] = None
    ) -> Optional[T]:
        """Получение сущности или default"""
        try:
            return await self.get_by_id(id)
        except Exception:
            return default
    
    async def get_list_by_ids(self, ids: List[str]) -> List[T]:
        """Получение списка сущностей по ID"""
        entities = []
        for id in ids:
            entity = await self.get_by_id(id)
            if entity:
                entities.append(entity)
        return entities


class InMemoryRepository(BaseRepository[T]):
    """
    Репозиторий в памяти (для тестов и прототипирования)
    
    Использование:
        class TestRepository(InMemoryRepository[TestEntity]):
            pass
    """
    
    def __init__(self, entity_class: type[T]):
        super().__init__()
        self._storage: Dict[str, T] = {}
        self._entity_class = entity_class
        self._auto_id_counter = 0
        logger.info(f"InMemoryRepository<{entity_class.__name__}> инициализирован")
    
    def _generate_id(self) -> str:
        """Генерация авто-ID"""
        self._auto_id_counter += 1
        return f"auto_{self._auto_id_counter}"
    
    async def get_by_id(self, id: str) -> Optional[T]:
        return self._storage.get(id)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        items = list(self._storage.values())
        return items[offset:offset + limit]
    
    async def find_by(self, filters: Dict[str, Any], limit: int = 100) -> List[T]:
        results = []
        for entity in self._storage.values():
            match = True
            for key, value in filters.items():
                if hasattr(entity, key):
                    if getattr(entity, key) != value:
                        match = False
                        break
                elif isinstance(entity, dict):
                    if entity.get(key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            if match:
                results.append(entity)
                if len(results) >= limit:
                    break
        return results
    
    async def create(self, entity: Union[T, Dict[str, Any]]) -> T:
        if isinstance(entity, dict):
            entity = self._entity_class(**entity)
        
        # Авто-ID если нет
        if not hasattr(entity, 'id') or not getattr(entity, 'id'):
            entity_id = self._generate_id()
            if hasattr(entity, 'id'):
                entity.id = entity_id
            else:
                entity_dict = entity.model_dump()
                entity_dict['id'] = entity_id
                entity = self._entity_class(**entity_dict)
        
        entity_id = getattr(entity, 'id', self._generate_id())
        self._storage[entity_id] = entity
        logger.debug(f"Создана сущность: {entity_id}")
        return entity
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        if id not in self._storage:
            return None
        
        entity = self._storage[id]
        if hasattr(entity, 'model_dump') and hasattr(entity, 'model_validate'):
            # Pydantic модель
            entity_dict = entity.model_dump()
            entity_dict.update(data)
            entity = self._entity_class(**entity_dict)
        else:
            # Dict или другой тип
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
        
        self._storage[id] = entity
        self._cache_invalidate(id)
        return entity
    
    async def delete(self, id: str) -> bool:
        if id in self._storage:
            del self._storage[id]
            self._cache_invalidate(id)
            return True
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        if not filters:
            return len(self._storage)
        
        matching = await self.find_by(filters, limit=1000)
        return len(matching)
    
    async def clear(self) -> None:
        """Полная очистка хранилища"""
        self._storage.clear()
        self._cache_clear()
        logger.info("Хранилище очищено")
