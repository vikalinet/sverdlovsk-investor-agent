"""
ML-модель оценки применимости лучших практик

Оценивает, насколько хорошо практика из одного региона
может быть применена в другом регионе на основе:
- Экономической схожести
- Отраслевой структуры
- Инфраструктурной готовности
- Кадрового потенциала
- Регуляторной среды
"""
import json
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using rule-based model.")

from loguru import logger


@dataclass
class RegionFeatures:
    """Признаки региона"""
    # Экономические
    gdp_per_capita: float  # ВРП на душу населения
    industrial_output: float  # Объём промпроизводства
    investment_volume: float  # Объём инвестиций
    unemployment_rate: float  # Уровень безработицы
    
    # Отраслевые
    industry_share: float  # Доля промышленности в ВРП
    manufacturing_share: float  # Доля обрабатывающих производств
    high_tech_share: float  # Доля высокотехнологичных отраслей
    
    # Инфраструктура
    infrastructure_score: float  # Общая оценка инфраструктуры
    transport_score: float  # Транспортная доступность
    digital_score: float  # Цифровизация
    
    # Кадры
    education_score: float  # Качество образования
    labor_potential: float  # Кадровый потенциал
    migration_balance: float  # Миграционное сальдо
    
    # Регуляторная среда
    business_climate: float  # Климат для бизнеса
    support_measures: float  # Количество мер поддержки
    tax_burden: float  # Налоговая нагрузка
    
    @property
    def to_array(self) -> np.ndarray:
        """Преобразование в массив признаков"""
        return np.array([
            self.gdp_per_capita,
            self.industrial_output,
            self.investment_volume,
            self.unemployment_rate,
            self.industry_share,
            self.manufacturing_share,
            self.high_tech_share,
            self.infrastructure_score,
            self.transport_score,
            self.digital_score,
            self.education_score,
            self.labor_potential,
            self.migration_balance,
            self.business_climate,
            self.support_measures,
            self.tax_burden
        ])
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RegionFeatures':
        """Создание из словаря"""
        return cls(**data)


@dataclass
class PracticeFeatures:
    """Признаки практики"""
    # Характеристики практики
    investment_required: float  # Требуемые инвестиции
    implementation_time: float  # Срок внедрения (мес)
    complexity: float  # Сложность (1-10)
    innovation_level: float  # Уровень инновационности (1-10)
    
    # Отраслевые
    industry_match: float  # Соответствие отрасли региона
    technology_level: float  # Уровень технологии
    
    # Эффекты
    economic_effect: float  # Экономический эффект
    social_effect: float  # Социальный эффект
    environmental_effect: float  # Экологический эффект
    
    @property
    def to_array(self) -> np.ndarray:
        """Преобразование в массив признаков"""
        return np.array([
            self.investment_required,
            self.implementation_time,
            self.complexity,
            self.innovation_level,
            self.industry_match,
            self.technology_level,
            self.economic_effect,
            self.social_effect,
            self.environmental_effect
        ])
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PracticeFeatures':
        """Создание из словаря"""
        return cls(**data)


@dataclass
class ApplicabilityResult:
    """Результат оценки применимости"""
    score: float  # Общая оценка (0.0 - 1.0)
    confidence: float  # Уверенность модели (0.0 - 1.0)
    category: str  # Категория: high, medium, low
    factors: Dict[str, float]  # Влияние факторов
    recommendations: List[str]  # Рекомендации


class ApplicabilityModel:
    """
    ML-модель оценки применимости лучших практик
    
    Использует ансамбль моделей для оценки:
    1. Экономической целесообразности
    2. Технической возможности
    3. Социальной приемлемости
    """
    
    def __init__(self, model_type: str = "gradient_boosting"):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_names = self._get_feature_names()
        self.is_fitted = False
        
        # Данные по регионам (для демонстрации)
        self.regions_data = self._load_regions_data()
        
        logger.info(f"ApplicabilityModel инициализирована: type={model_type}")
    
    def _get_feature_names(self) -> List[str]:
        """Названия признаков"""
        return [
            # Регион (16 признаков)
            "gdp_per_capita", "industrial_output", "investment_volume",
            "unemployment_rate", "industry_share", "manufacturing_share",
            "high_tech_share", "infrastructure_score", "transport_score",
            "digital_score", "education_score", "labor_potential",
            "migration_balance", "business_climate", "support_measures",
            "tax_burden",
            # Практика (9 признаков)
            "investment_required", "implementation_time", "complexity",
            "innovation_level", "industry_match", "technology_level",
            "economic_effect", "social_effect", "environmental_effect",
            # Схожесть регионов (4 признака)
            "economic_similarity", "industry_similarity",
            "infrastructure_gap", "cadre_gap"
        ]
    
    def _load_regions_data(self) -> Dict[str, Dict]:
        """Данные по регионам РФ (упрощённые)"""
        return {
            "Свердловская область": {
                "gdp_per_capita": 0.7,
                "industrial_output": 0.9,
                "investment_volume": 0.6,
                "unemployment_rate": 0.3,
                "industry_share": 0.8,
                "manufacturing_share": 0.7,
                "high_tech_share": 0.5,
                "infrastructure_score": 0.7,
                "transport_score": 0.8,
                "digital_score": 0.6,
                "education_score": 0.7,
                "labor_potential": 0.7,
                "migration_balance": 0.4,
                "business_climate": 0.6,
                "support_measures": 0.7,
                "tax_burden": 0.5
            },
            "Челябинская область": {
                "gdp_per_capita": 0.65,
                "industrial_output": 0.85,
                "investment_volume": 0.55,
                "unemployment_rate": 0.35,
                "industry_share": 0.85,
                "manufacturing_share": 0.75,
                "high_tech_share": 0.45,
                "infrastructure_score": 0.65,
                "transport_score": 0.75,
                "digital_score": 0.55,
                "education_score": 0.65,
                "labor_potential": 0.7,
                "migration_balance": 0.3,
                "business_climate": 0.55,
                "support_measures": 0.65,
                "tax_burden": 0.5
            },
            "Пермский край": {
                "gdp_per_capita": 0.6,
                "industrial_output": 0.7,
                "investment_volume": 0.5,
                "unemployment_rate": 0.4,
                "industry_share": 0.75,
                "manufacturing_share": 0.65,
                "high_tech_share": 0.4,
                "infrastructure_score": 0.6,
                "transport_score": 0.65,
                "digital_score": 0.5,
                "education_score": 0.6,
                "labor_potential": 0.65,
                "migration_balance": 0.2,
                "business_climate": 0.5,
                "support_measures": 0.6,
                "tax_burden": 0.45
            },
            "Татарстан": {
                "gdp_per_capita": 0.8,
                "industrial_output": 0.75,
                "investment_volume": 0.75,
                "unemployment_rate": 0.25,
                "industry_share": 0.7,
                "manufacturing_share": 0.6,
                "high_tech_share": 0.6,
                "infrastructure_score": 0.75,
                "transport_score": 0.7,
                "digital_score": 0.7,
                "education_score": 0.75,
                "labor_potential": 0.75,
                "migration_balance": 0.5,
                "business_climate": 0.7,
                "support_measures": 0.75,
                "tax_burden": 0.55
            },
            "Московская область": {
                "gdp_per_capita": 1.0,
                "industrial_output": 0.6,
                "investment_volume": 1.0,
                "unemployment_rate": 0.15,
                "industry_share": 0.4,
                "manufacturing_share": 0.35,
                "high_tech_share": 0.9,
                "infrastructure_score": 0.95,
                "transport_score": 0.9,
                "digital_score": 0.95,
                "education_score": 0.9,
                "labor_potential": 0.85,
                "migration_balance": 0.8,
                "business_climate": 0.85,
                "support_measures": 0.9,
                "tax_burden": 0.6
            },
            "Башкортостан": {
                "gdp_per_capita": 0.55,
                "industrial_output": 0.65,
                "investment_volume": 0.45,
                "unemployment_rate": 0.4,
                "industry_share": 0.7,
                "manufacturing_share": 0.6,
                "high_tech_share": 0.35,
                "infrastructure_score": 0.55,
                "transport_score": 0.6,
                "digital_score": 0.45,
                "education_score": 0.55,
                "labor_potential": 0.6,
                "migration_balance": 0.2,
                "business_climate": 0.5,
                "support_measures": 0.55,
                "tax_burden": 0.45
            }
        }
    
    def calculate_region_similarity(
        self,
        region1: str,
        region2: str
    ) -> Dict[str, float]:
        """
        Расчёт схожести двух регионов
        
        Returns:
            Словарь с метриками схожести
        """
        data1 = self.regions_data.get(region1, {})
        data2 = self.regions_data.get(region2, {})
        
        if not data1 or not data2:
            return {
                "economic_similarity": 0.5,
                "industry_similarity": 0.5,
                "infrastructure_gap": 0.5,
                "cadre_gap": 0.5
            }
        
        # Экономическая схожесть
        economic_features = ["gdp_per_capita", "investment_volume", "industrial_output"]
        economic_sim = 1 - np.mean([
            abs(data1.get(f, 0.5) - data2.get(f, 0.5))
            for f in economic_features
        ])
        
        # Отраслевая схожесть
        industry_features = ["industry_share", "manufacturing_share", "high_tech_share"]
        industry_sim = 1 - np.mean([
            abs(data1.get(f, 0.5) - data2.get(f, 0.5))
            for f in industry_features
        ])
        
        # Инфраструктурный разрыв
        infra_features = ["infrastructure_score", "transport_score", "digital_score"]
        infra_gap = np.mean([
            abs(data1.get(f, 0.5) - data2.get(f, 0.5))
            for f in infra_features
        ])
        
        # Кадровый разрыв
        cadre_features = ["education_score", "labor_potential", "migration_balance"]
        cadre_gap = np.mean([
            abs(data1.get(f, 0.5) - data2.get(f, 0.5))
            for f in cadre_features
        ])
        
        return {
            "economic_similarity": round(economic_sim, 3),
            "industry_similarity": round(industry_sim, 3),
            "infrastructure_gap": round(infra_gap, 3),
            "cadre_gap": round(cadre_gap, 3)
        }
    
    def prepare_features(
        self,
        source_region: str,
        target_region: str,
        practice: PracticeFeatures
    ) -> np.ndarray:
        """
        Подготовка признаков для модели
        
        Args:
            source_region: Регион, где практика успешно применена
            target_region: Регион, куда планируется внедрение
            practice: Характеристики практики
        
        Returns:
            Массив признаков
        """
        # Получаем признаки регионов
        source_data = self.regions_data.get(source_region, {})
        target_data = self.regions_data.get(target_region, {})
        
        source_features = RegionFeatures(**source_data) if source_data else RegionFeatures(
            gdp_per_capita=0.5, industrial_output=0.5, investment_volume=0.5,
            unemployment_rate=0.5, industry_share=0.5, manufacturing_share=0.5,
            high_tech_share=0.5, infrastructure_score=0.5, transport_score=0.5,
            digital_score=0.5, education_score=0.5, labor_potential=0.5,
            migration_balance=0.5, business_climate=0.5, support_measures=0.5,
            tax_burden=0.5
        )
        
        target_features = RegionFeatures(**target_data) if target_data else RegionFeatures(
            gdp_per_capita=0.5, industrial_output=0.5, investment_volume=0.5,
            unemployment_rate=0.5, industry_share=0.5, manufacturing_share=0.5,
            high_tech_share=0.5, infrastructure_score=0.5, transport_score=0.5,
            digital_score=0.5, education_score=0.5, labor_potential=0.5,
            migration_balance=0.5, business_climate=0.5, support_measures=0.5,
            tax_burden=0.5
        )
        
        # Схожесть регионов
        similarity = self.calculate_region_similarity(source_region, target_region)
        
        # Объединяем все признаки
        features = np.concatenate([
            target_features.to_array,  # 16 признаков целевого региона
            practice.to_array,  # 9 признаков практики
            np.array([
                similarity["economic_similarity"],
                similarity["industry_similarity"],
                1 - similarity["infrastructure_gap"],  # Инвертируем: меньше разрыв = лучше
                1 - similarity["cadre_gap"]
            ])
        ])
        
        return features
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Обучение модели
        
        Args:
            X: Матрица признаков
            y: Целевая переменная (0 - не применима, 1 - применима)
            test_size: Доля тестовой выборки
        
        Returns:
            Метрики качества
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn не доступен, использую rule-based модель")
            return {"accuracy": 0.0}
        
        # Разделение на train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Нормализация признаков
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Обучение модели
        if self.model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        
        self.model.fit(X_train_scaled, y_train)
        self.is_fitted = True
        
        # Оценка качества
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Модель обучена. Accuracy: {accuracy:.3f}")
        
        return {
            "accuracy": accuracy,
            "test_size": len(y_test),
            "train_size": len(y_train)
        }
    
    def predict(
        self,
        source_region: str,
        target_region: str,
        practice: PracticeFeatures
    ) -> ApplicabilityResult:
        """
        Предсказание применимости практики
        
        Args:
            source_region: Регион источника
            target_region: Целевой регион
            practice: Характеристики практики
        
        Returns:
            Результат оценки
        """
        # Подготовка признаков
        features = self.prepare_features(source_region, target_region, practice)
        features_scaled = self.scaler.transform([features]) if self.scaler else [features]
        
        # Предсказание
        if self.model and self.is_fitted:
            score = self.model.predict_proba(features_scaled)[0][1]
            confidence = float(np.max(self.model.predict_proba(features_scaled)))
        else:
            # Rule-based оценка если модель не обучена
            score, confidence = self._rule_based_predict(
                source_region, target_region, practice
            )
        
        # Определение категории
        if score >= 0.7:
            category = "high"
        elif score >= 0.4:
            category = "medium"
        else:
            category = "low"
        
        # Анализ факторов
        factors = self._analyze_factors(source_region, target_region, practice)
        
        # Рекомендации
        recommendations = self._generate_recommendations(
            score, category, factors
        )
        
        return ApplicabilityResult(
            score=round(score, 3),
            confidence=round(confidence, 3),
            category=category,
            factors=factors,
            recommendations=recommendations
        )
    
    def _rule_based_predict(
        self,
        source_region: str,
        target_region: str,
        practice: PracticeFeatures
    ) -> Tuple[float, float]:
        """
        Rule-based оценка (если модель не обучена)
        
        Возвращает (score, confidence)
        """
        similarity = self.calculate_region_similarity(source_region, target_region)
        
        # Базовая оценка на основе схожести регионов
        base_score = (
            similarity["economic_similarity"] * 0.3 +
            similarity["industry_similarity"] * 0.4 +
            (1 - similarity["infrastructure_gap"]) * 0.15 +
            (1 - similarity["cadre_gap"]) * 0.15
        )
        
        # Корректировка на сложность практики
        complexity_factor = 1 - (practice.complexity / 10) * 0.3
        
        # Корректировка на требуемые инвестиции
        investment_factor = 1.0
        if practice.investment_required > 0.8:  # Высокие инвестиции
            investment_factor = 0.8
        
        score = base_score * complexity_factor * investment_factor
        score = np.clip(score, 0.0, 1.0)
        
        # Уверенность
        confidence = 0.7  # Средняя уверенность для rule-based
        
        return score, confidence
    
    def _analyze_factors(
        self,
        source_region: str,
        target_region: str,
        practice: PracticeFeatures
    ) -> Dict[str, float]:
        """Анализ влияния факторов"""
        similarity = self.calculate_region_similarity(source_region, target_region)
        
        return {
            "economic_similarity": similarity["economic_similarity"],
            "industry_match": similarity["industry_similarity"],
            "infrastructure_readiness": 1 - similarity["infrastructure_gap"],
            "cadre_availability": 1 - similarity["cadre_gap"],
            "practice_complexity": 1 - (practice.complexity / 10),
            "investment_feasibility": 1 - (practice.investment_required * 0.3),
            "economic_effect": practice.economic_effect,
            "social_effect": practice.social_effect
        }
    
    def _generate_recommendations(
        self,
        score: float,
        category: str,
        factors: Dict[str, float]
    ) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        if category == "high":
            recommendations.append("Практика высоко применима для региона")
            recommendations.append("Рекомендуется к внедрению в приоритетном порядке")
        elif category == "medium":
            recommendations.append("Практика применима с некоторыми ограничениями")
            recommendations.append("Требуется адаптация под региональные особенности")
        else:
            recommendations.append("Применимость практики ограничена")
            recommendations.append("Рекомендуется рассмотреть альтернативные решения")
        
        # Рекомендации по факторам
        if factors.get("infrastructure_readiness", 0.5) < 0.5:
            recommendations.append("Необходимо развитие инфраструктуры перед внедрением")
        
        if factors.get("cadre_availability", 0.5) < 0.5:
            recommendations.append("Требуется программа подготовки кадров")
        
        if factors.get("practice_complexity", 0.5) < 0.5:
            recommendations.append("Высокая сложность требует поэтапного внедрения")
        
        return recommendations
    
    def generate_training_data(
        self,
        n_samples: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Генерация синтетических данных для обучения
        
        Args:
            n_samples: Количество образцов
        
        Returns:
            X, y
        """
        regions = list(self.regions_data.keys())
        X = []
        y = []
        
        for _ in range(n_samples):
            # Случайные регионы
            source = np.random.choice(regions)
            target = np.random.choice(regions)
            
            # Случайная практика
            practice = PracticeFeatures(
                investment_required=np.random.uniform(0.1, 1.0),
                implementation_time=np.random.uniform(3, 24),
                complexity=np.random.uniform(1, 10),
                innovation_level=np.random.uniform(1, 10),
                industry_match=np.random.uniform(0.3, 1.0),
                technology_level=np.random.uniform(1, 10),
                economic_effect=np.random.uniform(0.1, 1.0),
                social_effect=np.random.uniform(0.1, 1.0),
                environmental_effect=np.random.uniform(0.1, 1.0)
            )
            
            features = self.prepare_features(source, target, practice)
            X.append(features)
            
            # Генерация целевой переменной на основе схожести
            similarity = self.calculate_region_similarity(source, target)
            base_prob = (
                similarity["economic_similarity"] * 0.3 +
                similarity["industry_similarity"] * 0.4 +
                (1 - practice.complexity / 10) * 0.3
            )
            
            # Добавляем шум
            label = 1 if (base_prob + np.random.normal(0, 0.1)) > 0.5 else 0
            y.append(label)
        
        return np.array(X), np.array(y)
    
    def save_model(self, path: str):
        """Сохранение модели"""
        if not self.is_fitted:
            logger.warning("Модель не обучена, сохранение невозможно")
            return
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "model_type": self.model_type,
            "feature_names": self.feature_names
        }
        
        with open(path, "wb") as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Модель сохранена: {path}")
    
    def load_model(self, path: str):
        """Загрузка модели"""
        with open(path, "rb") as f:
            model_data = pickle.load(f)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.model_type = model_data["model_type"]
        self.is_fitted = True
        
        logger.info(f"Модель загружена: {path}")


# Пример использования
async def main():
    model = ApplicabilityModel(model_type="gradient_boosting")
    
    # Генерация данных для обучения
    X, y = model.generate_training_data(n_samples=200)
    
    # Обучение
    metrics = model.train(X, y, test_size=0.2)
    print(f"Метрики: {metrics}")
    
    # Оценка практики
    practice = PracticeFeatures(
        investment_required=0.5,
        implementation_time=12,
        complexity=6,
        innovation_level=7,
        industry_match=0.8,
        technology_level=7,
        economic_effect=0.7,
        social_effect=0.6,
        environmental_effect=0.5
    )
    
    result = model.predict(
        source_region="Челябинская область",
        target_region="Свердловская область",
        practice=practice
    )
    
    print(f"\nРезультат оценки:")
    print(f"  Score: {result.score:.3f}")
    print(f"  Confidence: {result.confidence:.3f}")
    print(f"  Category: {result.category}")
    print(f"  Рекомендации: {result.recommendations[:2]}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
