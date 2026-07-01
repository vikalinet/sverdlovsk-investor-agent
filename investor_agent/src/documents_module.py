"""
Модуль подготовки и верификации документов
"""
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger

from jinja2 import Environment, FileSystemLoader, select_autoescape

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DOCUMENTS_CONFIG, REGION


@dataclass
class DocumentTemplate:
    """Шаблон документа"""
    id: str
    name: str
    type: str  # grant, subsidy, fund
    filename: str
    required_fields: list[str]


@dataclass
class DocumentPackage:
    """Пакет документов для подачи"""
    id: str
    measure_name: str
    measure_type: str
    documents: list[dict]
    created_at: str
    status: str  # draft, ready, submitted
    validation_results: Optional[dict] = None


@dataclass
class ValidationResult:
    """Результат валидации документа"""
    document_name: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    checklist_passed: float  # Процент пройденных пунктов (0.0 - 1.0)


class DocumentsModule:
    """
    Модуль для работы с документами:
    - Генерация документов по шаблонам
    - Формирование пакетов документов
    - Валидация и верификация
    """
    
    def __init__(self):
        self.templates_dir = Path(DOCUMENTS_CONFIG.get("templates_dir", "templates/documents"))
        self.output_dir = Path(DOCUMENTS_CONFIG.get("output_dir", "output/documents"))
        
        # Создание директорий
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализация Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Загрузка шаблонов
        self.templates: dict[str, DocumentTemplate] = {}
        self._init_templates()
        
        logger.info(f"DocumentsModule инициализирован. Templates: {self.templates_dir}")
    
    def _init_templates(self):
        """Инициализация шаблонов документов"""
        # Шаблоны для грантов
        self.templates["grant_application"] = DocumentTemplate(
            id="grant_application",
            name="Заявка на грант",
            type="grant",
            filename="grant_application.docx",
            required_fields=[
                "applicant_name", "inn", "project_name",
                "investment_amount", "jobs_created", "description"
            ]
        )
        
        self.templates["business_plan"] = DocumentTemplate(
            id="business_plan",
            name="Бизнес-план",
            type="grant",
            filename="business_plan.docx",
            required_fields=[
                "project_name", "summary", "market_analysis",
                "financial_plan", "risk_analysis"
            ]
        )
        
        self.templates["financial_model"] = DocumentTemplate(
            id="financial_model",
            name="Финансовая модель",
            type="grant",
            filename="financial_model.xlsx",
            required_fields=[
                "revenue_forecast", "expenses_forecast",
                "cash_flow", "payback_period"
            ]
        )
        
        # Шаблоны для субсидий
        self.templates["subsidy_application"] = DocumentTemplate(
            id="subsidy_application",
            name="Заявление на субсидию",
            type="subsidy",
            filename="subsidy_application.docx",
            required_fields=[
                "applicant_name", "inn", "subsidy_type",
                "amount_requested", "justification"
            ]
        )
        
        # Шаблоны для фондов
        self.templates["fund_application"] = DocumentTemplate(
            id="fund_application",
            name="Инвестиционная заявка в фонд",
            type="fund",
            filename="fund_application.docx",
            required_fields=[
                "company_name", "project_description",
                "investment_needed", "equity_offered",
                "financials"
            ]
        )
        
        logger.info(f"Инициализировано {len(self.templates)} шаблонов")
    
    def create_template_files(self):
        """Создание файлов шаблонов (если не существуют)"""
        templates_content = {
            "grant_application.docx": self._get_grant_application_template(),
            "business_plan.docx": self._get_business_plan_template(),
            "financial_model.xlsx": "# Финансовая модель (Excel шаблон)",
            "subsidy_application.docx": self._get_subsidy_application_template(),
            "fund_application.docx": self._get_fund_application_template()
        }
        
        for filename, content in templates_content.items():
            filepath = self.templates_dir / filename
            if not filepath.exists():
                # Для .docx файлов нужен специальный формат, пока создаём .txt версии
                if filename.endswith('.docx'):
                    filepath = filepath.with_suffix('.txt')
                filepath.write_text(content, encoding='utf-8')
                logger.info(f"Создан шаблон: {filepath}")
    
    def _get_grant_application_template(self) -> str:
        """Шаблон заявки на грант"""
        return """
ЗАЯВКА НА ГРАНТ
Регион: {{ region }}

1. ЗАЯВИТЕЛЬ
   Наименование: {{ applicant_name }}
   ИНН: {{ inn }}
   ОГРН: {{ ogrn }}
   Адрес: {{ address }}
   Контакты: {{ contact_phone }}, {{ contact_email }}

2. ПРОЕКТ
   Наименование: {{ project_name }}
   Отрасль: {{ industry }}
   Описание: {{ description }}
   
3. ПАРАМЕТРЫ
   Сумма инвестиций: {{ investment_amount }} руб.
   Запрашиваемая сумма гранта: {{ grant_amount }} руб.
   Создаваемые рабочие места: {{ jobs_created }}
   Срок реализации: {{ implementation_period }} мес.

4. ОБОСНОВАНИЕ
   {{ justification }}

5. ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ
   {{ expected_results }}

Дата: {{ current_date }}
Подпись: _________________
"""
    
    def _get_business_plan_template(self) -> str:
        """Шаблон бизнес-плана"""
        return """
БИЗНЕС-ПЛАН
Проект: {{ project_name }}

1. РЕЗЮМЕ ПРОЕКТА
{{ summary }}

2. АНАЛИЗ РЫНКА
{{ market_analysis }}

3. ПРОИЗВОДСТВЕННЫЙ ПЛАН
{{ production_plan }}

4. ФИНАНСОВЫЙ ПЛАН
{{ financial_plan }}

5. АНАЛИЗ РИСКОВ
{{ risk_analysis }}

6. СОЦИАЛЬНО-ЭКОНОМИЧЕСКИЙ ЭФФЕКТ
{{ social_effect }}
"""
    
    def _get_subsidy_application_template(self) -> str:
        """Шаблон заявления на субсидию"""
        return """
ЗАЯВЛЕНИЕ НА СУБСИДИЮ
Регион: {{ region }}

Заявитель: {{ applicant_name }}
ИНН: {{ inn }}

Тип субсидии: {{ subsidy_type }}
Запрашиваемая сумма: {{ amount_requested }} руб.

Обоснование:
{{ justification }}

Прилагаемые документы:
{{ attached_documents }}

Дата: {{ current_date }}
"""
    
    def _get_fund_application_template(self) -> str:
        """Шаблон заявки в инвестиционный фонд"""
        return """
ИНВЕСТИЦИОННАЯ ЗАЯВКА

Компания: {{ company_name }}
Отрасль: {{ industry }}

Описание проекта:
{{ project_description }}

Требуемые инвестиции: {{ investment_needed }} руб.
Предлагаемая доля: {{ equity_offered }}%

Финансовые показатели:
{{ financials }}

Команда проекта:
{{ team }}
"""
    
    def generate_document(
        self,
        template_id: str,
        data: dict,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Генерация документа по шаблону
        
        Args:
            template_id: ID шаблона
            data: Данные для заполнения
            output_filename: Имя выходного файла
        
        Returns:
            Путь к сгенерированному файлу
        """
        if template_id not in self.templates:
            raise ValueError(f"Шаблон {template_id} не найден")
        
        template = self.templates[template_id]
        
        # Проверка обязательных полей
        missing_fields = [f for f in template.required_fields if f not in data]
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {missing_fields}")
        
        # Добавление стандартных данных
        data.setdefault("region", REGION["name"])
        data.setdefault("current_date", datetime.now().strftime("%d.%m.%Y"))
        
        # Получение шаблона
        template_filename = template.filename.replace('.docx', '.txt')
        template_path = self.templates_dir / template_filename
        
        if template_path.exists():
            tpl = self.jinja_env.get_template(template_filename)
            content = tpl.render(**data)
        else:
            # Используем встроенный шаблон
            content = self._render_builtin_template(template_id, data)
        
        # Сохранение
        if output_filename is None:
            output_filename = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        output_path = self.output_dir / output_filename
        output_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Сгенерирован документ: {output_path}")
        return output_path
    
    def _render_builtin_template(self, template_id: str, data: dict) -> str:
        """Рендеринг встроенного шаблона"""
        template_map = {
            "grant_application": self._get_grant_application_template(),
            "business_plan": self._get_business_plan_template(),
            "subsidy_application": self._get_subsidy_application_template(),
            "fund_application": self._get_fund_application_template()
        }
        
        template_str = template_map.get(template_id, "")
        
        # Простая замена плейсхолдеров
        content = template_str
        for key, value in data.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))
        
        return content
    
    def create_document_package(
        self,
        measure_name: str,
        measure_type: str,
        project_data: dict
    ) -> DocumentPackage:
        """
        Создание полного пакета документов для меры поддержки
        
        Args:
            measure_name: Название меры поддержки
            measure_type: Тип меры (grant, subsidy, fund)
            project_data: Данные проекта
        
        Returns:
            Пакет документов
        """
        logger.info(f"Создание пакета документов для: {measure_name}")
        
        # Определение необходимых документов по типу
        doc_types_map = {
            "grant": ["grant_application", "business_plan", "financial_model"],
            "subsidy": ["subsidy_application"],
            "fund": ["fund_application", "business_plan"]
        }
        
        doc_types = doc_types_map.get(measure_type, ["grant_application"])
        
        documents = []
        for doc_type in doc_types:
            try:
                output_path = self.generate_document(
                    template_id=doc_type,
                    data=project_data,
                    output_filename=f"{doc_type}_{measure_name.replace(' ', '_')}.txt"
                )
                documents.append({
                    "type": doc_type,
                    "filename": output_path.name,
                    "path": str(output_path),
                    "status": "generated"
                })
            except Exception as e:
                logger.error(f"Ошибка генерации {doc_type}: {e}")
                documents.append({
                    "type": doc_type,
                    "filename": f"{doc_type}.txt",
                    "path": "",
                    "status": "error",
                    "error": str(e)
                })
        
        package = DocumentPackage(
            id=f"PKG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            measure_name=measure_name,
            measure_type=measure_type,
            documents=documents,
            created_at=datetime.now().isoformat(),
            status="draft"
        )
        
        # Сохранение метаданных пакета
        self._save_package_metadata(package)
        
        return package
    
    def _save_package_metadata(self, package: DocumentPackage):
        """Сохранение метаданных пакета"""
        metadata_path = self.output_dir / f"{package.id}_metadata.json"
        metadata_path.write_text(
            json.dumps(asdict(package), ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def validate_document(
        self,
        document_path: Path,
        document_type: str
    ) -> ValidationResult:
        """
        Валидация документа
        
        Args:
            document_path: Путь к документу
            document_type: Тип документа
        
        Returns:
            Результат валидации
        """
        logger.info(f"Валидация документа: {document_path}")
        
        errors = []
        warnings = []
        checklist_items = []
        
        # Чек-лист валидации
        if not document_path.exists():
            errors.append("Файл не найден")
            return ValidationResult(
                document_name=document_path.name,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                checklist_passed=0.0
            )
        
        content = document_path.read_text(encoding='utf-8')
        
        # Проверки в зависимости от типа документа
        if document_type == "grant_application":
            checklist_items = [
                ("Наименование заявителя", "Заявитель" in content or "Наименование" in content),
                ("ИНН", "ИНН" in content),
                ("Сумма инвестиций", "инвестиций" in content.lower()),
                ("Описание проекта", "Описание" in content or "Проект" in content),
                ("Контакты", "тел" in content.lower() or "email" in content.lower())
            ]
        elif document_type == "business_plan":
            checklist_items = [
                ("Резюме", "резюме" in content.lower()),
                ("Анализ рынка", "рынк" in content.lower()),
                ("Финансовый план", "финанс" in content.lower()),
                ("Анализ рисков", "риск" in content.lower())
            ]
        else:
            checklist_items = [
                ("Наименование", "Наименование" in content or "компания" in content.lower()),
                ("Контактная информация", "тел" in content.lower() or "контакт" in content.lower())
            ]
        
        # Подсчёт пройденных пунктов
        passed = sum(1 for _, passed in checklist_items if passed)
        total = len(checklist_items)
        
        for item_name, is_passed in checklist_items:
            if not is_passed:
                warnings.append(f"Не заполнено: {item_name}")
        
        is_valid = len(errors) == 0 and passed / total >= 0.8 if total > 0 else False
        
        return ValidationResult(
            document_name=document_path.name,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            checklist_passed=passed / total if total > 0 else 0.0
        )
    
    def validate_package(self, package: DocumentPackage) -> dict:
        """
        Валидация всего пакета документов
        
        Returns:
            Результаты валидации по каждому документу
        """
        results = {}
        all_valid = True
        
        for doc in package.documents:
            if doc["status"] == "generated" and doc["path"]:
                validation = self.validate_document(
                    Path(doc["path"]),
                    doc["type"]
                )
                results[doc["type"]] = asdict(validation)
                if not validation.is_valid:
                    all_valid = False
            else:
                results[doc["type"]] = {
                    "is_valid": False,
                    "errors": [doc.get("error", "Документ не сгенерирован")],
                    "warnings": [],
                    "checklist_passed": 0.0
                }
                all_valid = False
        
        package.validation_results = results
        package.status = "ready" if all_valid else "needs_revision"
        
        # Обновление метаданных
        self._save_package_metadata(package)
        
        return results
    
    def get_checklist_for_measure(self, measure_type: str) -> list[str]:
        """Получение чек-листа документов для меры поддержки"""
        checklists = {
            "grant": [
                "✓ Заявка на грант (по форме)",
                "✓ Бизнес-план",
                "✓ Финансовая модель (3-5 лет)",
                "✓ Выписка из ЕГРЮЛ",
                "✓ Финансовая отчётность за 3 года",
                "✓ Документы о материально-техническом обеспечении",
                "✓ Рекомендательные письма (при наличии)"
            ],
            "subsidy": [
                "✓ Заявление на субсидию",
                "✓ Расчёт суммы субсидии",
                "✓ Договоры/счета на оборудование/услуги",
                "✓ Платёжные документы",
                "✓ Выписка из ЕГРЮЛ"
            ],
            "fund": [
                "✓ Инвестиционная заявка",
                "✓ Презентация проекта (Pitch Deck)",
                "✓ Due Diligence пакет",
                "✓ Финансовая отчётность",
                "✓ Документы на интеллектуальную собственность"
            ]
        }
        
        return checklists.get(measure_type, [])
