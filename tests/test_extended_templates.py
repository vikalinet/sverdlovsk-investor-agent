"""
Тесты для расширенных шаблонов документов
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.template_engine import TemplateEngine
from src.document_export import DocumentExporter
from src.documents_module import DocumentsModule


class TestTemplateEngine:
    """Тесты движка шаблонов"""
    
    @pytest.fixture
    def engine(self):
        return TemplateEngine()
    
    def test_init(self, engine):
        assert engine.templates_dir.exists()
        assert engine.env is not None
    
    def test_money_filter(self, engine):
        result = engine._filter_money(1000000)
        assert "1 000 000" in result
        assert "₽" in result
    
    def test_money_filter_with_currency(self, engine):
        result = engine._filter_money(50000, "$")
        assert "50 000" in result
        assert "$" in result
    
    def test_date_filter(self, engine):
        from datetime import datetime
        test_date = datetime(2024, 1, 15)
        result = engine._filter_date(test_date)
        assert result == "15.01.2024"
    
    def test_date_filter_custom_format(self, engine):
        from datetime import datetime
        test_date = datetime(2024, 1, 15)
        result = engine._filter_date(test_date, "%Y-%m-%d")
        assert result == "2024-01-15"
    
    def test_list_items_filter(self, engine):
        items = ["Документ 1", "Документ 2", "Документ 3"]
        result = engine._filter_list_items(items)
        assert "Документ 1" in result
        assert "Документ 2" in result
    
    def test_truncate_filter(self, engine):
        text = "Длинный текст для проверки обрезки"
        result = engine._filter_truncate(text, 10)
        assert len(result) <= 13  # 10 + "..."
        assert result.endswith("...")
    
    def test_percent_filter(self, engine):
        result = engine._filter_percent(0.25)
        assert result == "25.0%"
    
    def test_render_template(self, engine):
        # Создание тестового шаблона
        template_content = "Привет, {{ name }}! Сумма: {{ amount | money }}"
        template_path = engine.templates_dir / "test_template.jinja2"
        template_path.write_text(template_content, encoding='utf-8')
        
        # Рендеринг
        result = engine.render("test_template.jinja2", {
            "name": "Инвестор",
            "amount": 1000000
        })
        
        assert "Привет, Инвестор!" in result
        assert "1 000 000" in result
        
        # Очистка
        template_path.unlink()
    
    def test_validate_template_success(self, engine):
        template_content = "{{ name }} - {{ value }}"
        template_path = engine.templates_dir / "validate_test.jinja2"
        template_path.write_text(template_content, encoding='utf-8')
        
        is_valid, errors = engine.validate_template("validate_test.jinja2", {
            "name": "Тест",
            "value": 100
        })
        
        # Шаблон валиден если нет ошибок (предупреждения о лишних переменных допустимы)
        assert len(errors) == 0
        
        template_path.unlink()
    
    def test_validate_template_render_error(self, engine):
        # Шаблон с ошибкой (деление на ноль)
        template_content = "{{ name }} - {{ 1 / 0 }}"
        template_path = engine.templates_dir / "validate_test2.jinja2"
        template_path.write_text(template_content, encoding='utf-8')
        
        is_valid, errors = engine.validate_template("validate_test2.jinja2", {
            "name": "Тест"
        })
        
        assert is_valid == False
        assert len(errors) > 0
        
        template_path.unlink()


class TestDocumentExporter:
    """Тесты экспорта документов"""
    
    @pytest.fixture
    def exporter(self):
        return DocumentExporter()
    
    def test_init(self, exporter):
        assert exporter.output_dir.exists()
    
    def test_export_txt(self, exporter):
        content = "Тестовый документ"
        path = exporter.export(content, "test_doc", format="txt")
        
        assert path.exists()
        assert path.suffix == ".txt"
        assert path.read_text(encoding='utf-8') == content
    
    def test_export_txt_with_metadata(self, exporter):
        content = "Тестовый документ"
        metadata = {
            "title": "Тестовый документ",
            "author": "Инвестор"
        }
        path = exporter.export(content, "test_doc_meta", format="txt", metadata=metadata)
        
        assert path.exists()
        text = path.read_text(encoding='utf-8')
        assert "Тестовый документ" in text
        assert "Инвестор" in text
    
    @pytest.mark.skipif(not __import__('importlib.util').util.find_spec("docx"), reason="python-docx not installed")
    def test_export_docx(self, exporter):
        content = "Тестовый документ DOCX"
        path = exporter.export(content, "test_docx", format="docx")
        
        assert path.exists()
        assert path.suffix == ".docx"
    
    @pytest.mark.skipif(not __import__('importlib.util').util.find_spec("reportlab"), reason="reportlab not installed")
    def test_export_pdf(self, exporter):
        content = "Тестовый документ PDF"
        path = exporter.export(content, "test_pdf", format="pdf")
        
        assert path.exists()
        assert path.suffix == ".pdf"
    
    def test_export_unsupported_format(self, exporter):
        with pytest.raises(ValueError):
            exporter.export("content", "test", format="xlsx")


class TestDocumentsModuleV2:
    """Тесты расширенного модуля документов"""
    
    @pytest.fixture
    def module(self):
        return DocumentsModule(use_extended=True)
    
    def test_init_with_extended(self, module):
        assert module.use_extended == True
        if module.use_extended:
            assert module.template_engine is not None
            assert module.document_exporter is not None
    
    def test_generate_document_v2(self, module):
        # Создание тестового шаблона
        template_content = "Заявка от {{ project_data.applicant_name }}"
        template_path = module.templates_dir / "test_app.jinja2"
        template_path.write_text(template_content, encoding='utf-8')
        
        # Генерация
        project_data = {
            "applicant_name": "ООО Тест",
            "inn": "6601000001"
        }
        
        path = module.generate_document_v2(
            template_name="test_app.jinja2",
            context={"project_data": project_data},
            export_format="txt"
        )
        
        assert path.exists()
        content = path.read_text(encoding='utf-8')
        assert "ООО Тест" in content
        
        template_path.unlink()
    
    def test_create_document_package_v2(self, module):
        project_data = {
            "applicant_name": "ООО Пример",
            "inn": "6601000001",
            "project_name": "Тестовый проект",
            "investment_amount": 50000000,
            "grant_amount": 15000000,
            "jobs_created": 25
        }
        
        package = module.create_document_package_v2(
            measure_name="Грант на развитие",
            measure_type="grant",
            project_data=project_data,
            export_format="txt"
        )
        
        assert package.id.startswith("PKG-V2-")
        assert len(package.documents) > 0
        assert package.measure_name == "Грант на развитие"
    
    def test_get_checklist(self, module):
        checklist = module.get_checklist_for_measure("grant")
        assert len(checklist) > 0
        assert any("Заявка" in item for item in checklist)


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_document_workflow(self):
        """Полный цикл работы с документами"""
        # Инициализация
        module = DocumentsModule(use_extended=True)
        
        # Данные проекта
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
        
        # Создание шаблона
        template_content = """
ЗАЯВКА
От: {{ project_data.applicant_name }}
ИНН: {{ project_data.inn }}
Проект: {{ project_data.project_name }}
Сумма гранта: {{ project_data.grant_amount | money }}
"""
        template_path = module.templates_dir / "integration_test.jinja2"
        template_path.write_text(template_content, encoding='utf-8')
        
        # Генерация
        path = module.generate_document_v2(
            template_name="integration_test.jinja2",
            context={
                "project_data": project_data,
                "today": None
            },
            export_format="txt"
        )
        
        # Проверка
        assert path.exists()
        content = path.read_text(encoding='utf-8')
        assert "ООО ИнвестПром" in content
        assert "30 000 000 ₽" in content
        assert "Модернизация производства" in content
        
        # Очистка
        template_path.unlink()
        path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
