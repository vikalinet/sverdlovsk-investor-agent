"""
Тесты для репозиториев

Запуск:
    pytest tests/unit/test_repositories.py -v
"""
import pytest
import pytest_asyncio
from typing import Dict, Any


class TestSupportMeasuresRepository:
    """Тесты для SupportMeasuresRepository"""
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, support_measures_repo):
        """Тест получения меры по ID"""
        measure = await support_measures_repo.get_by_id("GRANT-IND-001")
        
        assert measure is not None
        assert measure.id == "GRANT-IND-001"
        assert measure.type == "grant"
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, support_measures_repo):
        """Тест получения несуществующей меры"""
        measure = await support_measures_repo.get_by_id("NONEXISTENT")
        
        assert measure is None
    
    @pytest.mark.asyncio
    async def test_find_by_industry(self, support_measures_repo, sample_industry):
        """Тест поиска по отрасли"""
        measures = await support_measures_repo.find_by_industry(sample_industry)
        
        assert isinstance(measures, list)
        assert len(measures) > 0
        assert all(m.industry and sample_industry.lower() in m.industry.lower() 
                   for m in measures)
    
    @pytest.mark.asyncio
    async def test_find_by_type(self, support_measures_repo):
        """Тест поиска по типу"""
        measures = await support_measures_repo.find_by_type("grant")
        
        assert isinstance(measures, list)
        assert all(m.type == "grant" for m in measures)
    
    @pytest.mark.asyncio
    async def test_find_by_filters(self, support_measures_repo):
        """Тест поиска по фильтрам"""
        filters = {
            "type": "grant",
            "min_amount": 5_000_000
        }
        measures = await support_measures_repo.find_by(filters)
        
        assert isinstance(measures, list)
        assert all(m.type == "grant" for m in measures)
        assert all(m.max_amount >= 5_000_000 for m in measures)
    
    @pytest.mark.asyncio
    async def test_create(self, support_measures_repo):
        """Тест создания меры"""
        new_measure = await support_measures_repo.create({
            "id": "TEST-NEW-001",
            "name": "Новая тестовая мера",
            "type": "fund",
            "max_amount": 20_000_000,
            "industry": "IT",
            "is_active": True
        })
        
        assert new_measure.id == "TEST-NEW-001"
        assert new_measure.name == "Новая тестовая мера"
        
        # Проверка что сохранена
        retrieved = await support_measures_repo.get_by_id("TEST-NEW-001")
        assert retrieved is not None
        assert retrieved.name == "Новая тестовая мера"
    
    @pytest.mark.asyncio
    async def test_update(self, support_measures_repo):
        """Тест обновления меры"""
        updated = await support_measures_repo.update(
            "GRANT-IND-001",
            {"max_amount": 35_000_000}
        )
        
        assert updated is not None
        assert updated.max_amount == 35_000_000
        
        # Проверка что обновлена в хранилище
        retrieved = await support_measures_repo.get_by_id("GRANT-IND-001")
        assert retrieved.max_amount == 35_000_000
    
    @pytest.mark.asyncio
    async def test_delete(self, support_measures_repo):
        """Тест удаления меры (мягкое)"""
        result = await support_measures_repo.delete("GRANT-IND-001")
        
        assert result is True
        
        # Мера должна быть деактивирована
        measure = await support_measures_repo.get_by_id("GRANT-IND-001")
        assert measure is not None
        assert measure.is_active is False
    
    @pytest.mark.asyncio
    async def test_count(self, support_measures_repo):
        """Тест подсчёта количества"""
        count = await support_measures_repo.count()
        
        assert count > 0
        assert isinstance(count, int)
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, support_measures_repo):
        """Тест получения статистики"""
        stats = await support_measures_repo.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total" in stats
        assert "active" in stats
        assert "by_type" in stats
        assert "total_funding" in stats


class TestInvestmentObjectsRepository:
    """Тесты для InvestmentObjectsRepository"""
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, investment_objects_repo):
        """Тест получения объекта по ID"""
        obj = await investment_objects_repo.get_by_id("INV-SVE-001")
        
        assert obj is not None
        assert obj.id == "INV-SVE-001"
        assert obj.type == "парк"
    
    @pytest.mark.asyncio
    async def test_find_by_location(self, investment_objects_repo):
        """Тест поиска по локации"""
        objects = await investment_objects_repo.find_by_location("Екатеринбург")
        
        assert isinstance(objects, list)
        assert all("Екатеринбург" in obj.location for obj in objects)
    
    @pytest.mark.asyncio
    async def test_find_by_industry(self, investment_objects_repo, sample_industry):
        """Тест поиска по отрасли"""
        objects = await investment_objects_repo.find_by_industry(sample_industry)
        
        assert isinstance(objects, list)
        assert all(
            obj.industry and sample_industry.lower() in obj.industry.lower()
            for obj in objects
        )
    
    @pytest.mark.asyncio
    async def test_find_by_price_range(self, investment_objects_repo):
        """Тест поиска по диапазону цены"""
        objects = await investment_objects_repo.find_by_price_range(
            min_price=100_000_000,
            max_price=600_000_000
        )
        
        assert isinstance(objects, list)
        assert all(
            obj.price and 100_000_000 <= obj.price <= 600_000_000
            for obj in objects
        )
    
    @pytest.mark.asyncio
    async def test_create(self, investment_objects_repo):
        """Тест создания объекта"""
        new_obj = await investment_objects_repo.create({
            "id": "TEST-OBJ-NEW",
            "name": "Новый тестовый объект",
            "type": "площадка",
            "location": "Тестовый город",
            "price": 75_000_000,
            "area": 2000,
            "industry": "металлургия",
            "status": "active"
        })
        
        assert new_obj.id == "TEST-OBJ-NEW"
        assert new_obj.name == "Новый тестовый объект"
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, investment_objects_repo):
        """Тест получения статистики"""
        stats = await investment_objects_repo.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total" in stats
        assert "active" in stats
        assert "by_type" in stats
        assert "by_industry" in stats
        assert "total_investment" in stats


class TestRepositoryCaching:
    """Тесты кэширования в репозиториях"""
    
    @pytest.mark.asyncio
    async def test_cache_get_after_first_call(self, support_measures_repo):
        """Тест что кэш заполняется после первого запроса"""
        # Первый запрос
        await support_measures_repo.get_by_id("GRANT-IND-001")
        
        # Проверка кэша
        cached = support_measures_repo._cache_get("measure:GRANT-IND-001")
        assert cached is not None
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_update(self, support_measures_repo):
        """Тест инвалидации кэша при обновлении"""
        # Получение и кэширование
        await support_measures_repo.get_by_id("GRANT-IND-001")
        
        # Обновление
        await support_measures_repo.update("GRANT-IND-001", {"max_amount": 999})
        
        # Кэш должен быть инвалидирован
        cached = support_measures_repo._cache_get("measure:GRANT-IND-001")
        assert cached is None


class TestInMemoryRepository:
    """Тесты для базового InMemoryRepository"""
    
    @pytest.mark.asyncio
    async def test_crud_operations(self):
        """Тест CRUD операций"""
        from src.repositories import InMemoryRepository
        from pydantic import BaseModel
        
        class TestEntity(BaseModel):
            id: str
            name: str
            value: int = 0
        
        repo = InMemoryRepository(TestEntity)
        
        # Create
        entity = await repo.create({"id": "test-1", "name": "Test", "value": 10})
        assert entity.id == "test-1"
        
        # Read
        retrieved = await repo.get_by_id("test-1")
        assert retrieved is not None
        assert retrieved.name == "Test"
        
        # Update
        updated = await repo.update("test-1", {"value": 20})
        assert updated.value == 20
        
        # Delete
        deleted = await repo.delete("test-1")
        assert deleted is True
        
        not_found = await repo.get_by_id("test-1")
        assert not_found is None
