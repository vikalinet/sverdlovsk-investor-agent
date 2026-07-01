"""
Движок шаблонов документов на основе Jinja2
"""
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from loguru import logger
import json


class TemplateEngine:
    """
    Движок для рендеринга шаблонов документов
    
    Поддерживает:
    - Jinja2 шаблоны
    - Переменные окружения
    - Кастомные фильтры
    - Наследование шаблонов
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates" / "documents"
        
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализация Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Регистрация кастомных фильтров
        self._register_filters()
        
        logger.info(f"TemplateEngine инициализирован: {templates_dir}")
    
    def _register_filters(self):
        """Регистрация кастомных фильтров"""
        
        # Форматирование денег
        self.env.filters['money'] = self._filter_money
        
        # Форматирование даты
        self.env.filters['date'] = self._filter_date
        
        # Форматирование списка
        self.env.filters['list_items'] = self._filter_list_items
        
        # Верхний регистр
        self.env.filters['uppercase'] = str.upper
        
        # Нижний регистр
        self.env.filters['lowercase'] = str.lower
        
        # Обрезка текста
        self.env.filters['truncate'] = self._filter_truncate
        
        # Форматирование процентов
        self.env.filters['percent'] = self._filter_percent
    
    def _filter_money(self, value: float, currency: str = "₽") -> str:
        """Форматирование денежной суммы"""
        if value is None:
            return f"0 {currency}"
        
        # Форматирование с разделителями тысяч
        formatted = f"{value:,.0f}".replace(",", " ")
        return f"{formatted} {currency}"
    
    def _filter_date(self, value, format_str: str = "%d.%m.%Y") -> str:
        """Форматирование даты"""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        
        if isinstance(value, datetime):
            return value.strftime(format_str)
        
        return str(value)
    
    def _filter_list_items(self, items: list, separator: str = "\n- ") -> str:
        """Форматирование списка"""
        if not items:
            return "Не указано"
        
        return separator + separator.join(str(item) for item in items)
    
    def _filter_truncate(self, text: str, length: int = 100) -> str:
        """Обрезка текста"""
        if len(text) <= length:
            return text
        
        return text[:length] + "..."
    
    def _filter_percent(self, value: float, decimals: int = 1) -> str:
        """Форматирование процентов"""
        return f"{value * 100:.{decimals}f}%"
    
    def render(self, template_name: str, context: dict) -> str:
        """
        Рендеринг шаблона
        
        Args:
            template_name: Имя файла шаблона
            context: Контекст для рендеринга
        
        Returns:
            Отрендеренный текст
        """
        try:
            template = self.env.get_template(template_name)
            result = template.render(**context)
            logger.debug(f"Шаблон {template_name} отрендерен")
            return result
            
        except TemplateNotFound:
            logger.error(f"Шаблон не найден: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Ошибка рендеринга шаблона {template_name}: {e}")
            raise
    
    def render_to_file(
        self,
        template_name: str,
        context: dict,
        output_path: Path
    ) -> Path:
        """
        Рендеринг шаблона в файл
        
        Args:
            template_name: Имя файла шаблона
            context: Контекст для рендеринга
            output_path: Путь для сохранения
        
        Returns:
            Путь к сохранённому файлу
        """
        content = self.render(template_name, context)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Шаблон сохранён: {output_path}")
        return output_path
    
    def get_template_variables(self, template_name: str) -> list[str]:
        """
        Получение списка переменных шаблона
        
        Args:
            template_name: Имя файла шаблона
        
        Returns:
            Список имён переменных
        """
        template = self.env.get_template(template_name)
        # В новых версиях Jinja2 используем ast для получения переменных
        try:
            # Пытаемся получить переменные через ast
            variables = set()
            for node in template.environment.parse(template.source).find_all():
                if isinstance(node, self.env.context_class):
                    variables.update(node.keys())
            return list(variables) if variables else []
        except:
            return []
    
    def validate_template(self, template_name: str, context: dict) -> tuple[bool, list[str]]:
        """
        Валидация шаблона и контекста
        
        Args:
            template_name: Имя файла шаблона
            context: Контекст для валидации
        
        Returns:
            (успех, список ошибок)
        """
        errors = []
        
        try:
            template = self.env.get_template(template_name)
            
            # Пытаемся отрендерить шаблон с данным контекстом
            try:
                template.render(**context)
                # Если рендеринг успешен, шаблон валиден
                return True, []
            except Exception as render_error:
                errors.append(f"Ошибка рендеринга: {str(render_error)}")
                return False, errors
            
        except TemplateNotFound:
            errors.append(f"Шаблон не найден: {template_name}")
            return False, errors
        except Exception as e:
            errors.append(str(e))
            return False, errors
