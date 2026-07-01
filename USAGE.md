# 📖 Руководство по использованию агента «Помощник инвестора»

## 🚀 Быстрый старт

### Установка зависимостей

```powershell
cd investor_agent
pip install -r requirements.txt
```

### Запуск демонстрации

```powershell
python main.py
```

## 📁 Структура проекта

```
investor_agent/
├── config.py              # Конфигурация проекта
├── main.py                # Точка входа, демонстрация
├── requirements.txt       # Зависимости
├── .env.example          # Шаблон переменных окружения
│
├── src/                   # Исходный код
│   ├── __init__.py
│   ├── agent.py          # Основной класс агента
│   ├── search_module.py  # Поиск практик и возможностей
│   ├── database_module.py # Работа с БД через MCP
│   ├── documents_module.py # Документы и шаблоны
│   └── analysis_module.py # Анализ и предложения
│
├── templates/documents/   # Шаблоны документов
├── output/                # Выходные файлы
│   ├── documents/        # Сгенерированные документы
│   └── reports/          # Отчёты анализа
├── logs/                  # Логи работы
└── tests/                 # Тесты
```

## 🔧 Настройка

### 1. Переменные окружения

Скопируйте `.env.example` в `.env` и заполните:

```env
# MCP Server URLs (для подключения к базам данных)
MCP_SUPPORT_MEASURES_URL=http://localhost:8001
MCP_INVESTMENT_OBJECTS_URL=http://localhost:8002
MCP_BUSINESS_REGISTRY_URL=http://localhost:8003

# API Keys (для поисковых сервисов)
SEARCH_API_KEY=your_api_key
DOCS_API_KEY=your_api_key
```

### 2. Конфигурация региона

В `config.py` можно изменить:

- `REGION` — целевой регион
- `PRIORITY_INDUSTRIES` — приоритетные отрасли
- `SEARCH_CONFIG` — регионы для сравнения
- `ANALYSIS_CONFIG` — параметры анализа

## 📋 Основные возможности

### 1. Поиск лучших отраслевых практик

```python
async with InvestorAgent() as agent:
    practices = await agent.find_best_practices(
        industry="металлургия"
    )
    
    for practice in practices:
        print(f"{practice.practice.name}")
        print(f"Применимость: {practice.applicability_score:.1%}")
        print(f"Рекомендации: {practice.adaptation_recommendations}")
```

### 2. Поиск инвестиционных возможностей

```python
opportunities = await agent.find_investment_opportunities(
    industry="IT",
    min_investment=10_000_000,
    location="Екатеринбург"
)
```

### 3. Подбор мер господдержки

```python
measures = await agent.find_support_measures(
    industry="металлургия",
    business_size="medium"
)

for measure in measures:
    print(f"{measure.name}: до {measure.max_amount} руб.")
```

### 4. Формирование инвестиционного предложения

```python
proposal = await agent.create_investment_proposal(
    opportunity=opportunities[0],
    industry="металлургия"
)

print(f"Инвестиции: {proposal.total_investment} руб.")
print(f"Окупаемость: {proposal.payback_period} лет")
print(f"ROI: {proposal.roi}%")
```

### 5. Подготовка документов

```python
project_data = {
    "applicant_name": "ООО 'Пример'",
    "inn": "6601000001",
    "project_name": "Расширение производства",
    "investment_amount": 100_000_000,
    "grant_amount": 30_000_000,
    "jobs_created": 50,
    "description": "Описание проекта..."
}

package = await agent.prepare_documents_package(
    measure_name="Грант на развитие производства",
    measure_type="grant",
    project_data=project_data
)
```

### 6. Верификация документов

```python
verification = await agent.verify_documents(package)

if verification['overall_valid']:
    print("✅ Документы готовы к подаче")
else:
    print("⚠️ Требуется доработка:")
    for rec in verification['recommendations']:
        print(f"  • {rec}")
```

### 7. Комплексный анализ

```python
full_analysis = await agent.full_investment_analysis(
    industry="металлургия",
    min_investment=50_000_000
)

# Результат включает:
# - Лучшие практики
# - Инвестиционные возможности
# - Меры поддержки
# - Чек-листы документов
# - Рекомендации
```

## 🧪 Тестирование

```powershell
# Запуск всех тестов
pytest tests/ -v

# Запуск конкретного теста
pytest tests/test_agent.py::TestInvestorAgent -v
```

## 🔌 Работа с MCP-серверами

### Подключение к серверам

```python
agent = InvestorAgent()

# Подключение к MCP-серверу мер поддержки
await agent.database.connect_to_mcp_server(
    server_name="support_measures_db",
    command="python",
    args=["mcp_server_support.py"]
)

# Получение данных через MCP
measures = await agent.database.get_support_measures(
    industry="металлургия"
)

# Отключение
await agent.database.disconnect_all()
```

### Пример MCP-сервера

Для работы с реальными базами данных необходимо создать MCP-серверы:

```python
# mcp_server_support.py
from mcp.server import Server
import sqlite3

server = Server("support-measures")

@server.call_tool()
async def query_support_measures(arguments: dict) -> list:
    conn = sqlite3.connect("support_measures.db")
    # ... логика запроса
    return results
```

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    InvestorAgent                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Search    │  │   Database   │  │   Documents   │  │
│  │   Module    │  │    Module    │  │    Module     │  │
│  │             │  │              │  │               │  │
│  │ • Поиск     │  │ • MCP        │  │ • Шаблоны     │  │
│  │   практик   │  │ • Базы данных│  │ • Генерация   │  │
│  │ • Возможн.  │  │ • Реестры    │  │ • Валидация   │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Analysis Module                      │    │
│  │  • Анализ практик                               │    │
│  │  • Инвестпредложения                            │    │
│  │  • Сравнение регионов                           │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Расширение функционала

### Добавление нового шаблона документа

1. Добавьте шаблон в `templates/documents/`
2. Зарегистрируйте в `DocumentsModule._init_templates()`
3. Добавьте чек-лист валидации

### Добавление нового источника данных

1. Создайте MCP-сервер или API-клиент
2. Добавьте метод в соответствующий модуль
3. Обновите конфигурацию

### Настройка под другой регион

Измените в `config.py`:

```python
REGION = {
    "name": "Ваш регион",
    "code": "XX",
    "capital": "Город"
}

PRIORITY_INDUSTRIES = ["отрасль 1", "отрасль 2"]
```

## 📝 Лицензия

Прототип создан для демонстрации возможностей AI-агента для поддержки инвесторов.
