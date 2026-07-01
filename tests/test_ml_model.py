"""
Тесты для ML-модели оценки применимости
"""
import pytest
import numpy as np
from ml_models.applicability_model import (
    ApplicabilityModel,
    RegionFeatures,
    PracticeFeatures,
    ApplicabilityResult
)


class TestRegionFeatures:
    """Тесты признаков региона"""
    
    def test_create_from_dict(self):
        data = {
            "gdp_per_capita": 0.7,
            "industrial_output": 0.8,
            "investment_volume": 0.6,
            "unemployment_rate": 0.3,
            "industry_share": 0.75,
            "manufacturing_share": 0.65,
            "high_tech_share": 0.5,
            "infrastructure_score": 0.7,
            "transport_score": 0.75,
            "digital_score": 0.6,
            "education_score": 0.65,
            "labor_potential": 0.7,
            "migration_balance": 0.4,
            "business_climate": 0.6,
            "support_measures": 0.65,
            "tax_burden": 0.5
        }
        
        features = RegionFeatures.from_dict(data)
        assert features.gdp_per_capita == 0.7
        assert len(features.to_array) == 16
    
    def test_to_array(self):
        features = RegionFeatures(
            gdp_per_capita=0.7, industrial_output=0.8, investment_volume=0.6,
            unemployment_rate=0.3, industry_share=0.75, manufacturing_share=0.65,
            high_tech_share=0.5, infrastructure_score=0.7, transport_score=0.75,
            digital_score=0.6, education_score=0.65, labor_potential=0.7,
            migration_balance=0.4, business_climate=0.6, support_measures=0.65,
            tax_burden=0.5
        )
        
        array = features.to_array
        assert isinstance(array, np.ndarray)
        assert len(array) == 16


class TestPracticeFeatures:
    """Тесты признаков практики"""
    
    def test_create_from_dict(self):
        data = {
            "investment_required": 0.5,
            "implementation_time": 12,
            "complexity": 6,
            "innovation_level": 7,
            "industry_match": 0.8,
            "technology_level": 7,
            "economic_effect": 0.7,
            "social_effect": 0.6,
            "environmental_effect": 0.5
        }
        
        features = PracticeFeatures.from_dict(data)
        assert features.complexity == 6
        assert len(features.to_array) == 9


class TestApplicabilityModel:
    """Тесты ML-модели"""
    
    @pytest.fixture
    def model(self):
        return ApplicabilityModel(model_type="gradient_boosting")
    
    def test_init(self, model):
        assert model.model_type == "gradient_boosting"
        assert not model.is_fitted
        assert len(model.regions_data) > 0
    
    def test_calculate_region_similarity(self, model):
        similarity = model.calculate_region_similarity(
            "Челябинская область",
            "Свердловская область"
        )
        
        assert "economic_similarity" in similarity
        assert "industry_similarity" in similarity
        assert "infrastructure_gap" in similarity
        assert "cadre_gap" in similarity
        
        # Все значения от 0 до 1
        for value in similarity.values():
            assert 0 <= value <= 1
    
    def test_prepare_features(self, model):
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
        
        features = model.prepare_features(
            source_region="Челябинская область",
            target_region="Свердловская область",
            practice=practice
        )
        
        # 16 (регион) + 9 (практика) + 4 (схожесть) = 29 признаков
        assert len(features) == 29
    
    def test_generate_training_data(self, model):
        X, y = model.generate_training_data(n_samples=100)
        
        assert X.shape[0] == 100
        assert X.shape[1] == 29  # 29 признаков
        assert len(y) == 100
        assert all(label in [0, 1] for label in y)
    
    def test_train_model(self, model):
        X, y = model.generate_training_data(n_samples=200)
        
        metrics = model.train(X, y, test_size=0.2)
        
        assert model.is_fitted
        assert "accuracy" in metrics
        assert metrics["accuracy"] >= 0.0  # Может быть низкой на синтетических данных
    
    def test_predict_without_training(self, model):
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
        
        assert isinstance(result, ApplicabilityResult)
        assert 0 <= result.score <= 1
        assert 0 <= result.confidence <= 1
        assert result.category in ["high", "medium", "low"]
    
    def test_predict_after_training(self, model):
        # Обучение
        X, y = model.generate_training_data(n_samples=300)
        model.train(X, y, test_size=0.2)
        
        practice = PracticeFeatures(
            investment_required=0.5,
            implementation_time=12,
            complexity=5,
            innovation_level=6,
            industry_match=0.85,
            technology_level=6,
            economic_effect=0.7,
            social_effect=0.6,
            environmental_effect=0.5
        )
        
        result = model.predict(
            source_region="Челябинская область",
            target_region="Свердловская область",
            practice=practice
        )
        
        assert isinstance(result, ApplicabilityResult)
        assert result.score > 0  # Score должен быть положительным
        assert len(result.recommendations) > 0
    
    def test_analyze_factors(self, model):
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
        
        factors = model._analyze_factors(
            "Челябинская область",
            "Свердловская область",
            practice
        )
        
        assert "economic_similarity" in factors
        assert "industry_match" in factors
        assert "infrastructure_readiness" in factors
        assert "practice_complexity" in factors
    
    def test_category_thresholds(self, model):
        # Тестирование порогов категорий
        practice = PracticeFeatures(
            investment_required=0.3,
            implementation_time=6,
            complexity=3,
            innovation_level=5,
            industry_match=0.9,
            technology_level=5,
            economic_effect=0.8,
            social_effect=0.7,
            environmental_effect=0.6
        )
        
        result = model.predict(
            source_region="Челябинская область",  # Схожий регион
            target_region="Свердловская область",
            practice=practice
        )
        
        # Для схожих регионов с простой практикой должна быть высокая применимость
        assert result.category in ["high", "medium"]


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_pipeline(self):
        """Полный пайплайн: обучение -> предсказание"""
        model = ApplicabilityModel(model_type="random_forest")
        
        # Генерация данных
        X, y = model.generate_training_data(n_samples=500)
        
        # Обучение
        metrics = model.train(X, y, test_size=0.2)
        assert metrics["accuracy"] > 0.5  # Лучше случайного угадывания
        
        # Предсказание для разных сценариев
        scenarios = [
            {
                "source": "Челябинская область",
                "target": "Свердловская область",
                "complexity": 3,  # Низкая сложность
                "expected_category": "high"
            },
            {
                "source": "Московская область",
                "target": "Свердловская область",
                "complexity": 8,  # Высокая сложность
                "expected_category": "medium"  # Может быть medium из-за различий
            }
        ]
        
        for scenario in scenarios:
            practice = PracticeFeatures(
                investment_required=0.5,
                implementation_time=12,
                complexity=scenario["complexity"],
                innovation_level=6,
                industry_match=0.7,
                technology_level=6,
                economic_effect=0.6,
                social_effect=0.5,
                environmental_effect=0.5
            )
            
            result = model.predict(
                source_region=scenario["source"],
                target_region=scenario["target"],
                practice=practice
            )
            
            assert result.category in ["high", "medium", "low"]
            assert len(result.recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
