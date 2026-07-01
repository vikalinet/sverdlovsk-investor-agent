# 🤖 ML-модель оценки применимости практик

## Обзор

Модель машинного обучения для оценки того, насколько хорошо лучшая практика из одного региона может быть применена в другом регионе.

## 📁 Структура

```
ml_models/
├── __init__.py
└── applicability_model.py    # Основная ML-модель
```

## 🔬 Методология

### Признаки модели (29 признаков)

#### 1. Признаки региона (16)
- **Экономические**: ВРП на душу населения, объём промпроизводства, инвестиции
- **Отраслевые**: Доля промышленности, обрабатывающих производств, high-tech
- **Инфраструктура**: Общая оценка, транспорт, цифровизация
- **Кадры**: Образование, кадровый потенциал, миграция
- **Регуляторика**: Климат для бизнеса, меры поддержки, налоги

#### 2. Признаки практики (9)
- Требуемые инвестиции
- Срок внедрения
- Сложность (1-10)
- Инновационность (1-10)
- Соответствие отрасли
- Уровень технологии
- Экономический эффект
- Социальный эффект
- Экологический эффект

#### 3. Схожесть регионов (4)
- Экономическая схожесть
- Отраслевая схожесть
- Инфраструктурный разрыв
- Кадровый разрыв

### Алгоритмы

**По умолчанию**: Gradient Boosting Classifier
- 100 деревьев
- Максимальная глубина: 5
- Random state: 42

**Альтернатива**: Random Forest Classifier
- 100 деревьев
- Максимальная глубина: 10

### Rule-based модель

Если scikit-learn недоступен, используется экспертная система:

```python
score = (
    economic_similarity * 0.3 +
    industry_similarity * 0.4 +
    (1 - infrastructure_gap) * 0.15 +
    (1 - cadre_gap) * 0.15
) * complexity_factor * investment_factor
```

## 🚀 Использование

### Базовое

```python
from ml_models.applicability_model import ApplicabilityModel, PracticeFeatures

# Инициализация
model = ApplicabilityModel(model_type="gradient_boosting")

# Генерация данных для обучения
X, y = model.generate_training_data(n_samples=300)

# Обучение
metrics = model.train(X, y, test_size=0.2)
print(f"Accuracy: {metrics['accuracy']:.3f}")

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

print(f"Score: {result.score:.3f}")
print(f"Category: {result.category}")
print(f"Recommendations: {result.recommendations}")
```

### Интеграция с агентом

```python
from src.analysis_module import AnalysisModule

# С ML-моделью
analysis = AnalysisModule(use_ml=True)

# Анализ практики с ML
practice_analysis = analysis.analyze_practice(
    practice=best_practice,
    use_ml=True
)

print(f"ML Score: {practice_analysis.applicability_score:.3f}")
```

## 📊 Категории применимости

| Категория | Score | Описание |
|-----------|-------|----------|
| **High** | ≥ 0.7 | Практика высоко применима, рекомендуется к внедрению |
| **Medium** | 0.4 - 0.7 | Применима с ограничениями, требуется адаптация |
| **Low** | < 0.4 | Применимость ограничена, рассмотреть альтернативы |

## 🧪 Тестирование

```powershell
# Запуск тестов
pytest tests/test_ml_model.py -v

# Тесты с выводом
pytest tests/test_ml_model.py -v -s
```

### Покрытие тестов

- ✅ Создание признаков региона
- ✅ Создание признаков практики
- ✅ Расчёт схожести регионов
- ✅ Подготовка признаков
- ✅ Генерация обучающих данных
- ✅ Обучение модели
- ✅ Предсказание (с обучением и без)
- ✅ Анализ факторов
- ✅ Категоризация
- ✅ Полный пайплайн

## 📈 Метрики качества

На синтетических данных (300 образцов):
- **Accuracy**: ~0.85-0.95
- **Precision**: зависит от баланса классов
- **Recall**: зависит от баланса классов

Для продакшена требуется:
1. Реальные данные по внедрению практик
2. Экспертная валидация
3. Дообучение на актуальных данных

## 🔧 Настройка

### Изменение типа модели

```python
model = ApplicabilityModel(model_type="random_forest")
```

### Сохранение/загрузка

```python
# Сохранение
model.save_model("models/applicability.pkl")

# Загрузка
model.load_model("models/applicability.pkl")
```

### Добавление регионов

```python
model.regions_data["Новый регион"] = {
    "gdp_per_capita": 0.7,
    "industrial_output": 0.8,
    # ... остальные признаки
}
```

## 📝 Интерпретация результатов

### Пример вывода

```
Score: 0.823
Confidence: 0.912
Category: high

Факторы:
  - economic_similarity: 0.85
  - industry_match: 0.90
  - infrastructure_readiness: 0.75
  - cadre_availability: 0.70
  - practice_complexity: 0.60

Рекомендации:
  1. Практика высоко применима для региона
  2. Рекомендуется к внедрению в приоритетном порядке
  3. Требуется программа подготовки кадров
```

### Анализ факторов

- **economic_similarity > 0.8**: Отличная экономическая схожесть
- **industry_match > 0.7**: Хорошее соответствие отраслевой структуры
- **infrastructure_readiness < 0.5**: Требуется развитие инфраструктуры
- **practice_complexity < 0.5**: Высокая сложность внедрения

## 🛠️ Расширение

### Добавление новых признаков

```python
@dataclass
class RegionFeatures:
    # Добавить новое поле
    innovation_index: float
    
    @property
    def to_array(self) -> np.ndarray:
        return np.array([
            # ... существующие
            self.innovation_index  # Новый признак
        ])
```

### Кастомная функция схожести

```python
def custom_similarity(self, region1: str, region2: str) -> float:
    # Ваша логика расчёта
    return similarity_score
```

### Ансамбль моделей

```python
from sklearn.ensemble import VotingClassifier

ensemble = VotingClassifier(
    estimators=[
        ('gb', GradientBoostingClassifier()),
        ('rf', RandomForestClassifier()),
        ('xgb', XGBClassifier())
    ],
    voting='soft'
)
```

## 📋 Рекомендации для продакшена

1. **Данные**
   - Собрать реальные кейсы внедрения практик
   - Разметить данные с экспертами
   - Регулярно обновлять датасет

2. **Валидация**
   - Кросс-валидация на реальных данных
   - Экспертная оценка предсказаний
   - A/B тестирование рекомендаций

3. **Мониторинг**
   - Логировать все предсказания
   - Отслеживать accuracy на новых данных
   - Переобучать при drift

4. **Интерпретируемость**
   - Использовать SHAP/LIME для объяснений
   - Показывать важность признаков
   - Предоставлять confidence интервалы

## 🔗 Ссылки

- [scikit-learn Gradient Boosting](https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)
- [Feature Engineering](https://scikit-learn.org/stable/modules/preprocessing.html)
- [Model Interpretation with SHAP](https://github.com/slundberg/shap)
