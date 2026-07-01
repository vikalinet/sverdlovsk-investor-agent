# 📝 .gitignore для проекта

## Что игнорируется

### 🔒 Секреты и конфигурация
- `.env` - файлы с переменными окружения (API ключи, пароли)
- `*.key`, `*.secret` - файлы с секретными ключами
- `credentials.json` - учётные данные

### 📝 Логи
- `logs/` - все лог-файлы приложения
- `*.log` - отдельные лог-файлы

### 📤 Выходные файлы
- `output/` - сгенерированные документы и отчёты
- `documents/` - пакеты документов
- `reports/` - аналитические отчёты

### 🗄️ Базы данных
- `*.db` - SQLite базы данных (генерируемые)
- `*.db-journal` - журналы SQLite

### 🐍 Python
- `__pycache__/` - скомпилированные файлы
- `*.pyc`, `*.pyo` - byte-compiled файлы
- `.pytest_cache/` - кэш pytest
- `.coverage`, `htmlcov/` - отчёты coverage
- `*.egg-info/` - информация о пакетах

### 🌐 Веб
- `.venv/`, `venv/` - виртуальные окружения
- `.idea/`, `.vscode/` - настройки IDE

### 🖥️ ОС
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)
- `Desktop.ini` (Windows)

### 🧪 Тестовые файлы
- `test_*.txt`, `test_*.json` - временные тестовые файлы
- `*.zip` - архивы с документами

## Что НЕ игнорируется

### ✅ Важные файлы проекта
- `config.py` - основная конфигурация
- `requirements.txt` - зависимости
- `README.md`, `*.md` - документация
- `tests/` - тесты
- `templates/` - шаблоны документов

### ✅ .gitkeep файлы
- `logs/.gitkeep` - сохраняет директорию логов
- `output/.gitkeep` - сохраняет директорию output
- `mcp_servers/data/.gitkeep` - сохраняет директорию БД

## Настройка

### 1. Создание .env файла

```bash
# Скопируйте пример
cp .env.example .env

# Заполните реальными значениями
# Отредактируйте .env
```

### 2. Инициализация баз данных

```bash
# Базы данных создадутся автоматически при запуске
python -c "from mcp_servers.support_measures_server import init_database; init_database()"
```

### 3. Проверка .gitignore

```bash
# Проверка что игнорируется
git status --ignored

# Проверка конкретных файлов
git check-ignore -v logs/agent.log
git check-ignore -v output/documents/
git check-ignore -v mcp_servers/data/*.db
```

## Исключения

Если нужно закоммитить что-то из игнорируемого:

```bash
# Принудительно добавить файл
git add -f output/important_report.json

# Или изменить .gitignore для конкретного случая
# Например, коммитить только .gitkeep из output/
!output/.gitkeep
```

## Рекомендации

1. **Никогда не коммитьте `.env`** - создайте `.env.example` с шаблоном
2. **Очищайте `output/`** перед коммитом - это временные файлы
3. **Логи в `.gitignore`** - они большие и содержат чувствительные данные
4. **Базы данных не коммитьте** - они создаются скриптами инициализации

## Очистка репозитория

Если файлы уже закоммичены, но должны игнорироваться:

```bash
# Удалить из индекса (но оставить в рабочей директории)
git rm -r --cached logs/
git rm -r --cached output/
git rm --cached mcp_servers/data/*.db

# Закоммитить изменения
git commit -m "Remove tracked files that should be ignored"
```
