"""
Конфигурация агента-помощника инвестора
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# ==================== РЕГИОН ====================
REGION = {
    "name": "Свердловская область",
    "code": "66",
    "capital": "Екатеринбург"
}

# Приоритетные отрасли для региона
PRIORITY_INDUSTRIES = [
    "металлургия",
    "машиностроение",
    "химическая промышленность",
    "IT и цифровые технологии",
    "логистика и транспорт",
    "сельское хозяйство",
    "туризм"
]

# Настройки поиска
SEARCH_CONFIG = {
    "api_key": os.getenv("SEARCH_API_KEY", ""),
    "max_results": 10,
    "timeout": 30,
    "regions_to_compare": [
        "Московская область",
        "Ленинградская область",
        "Татарстан",
        "Башкортостан",
        "Челябинская область",
        "Пермский край"
    ]
}

# MCP серверы
MCP_CONFIG = {
    "support_measures_db": os.getenv("MCP_SUPPORT_MEASURES_URL", ""),
    "investment_objects_db": os.getenv("MCP_INVESTMENT_OBJECTS_URL", ""),
    "business_registry_db": os.getenv("MCP_BUSINESS_REGISTRY_URL", "")
}

# Документы
DOCUMENTS_CONFIG = {
    "templates_dir": BASE_DIR / "templates" / "documents",
    "output_dir": BASE_DIR / "output" / "documents",
    "supported_formats": ["docx", "pdf"],
    "document_types": {
        "grant": [
            "Заявка на грант",
            "Бизнес-план",
            "Финансовая модель",
            "Презентация проекта"
        ],
        "subsidy": [
            "Заявление на субсидию",
            "Расчёт необходимых средств",
            "Обоснование целесообразности"
        ],
        "fund": [
            "Инвестиционная заявка",
            "Due Diligence пакет",
            "Финансовая отчётность"
        ]
    }
}

# Аналитика
ANALYSIS_CONFIG = {
    "priority_industries": PRIORITY_INDUSTRIES,
    "min_investment_amount": 10_000_000,
    "max_payback_period": 5
}

# Логирование
LOG_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    "file": BASE_DIR / "logs" / "agent.log"
}
