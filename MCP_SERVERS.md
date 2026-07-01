# 🔌 MCP-серверы агента-помощника инвестора

## Обзор

Проект включает 3 MCP-сервера для работы с базами данных:

| Сервер | Порт | Описание |
|--------|------|----------|
| `support_measures_server` | - | Реестр мер государственной поддержки |
| `investment_objects_server` | - | База инвестиционных объектов и площадок |
| `business_registry_server` | - | Реестр предприятий региона |

## 📁 Структура

```
mcp_servers/
├── __init__.py
├── support_measures_server.py    # Сервер мер поддержки
├── investment_objects_server.py  # Сервер инвестобъектов
├── business_registry_server.py   # Сервер реестра предприятий
├── run_mcp_servers.py            # Скрипт запуска
└── data/                         # SQLite базы данных
    ├── support_measures.db
    ├── investment_objects.db
    └── business_registry.db
```

## 🚀 Запуск серверов

### Все серверы сразу

```powershell
python run_mcp_servers.py all
```

### Отдельный сервер

```powershell
# Только меры поддержки
python run_mcp_servers.py support

# Только инвестобъекты
python run_mcp_servers.py investment

# Только реестр предприятий
python run_mcp_servers.py business
```

## 🔧 Инструменты (Tools)

### Support Measures Server

| Инструмент | Описание |
|------------|----------|
| `query_support_measures` | Поиск мер поддержки по фильтрам (регион, отрасль, тип, сумма) |
| `get_measure_details` | Детальная информация о мере по ID |
| `get_statistics` | Статистика по мерам в регионе |

**Пример запроса:**
```json
{
  "name": "query_support_measures",
  "arguments": {
    "region": "Свердловская область",
    "industry": "металлургия",
    "type": "grant"
  }
}
```

### Investment Objects Server

| Инструмент | Описание |
|------------|----------|
| `query_investment_objects` | Поиск объектов по фильтрам |
| `get_object_details` | Детали объекта по ID |
| `get_available_objects_summary` | Сводка по доступным объектам |

**Пример запроса:**
```json
{
  "name": "query_investment_objects",
  "arguments": {
    "region": "Свердловская область",
    "type": "industrial_park",
    "status": "available"
  }
}
```

### Business Registry Server

| Инструмент | Описание |
|------------|----------|
| `query_businesses` | Поиск предприятий по фильтрам |
| `get_business_details` | Информация о предприятии по ИНН |
| `get_industry_statistics` | Статистика по отрасли |
| `search_partners` | Поиск потенциальных партнёров |

## 📊 Структура баз данных

### support_measures.db

**Таблица: `support_measures`**
- `id` - ID меры (SVE-GRANT-001)
- `name` - Название
- `type` - Тип (grant, subsidy, tax_benefit, guarantee)
- `max_amount`, `min_amount` - Суммы
- `description` - Описание
- `eligibility` - Требования (JSON)
- `documents_required` - Документы (JSON)
- `deadline` - Срок подачи
- `contact_info` - Контакты
- `region`, `industry`, `business_size` - Фильтры

### investment_objects.db

**Таблица: `investment_objects`**
- `id` - ID объекта
- `name` - Название
- `type` - Тип (industrial_park, business_incubator, facility, etc.)
- `location`, `region` - Геолокация
- `area`, `area_unit` - Площадь
- `price`, `price_unit` - Цена
- `infrastructure` - Инфраструктура (JSON)
- `status` - Статус (available, reserved, sold)
- `contacts` - Контакты (JSON)
- `latitude`, `longitude` - Координаты

### business_registry.db

**Таблица: `businesses`**
- `inn` - ИНН (PK)
- `name`, `full_name` - Название
- `ogrn`, `kpp` - Регистрационные данные
- `address`, `region`, `city` - Адрес
- `industry`, `industry_code` - Отрасль + ОКВЭД
- `employees`, `revenue` - Сотрудники, выручка
- `status` - Статус
- `director`, `phone`, `email`, `website` - Контакты

## 🧪 Тестирование

```powershell
# Тесты баз данных
python -m pytest tests/test_mcp_servers.py -v

# Тесты с выводом
python -m pytest tests/test_mcp_servers.py -v -s
```

## 🔗 Интеграция с агентом

DatabaseModule автоматически подключается к MCP-серверам:

```python
from src.database_module import DatabaseModule

db = DatabaseModule()

# Подключение к серверу
await db.connect_to_mcp_server(
    server_name="support_measures_db",
    command="python",
    args=["mcp_servers/support_measures_server.py"]
)

# Запрос данных
measures = await db.get_support_measures(industry="металлургия")

# Отключение
await db.disconnect_all()
```

## 📝 Добавление новых данных

### Через SQL

```python
import sqlite3
from pathlib import Path

db_path = Path("mcp_servers/data/support_measures.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO support_measures (id, name, type, max_amount, ...)
    VALUES (?, ?, ?, ?, ...)
""", (id, name, type, amount, ...))

conn.commit()
conn.close()
```

### Через seed-функцию

1. Добавьте данные в `seed_database()` соответствующего сервера
2. Удалите старую БД
3. Запустите сервер — данные загрузятся автоматически

## 🛠️ Расширение

### Добавление нового инструмента

```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="new_tool",
            description="Описание",
            inputSchema={...}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "new_tool":
        # Логика
        return [TextContent(type="text", text=result)]
```

### Подключение к внешним источникам

Для работы с реальными API Министерства инвестиций:

1. Создайте новый MCP-сервер с HTTP-клиентом
2. Реализуйте кэширование ответов
3. Настройте авторизацию (если требуется)
4. Обновите конфигурацию агента

## 📋 Чек-лист развёртывания

- [ ] Инициализировать базы данных
- [ ] Запустить MCP-серверы
- [ ] Проверить подключение из агента
- [ ] Настроить логирование
- [ ] Протестировать все инструменты
- [ ] Документировать API
