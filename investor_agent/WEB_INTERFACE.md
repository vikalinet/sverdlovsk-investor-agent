# 🌐 Веб-интерфейс AI-агента

## Обзор

Веб-интерфейс на Flask + React для удобной работы с агентом-помощником инвестора.

## 📁 Структура

```
web/
├── __init__.py
├── app.py                    # Flask API
└── static/
    ├── index.html            # React SPA
    ├── css/                  # Стили (опционально)
    └── js/                   # Скрипты (опционально)
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```powershell
pip install flask flask-cors
```

### 2. Запуск сервера

```powershell
python web/app.py
```

### 3. Открытие в браузере

```
http://localhost:5000
```

## 📡 API Endpoints

### Health & Info

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/health` | GET | Проверка здоровья API |
| `/api/region` | GET | Информация о регионе |

### Поиск

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/practices` | POST | Поиск лучших практик |
| `/api/opportunities` | POST | Поиск инвествозможностей |
| `/api/support-measures` | POST | Поиск мер поддержки |

### Документы

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/documents/package` | POST | Подготовка пакета документов |
| `/api/documents/checklist` | GET | Получение чек-листа |

### Анализ

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/analysis/full` | POST | Комплексный анализ отрасли |

### MCP

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/mcp/status` | GET | Статус MCP-серверов |

## 📋 Примеры запросов

### Поиск лучших практик

```bash
curl -X POST http://localhost:5000/api/practices \
  -H "Content-Type: application/json" \
  -d '{"industry": "металлургия"}'
```

**Ответ:**
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "name": "Цифровизация производства",
      "region": "Челябинская область",
      "industry": "металлургия",
      "applicability_score": 0.85,
      "recommendations": [...]
    }
  ]
}
```

### Поиск мер поддержки

```bash
curl -X POST http://localhost:5000/api/support-measures \
  -H "Content-Type: application/json" \
  -d '{"industry": "металлургия", "business_size": "medium"}'
```

### Подготовка документов

```bash
curl -X POST http://localhost:5000/api/documents/package \
  -H "Content-Type: application/json" \
  -d '{
    "measure_name": "Грант на развитие",
    "measure_type": "grant",
    "project_data": {
      "applicant_name": "ООО Пример",
      "inn": "6601000001"
    }
  }'
```

## 🧪 Тестирование

```powershell
# Все тесты веб-API
pytest tests/test_web_api.py -v

# Запуск с покрытием
pytest tests/test_web_api.py -v --cov=web
```

### Покрытие тестов

- ✅ Health check endpoint
- ✅ Region info endpoint
- ✅ Поиск практик
- ✅ Поиск возможностей
- ✅ Поиск мер поддержки
- ✅ Подготовка документов
- ✅ Чек-лист документов
- ✅ Комплексный анализ
- ✅ Статус MCP
- ✅ Обработка ошибок (404, 405)

## 🎨 Интерфейс

### Вкладки

1. **📊 Лучшие практики** - поиск успешных кейсов
2. **💰 Инвествозможности** - готовые площадки
3. **📋 Меры поддержки** - гранты и субсидии
4. **📄 Документы** - генерация пакета
5. **📈 Анализ** - комплексный отчёт

### Особенности

- ✨ Адаптивный дизайн
- 🎯 Интуитивная навигация
- ⚡ Быстрая загрузка
- 📱 Мобильная версия
- 🎨 Градиентный UI

## 🔧 Конфигурация

### Переменные окружения

```bash
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=5000
```

### Настройки в app.py

```python
app.run(
    host='0.0.0.0',  # Все интерфейсы
    port=5000,       # Порт
    debug=True,      # Режим отладки
    threaded=True    # Многопоточность
)
```

## 🛠️ Расширение

### Добавление нового endpoint

```python
@app.route('/api/custom', methods=['POST'])
def custom_endpoint():
    data = request.get_json()
    
    # Логика
    result = process(data)
    
    return jsonify({
        "success": True,
        "data": result
    })
```

### Интеграция с базой данных

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
```

### Добавление аутентификации

```python
from flask_jwt_extended import JWTManager, jwt_required

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/api/protected')
@jwt_required()
def protected():
    return jsonify({"message": "Access granted"})
```

## 📊 Мониторинг

### Логи

```
logs/web_api.log - логи API запросов
```

### Метрики

- Количество запросов
- Время ответа
- Ошибки по типам
- Активные сессии

## 🚀 Деплой

### Production режим

```python
# production.py
from web.app import app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
```

### Gunicorn (Linux)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```

### Waitress (Windows)

```bash
waitress-serve --port=5000 --host=0.0.0.0 web.app:app
```

## 🔗 Ссылки

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [React](https://react.dev/)
