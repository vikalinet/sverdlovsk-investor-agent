"""
Модуль работы с базами данных через MCP-серверы
"""
import asyncio
from typing import Optional, Any
from dataclasses import dataclass
from loguru import logger

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP SDK не установлен. Работа с MCP будет ограничена.")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MCP_CONFIG, REGION


@dataclass
class SupportMeasure:
    """Мера государственной поддержки"""
    id: str
    name: str
    type: str  # grant, subsidy, tax_benefit, guarantee
    max_amount: float
    min_amount: float
    description: str
    eligibility: list[str]  # Требования к заявителю
    documents_required: list[str]
    deadline: Optional[str]
    contact_info: str
    region: str


@dataclass
class InvestmentObject:
    """Инвестиционный объект/площадка"""
    id: str
    name: str
    type: str  # industrial_park, business_incubator, land_plot, facility
    location: str
    area: float  # Площадь (га или м²)
    infrastructure: list[str]
    price: Optional[float]
    status: str  # available, reserved, sold
    contacts: str


@dataclass
class BusinessEntity:
    """Субъект бизнеса из реестра"""
    inn: str
    name: str
    industry: str
    region: str
    employees: int
    revenue: float
    status: str  # active, liquidated


class DatabaseModule:
    """
    Модуль для работы с базами данных через MCP-серверы:
    - Реестр мер господдержки
    - База инвестиционных объектов
    - Реестр предприятий
    """
    
    def __init__(self):
        self.mcp_config = MCP_CONFIG
        self.sessions: dict[str, ClientSession] = {}
        self.contexts: dict[str, Any] = {}
        self.target_region = REGION["name"]
        
        logger.info(f"DatabaseModule инициализирован. MCP доступен: {MCP_AVAILABLE}")
    
    async def connect_to_mcp_server(
        self,
        server_name: str,
        command: str = "python",
        args: list[str] = None
    ) -> bool:
        """
        Подключение к MCP-серверу
        
        Args:
            server_name: Имя сервера из конфигурации
            command: Команда запуска сервера
            args: Аргументы команды
        
        Returns:
            True если подключение успешно
        """
        if not MCP_AVAILABLE:
            logger.error("MCP SDK не установлен")
            return False
        
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args or []
            )
            
            stdio_transport = await stdio_client(server_params)
            read, write = stdio_transport
            session = await ClientSession(read, write).__aenter__()
            
            await session.initialize()
            
            self.sessions[server_name] = session
            logger.info(f"Подключено к MCP-серверу: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подключения к {server_name}: {e}")
            return False
    
    async def disconnect_all(self):
        """Отключение от всех MCP-серверов"""
        for name, session in self.sessions.items():
            try:
                await session.__aexit__(None, None, None)
                logger.info(f"Отключено от сервера: {name}")
            except Exception as e:
                logger.error(f"Ошибка отключения от {name}: {e}")
        self.sessions.clear()
    
    # ==================== МЕРЫ ПОДДЕРЖКИ ====================
    
    async def get_support_measures(
        self,
        industry: Optional[str] = None,
        measure_type: Optional[str] = None,
        max_amount_from: Optional[float] = None
    ) -> list[SupportMeasure]:
        """
        Получение мер господдержки из базы
        
        Args:
            industry: Фильтр по отрасли
            measure_type: Тип меры (grant, subsidy, etc.)
            max_amount_from: Минимальная сумма поддержки
        
        Returns:
            Список мер поддержки
        """
        logger.info(f"Запрос мер поддержки: industry={industry}, type={measure_type}")
        
        # Попытка получить данные через MCP
        if "support_measures_db" in self.sessions:
            measures = await self._query_support_measures_mcp(
                industry=industry,
                measure_type=measure_type,
                max_amount_from=max_amount_from
            )
            if measures:
                return measures
        
        # Fallback: имитация данных для прототипа
        return self._get_mock_support_measures(industry, measure_type)
    
    async def _query_support_measures_mcp(
        self,
        industry: Optional[str],
        measure_type: Optional[str],
        max_amount_from: Optional[float]
    ) -> list[SupportMeasure]:
        """Запрос к MCP-серверу мер поддержки"""
        session = self.sessions.get("support_measures_db")
        if not session:
            return []
        
        try:
            # Формирование запроса к MCP
            query = {
                "action": "query",
                "filters": {
                    "region": self.target_region,
                    "industry": industry,
                    "type": measure_type,
                    "min_amount": max_amount_from
                }
            }
            
            result = await session.call_tool("query_support_measures", query)
            
            # Парсинг результата
            measures = []
            for item in result.get("data", []):
                measures.append(SupportMeasure(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    type=item.get("type", ""),
                    max_amount=item.get("max_amount", 0),
                    min_amount=item.get("min_amount", 0),
                    description=item.get("description", ""),
                    eligibility=item.get("eligibility", []),
                    documents_required=item.get("documents_required", []),
                    deadline=item.get("deadline"),
                    contact_info=item.get("contact_info", ""),
                    region=item.get("region", "")
                ))
            
            return measures
            
        except Exception as e:
            logger.error(f"Ошибка запроса к MCP: {e}")
            return []
    
    def _get_mock_support_measures(
        self,
        industry: Optional[str],
        measure_type: Optional[str]
    ) -> list[SupportMeasure]:
        """Моковые данные мер поддержки (для прототипа)"""
        measures = [
            SupportMeasure(
                id="SVE-GRANT-001",
                name="Грант на развитие промышленного производства",
                type="grant",
                max_amount=30_000_000,
                min_amount=5_000_000,
                description="Грант для промышленных предприятий на расширение производства",
                eligibility=[
                    "Регистрация в Свердловской области",
                    "Отрасль: обрабатывающее производство",
                    "Создание не менее 50 рабочих мест"
                ],
                documents_required=[
                    "Заявка по форме",
                    "Бизнес-план",
                    "Финансовая отчётность за 3 года",
                    "Выписка из ЕГРЮЛ"
                ],
                deadline="2024-12-31",
                contact_info="Министерство инвестиций Свердловской области, +7 (343) 000-00-00",
                region="Свердловская область"
            ),
            SupportMeasure(
                id="SVE-SUB-002",
                name="Субсидия на модернизацию оборудования",
                type="subsidy",
                max_amount=15_000_000,
                min_amount=1_000_000,
                description="Компенсация до 50% затрат на приобретение оборудования",
                eligibility=[
                    "МСП",
                    "Действующее производство"
                ],
                documents_required=[
                    "Заявление",
                    "Договоры на оборудование",
                    "Платёжные документы"
                ],
                deadline="2024-10-31",
                contact_info="Фонд развития промышленности, +7 (343) 000-00-01",
                region="Свердловская область"
            ),
            SupportMeasure(
                id="SVE-TAX-003",
                name="Налоговые льготы для резидентов ОЭЗ",
                type="tax_benefit",
                max_amount=0,
                min_amount=0,
                description="Снижение налога на прибыль до 2% в первые 5 лет",
                eligibility=[
                    "Резидент ОЭЗ 'Титановая долина'",
                    "Инвестиции не менее 50 млн руб"
                ],
                documents_required=[
                    "Заявление на получение статуса резидента",
                    "Инвестиционный проект"
                ],
                deadline=None,
                contact_info="Управляющая компания ОЭЗ, +7 (343) 000-00-02",
                region="Свердловская область"
            )
        ]
        
        # Фильтрация
        if measure_type:
            measures = [m for m in measures if m.type == measure_type]
        if industry:
            # Упрощённая фильтрация по отрасли
            pass
        
        return measures
    
    # ==================== ИНВЕСТИЦИОННЫЕ ОБЪЕКТЫ ====================
    
    async def get_investment_objects(
        self,
        object_type: Optional[str] = None,
        location: Optional[str] = None,
        min_area: Optional[float] = None
    ) -> list[InvestmentObject]:
        """
        Получение инвестиционных объектов
        
        Args:
            object_type: Тип объекта
            location: Локация
            min_area: Минимальная площадь
        
        Returns:
            Список объектов
        """
        logger.info(f"Запрос инвестобъектов: type={object_type}, location={location}")
        
        # Попытка MCP
        if "investment_objects_db" in self.sessions:
            objects = await self._query_investment_objects_mcp(
                object_type=object_type,
                location=location,
                min_area=min_area
            )
            if objects:
                return objects
        
        # Fallback: моковые данные
        return self._get_mock_investment_objects(object_type, location)
    
    async def _query_investment_objects_mcp(
        self,
        object_type: Optional[str],
        location: Optional[str],
        min_area: Optional[float]
    ) -> list[InvestmentObject]:
        """Запрос к MCP-серверу инвестобъектов"""
        session = self.sessions.get("investment_objects_db")
        if not session:
            return []
        
        try:
            query = {
                "action": "query",
                "filters": {
                    "region": self.target_region,
                    "type": object_type,
                    "location": location,
                    "min_area": min_area
                }
            }
            
            result = await session.call_tool("query_investment_objects", query)
            
            objects = []
            for item in result.get("data", []):
                objects.append(InvestmentObject(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    type=item.get("type", ""),
                    location=item.get("location", ""),
                    area=item.get("area", 0),
                    infrastructure=item.get("infrastructure", []),
                    price=item.get("price"),
                    status=item.get("status", "available"),
                    contacts=item.get("contacts", "")
                ))
            
            return objects
            
        except Exception as e:
            logger.error(f"Ошибка запроса к MCP: {e}")
            return []
    
    def _get_mock_investment_objects(
        self,
        object_type: Optional[str],
        location: Optional[str]
    ) -> list[InvestmentObject]:
        """Моковые данные инвестобъектов"""
        objects = [
            InvestmentObject(
                id="INV-001",
                name="Индустриальный парк 'Титановая долина'",
                type="industrial_park",
                location="Верхняя Салда, Свердловская область",
                area=500.0,
                infrastructure=["электричество", "газ", "вода", "Ж/Д подъезд"],
                price=None,
                status="available",
                contacts="+7 (343) 100-00-01"
            ),
            InvestmentObject(
                id="INV-002",
                name="Бизнес-инкубатор 'Технопарк'",
                type="business_incubator",
                location="Екатеринбург, Свердловская область",
                area=2500.0,
                infrastructure=["офисы", "конференц-зал", "интернет"],
                price=500,  # руб/м²
                status="available",
                contacts="+7 (343) 100-00-02"
            ),
            InvestmentObject(
                id="INV-003",
                name="Производственная площадка",
                type="facility",
                location="Нижний Тагил, Свердловская область",
                area=15000.0,
                infrastructure=["электричество", "газ", "краны"],
                price=100_000_000,
                status="available",
                contacts="+7 (343) 100-00-03"
            )
        ]
        
        if object_type:
            objects = [o for o in objects if o.type == object_type]
        if location:
            objects = [o for o in objects if location.lower() in o.location.lower()]
        
        return objects
    
    # ==================== РЕЕСТР ПРЕДПРИЯТИЙ ====================
    
    async def get_business_entities(
        self,
        industry: Optional[str] = None,
        min_employees: Optional[int] = None
    ) -> list[BusinessEntity]:
        """Получение данных из реестра предприятий"""
        logger.info(f"Запрос реестра предприятий: industry={industry}")
        
        # Для прототипа - моковые данные
        entities = [
            BusinessEntity(
                inn="6601000001",
                name="ООО 'Уральский завод'",
                industry="металлургия",
                region="Свердловская область",
                employees=500,
                revenue=1_000_000_000,
                status="active"
            )
        ]
        
        return entities
    
    # ==================== АНАЛИТИЧЕСКИЕ ЗАПРОСЫ ====================
    
    async def get_regional_statistics(
        self,
        industry: Optional[str] = None
    ) -> dict:
        """Получение статистики по региону"""
        return {
            "region": self.target_region,
            "industry": industry or "all",
            "total_businesses": 15000,
            "total_employment": 250000,
            "investment_volume_2023": 150_000_000_000,
            "support_measures_count": 25,
            "industrial_parks": 5
        }
