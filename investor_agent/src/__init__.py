"""
Модули агента-помощника инвестора
"""
from .agent import InvestorAgent
from .search_module import SearchModule
from .database_module import DatabaseModule
from .documents_module import DocumentsModule
from .analysis_module import AnalysisModule

__all__ = [
    "InvestorAgent",
    "SearchModule",
    "DatabaseModule", 
    "DocumentsModule",
    "AnalysisModule"
]
