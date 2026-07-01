# 🚀 Руководство по настройке проекта

## Быстрый старт

### 1. Установка зависимостей

```bash
# Создание виртуального окружения (рекомендуется)
python -m venv .venv

# Активация виртуального окружения
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка основных зависимостей
pip install -r requirements.txt

# Установка dev зависимостей (для разработки)
pip install -r requirements-dev.txt
```

### 2. Настройка окружения

```bash
# Копирование примера .env файла
copy .env.example .env
# или для Linux/Mac:
cp .env.example .env

# Редактирование .env файла
# Обязательно укажите:
# - SEARCH_API_KEY (если используете поисковый API)
# - MCP_*_URL (адреса MCP серверов)
```

### 3. Установка pre-commit хуков

```bash
# Установка pre-commit
pre-commit install

# Проверка работы (опционально)
pre-commit run --all-files
```

**Что делают pre-commit хуки:**
- ✅ Удаляют пробелы в конце строк
- ✅ Добавляют перевод строки в конце файла
- ✅ Проверяют YAML/JSON/TOML синтаксис
- ✅ Проверяют конфликты слияния
- ✅ Форматируют код (Black)
- ✅ Сортируют импорты (isort)
- ✅ Линтят код (flake8)
- ✅ Проверяют типы (mypy)
- ✅ Проверяют безопасность (bandit)
- ✅ Ищут секреты и ключи (detect-secrets)

### 4. Запуск проекта

#### Запуск основного агента (демо):
```bash
python main.py
```

#### Запуск Web API:
```bash
python run_web.py
# или
python web/app.py
```

#### Запуск MCP серверов:
```bash
python run_mcp_servers.py
```

### 5. Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src --cov=web

# Запуск конкретных тестов
pytest tests/unit/test_search_module.py -v

# Запуск с выводом в HTML
pytest --cov=src --cov=web --cov-report=html
# Отчёт откроется в: htmlcov/index.html
```

### 6. Линтинг и форматирование

```bash
# Форматирование кода (Black)
black src/ web/ tests/

# Сортировка импортов (isort)
isort src/ web/ tests/

# Линтинг (flake8)
flake8 src/ web/ tests/

# Проверка типов (mypy)
mypy src/ web/

# Проверка безопасности (bandit)
bandit -r src/ web/
```

---

## 🔧 Настройка IDE

### VS Code

Рекомендуемые расширения:
- Python (Microsoft)
- Black Formatter
- isort
- Pylance
- Python Test Explorer

**settings.json:**
```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackPath": ".venv/Scripts/black.exe",
    "python.sortImports.path": ".venv/Scripts/isort.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests",
        "--cov=src",
        "--cov=web"
    ]
}
```

### PyCharm

1. **Настройка интерпретатора:**
   - File → Settings → Project → Python Interpreter
   - Выберите `.venv/Scripts/python.exe`

2. **Настройка форматирования:**
   - Settings → Tools → Black
   - Включить "Run Black on code reformat"

3. **Настройка тестов:**
   - Settings → Tools → Python Integrated Tools
   - Testing: pytest

---

## 📦 Структура проекта

```
investor_agent/
├── .venv/                    # Виртуальное окружение
├── .git/                     # Git репозиторий
├── config.py                 # Конфигурация
├── main.py                   # Точка входа (демо)
├── run_web.py                # Запуск Web API
├── run_mcp_servers.py        # Запуск MCP серверов
├── requirements.txt          # Основные зависимости
├── requirements-dev.txt      # Dev зависимости
├── pyproject.toml            # Конфигурация инструментов
├── .pre-commit-config.yaml   # Pre-commit хуки
├── pytest.ini                # Настройки pytest
├── .env.example              # Пример переменных окружения
│
├── src/                      # Исходный код агента
│   ├── agent.py              # Основной класс агента
│   ├── search_module.py      # Поиск практик
│   ├── database_module.py    # Работа с БД
│   ├── documents_module.py   # Генерация документов
│   └── analysis_module.py    # Аналитика
│
├── web/                      # Web API
│   ├── app.py                # Flask приложение
│   ├── schemas.py            # Pydantic схемы
│   ├── error_handlers.py     # Обработка ошибок
│   └── static/               # Frontend файлы
│
├── mcp_servers/              # MCP серверы
│   ├── support_measures_server.py
│   ├── investment_objects_server.py
│   └── business_registry_server.py
│
├── tests/                    # Тесты
│   ├── unit/                 # Unit тесты
│   ├── integration/          # Integration тесты
│   └── conftest.py           # pytest фикстуры
│
├── templates/                # Шаблоны документов
├── logs/                     # Логи (создаётся автоматически)
└── output/                   # Выходные файлы
    ├── documents/            # Сгенерированные документы
    └── reports/              # Отчёты
```

---

## 🔐 Безопасность

### Переменные окружения

Никогда не коммитьте `.env` файл! В нём содержатся секреты:

```bash
# .env (НЕ КОММИТИТЬ!)
SEARCH_API_KEY=your_secret_key
MCP_SUPPORT_MEASURES_URL=...
```

Для примера используйте `.env.example`:

```bash
# .env.example (можно коммитить)
SEARCH_API_KEY=
MCP_SUPPORT_MEASURES_URL=
```

### API ключи

Для защиты API используйте заголовок `X-API-Key`:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/practices
```

---

## 🐛 Отладка

### Логирование

Логи сохраняются в:
- `logs/agent.log` - логи агента
- `logs/web_api.log` - логи Web API

Просмотр в реальном времени:
```bash
# Windows
Get-Content logs/agent.log -Wait -Tail 50

# Linux/Mac
tail -f logs/agent.log
```

### Отладка с pdb

```python
import pdb; pdb.set_trace()  # Точка останова
```

Или используйте `breakpoint()` в Python 3.7+:
```python
breakpoint()
```

---

## 📝 Чек-лист перед коммитом

- [ ] Код отформатирован (black)
- [ ] Импорты отсортированы (isort)
- [ ] Линтер не выдаёт ошибок (flake8)
- [ ] Типы проверены (mypy)
- [ ] Тесты проходят (pytest)
- [ ] Нет секретов в коде (detect-secrets)
- [ ] Pre-commit хуки прошли успешно

```bash
# Быстрая проверка всего
pre-commit run --all-files
```

---

## 🆘 Решение проблем

### Ошибка: "ModuleNotFoundError"

```bash
# Убедитесь, что виртуальное окружение активировано
# Проверьте установку зависимостей
pip install -r requirements.txt
```

### Ошибка: "pre-commit: command not found"

```bash
# Установите pre-commit
pip install pre-commit

# Или через pre-commit-completions
pre-commit install
```

### Ошибка: "Port 5000 is already in use"

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Ошибка mypy с типами

```bash
# Игнорирование конкретных ошибок (только если уверены)
# type: ignore

# Или отключение строгой проверки для файла
# mypy: disable-error-code="union-attr"
```

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в `logs/`
2. Поищите в [Issues](https://github.com/NLP-Core-Team/investor-agent/issues)
3. Создайте новый issue с описанием проблемы

---

*Последнее обновление: 2024*
*Версия проекта: 1.0.0*
