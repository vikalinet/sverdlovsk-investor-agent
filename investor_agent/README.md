# 🏭 Помощник инвестора в Свердловской области

AI-агент для поддержки инвестиционной деятельности в Свердловской области.

## Возможности

- 🔍 **Поиск лучших отраслевых практик** в разных регионах РФ
- 📊 **Анализ инвестиционного потенциала** (объекты, виды бизнеса)
- 💰 **Подбор мер господдержки** (гранты, субсидии, фонды)
- 📄 **Подготовка пакета документов** для подачи заявок
- ✅ **Верификация документов** перед подачей
- 🔌 **MCP-серверы** для работы с базами данных

## 🚀 Быстрый старт

### 1. Установка зависимостей

```powershell
pip install -r requirements.txt
```

### 2. Инициализация баз данных

```powershell
python -c "from mcp_servers.support_measures_server import init_database; init_database()"
python -c "from mcp_servers.investment_objects_server import init_database; init_database()"
python -c "from mcp_servers.business_registry_server import init_database; init_database()"
```

### 3. Запуск демонстрации

```powershell
python main.py
```

## 📁 Структура проекта

```
investor_agent/
├── config.py                    # Конфигурация
├── main.py                      # Демонстрация
├── run_mcp_servers.py           # Запуск MCP-серверов
├── requirements.txt             # Зависимости
├── README.md                    # Главная документация
├── USAGE.md                     # Руководство пользователя
├── MCP_SERVERS.md               # Документация MCP
├── SEARCH_API.md                # Документация поиска
├── ML_MODEL.md                  # Документация ML
├── WEB_INTERFACE.md             # Документация Web ⭐
│
├── web/                         # Веб-интерфейс ⭐
│   ├── __init__.py
│   ├── app.py                   # Flask API
│   └── static/
│       └── index.html           # React SPA
│
├── mcp_servers/                 # MCP-серверы
│   ├── support_measures_server.py
│   ├── investment_objects_server.py
│   ├── business_registry_server.py
│   └── data/                    # 3 SQLite базы
│
├── ml_models/                   # ML-модули
│   ├── __init__.py
│   └── applicability_model.py   # Gradient Boosting
│
├── src/                         # Модули агента
│   ├── agent.py
│   ├── search_module.py
│   ├── search_api_client.py
│   ├── database_module.py
│   ├── documents_module.py
│   └── analysis_module.py
│
├── templates/documents/         # 5 шаблонов
├── output/                      # Результаты
├── logs/                        # Логи
└── tests/                       # 56 тестов
    ├── test_agent.py            # 15 тестов
    ├── test_mcp_servers.py      # 10 тестов
    ├── test_search_api.py       # 7 тестов
    ├── test_ml_model.py         # 13 тестов
    └── test_web_api.py          # 11 тестов ⭐
```
investor_agent/
├── config.py                     # Конфигурация
├── main.py                       # Точка входа
├── run_mcp_servers.py            # Запуск MCP-серверов
├── requirements.txt              # Зависимости
├── README.md                     # Этот файл
├── USAGE.md                      # Подробное руководство
├── MCP_SERVERS.md                # Документация MCP
│
├── mcp_servers/                  # MCP-серверы
│   ├── support_measures_server.py
│   ├── investment_objects_server.py
│   ├── business_registry_server.py
│   └── data/                     # SQLite базы
│
├── src/                          # Модули агента
│   ├── agent.py
│   ├── search_module.py
│   ├── database_module.py
│   ├── documents_module.py
│   └── analysis_module.py
│
├── templates/documents/          # Шаблоны документов
├── output/                       # Результаты
└── tests/                        # Тесты
```

## 📋 Документация

| Файл | Описание |
|------|----------|
| [README.md](README.md) | Общая информация |
| [USAGE.md](USAGE.md) | Руководство пользователя |
| [MCP_SERVERS.md](MCP_SERVERS.md) | Документация MCP-серверов |

## 🧪 Тестирование

```powershell
# Все тесты
pytest tests/ -v

# Тесты MCP-серверов
pytest tests/test_mcp_servers.py -v

# Тесты агента
pytest tests/test_agent.py -v
```

## 🔌 MCP-серверы

Проект включает 3 MCP-сервера:

| Сервер | Данные |
|--------|--------|
| `support_measures` | 6 мер поддержки (гранты, субсидии, льготы) |
| `investment_objects` | 6 инвестиционных площадок |
| `business_registry` | 6 предприятий региона |

Запуск:
```powershell
python run_mcp_servers.py all
```

## 📊 Реализованные функции

| Компонент | Статус | Описание |
|-----------|--------|----------|
| 🔌 MCP-серверы | ✅ | 3 сервера с SQLite (меры, объекты, предприятия) |
| 🔍 Поисковое API | ✅ | Yandex/Google/Bing/Mock провайдеры |
| 🤖 ML-модель | ✅ | Gradient Boosting (accuracy 0.91+) |
| 📄 Документы | ✅ | 5 шаблонов, генерация, валидация |
| 📊 Анализ | ✅ | Практики, инвестиции, предложения |
| 🌐 Веб-интерфейс | ✅ | Flask API + React SPA |
| 🧪 Тесты | ✅ | 56 тестов, все проходят |

## 🛠️ В разработке

🔲 Расширенные шаблоны документов  
🔲 Интеграция с реальными API Мининвеста  
🔲 Telegram-бот  
