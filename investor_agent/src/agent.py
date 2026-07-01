"""
Основной класс агента-помощника инвестора
"""
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

from .search_module import SearchModule, BestPractice, InvestmentOpportunity
from .database_module import DatabaseModule, SupportMeasure
from .documents_module import DocumentsModule, DocumentPackage
from .analysis_module import AnalysisModule, InvestmentProposal, PracticeAnalysis

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import REGION, LOG_CONFIG


@dataclass
class AgentSession:
    """Сессия работы с агентом"""
    id: str
    user_id: Optional[str]
    started_at: str
    queries: list[dict]
    results: dict


class InvestorAgent:
    """
    AI-агент Помощник инвестора в Свердловской области
    
    Возможности:
    - Поиск лучших отраслевых практик
    - Поиск инвестиционных возможностей
    - Подбор мер господдержки
    - Подготовка и верификация документов
    - Формирование инвестиционных предложений
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Инициализация агента
        
        Args:
            config: Конфигурация (опционально)
        """
        self.config = config or {}
        self.target_region = REGION["name"]
        
        # Инициализация модулей
        self.search = SearchModule()
        self.database = DatabaseModule()
        self.documents = DocumentsModule()
        self.analysis = AnalysisModule()
        
        # Настройка логирования
        self._setup_logging()
        
        # Сессии
        self.sessions: dict[str, AgentSession] = {}
        self.current_session: Optional[AgentSession] = None
        
        logger.info(f"InvestorAgent инициализирован для региона: {self.target_region}")
    
    def _setup_logging(self):
        """Настройка логирования"""
        log_file = LOG_CONFIG.get("file", "logs/agent.log")
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format=LOG_CONFIG.get("format", "{time} | {level} | {message}"),
            level=LOG_CONFIG.get("level", "INFO"),
            rotation="10 MB",
            retention="30 days"
        )
        
        logger.info("Логирование настроено")
    
    async def start_session(self, user_id: Optional[str] = None) -> str:
        """
        Начало новой сессии
        
        Returns:
            ID сессии
        """
        session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        session = AgentSession(
            id=session_id,
            user_id=user_id,
            started_at=datetime.now().isoformat(),
            queries=[],
            results={}
        )
        
        self.sessions[session_id] = session
        self.current_session = session
        
        logger.info(f"Начата сессия: {session_id}")
        return session_id
    
    async def end_session(self) -> bool:
        """Завершение текущей сессии"""
        if self.current_session:
            # Отключение от MCP-серверов
            await self.database.disconnect_all()
            
            logger.info(f"Завершена сессия: {self.current_session.id}")
            self.current_session = None
            return True
        return False
    
    # ==================== ПОИСК ПРАКТИК ====================
    
    async def find_best_practices(
        self,
        industry: str,
        practice_type: str = "all"
    ) -> list[PracticeAnalysis]:
        """
        Поиск и анализ лучших отраслевых практик
        
        Args:
            industry: Отрасль (например, "металлургия", "IT")
            practice_type: Тип практики
        
        Returns:
            Список проанализированных практик
        """
        logger.info(f"Поиск лучших практик: industry={industry}")
        
        # Поиск практик
        practices = await self.search.search_best_practices(
            industry=industry,
            practice_type=practice_type
        )
        
        # Анализ каждой практики
        analyses = []
        for practice in practices:
            analysis = self.analysis.analyze_practice(practice)
            analyses.append(analysis)
        
        # Сохранение в сессию
        if self.current_session:
            self.current_session.queries.append({
                "type": "find_best_practices",
                "industry": industry,
                "timestamp": datetime.now().isoformat()
            })
            self.current_session.results["practices"] = [
                {"name": a.practice.name, "score": a.applicability_score}
                for a in analyses
            ]
        
        return analyses
    
    # ==================== ИНВЕСТИЦИОННЫЕ ВОЗМОЖНОСТИ ====================
    
    async def find_investment_opportunities(
        self,
        industry: Optional[str] = None,
        min_investment: float = 0,
        location: Optional[str] = None
    ) -> list[InvestmentOpportunity]:
        """
        Поиск инвестиционных возможностей
        
        Args:
            industry: Отрасль
            min_investment: Минимальные инвестиции
            location: Локация
        
        Returns:
            Список возможностей
        """
        logger.info(f"Поиск инвествозможностей: {industry}, {min_investment}")
        
        # Поиск через базу данных
        objects = await self.database.get_investment_objects(
            object_type=None,
            location=location
        )
        
        opportunities = []
        for obj in objects:
            opp = InvestmentOpportunity(
                title=obj.name,
                type=obj.type,
                location=obj.location,
                industry=industry or "general",
                investment_required=obj.price or 0,
                description=f"Площадь: {obj.area}, Инфраструктура: {', '.join(obj.infrastructure)}",
                status=obj.status
            )
            opportunities.append(opp)
        
        # Дополнительно через поиск
        search_opps = await self.search.search_investment_opportunities(
            industry=industry,
            min_investment=min_investment,
            location=location
        )
        opportunities.extend(search_opps)
        
        return opportunities
    
    # ==================== МЕРЫ ПОДДЕРЖКИ ====================
    
    async def find_support_measures(
        self,
        industry: str,
        business_size: str = "smo"
    ) -> list[SupportMeasure]:
        """
        Поиск мер государственной поддержки
        
        Args:
            industry: Отрасль
            business_size: Размер бизнеса (small, medium, large)
        
        Returns:
            Список мер поддержки
        """
        logger.info(f"Поиск мер поддержки: {industry}, {business_size}")
        
        measures = await self.database.get_support_measures(
            industry=industry,
            measure_type=None
        )
        
        return measures
    
    # ==================== ИНВЕСТПРЕДЛОЖЕНИЯ ====================
    
    async def create_investment_proposal(
        self,
        opportunity: InvestmentOpportunity,
        industry: str
    ) -> InvestmentProposal:
        """
        Создание полного инвестиционного предложения
        
        Args:
            opportunity: Инвестиционная возможность
            industry: Отрасль
        
        Returns:
            Инвестиционное предложение
        """
        logger.info(f"Создание инвестпредложения: {opportunity.title}")
        
        # Поиск мер поддержки
        support_measures = await self.find_support_measures(
            industry=industry,
            business_size="medium"
        )
        
        # Создание предложения
        proposal = self.analysis.create_investment_proposal(
            opportunity=opportunity,
            support_measures=support_measures
        )
        
        # Сохранение в сессию
        if self.current_session:
            self.current_session.results["proposal"] = proposal.id
        
        return proposal
    
    # ==================== ДОКУМЕНТЫ ====================
    
    async def prepare_documents_package(
        self,
        measure_name: str,
        measure_type: str,
        project_data: dict
    ) -> DocumentPackage:
        """
        Подготовка пакета документов для меры поддержки
        
        Args:
            measure_name: Название меры
            measure_type: Тип меры (grant, subsidy, fund)
            project_data: Данные проекта
        
        Returns:
            Пакет документов
        """
        logger.info(f"Подготовка документов: {measure_name}")
        
        # Создание пакета
        package = self.documents.create_document_package(
            measure_name=measure_name,
            measure_type=measure_type,
            project_data=project_data
        )
        
        # Валидация
        validation_results = self.documents.validate_package(package)
        
        logger.info(f"Пакет документов: {package.id}, статус: {package.status}")
        
        return package
    
    async def verify_documents(
        self,
        package: DocumentPackage
    ) -> dict:
        """
        Верификация пакета документов
        
        Args:
            package: Пакет документов
        
        Returns:
            Результаты верификации
        """
        logger.info(f"Верификация пакета: {package.id}")
        
        results = self.documents.validate_package(package)
        
        # Формирование отчёта
        report = {
            "package_id": package.id,
            "measure": package.measure_name,
            "status": package.status,
            "documents": results,
            "overall_valid": all(
                doc.get("is_valid", False) for doc in results.values()
            ),
            "recommendations": []
        }
        
        # Добавление рекомендаций
        for doc_name, result in results.items():
            if not result["is_valid"]:
                report["recommendations"].extend([
                    f"Документ '{doc_name}': {', '.join(result['errors'] + result['warnings'])}"
                ])
        
        return report
    
    def get_documents_checklist(
        self,
        measure_type: str
    ) -> list[str]:
        """
        Получение чек-листа документов
        
        Args:
            measure_type: Тип меры
        
        Returns:
            Чек-лист
        """
        return self.documents.get_checklist_for_measure(measure_type)
    
    # ==================== АНАЛИТИКА ====================
    
    async def get_regional_comparison(
        self,
        industry: str
    ) -> dict:
        """
        Сравнительный анализ региона
        
        Args:
            industry: Отрасль
        
        Returns:
            Данные сравнения
        """
        logger.info(f"Сравнительный анализ: {industry}")
        
        # Получение данных
        comparison_data = await self.search.get_regional_comparison(
            industry=industry,
            metrics=["investment_volume", "tax_benefits", "infrastructure"]
        )
        
        # Создание отчёта
        report = self.analysis.create_regional_comparison(
            industry=industry,
            regions_data=comparison_data.get("data", {})
        )
        
        return {
            "report": report,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "recommendations": report.recommendations
        }
    
    # ==================== КОМПЛЕКСНЫЕ ЗАПРОСЫ ====================
    
    async def full_investment_analysis(
        self,
        industry: str,
        min_investment: float = 10_000_000
    ) -> dict:
        """
        Комплексный анализ инвестиционной возможности
        
        Args:
            industry: Отрасль
            min_investment: Минимальные инвестиции
        
        Returns:
            Полный отчёт
        """
        logger.info(f"Комплексный анализ: {industry}")
        
        result = {
            "industry": industry,
            "region": self.target_region,
            "timestamp": datetime.now().isoformat(),
            "sections": {}
        }
        
        # 1. Лучшие практики
        practices = await self.find_best_practices(industry)
        result["sections"]["best_practices"] = [
            {
                "name": p.practice.name,
                "region": p.practice.region,
                "applicability": p.applicability_score,
                "recommendations": p.adaptation_recommendations[:3]
            }
            for p in practices[:5]
        ]
        
        # 2. Инвествозможности
        opportunities = await self.find_investment_opportunities(
            industry=industry,
            min_investment=min_investment
        )
        result["sections"]["opportunities"] = [
            {
                "title": o.title,
                "location": o.location,
                "investment": o.investment_required,
                "type": o.type
            }
            for o in opportunities[:5]
        ]
        
        # 3. Меры поддержки
        measures = await self.find_support_measures(industry)
        result["sections"]["support_measures"] = [
            {
                "name": m.name,
                "type": m.type,
                "max_amount": m.max_amount,
                "deadline": m.deadline
            }
            for m in measures
        ]
        
        # 4. Чек-лист документов
        result["sections"]["documents_checklist"] = {
            "grant": self.get_documents_checklist("grant"),
            "subsidy": self.get_documents_checklist("subsidy")
        }
        
        # 5. Рекомендации
        result["sections"]["recommendations"] = [
            f"Рассмотреть {len(opportunities)} инвестиционных площадок",
            f"Подать заявки на {len(measures)} мер поддержки",
            "Подготовить бизнес-план и финансовую модель",
            "Провести встречу с представителями Мининвеста"
        ]
        
        return result
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.end_session()
