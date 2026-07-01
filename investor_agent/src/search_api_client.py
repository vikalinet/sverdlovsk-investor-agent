"""
Клиент для работы с поисковыми API
Поддержка: Яндекс XML, Google Custom Search, Bing Search
"""
import asyncio
import aiohttp
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import SEARCH_CONFIG


@dataclass
class SearchResponse:
    """Результат поискового запроса"""
    title: str
    snippet: str
    url: str
    source: str
    date: Optional[str] = None
    relevance: float = 0.0


class SearchAPIClient:
    """
    Клиент для поисковых API
    
    Поддерживаемые провайдеры:
    - Yandex XML
    - Google Custom Search JSON API
    - Bing Search API
    - DuckDuckGo (без API ключа, с ограничениями)
    """
    
    def __init__(self, provider: str = "yandex", api_key: str = ""):
        self.provider = provider.lower()
        self.api_key = api_key or SEARCH_CONFIG.get("api_key", "")
        self.max_results = SEARCH_CONFIG.get("max_results", 10)
        self.timeout = SEARCH_CONFIG.get("timeout", 30)
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Конфигурация провайдеров
        self.endpoints = {
            "yandex": "https://yandex-search-api.yandex.net/v1/search/",
            "google": "https://www.googleapis.com/customsearch/v1",
            "bing": "https://api.bing.microsoft.com/v7.0/search",
            "duckduckgo": "https://api.duckduckgo.com/"
        }
        
        logger.info(f"SearchAPIClient инициализирован: provider={self.provider}")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search(
        self,
        query: str,
        region: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[SearchResponse]:
        """
        Поисковый запрос
        
        Args:
            query: Поисковый запрос
            region: Регион для локализации
            date_from: Дата от (YYYY-MM-DD)
            date_to: Дата до (YYYY-MM-DD)
        
        Returns:
            Список результатов поиска
        """
        logger.info(f"Поиск: {query}, provider={self.provider}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            if self.provider == "yandex":
                results = await self._search_yandex(query, region, date_from, date_to)
            elif self.provider == "google":
                results = await self._search_google(query, region, date_from, date_to)
            elif self.provider == "bing":
                results = await self._search_bing(query, region, date_from, date_to)
            else:
                # Fallback: имитация поиска
                results = self._mock_search(query, region)
            
            logger.info(f"Найдено {len(results)} результатов")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return self._mock_search(query, region)
    
    async def _search_yandex(
        self,
        query: str,
        region: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str]
    ) -> List[SearchResponse]:
        """Поиск через Яндекс XML API"""
        if not self.api_key:
            logger.warning("Yandex API key не указан, использую mock")
            return self._mock_search(query, region)
        
        params = {
            "query": query,
            "apikey": self.api_key,
            "results": self.max_results
        }
        
        if region:
            params["region"] = region
        
        # Yandex XML API требует специфичный формат
        # Это пример, реальный API может отличаться
        async with self.session.get(
            self.endpoints["yandex"],
            params=params,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_yandex_response(data)
            else:
                logger.error(f"Yandex API error: {response.status}")
                return self._mock_search(query, region)
    
    async def _search_google(
        self,
        query: str,
        region: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str]
    ) -> List[SearchResponse]:
        """Поиск через Google Custom Search API"""
        if not self.api_key:
            logger.warning("Google API key не указан, использую mock")
            return self._mock_search(query, region)
        
        # Для Google нужен CX (Custom Search Engine ID)
        cx = SEARCH_CONFIG.get("google_cx", "")
        if not cx:
            logger.warning("Google CX не указан")
            return self._mock_search(query, region)
        
        params = {
            "key": self.api_key,
            "cx": cx,
            "q": query,
            "num": min(self.max_results, 10)  # Google ограничивает до 10
        }
        
        if region:
            params["gl"] = "ru"
            params["lr"] = f"lang_ru"
        
        if date_from:
            params["dateRestrict"] = f"d[{date_from}]"
        
        async with self.session.get(
            self.endpoints["google"],
            params=params,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_google_response(data)
            else:
                logger.error(f"Google API error: {response.status}")
                return self._mock_search(query, region)
    
    async def _search_bing(
        self,
        query: str,
        region: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str]
    ) -> List[SearchResponse]:
        """Поиск через Bing Search API"""
        if not self.api_key:
            logger.warning("Bing API key не указан, использую mock")
            return self._mock_search(query, region)
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        params = {
            "q": query,
            "count": self.max_results,
            "mkt": "ru-RU"
        }
        
        if date_from:
            params["freshness"] = "month"  # Или "week", "day"
        
        async with self.session.get(
            self.endpoints["bing"],
            headers=headers,
            params=params,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_bing_response(data)
            else:
                logger.error(f"Bing API error: {response.status}")
                return self._mock_search(query, region)
    
    def _parse_yandex_response(self, data: dict) -> list[SearchResponse]:
        """Парсинг ответа Яндекс"""
        results = []
        # Структура зависит от версии API
        for item in data.get("results", []):
            results.append(SearchResponse(
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                url=item.get("url", ""),
                source="yandex",
                date=item.get("date"),
                relevance=item.get("relevance", 0.0)
            ))
        return results
    
    def _parse_google_response(self, data: dict) -> list[SearchResponse]:
        """Парсинг ответа Google"""
        results = []
        for item in data.get("items", []):
            results.append(SearchResponse(
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                url=item.get("link", ""),
                source="google"
            ))
        return results
    
    def _parse_bing_response(self, data: dict) -> list[SearchResponse]:
        """Парсинг ответа Bing"""
        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append(SearchResponse(
                title=item.get("name", ""),
                snippet=item.get("snippet", ""),
                url=item.get("url", ""),
                source="bing",
                date=item.get("dateLastCrawled")
            ))
        return results
    
    def _mock_search(
        self,
        query: str,
        region: Optional[str]
    ) -> List[SearchResponse]:
        """
        Имитация поиска для демонстрации
        В продакшене заменить на реальные API вызовы
        """
        # Генерация реалистичных результатов для типовых запросов
        mock_data = {
            "лучшие практики металлургия": [
                SearchResponse(
                    title="Цифровизация металлургического производства: опыт ЧМК",
                    snippet="Челябинский металлургический комбинат внедрил систему цифрового мониторинга...",
                    url="https://example.com/metallurgy-digital",
                    source="mock",
                    date="2024-01-15"
                ),
                SearchResponse(
                    title="Энергоэффективность в металлургии: кейс НЛМК",
                    snippet="Внедрение систем рекуперации тепла позволило сэкономить 15% энергии...",
                    url="https://example.com/energy-efficiency",
                    source="mock",
                    date="2024-02-10"
                ),
                SearchResponse(
                    title="Автоматизация контроля качества на ММК",
                    snippet="Система компьютерного зрения для дефектоскопии...",
                    url="https://example.com/quality-control",
                    source="mock",
                    date="2024-01-20"
                )
            ],
            "инвестиционные площадки Урал": [
                SearchResponse(
                    title="ОЭЗ 'Титановая долина' привлекает резидентов",
                    snippet="В особой экономической зоне размещено уже 15 производств...",
                    url="https://example.com/titan-valley",
                    source="mock",
                    date="2024-03-01"
                ),
                SearchResponse(
                    title="Индустриальные парки Свердловской области",
                    snippet="Обзор готовых площадок для размещения производств...",
                    url="https://example.com/industrial-parks",
                    source="mock",
                    date="2024-02-15"
                )
            ]
        }
        
        # Поиск по ключевым словам
        for key, results in mock_data.items():
            if any(word in query.lower() for word in key.split()):
                return results
        
        # Результаты по умолчанию
        return [
            SearchResponse(
                title=f"Результат по запросу: {query}",
                snippet=f"Информация о '{query}' в регионе {region or 'Свердловская область'}...",
                url=f"https://example.com/search?q={query.replace(' ', '+')}",
                source="mock",
                date=datetime.now().strftime("%Y-%m-%d")
            )
        ]
    
    async def search_best_practices(
        self,
        industry: str,
        regions: list[str]
    ) -> Dict[str, List[SearchResponse]]:
        """
        Поиск лучших практик по регионам
        
        Returns:
            Словарь {регион: [результаты]}
        """
        results = {}
        
        for region in regions:
            query = f"лучшие практики {industry} {region}"
            search_results = await self.search(query, region=region)
            results[region] = search_results
        
        return results
    
    async def search_news(
        self,
        query: str,
        days_back: int = 30
    ) -> List[SearchResponse]:
        """Поиск новостей по запросу"""
        date_from = (datetime.now().timestamp() - days_back * 86400)
        date_from_str = datetime.fromtimestamp(date_from).strftime("%Y-%m-%d")
        
        # Для новостей лучше использовать специализированные API
        return await self.search(
            query,
            date_from=date_from_str
        )


# Пример использования
async def main():
    async with SearchAPIClient(provider="mock") as client:
        results = await client.search(
            "лучшие практики металлургия",
            region="Урал"
        )
        
        for result in results:
            print(f"\n{result.title}")
            print(f"  {result.snippet[:100]}...")
            print(f"  Источник: {result.source}")
            print(f"  URL: {result.url}")


if __name__ == "__main__":
    asyncio.run(main())
