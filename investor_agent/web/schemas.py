"""
Pydantic схемы для валидации API запросов и ответов
"""
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ============================================================
# Request схемы
# ============================================================

class PracticeRequest(BaseModel):
    """Запрос на поиск лучших практик"""
    industry: str = Field(..., min_length=1, max_length=100, description="Отрасль")
    practice_type: str = Field(
        default="all",
        pattern=r"^(all|технологии|управление|финансы|производство)$",
        description="Тип практики"
    )
    
    @field_validator('industry')
    @classmethod
    def validate_industry_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('industry не может быть пустым')
        return v.strip()


class OpportunityRequest(BaseModel):
    """Запрос на поиск инвестиционных возможностей"""
    industry: Optional[str] = Field(None, max_length=100, description="Отрасль")
    min_investment: float = Field(default=0, ge=0, description="Минимальные инвестиции")
    location: Optional[str] = Field(None, max_length=200, description="Локация")


class SupportMeasuresRequest(BaseModel):
    """Запрос на поиск мер поддержки"""
    industry: str = Field(..., min_length=1, max_length=100, description="Отрасль")
    business_size: str = Field(
        default="medium",
        pattern=r"^(small|medium|large|smo)$",
        description="Размер бизнеса"
    )


class ProjectData(BaseModel):
    """Данные проекта для подготовки документов"""
    applicant_name: str = Field(..., min_length=1, max_length=200)
    inn: str = Field(..., pattern=r'^\d{10}$', description="ИНН (10 цифр)")
    ogrn: str = Field(..., pattern=r'^\d{13}$', description="ОГРН (13 цифр)")
    address: str = Field(..., min_length=1, max_length=500)
    contact_phone: str = Field(..., pattern=r'^[\d\+\-\(\)\s]{10,20}$')
    contact_email: str = Field(..., description="Email")
    project_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=2000)
    investment_amount: float = Field(..., gt=0, description="Объём инвестиций")
    grant_amount: float = Field(..., ge=0, description="Запрашиваемая сумма гранта")
    jobs_created: int = Field(..., ge=0, description="Создаваемые рабочие места")
    implementation_period: int = Field(..., ge=1, description="Срок реализации (месяцев)")
    
    @field_validator('contact_email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, v):
            raise ValueError('Некорректный email адрес')
        return v.lower()
    
    @field_validator('grant_amount')
    @classmethod
    def validate_grant_amount(cls, v: float, info) -> float:
        if 'investment_amount' in info.data and v > info.data['investment_amount']:
            raise ValueError('Сумма гранта не может превышать объём инвестиций')
        return v


class DocumentsPackageRequest(BaseModel):
    """Запрос на подготовку пакета документов"""
    measure_name: str = Field(..., min_length=1, max_length=200)
    measure_type: str = Field(
        ...,
        pattern=r"^(grant|subsidy|fund)$",
        description="Тип меры поддержки"
    )
    project_data: ProjectData


class AnalysisRequest(BaseModel):
    """Запрос на комплексный анализ"""
    industry: str = Field(..., min_length=1, max_length=100)
    min_investment: float = Field(default=10_000_000, ge=0)


class ProposalRequest(BaseModel):
    """Запрос на создание инвестиционного предложения"""
    opportunity_id: Optional[str] = Field(None, max_length=100)
    industry: str = Field(..., min_length=1, max_length=100)


# ============================================================
# Response схемы
# ============================================================

class BestPracticeResponse(BaseModel):
    """Ответ с информацией о лучшей практике"""
    name: str
    region: str
    industry: str
    description: str
    results: str
    applicability_score: float
    implementation_cost: Optional[str] = None
    recommendations: List[str] = []
    risks: List[str] = []


class InvestmentOpportunityResponse(BaseModel):
    """Ответ с информацией об инвестиционной возможности"""
    title: str
    type: str
    location: str
    industry: str
    investment_required: float
    description: str
    potential_return: Optional[str] = None
    status: str


class SupportMeasureResponse(BaseModel):
    """Ответ с информацией о мере поддержки"""
    id: str
    name: str
    type: str
    max_amount: float
    min_amount: Optional[float] = None
    description: str
    eligibility: Optional[str] = None
    documents_required: List[str] = []
    deadline: Optional[str] = None
    contact_info: Optional[str] = None


class DocumentInfo(BaseModel):
    """Информация о документе в пакете"""
    type: str
    filename: str
    status: str
    is_valid: bool = False
    errors: List[str] = []
    warnings: List[str] = []


class DocumentPackageResponse(BaseModel):
    """Ответ с информацией о пакете документов"""
    package_id: str
    measure_name: str
    measure_type: str
    status: str
    created_at: str
    documents: List[DocumentInfo]
    validation: Dict[str, Any]


class ProposalResponse(BaseModel):
    """Ответ с инвестиционным предложением"""
    id: str
    title: str
    total_investment: float
    own_funds_required: float
    support_funds_available: float
    payback_period: float
    roi: float
    implementation_plan: List[Dict[str, Any]]
    risks: List[str]
    recommendations: List[str]


class APIResponse(BaseModel):
    """Базовый ответ API"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str
    timestamp: str
    region: str
    version: str


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# Словари для быстрых ответов
# ============================================================

def success_response(data: Any, message: str = None) -> dict:
    """Создать успешный ответ"""
    return {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def error_response(message: str, details: dict = None, status_code: int = 400) -> dict:
    """Создать ответ с ошибкой"""
    return {
        "success": False,
        "error": message,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
