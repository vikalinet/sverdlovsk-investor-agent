"""
Dependency Injection контейнер

Использование:
    from src.dependencies import get_container, get_agent
    
    # Получение зависимостей
    container = get_container()
    agent = await container.get_agent()
    
    # Или через контекстный менеджер
    async with get_agent_session() as agent:
        # работа с агентом
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
from loguru import logger
import asyncio

from config import settings, BASE_DIR
from src.agent import InvestorAgent
from src.search_module import SearchModule
from src.database_module import DatabaseModule
from src.documents_module import DocumentsModule
from src.analysis_module import AnalysisModule


class DependencyContainer:
    """
    Контейнер зависимостей для управления жизненным циклом объектов
    
    Паттерны:
    - Singleton для тяжёлых объектов (агент)
    - Factory для создания новых экземпляров
    - Context Manager для ресурсов
    """
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        Инициализация контейнера
        
        Args:
            config_override: Переопределение настроек (для тестов)
        """
        self.config = config_override or {}
        self._initialized = False
        
        #Singleton объекты
        self._agent: Optional[InvestorAgent] = None
        self._search_module: Optional[SearchModule] = None
        self._database_module: Optional[DatabaseModule] = None
        self._documents_module: Optional[DocumentsModule] = None
        self._analysis_module: Optional[AnalysisModule] = None
        
        # Счётчики для мониторинга
        self._session_count = 0
        self._request_count = 0
        
        logger.info("DependencyContainer инициализирован")
    
    async def initialize(self) -> None:
        """Инициализация контейнера"""
        if self._initialized:
            return
        
        logger.info("Инициализация DependencyContainer")
        self._initialized = True
    
    # ============================================================
    # Агент (Singleton)
    # ============================================================
    
    async def get_agent(self) -> InvestorAgent:
        """
        Получение экземпляра агента (Singleton)
        
        Returns:
            InvestorAgent: Экземпляр агента
        """
        if self._agent is None:
            logger.debug("Создание нового экземпляра InvestorAgent")
            self._agent = InvestorAgent(config=self.config)
            await self._agent.start_session()
        
        self._request_count += 1
        return self._agent
    
    async def reset_agent(self) -> None:
        """Сброс и пересоздание агента"""
        if self._agent:
            await self._agent.end_session()
            self._agent = None
            logger.info("Агент сброшен")
    
    # ============================================================
    # Модули (Singleton)
    # ============================================================
    
    async def get_search_module(self) -> SearchModule:
        """Получение модуля поиска"""
        if self._search_module is None:
            logger.debug("Создание SearchModule")
            self._search_module = SearchModule(
                api_key=settings.SEARCH_API_KEY,
                search_provider=settings.SEARCH_PROVIDER
            )
        return self._search_module
    
    async def get_database_module(self) -> DatabaseModule:
        """Получение модуля базы данных"""
        if self._database_module is None:
            logger.debug("Создание DatabaseModule")
            self._database_module = DatabaseModule()
        return self._database_module
    
    async def get_documents_module(self) -> DocumentsModule:
        """Получение модуля документов"""
        if self._documents_module is None:
            logger.debug("Создание DocumentsModule")
            self._documents_module = DocumentsModule()
        return self._documents_module
    
    async def get_analysis_module(self) -> AnalysisModule:
        """Получение модуля аналитики"""
        if self._analysis_module is None:
            logger.debug("Создание AnalysisModule")
            self._analysis_module = AnalysisModule()
        return self._analysis_module
    
    # ============================================================
    # Фабрики (Factory)
    # ============================================================
    
    async def create_new_agent_session(self) -> InvestorAgent:
        """
        Создание новой сессии агента (Factory)
        
        Используйте для изолированных сессий
        
        Returns:
            InvestorAgent: Новый экземпляр агента с активной сессией
        """
        agent = InvestorAgent(config=self.config)
        await agent.start_session()
        self._session_count += 1
        logger.debug(f"Создана новая сессия агента #{self._session_count}")
        return agent
    
    # ============================================================
    # Статистика
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики контейнера
        
        Returns:
            Dict со статистикой
        """
        return {
            "initialized": self._initialized,
            "session_count": self._session_count,
            "request_count": self._request_count,
            "agent_exists": self._agent is not None,
            "modules": {
                "search": self._search_module is not None,
                "database": self._database_module is not None,
                "documents": self._documents_module is not None,
                "analysis": self._analysis_module is not None,
            }
        }
    
    # ============================================================
    # Очистка
    # ============================================================
    
    async def shutdown(self) -> None:
        """
        Корректное завершение работы контейнера
        
        Освобождает все ресурсы
        """
        logger.info("Завершение работы DependencyContainer")
        
        # Завершение сессии агента
        if self._agent:
            await self._agent.end_session()
            self._agent = None
            logger.info("Сессия агента завершена")
        
        # Закрытие модулей
        if self._database_module:
            await self._database_module.disconnect_all()
            logger.info("База данных отключена")
        
        if self._search_module and hasattr(self._search_module, 'close'):
            await self._search_module.close()
        
        # Сброс всех ссылок
        self._search_module = None
        self._database_module = None
        self._documents_module = None
        self._analysis_module = None
        self._initialized = False
        
        logger.info("DependencyContainer завершён")


# ============================================================
# Глобальный контейнер
# ============================================================

_container: Optional[DependencyContainer] = None


def get_container(config_override: Optional[Dict[str, Any]] = None) -> DependencyContainer:
    """
    Получение глобального контейнера зависимостей
    
    Args:
        config_override: Переопределение настроек
    
    Returns:
        DependencyContainer: Глобальный контейнер
    """
    global _container
    
    if _container is None:
        _container = DependencyContainer(config_override)
        asyncio.run(_container.initialize())
    
    return _container


def reset_container() -> None:
    """
    Сброс глобального контейнера
    
    Используйте только в тестах!
    """
    global _container
    if _container:
        asyncio.run(_container.shutdown())
    _container = None


# ============================================================
# Контекстные менеджеры
# ============================================================

@asynccontextmanager
async def get_agent_session() -> AsyncGenerator[InvestorAgent, None]:
    """
    Контекстный менеджер для работы с сессией агента
    
    Usage:
        async with get_agent_session() as agent:
            result = await agent.find_best_practices("металлургия")
    
    Yields:
        InvestorAgent: Агент с активной сессией
    """
    container = get_container()
    agent = await container.create_new_agent_session()
    try:
        yield agent
    finally:
        await agent.end_session()


@asynccontextmanager
async def get_search_module() -> AsyncGenerator[SearchModule, None]:
    """Контекстный менеджер для модуля поиска"""
    container = get_container()
    module = await container.get_search_module()
    yield module


@asynccontextmanager
async def get_database_module() -> AsyncGenerator[DatabaseModule, None]:
    """Контекстный менеджер для модуля базы данных"""
    container = get_container()
    module = await container.get_database_module()
    try:
        yield module
    finally:
        await module.disconnect_all()


@asynccontextmanager
async def get_documents_module() -> AsyncGenerator[DocumentsModule, None]:
    """Контекстный менеджер для модуля документов"""
    container = get_container()
    module = await container.get_documents_module()
    yield module


@asynccontextmanager
async def get_analysis_module() -> AsyncGenerator[AnalysisModule, None]:
    """Контекстный менеджер для модуля аналитики"""
    container = get_container()
    module = await container.get_analysis_module()
    yield module


# ============================================================
# Декораторы для внедрения зависимостей
# ============================================================

def inject_agent(func):
    """
    Декоратор для внедрения агента в асинхронные функции
    
    Usage:
        @inject_agent
        async def my_function(agent: InvestorAgent):
            ...
    """
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with get_agent_session() as agent:
            return await func(agent, *args, **kwargs)
    
    return wrapper
