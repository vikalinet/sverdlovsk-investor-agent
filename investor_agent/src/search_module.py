"""
Модуль поиска лучших практик и инвестиционных возможностей
"""
import asyncio
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import SEARCH_CONFIG, REGION

# Поиск API клиент
try:
    from .search_api_client import SearchAPIClient
except ImportError:
    SearchAPIClient = None


@dataclass
class SearchResult:
    """Результат поиска"""
    title: str
    source: str
    url: str
    content: str
    region: str
    category: str
    relevance_score: float
    found_at: datetime


@dataclass
class BestPractice:
    """Лучшая отраслевая практика"""
    name: str
    region: str
    industry: str
    description: str
    results: str  # Достигнутые результаты
    applicability_score: float  # Пригодность для Свердловской области
    implementation_cost: Optional[str] = None
    contacts: Optional[str] = None


@dataclass
class InvestmentOpportunity:
    """Инвестиционная возможность"""
    title: str
    type: str  # "площадка", "бизнес", "объект"
    location: str
    industry: str
    investment_required: float
    description: str
    potential_return: Optional[str] = None
    status: str = "active"


class SearchModule:
    """
    Модуль для поиска:
    - Лучших отраслевых практик в регионах
    - Инвестиционных возможностей
    - Мер государственной поддержки
    """
    
    def __init__(self, api_key: str = "", search_provider: str = "mock"):
        self.api_key = api_key or SEARCH_CONFIG.get("api_key", "")
        self.max_results = SEARCH_CONFIG.get("max_results", 10)
        self.compare_regions = SEARCH_CONFIG.get("regions_to_compare", [])
        self.target_region = REGION["name"]
        self.session: Optional[aiohttp.ClientSession] = None
        self.search_provider = search_provider
        
        # Инициализация API клиента
        self.api_client = None
        if SearchAPIClient:
            self.api_client = SearchAPIClient(
                provider=search_provider,
                api_key=self.api_key
            )
        
        logger.info(f"SearchModule инициализирован для региона: {self.target_region}, provider={search_provider}")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_best_practices(
        self,
        industry: str,
        practice_type: str = "all"
    ) -> list[BestPractice]:
        """
        Поиск лучших отраслевых практик в регионах для сравнения
        
        Args:
            industry: Отрасль (например, "металлургия", "IT")
            practice_type: Тип практики ("технологии", "управление", "все")
        
        Returns:
            Список лучших практик
        """
        logger.info(f"Поиск лучших практик для отрасли: {industry}")
        
        practices = []
        
        # Поиск по регионам для сравнения
        for region in self.compare_regions:
            region_practices = await self._search_region_practices(
                region=region,
                industry=industry,
                practice_type=practice_type
            )
            practices.extend(region_practices)
        
        # Оценка применимости для Свердловской области
        scored_practices = await self._evaluate_applicability(practices)
        
        logger.info(f"Найдено {len(scored_practices)} практик для анализа")
        return scored_practices
    
    async def _search_region_practices(
        self,
        region: str,
        industry: str,
        practice_type: str
    ) -> list[BestPractice]:
        """Поиск практик в конкретном регионе"""
        query = f"лучшие практики {industry} {region}"
        logger.debug(f"Поисковый запрос: {query}")
        
        practices = []
        
        # Использование API если доступен
        if self.api_client:
            search_results = await self.api_client.search(query, region=region)
            for result in search_results[:3]:  # Берём топ-3
                practices.append(BestPractice(
                    name=result.title,
                    region=region,
                    industry=industry,
                    description=result.snippet,
                    results="Данные из поискового запроса",
                    applicability_score=0.0,
                    implementation_cost="Требует уточнения",
                    contacts=result.url
                ))
        else:
            # Имитация результатов (для прототипа)
            practices.append(BestPractice(
                name=f"Цифровизация {industry.lower()} в {region}",
                region=region,
                industry=industry,
                description=f"Внедрение цифровых технологий в {industry}...",
                results="Рост производительности на 25%",
                applicability_score=0.0,
                implementation_cost="50-100 млн руб"
            ))
        
        return practices
    
    async def _evaluate_applicability(
        self,
        practices: list[BestPractice]
    ) -> list[BestPractice]:
        """
        Оценка применимости практик для Свердловской области
        
        Критерии:
        -Similarity отраслевой структуры
        - Экономические показатели
        - Инфраструктурная готовность
        - Кадровый потенциал
        """
        for practice in practices:
            score = await self._calculate_applicability_score(practice)
            practice.applicability_score = score
        
        # Сортировка по применимости
        practices.sort(key=lambda p: p.applicability_score, reverse=True)
        return practices
    
    async def _calculate_applicability_score(
        self,
        practice: BestPractice
    ) -> float:
        """Расчёт scores применимости (0.0 - 1.0)"""
        # Для прототипа - упрощённая логика
        # В продакшене здесь будет ML-модель или экспертная система
        
        base_score = 0.5
        
        # Бонус за соседние регионы
        if practice.region in ["Челябинская область", "Пермский край"]:
            base_score += 0.2
        
        # Бонус за экономически схожие регионы
        if practice.region in ["Татарстан", "Башкортостан"]:
            base_score += 0.15
        
        return min(base_score, 1.0)
    
    async def search_investment_opportunities(
        self,
        industry: Optional[str] = None,
        min_investment: float = 0,
        location: Optional[str] = None
    ) -> list[InvestmentOpportunity]:
        """
        Поиск инвестиционных возможностей
        
        Args:
            industry: Фильтр по отрасли
            min_investment: Минимальный объём инвестиций
            location: Локация (город, район)
        
        Returns:
            Список инвестиционных возможностей
        """
        logger.info(f"Поиск инвестиционных возможностей: industry={industry}, min={min_investment}")
        
        opportunities = []
        
        # Поиск будет через MCP-сервер с базой данных
        # Для прототипа - имитация
        opportunities.append(InvestmentOpportunity(
            title="Индустриальный парк 'Титановая долина'",
            type="площадка",
            location="Верхняя Салда, Свердловская область",
            industry=industry or "металлургия",
            investment_required=500_000_000,
            description="Готовая инфраструктура для производств...",
            potential_return="15-20% годовых",
            status="active"
        ))
        
        return opportunities
    
    async def search_support_measures(
        self,
        industry: str,
        business_size: str = "smo"  # small, medium, large
    ) -> list[dict]:
        """
        Поиск мер государственной поддержки
        
        Args:
            industry: Отрасль бизнеса
            business_size: Размер бизнеса
        
        Returns:
            Список мер поддержки
        """
        logger.info(f"Поиск мер поддержки: {industry}, {business_size}")
        
        # Данные будут получаться через MCP-сервер
        measures = [
            {
                "name": "Грант на развитие производства",
                "type": "grant",
                "max_amount": 30_000_000,
                "conditions": "Создание не менее 50 рабочих мест",
                "deadline": "2024-12-31"
            },
            {
                "name": "Субсидия на лизинг оборудования",
                "type": "subsidy",
                "max_amount": 10_000_000,
                "conditions": "Компенсация до 30% стоимости",
                "deadline": "2024-06-30"
            }
        ]
        
        return measures
    
    async def get_regional_comparison(
        self,
        industry: str,
        metrics: list[str]
    ) -> dict:
        """
        Сравнительный анализ региона по отрасли
        
        Args:
            industry: Отрасль для анализа
            metrics: Список метрик для сравнения
        
        Returns:
            Данные для сравнительного анализа
        """
        logger.info(f"Сравнительный анализ: {industry}, метрики={metrics}")
        
        comparison = {
            "target_region": self.target_region,
            "compare_regions": self.compare_regions,
            "industry": industry,
            "data": {}
        }
        
        # Заполнение данных (в продакшене - из БД)
        for region in [self.target_region] + self.compare_regions:
            comparison["data"][region] = {
                "investment_volume": 0,
                "tax_benefits": [],
                "infrastructure_score": 0.0
            }
        
        return comparison
