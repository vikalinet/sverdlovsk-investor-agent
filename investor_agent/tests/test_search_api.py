"""
Тесты для поискового API клиента
"""
import pytest
import asyncio
from src.search_api_client import SearchAPIClient, SearchResponse


class TestSearchAPIClient:
    """Тесты поискового клиента"""
    
    def test_init(self):
        client = SearchAPIClient(provider="mock")
        assert client.provider == "mock"
        assert client.max_results > 0
    
    @pytest.mark.asyncio
    async def test_search_mock(self):
        async with SearchAPIClient(provider="mock") as client:
            results = await client.search("лучшие практики металлургия")
            
            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, SearchResponse) for r in results)
    
    @pytest.mark.asyncio
    async def test_search_with_region(self):
        async with SearchAPIClient(provider="mock") as client:
            results = await client.search(
                "инвестиционные площадки",
                region="Урал"
            )
            
            assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_search_best_practices(self):
        async with SearchAPIClient(provider="mock") as client:
            regions = ["Челябинская область", "Пермский край"]
            results = await client.search_best_practices(
                industry="металлургия",
                regions=regions
            )
            
            assert isinstance(results, dict)
            assert "Челябинская область" in results
            assert "Пермский край" in results
    
    @pytest.mark.asyncio
    async def test_search_news(self):
        async with SearchAPIClient(provider="mock") as client:
            results = await client.search_news(
                "инвестиции Свердловская область",
                days_back=7
            )
            
            assert isinstance(results, list)


class TestSearchModuleWithAPI:
    """Тесты search_module с API"""
    
    @pytest.mark.asyncio
    async def test_search_with_mock_provider(self):
        from src.search_module import SearchModule
        
        module = SearchModule(search_provider="mock")
        practices = await module.search_best_practices(
            industry="металлургия"
        )
        
        assert len(practices) > 0
        assert all(hasattr(p, 'applicability_score') for p in practices)
    
    @pytest.mark.asyncio
    async def test_practices_sorted_by_score(self):
        from src.search_module import SearchModule
        
        module = SearchModule(search_provider="mock")
        practices = await module.search_best_practices(
            industry="IT"
        )
        
        if len(practices) > 1:
            scores = [p.applicability_score for p in practices]
            assert scores == sorted(scores, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
