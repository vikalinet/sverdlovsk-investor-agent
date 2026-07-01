# 🔍 Поисковое API

## Обзор

Модуль для интеграции с поисковыми системами для поиска:
- Лучших отраслевых практик
- Новостей и событий
- Инвестиционных возможностей
- Информации о компаниях

## 📁 Структура

```
src/
└── search_api_client.py    # Клиент поисковых API
```

## 🔌 Поддерживаемые провайдеры

| Провайдер | API | Статус |
|-----------|-----|--------|
| **Yandex XML** | yandex-search-api.yandex.net | ✅ Поддержка |
| **Google Custom Search** | googleapis.com/customsearch | ✅ Поддержка |
| **Bing Search** | api.bing.microsoft.com | ✅ Поддержка |
| **Mock** | - | ✅ По умолчанию |

## 🚀 Быстрый старт

### 1. Получение API ключей

#### Yandex XML
1. Зарегистрируйтесь в [Yandex XML](https://yandex.ru/dev/xml/)
2. Получите API ключ
3. Добавьте в `.env`:
   ```env
   SEARCH_API_KEY=your_yandex_api_key
   ```

#### Google Custom Search
1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Custom Search API
3. Получите API ключ и CX (Custom Search Engine ID)
4. Добавьте в `.env`:
   ```env
   SEARCH_API_KEY=your_google_api_key
   GOOGLE_CX=your_cx_id
   ```

#### Bing Search
1. Зарегистрируйтесь в [Azure Portal](https://portal.azure.com/)
2. Создайте ресурс Bing Search
3. Получите API ключ
4. Добавьте в `.env`:
   ```env
   SEARCH_API_KEY=your_bing_api_key
   ```

### 2. Использование

```python
import asyncio
from src.search_api_client import SearchAPIClient

async def main():
    async with SearchAPIClient(provider="yandex") as client:
        # Обычный поиск
        results = await client.search(
            "лучшие практики металлургия",
            region="Урал"
        )
        
        for result in results:
            print(f"{result.title}")
            print(f"  {result.snippet}")
            print(f"  URL: {result.url}")
        
        # Поиск лучших практик по регионам
        practices = await client.search_best_practices(
            industry="IT",
            regions=["Татарстан", "Челябинская область"]
        )
        
        # Поиск новостей
        news = await client.search_news(
            "инвестиции Свердловская область",
            days_back=30
        )

asyncio.run(main())
```

## 📊 SearchModule с API

```python
from src.search_module import SearchModule

# Инициализация с провайдером
module = SearchModule(
    api_key="your_api_key",
    search_provider="google"  # или "yandex", "bing", "mock"
)

# Поиск практик
practices = await module.search_best_practices(
    industry="металлургия",
    practice_type="технологии"
)

# Анализ применимости
for practice in practices:
    print(f"{practice.name}")
    print(f"  Применимость: {practice.applicability_score:.1%}")
```

## 🔧 Конфигурация

В `config.py`:

```python
SEARCH_CONFIG = {
    "api_key": os.getenv("SEARCH_API_KEY", ""),
    "max_results": 10,
    "timeout": 30,
    "regions_to_compare": [
        "Челябинская область",
        "Пермский край",
        "Татарстан"
    ],
    "google_cx": os.getenv("GOOGLE_CX", "")
}
```

## 🧪 Тестирование

```powershell
# Тесты поискового API
pytest tests/test_search_api.py -v

# Тест с mock-провайдером
pytest tests/test_search_api.py::TestSearchAPIClient::test_search_mock -v
```

## 📝 Классы

### SearchAPIClient

**Основные методы:**
- `search(query, region, date_from, date_to)` - базовый поиск
- `search_best_practices(industry, regions)` - поиск практик
- `search_news(query, days_back)` - поиск новостей

### SearchResponse

**Поля:**
- `title` - заголовок
- `snippet` - описание
- `url` - ссылка
- `source` - источник (yandex/google/bing/mock)
- `date` - дата (если доступна)
- `relevance` - релевантность (0.0-1.0)

## 🛠️ Расширение

### Добавление нового провайдера

```python
class SearchAPIClient:
    async def _search_new_provider(
        self,
        query: str,
        region: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str]
    ) -> List[SearchResponse]:
        # Реализация
        pass
    
    async def search(self, query: str, ...):
        if self.provider == "new_provider":
            return await self._search_new_provider(...)
```

### Парсинг результатов

```python
def _parse_new_provider_response(self, data: dict) -> List[SearchResponse]:
    results = []
    for item in data.get("items", []):
        results.append(SearchResponse(
            title=item.get("title", ""),
            snippet=item.get("snippet", ""),
            url=item.get("link", ""),
            source="new_provider"
        ))
    return results
```

## 📋 Рекомендации

### Для продакшена:
1. **Используйте Yandex XML** для поиска по русскоязычным источникам
2. **Настройте кэширование** результатов (Redis/Memcached)
3. **Добавьте retry logic** для обработки временных ошибок API
4. **Ограничьте частоту запросов** (rate limiting)
5. **Логируйте все запросы** для отладки и аудита

### Mock-режим:
- Используйте для разработки и тестирования
- Не требует API ключей
- Возвращает реалистичные данные для типовых запросов

## 🔗 Ссылки

- [Yandex XML API](https://yandex.ru/dev/xml/)
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- [Bing Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
