"""
Модуль анализа и формирования предложений
"""
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ANALYSIS_CONFIG, REGION
from .search_module import BestPractice, InvestmentOpportunity
from .database_module import SupportMeasure

# ML-модель оценки применимости
try:
    from ml_models.applicability_model import ApplicabilityModel, PracticeFeatures
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    ApplicabilityModel = None
    PracticeFeatures = None


@dataclass
class PracticeAnalysis:
    """Анализ лучшей практики"""
    practice: BestPractice
    applicability_score: float
    adaptation_recommendations: list[str]
    estimated_cost: str
    expected_benefit: str
    implementation_timeline: str
    risks: list[str]


@dataclass
class InvestmentProposal:
    """Инвестиционное предложение"""
    id: str
    title: str
    opportunity: InvestmentOpportunity
    recommended_support_measures: list[SupportMeasure]
    total_investment: float
    own_funds_required: float
    support_funds_available: float
    payback_period: float  # лет
    roi: float  # % годовых
    implementation_plan: list[dict]
    risks: list[str]
    recommendations: list[str]


@dataclass
class RegionalComparisonReport:
    """Отчёт о сравнительном анализе регионов"""
    target_region: str
    industry: str
    compared_regions: list[str]
    metrics: dict
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    generated_at: str


class AnalysisModule:
    """
    Модуль для анализа данных и формирования предложений:
    - Анализ лучших практик
    - Формирование инвестиционных предложений
    - Сравнительный анализ регионов
    """
    
    def __init__(self, use_ml: bool = True):
        self.priority_industries = ANALYSIS_CONFIG.get("priority_industries", [])
        self.min_investment = ANALYSIS_CONFIG.get("min_investment_amount", 10_000_000)
        self.max_payback = ANALYSIS_CONFIG.get("max_payback_period", 5)
        self.target_region = REGION["name"]
        self.use_ml = use_ml and ML_AVAILABLE
        
        # Инициализация ML-модели
        self.ml_model = None
        if self.use_ml and ApplicabilityModel:
            self.ml_model = ApplicabilityModel(model_type="gradient_boosting")
            # Обучение на синтетических данных
            X, y = self.ml_model.generate_training_data(n_samples=300)
            self.ml_model.train(X, y, test_size=0.2)
            logger.info("ML-модель оценки применимости инициализирована")
        
        logger.info(f"AnalysisModule инициализирован для: {self.target_region}, ML={self.use_ml}")
    
    def analyze_practice(
        self,
        practice: BestPractice,
        use_ml: bool = True
    ) -> PracticeAnalysis:
        """
        Детальный анализ лучшей практики
        
        Args:
            practice: Объект лучшей практики
            use_ml: Использовать ML-модель для оценки
        
        Returns:
            Результаты анализа с рекомендациями
        """
        logger.info(f"Анализ практики: {practice.name}")
        
        # ML-оценка применимости
        ml_score = practice.applicability_score
        ml_recommendations = []
        
        if use_ml and self.ml_model and PracticeFeatures:
            try:
                # Преобразование практики в признаки для ML
                practice_features = PracticeFeatures(
                    investment_required=0.5,  # Средняя оценка
                    implementation_time=12,
                    complexity=5,
                    innovation_level=6,
                    industry_match=0.8 if practice.industry in self.priority_industries else 0.6,
                    technology_level=6,
                    economic_effect=0.7,
                    social_effect=0.6,
                    environmental_effect=0.5
                )
                
                ml_result = self.ml_model.predict(
                    source_region=practice.region,
                    target_region=self.target_region,
                    practice=practice_features
                )
                
                ml_score = ml_result.score
                ml_recommendations = ml_result.recommendations
                logger.debug(f"ML оценка: {ml_score:.3f}, категория: {ml_result.category}")
                
            except Exception as e:
                logger.warning(f"ML-оценка не удалась: {e}, использую rule-based")
        
        # Генерация рекомендаций по адаптации
        adaptation_recs = self._generate_adaptation_recommendations(practice)
        adaptation_recs.extend(ml_recommendations[:2])  # Добавляем ML-рекомендации
        
        # Оценка рисков
        risks = self._assess_implementation_risks(practice)
        
        # Расчёт ожидаемой выгоды
        expected_benefit = self._calculate_expected_benefit(practice, ml_score)
        
        # Timeline реализации
        timeline = self._estimate_timeline(practice)
        
        analysis = PracticeAnalysis(
            practice=practice,
            applicability_score=ml_score,
            adaptation_recommendations=adaptation_recs,
            estimated_cost=practice.implementation_cost or "Требует уточнения",
            expected_benefit=expected_benefit,
            implementation_timeline=timeline,
            risks=risks
        )
        
        return analysis
    
    def _generate_adaptation_recommendations(
        self,
        practice: BestPractice
    ) -> list[str]:
        """Генерация рекомендаций по адаптации практики"""
        recommendations = []
        
        # Общие рекомендации
        recommendations.append(
            f"Адаптировать практику '{practice.name}' к условиям {self.target_region}"
        )
        
        # Отраслевые рекомендации
        if practice.industry in self.priority_industries:
            recommendations.append(
                f"Использовать приоритетный статус отрасли '{practice.industry}' "
                "для получения дополнительных мер поддержки"
            )
        
        # Региональные особенности
        if practice.region in ["Московская область", "Ленинградская область"]:
            recommendations.append(
                "Учесть различия в стоимости ресурсов и рабочей силы "
                f"между {practice.region} и {self.target_region}"
            )
        
        if practice.region in ["Челябинская область", "Пермский край"]:
            recommendations.append(
                f"Практика из соседнего региона может быть применена "
                "с минимальной адаптацией"
            )
        
        # Инфраструктурные рекомендации
        recommendations.append(
            "Провести аудит существующей инфраструктуры для выявления "
            "необходимых модернизаций"
        )
        
        # Кадровые рекомендации
        recommendations.append(
            "Оценить доступность квалифицированных кадров в регионе "
            "и при необходимости разработать программу обучения"
        )
        
        return recommendations
    
    def _assess_implementation_risks(
        self,
        practice: BestPractice
    ) -> list[str]:
        """Оценка рисков внедрения"""
        risks = []
        
        # Экономические риски
        risks.append("Изменение экономической конъюнктуры")
        risks.append("Рост стоимости ресурсов и оборудования")
        
        # Регуляторные риски
        risks.append("Изменения в законодательстве о мерах поддержки")
        
        # Кадровые риски
        risks.append("Дефицит квалифицированных специалистов")
        
        # Инфраструктурные риски
        risks.append("Недостаточность инфраструктуры для реализации")
        
        # Специфические риски по отрасли
        if practice.industry == "металлургия":
            risks.append("Волатильность цен на металлы")
        elif practice.industry == "IT и цифровые технологии":
            risks.append("Быстрое устаревание технологий")
        elif practice.industry == "сельское хозяйство":
            risks.append("Климатические риски")
        
        return risks
    
    def _calculate_expected_benefit(
        self,
        practice: BestPractice,
        applicability_score: Optional[float] = None
    ) -> str:
        """Расчёт ожидаемой выгоды"""
        score = applicability_score if applicability_score is not None else practice.applicability_score
        
        # Парсинг результатов из практики
        base_results = practice.results or "Данные отсутствуют"
        
        # Добавление прогноза для региона
        benefit = (
            f"{base_results}. "
            f"Для {self.target_region} прогнозируется аналогичный эффект "
            f"с коэффициентом применимости {score:.2f}"
        )
        
        return benefit
    
    def _estimate_timeline(self, practice: BestPractice) -> str:
        """Оценка сроков реализации"""
        # Стандартные этапы
        stages = [
            "Подготовка и планирование: 1-2 мес.",
            "Согласование и получение поддержки: 2-4 мес.",
            "Внедрение: 6-12 мес.",
            "Вывод на проектную мощность: 3-6 мес."
        ]
        
        total = "12-24 месяца с учётом всех этапов"
        return f"Этапы: {'; '.join(stages)}. Общий срок: {total}"
    
    def create_investment_proposal(
        self,
        opportunity: InvestmentOpportunity,
        support_measures: list[SupportMeasure],
        project_data: Optional[dict] = None
    ) -> InvestmentProposal:
        """
        Создание инвестиционного предложения
        
        Args:
            opportunity: Инвестиционная возможность
            support_measures: Доступные меры поддержки
            project_data: Дополнительные данные проекта
        
        Returns:
            Инвестиционное предложение
        """
        logger.info(f"Создание инвестпредложения: {opportunity.title}")
        
        # Расчёт финансовых показателей
        total_investment = opportunity.investment_required
        
        # Подсчёт доступной поддержки
        support_total = sum(m.max_amount for m in support_measures)
        own_funds = max(0, total_investment - support_total)
        
        # Расчёт окупаемости и ROI
        payback = self._calculate_payback(opportunity, project_data)
        roi = self._calculate_roi(opportunity, project_data)
        
        # План реализации
        implementation_plan = self._create_implementation_plan(opportunity)
        
        # Риски
        risks = self._assess_investment_risks(opportunity)
        
        # Рекомендации
        recommendations = self._generate_investment_recommendations(
            opportunity, support_measures
        )
        
        proposal = InvestmentProposal(
            id=f"INV-PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=f"Инвестиционное предложение: {opportunity.title}",
            opportunity=opportunity,
            recommended_support_measures=support_measures,
            total_investment=total_investment,
            own_funds_required=own_funds,
            support_funds_available=support_total,
            payback_period=payback,
            roi=roi,
            implementation_plan=implementation_plan,
            risks=risks,
            recommendations=recommendations
        )
        
        return proposal
    
    def _calculate_payback(
        self,
        opportunity: InvestmentOpportunity,
        project_data: Optional[dict]
    ) -> float:
        """Расчёт срока окупаемости"""
        # Упрощённая формула для прототипа
        if project_data and "annual_revenue" in project_data:
            annual_revenue = project_data["annual_revenue"]
            annual_profit = annual_revenue * 0.2  # Предполагаемая маржа 20%
            if annual_profit > 0:
                return round(opportunity.investment_required / annual_profit, 2)
        
        # Значение по умолчанию на основе типа
        payback_map = {
            "industrial_park": 4.5,
            "business_incubator": 3.5,
            "facility": 5.0,
            "land_plot": 6.0
        }
        
        return payback_map.get(opportunity.type, 5.0)
    
    def _calculate_roi(
        self,
        opportunity: InvestmentOpportunity,
        project_data: Optional[dict]
    ) -> float:
        """Расчёт ROI"""
        payback = self._calculate_payback(opportunity, project_data)
        if payback > 0:
            return round(100 / payback, 2)
        return 0.0
    
    def _create_implementation_plan(
        self,
        opportunity: InvestmentOpportunity
    ) -> list[dict]:
        """Создание плана реализации"""
        return [
            {
                "stage": 1,
                "name": "Подготовка",
                "duration": "1-2 месяца",
                "activities": [
                    "Разработка детального бизнес-плана",
                    "Получение необходимых согласований",
                    "Подача заявок на меры поддержки"
                ]
            },
            {
                "stage": 2,
                "name": "Финансирование",
                "duration": "2-4 месяца",
                "activities": [
                    "Привлечение собственных средств",
                    "Получение одобренной поддержки",
                    "Открытие счетов и финансирование"
                ]
            },
            {
                "stage": 3,
                "name": "Реализация",
                "duration": "6-18 месяцев",
                "activities": [
                    "Подготовка площадки",
                    "Закупка и установка оборудования",
                    "Найм и обучение персонала"
                ]
            },
            {
                "stage": 4,
                "name": "Запуск",
                "duration": "3-6 месяцев",
                "activities": [
                    "Пуско-наладочные работы",
                    "Выход на проектную мощность",
                    "Начало коммерческой эксплуатации"
                ]
            }
        ]
    
    def _assess_investment_risks(
        self,
        opportunity: InvestmentOpportunity
    ) -> list[str]:
        """Оценка инвестиционных рисков"""
        risks = [
            "Рыночные риски (спрос, конкуренция)",
            "Финансовые риски (стоимость финансирования)",
            "Операционные риски (производство, логистика)",
            "Регуляторные риски (изменения законодательства)"
        ]
        
        # Специфические риски по типу
        if opportunity.type == "industrial_park":
            risks.append("Риск незаполненности площадей")
        elif opportunity.type == "facility":
            risks.append("Риск скрытых дефектов объекта")
        
        return risks
    
    def _generate_investment_recommendations(
        self,
        opportunity: InvestmentOpportunity,
        support_measures: list[SupportMeasure]
    ) -> list[str]:
        """Генерация рекомендаций по инвестпроекту"""
        recommendations = []
        
        # Рекомендации по финансированию
        if support_measures:
            recommendations.append(
                f"Рекомендуется подать заявки на {len(support_measures)} мер поддержки "
                f"на общую сумму до {sum(m.max_amount for m in support_measures):,.0f} руб."
            )
        
        # Рекомендации по реализации
        recommendations.append(
            "Начать с подачи заявок на меры поддержки параллельно "
            "с разработкой детального бизнес-плана"
        )
        
        # Рекомендации по локации
        recommendations.append(
            f"Локация: {opportunity.location} - "
            "провести дополнительный анализ транспортной доступности"
        )
        
        # Следующие шаги
        recommendations.extend([
            "Заказать независимую оценку объекта",
            "Провести due diligence",
            "Подготовить презентацию для инвесторов/фондов"
        ])
        
        return recommendations
    
    def create_regional_comparison(
        self,
        industry: str,
        regions_data: dict
    ) -> RegionalComparisonReport:
        """
        Создание отчёта о сравнительном анализе регионов
        
        Args:
            industry: Отрасль для анализа
            regions_data: Данные по регионам
        
        Returns:
            Отчёт о сравнительном анализе
        """
        logger.info(f"Сравнительный анализ: {industry}")
        
        # Анализ сильных сторон
        strengths = self._identify_strengths(regions_data)
        
        # Анализ слабых сторон
        weaknesses = self._identify_weaknesses(regions_data)
        
        # Рекомендации
        recommendations = self._generate_regional_recommendations(
            industry, strengths, weaknesses
        )
        
        report = RegionalComparisonReport(
            target_region=self.target_region,
            industry=industry,
            compared_regions=list(regions_data.keys()),
            metrics=regions_data,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        return report
    
    def _identify_strengths(self, regions_data: dict) -> list[str]:
        """Выявление сильных сторон региона"""
        strengths = []
        
        target_data = regions_data.get(self.target_region, {})
        
        # Анализ данных
        if target_data.get("investment_volume", 0) > 100_000_000_000:
            strengths.append("Высокий объём инвестиций в отрасль")
        
        if target_data.get("infrastructure_score", 0) > 0.7:
            strengths.append("Хорошо развитая инфраструктура")
        
        # Стандартные сильные стороны Свердловской области
        strengths.extend([
            "Богатая минерально-сырьевая база",
            "Развитая промышленная инфраструктура",
            "Наличие квалифицированных кадров",
            "Транспортная доступность (Узел ж/д и автодорог)",
            "Наличие ОЭЗ 'Титановая долина'"
        ])
        
        return strengths
    
    def _identify_weaknesses(self, regions_data: dict) -> list[str]:
        """Выявление слабых сторон региона"""
        weaknesses = [
            "Высокая экологическая нагрузка в промышленных центрах",
            "Износ части инфраструктуры",
            "Отток квалифицированных кадров в центральные регионы"
        ]
        
        return weaknesses
    
    def _generate_regional_recommendations(
        self,
        industry: str,
        strengths: list[str],
        weaknesses: list[str]
    ) -> list[str]:
        """Генерация рекомендаций по развитию"""
        recommendations = [
            f"Использовать сильные стороны в отрасли '{industry}' для привлечения инвестиций",
            "Развивать инфраструктурные проекты в приоритетных локациях",
            "Внедрять лучшие практики из регионов-лидеров",
            "Усилить работу по удержанию квалифицированных кадров",
            "Развивать меры поддержки для целевой отрасли"
        ]
        
        return recommendations
    
    def export_analysis(
        self,
        analysis_result: any,
        output_path: Path
    ) -> Path:
        """Экспорт результатов анализа в JSON"""
        if hasattr(analysis_result, '__dataclass_fields__'):
            data = asdict(analysis_result)
        else:
            data = analysis_result
        
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding='utf-8'
        )
        
        logger.info(f"Результаты анализа экспортированы: {output_path}")
        return output_path
