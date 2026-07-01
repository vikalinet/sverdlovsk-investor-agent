# 📄 Расширенные шаблоны документов

## Обзор

Расширенная система генерации документов с использованием Jinja2, поддержкой множественных форматов экспорта и улучшенной валидацией.

## 📁 Структура

```
src/
├── template_engine.py        # Движок шаблонов Jinja2
├── document_export.py        # Экспорт в TXT/DOCX/PDF
└── documents_module.py       # Модуль документов (обновлён)

templates/documents/
├── grant_application_v2.jinja2      # Заявка на грант (v2)
├── investment_proposal_v2.jinja2    # Инвестпредложение (v2)
└── ...

tests/
└── test_extended_templates.py  # 22 теста
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```powershell
pip install jinja2 reportlab python-docx
```

### 2. Использование

```python
from src.documents_module import DocumentsModule

# Инициализация с расширенными возможностями
module = DocumentsModule(use_extended=True)

# Данные проекта
project_data = {
    "applicant_name": "ООО Пример",
    "inn": "6601000001",
    "project_name": "Модернизация производства",
    "investment_amount": 100000000,
    "grant_amount": 30000000
}

# Генерация документа
path = module.generate_document_v2(
    template_name="grant_application_v2.jinja2",
    context={"project_data": project_data},
    export_format="txt"  # или "docx", "pdf"
)
```

## 🔧 Template Engine

### Кастомные фильтры Jinja2

| Фильтр | Описание | Пример |
|--------|----------|--------|
| `money` | Форматирование денег | `{{ amount | money }}` → `1 000 000 ₽` |
| `date` | Форматирование даты | `{{ today | date }}` → `15.01.2024` |
| `percent` | Проценты | `{{ 0.25 | percent }}` → `25.0%` |
| `list_items` | Список | `{{ items | list_items }}` |
| `truncate` | Обрезка текста | `{{ text | truncate(50) }}` |
| `uppercase` | Верхний регистр | `{{ name | uppercase }}` |
| `lowercase` | Нижний регистр | `{{ name | lowercase }}` |

### Пример шаблона

```jinja2
ЗАЯВКА
От: {{ project_data.applicant_name | uppercase }}
ИНН: {{ project_data.inn }}
Сумма: {{ project_data.grant_amount | money }}

Дата: {{ today | date }}

Документы:
{{ documents_required | list_items }}
```

### Валидация шаблонов

```python
from src.template_engine import TemplateEngine

engine = TemplateEngine()

# Проверка шаблона
is_valid, errors = engine.validate_template(
    "grant_application_v2.jinja2",
    {"project_data": {...}}
)

if not is_valid:
    print(f"Ошибки: {errors}")
```

## 📤 Document Export

### Поддерживаемые форматы

- **TXT** - текстовый файл (по умолчанию)
- **DOCX** - Microsoft Word (требуется python-docx)
- **PDF** - PDF документ (требуется reportlab)

### Экспорт документа

```python
from src.document_export import DocumentExporter

exporter = DocumentExporter()

content = "Текст документа"
metadata = {
    "title": "Заявка на грант",
    "author": "ООО Пример",
    "generated_at": "15.01.2024"
}

# TXT
path_txt = exporter.export(content, "doc", format="txt", metadata=metadata)

# DOCX
path_docx = exporter.export(content, "doc", format="docx", metadata=metadata)

# PDF
path_pdf = exporter.export(content, "doc", format="pdf", metadata=metadata)
```

### Создание архива

```python
# Экспорт нескольких документов
documents = [
    {"content": "...", "filename": "doc1", "metadata": {...}},
    {"content": "...", "filename": "doc2", "metadata": {...}}
]

paths = exporter.export_multiple(documents, format="txt")

# Создание архива
archive_path = exporter.create_archive(paths, "package_grant")
```

## 📋 Templates

### grant_application_v2.jinja2

**Назначение:** Заявка на грант  
**Переменные:**
- `project_data.applicant_name` - заявитель
- `project_data.inn` - ИНН
- `project_data.kpp` - КПП
- `project_data.address` - адрес
- `project_data.phone` - телефон
- `project_data.email` - email
- `project_data.project_name` - название проекта
- `project_data.project_goal` - цель
- `project_data.investment_amount` - инвестиции
- `project_data.grant_amount` - сумма гранта
- `project_data.jobs_created` - рабочие места
- `project_data.director_name` - директор
- `measure.name` - название меры
- `documents_required` - список документов
- `today` - текущая дата

### investment_proposal_v2.jinja2

**Назначение:** Инвестиционное предложение  
**Переменные:**
- `proposal.title` - заголовок
- `proposal.summary` - резюме
- `proposal.total_investment` - инвестиции
- `proposal.payback_period` - окупаемость
- `proposal.roi` - ROI
- `proposal.npv` - NPV
- `proposal.implementation_plan` - план
- `proposal.risks` - риски
- `proposal.recommendations` - рекомендации
- `proposal.swot_strengths` - сильные стороны
- `proposal.swot_weaknesses` - слабые стороны
- `proposal.swot_opportunities` - возможности
- `proposal.swot_threats` - угрозы

## 🧪 Тестирование

```powershell
# Все тесты расширенных шаблонов
pytest tests/test_extended_templates.py -v

# Конкретный тест
pytest tests/test_extended_templates.py::TestTemplateEngine::test_money_filter -v
```

### Покрытие тестов

- ✅ Инициализация TemplateEngine
- ✅ Фильтр money
- ✅ Фильтр date
- ✅ Фильтр percent
- ✅ Фильтр list_items
- ✅ Фильтр truncate
- ✅ Рендеринг шаблона
- ✅ Валидация шаблона
- ✅ Экспорт в TXT
- ✅ Экспорт в DOCX
- ✅ Экспорт в PDF
- ✅ Создание пакета документов
- ✅ Интеграционный тест

## 🔗 Интеграция с DocumentsModule

### Методы v2

```python
from src.documents_module import DocumentsModule

module = DocumentsModule(use_extended=True)

# Генерация одного документа
path = module.generate_document_v2(
    template_name="grant_application_v2.jinja2",
    context={...},
    export_format="pdf"
)

# Создание пакета документов
package = module.create_document_package_v2(
    measure_name="Грант на развитие",
    measure_type="grant",
    project_data={...},
    export_format="docx"
)

# Автоматически создаётся архив с документами
```

## 📊 Расширения

### Добавление нового фильтра

```python
# В template_engine.py
def _filter_custom(self, value):
    """Кастомный фильтр"""
    return value.upper()

def _register_filters(self):
    self.env.filters['custom'] = self._filter_custom
```

### Добавление шаблона

1. Создать файл `.jinja2` в `templates/documents/`
2. Использовать переменные и фильтры
3. Добавить в `doc_templates` в `documents_module.py`

### Добавление формата экспорта

```python
# В document_export.py
def _export_xlsx(self, content, filename, metadata):
    """Экспорт в XLSX"""
    # Реализация
    pass

def export(self, content, filename, format="txt", metadata=None):
    if format == "xlsx":
        return self._export_xlsx(content, filename, metadata)
```

## 🛠️ Конфигурация

### Настройки Jinja2

```python
self.env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=True,      # Авто-экранирование
    trim_blocks=True,     # Удаление пустых строк
    lstrip_blocks=True    # Удаление пробелов
)
```

### Настройки экспорта

```python
# PDF настройки
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate(
    str(output_path),
    pagesize=A4,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch
)
```

## 📝 Примеры использования

### Пример 1: Заявка на грант

```python
project_data = {
    "applicant_name": "ООО ИнвестПром",
    "inn": "6601000001",
    "kpp": "660101001",
    "address": "г. Екатеринбург, ул. Ленина, 1",
    "phone": "+7 (343) 123-45-67",
    "email": "info@investprom.ru",
    "project_name": "Модернизация производства",
    "project_goal": "Увеличение производственных мощностей",
    "investment_amount": 100000000,
    "grant_amount": 30000000,
    "jobs_created": 50,
    "director_name": "Иванов И.И.",
    "director_position": "Генеральный директор"
}

module = DocumentsModule(use_extended=True)
package = module.create_document_package_v2(
    measure_name="Грант на развитие производства",
    measure_type="grant",
    project_data=project_data,
    export_format="pdf"
)

print(f"Пакет создан: {package.id}")
print(f"Документов: {len(package.documents)}")
```

### Пример 2: Инвестиционное предложение

```python
proposal_data = {
    "title": "Создание технопарка",
    "summary": "Современный технопарк для IT-компаний",
    "total_investment": 500000000,
    "own_funds": 150000000,
    "debt_funds": 100000000,
    "support_funds": 250000000,
    "payback_period": "4.5 года",
    "roi": 0.22,
    "npv": 120000000,
    "irr": 0.18,
    "tasks": [
        "Разработка проектной документации",
        "Строительство объекта",
        "Закупка оборудования",
        "Найм персонала"
    ],
    "risks": ["Рыночные", "Финансовые", "Операционные"],
    "recommendations": [
        "Подать заявку на меры господдержки",
        "Провести due diligence"
    ]
}

path = module.generate_document_v2(
    template_name="investment_proposal_v2.jinja2",
    context={"proposal": proposal_data, "today": datetime.now()},
    export_format="docx"
)
```

## 🔗 Ссылки

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [python-docx](https://python-docx.readthedocs.io/)
- [reportlab](https://www.reportlab.com/docs/reportlab-userguide.pdf)
