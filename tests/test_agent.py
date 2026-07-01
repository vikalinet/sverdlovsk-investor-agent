"""
Тесты для агента-помощника инвестора
"""
import pytest
import asyncio
from pathlib import Path

from src.agent import InvestorAgent
from src.search_module import SearchModule, BestPractice
from src.database_module import DatabaseModule, SupportMeasure
from src.documents_module import DocumentsModule
from src.analysis_module import AnalysisModule


class TestSearchModule:
    """Тесты модуля поиска"""
    
    @pytest.fixture
    def search_module(self):
        return SearchModule()
    
    def test_init(self, search_module):
        assert search_module.target_region == "Свердловская область"
        assert search_module.max_results > 0
    
    @pytest.mark.asyncio
    async def test_search_best_practices(self, search_module):
        practices = await search_module.search_best_practices(
            industry="металлургия"
        )
        assert isinstance(practices, list)
        # Практики должны быть отсортированы по применимости
        if len(practices) > 1:
            assert practices[0].applicability_score >= practices[1].applicability_score
    
    @pytest.mark.asyncio
    async def test_search_investment_opportunities(self, search_module):
        opportunities = await search_module.search_investment_opportunities(
            industry="IT"
        )
        assert isinstance(opportunities, list)
        for opp in opportunities:
            assert opp.title
            assert opp.type in ["площадка", "бизнес", "объект"]


class TestDatabaseModule:
    """Тесты модуля базы данных"""
    
    @pytest.fixture
    def db_module(self):
        return DatabaseModule()
    
    def test_init(self, db_module):
        assert db_module.target_region == "Свердловская область"
    
    @pytest.mark.asyncio
    async def test_get_support_measures(self, db_module):
        measures = await db_module.get_support_measures(
            industry="металлургия"
        )
        assert isinstance(measures, list)
        for measure in measures:
            assert isinstance(measure, SupportMeasure)
            assert measure.id
            assert measure.name
    
    @pytest.mark.asyncio
    async def test_get_investment_objects(self, db_module):
        objects = await db_module.get_investment_objects(
            location="Екатеринбург"
        )
        assert isinstance(objects, list)
        for obj in objects:
            assert obj.name
            assert "Свердловская область" in obj.location


class TestDocumentsModule:
    """Тесты модуля документов"""
    
    @pytest.fixture
    def docs_module(self, tmp_path):
        module = DocumentsModule()
        module.output_dir = tmp_path
        return module
    
    def test_init(self, docs_module):
        assert len(docs_module.templates) > 0
        assert "grant_application" in docs_module.templates
    
    def test_generate_document(self, docs_module, tmp_path):
        data = {
            "applicant_name": "ООО 'Тест'",
            "inn": "6601000001",
            "project_name": "Тестовый проект",
            "investment_amount": 10_000_000,
            "grant_amount": 3_000_000,
            "jobs_created": 10,
            "description": "Описание проекта",
            "industry": "металлургия"
        }
        
        output_path = docs_module.generate_document(
            template_id="grant_application",
            data=data,
            output_filename="test_grant.txt"
        )
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert "ООО 'Тест'" in content
        assert "6601000001" in content
    
    def test_create_document_package(self, docs_module, tmp_path):
        project_data = {
            "applicant_name": "ООО 'Тест'",
            "inn": "6601000001",
            "project_name": "Тест",
            "investment_amount": 10_000_000,
            "grant_amount": 3_000_000,
            "jobs_created": 10,
            "description": "Описание"
        }
        
        package = docs_module.create_document_package(
            measure_name="Тестовый грант",
            measure_type="grant",
            project_data=project_data
        )
        
        assert package.id.startswith("PKG-")
        assert package.measure_type == "grant"
        assert len(package.documents) > 0
    
    def test_get_checklist(self, docs_module):
        checklist = docs_module.get_checklist_for_measure("grant")
        assert isinstance(checklist, list)
        assert len(checklist) > 0
        assert any("Бизнес-план" in item for item in checklist)


class TestAnalysisModule:
    """Тесты модуля анализа"""
    
    @pytest.fixture
    def analysis_module(self):
        return AnalysisModule()
    
    def test_init(self, analysis_module):
        assert analysis_module.target_region == "Свердловская область"
    
    def test_analyze_practice(self, analysis_module):
        practice = BestPractice(
            name="Тестовая практика",
            region="Челябинская область",
            industry="металлургия",
            description="Описание",
            results="Рост 25%",
            applicability_score=0.8
        )
        
        analysis = analysis_module.analyze_practice(practice)
        
        assert analysis.practice == practice
        assert len(analysis.adaptation_recommendations) > 0
        assert len(analysis.risks) > 0
    
    def test_create_investment_proposal(self, analysis_module):
        from src.search_module import InvestmentOpportunity
        from src.database_module import SupportMeasure
        
        opportunity = InvestmentOpportunity(
            title="Тестовый объект",
            type="facility",
            location="Екатеринбург",
            industry="металлургия",
            investment_required=100_000_000,
            description="Описание"
        )
        
        measure = SupportMeasure(
            id="TEST-001",
            name="Тестовая мера",
            type="grant",
            max_amount=30_000_000,
            min_amount=5_000_000,
            description="Описание",
            eligibility=[],
            documents_required=[],
            deadline="2024-12-31",
            contact_info="test@test.ru",
            region="Свердловская область"
        )
        
        proposal = analysis_module.create_investment_proposal(
            opportunity=opportunity,
            support_measures=[measure]
        )
        
        assert proposal.id.startswith("INV-PROP-")
        assert proposal.total_investment == 100_000_000
        assert proposal.payback_period > 0
        assert len(proposal.implementation_plan) > 0


class TestInvestorAgent:
    """Интеграционные тесты агента"""
    
    @pytest.mark.asyncio
    async def test_full_investment_analysis(self):
        async with InvestorAgent() as agent:
            result = await agent.full_investment_analysis(
                industry="металлургия",
                min_investment=10_000_000
            )
            
            assert result["industry"] == "металлургия"
            assert result["region"] == "Свердловская область"
            assert "sections" in result
            assert "best_practices" in result["sections"]
            assert "opportunities" in result["sections"]
            assert "support_measures" in result["sections"]
    
    @pytest.mark.asyncio
    async def test_session_management(self):
        async with InvestorAgent() as agent:
            session_id = await agent.start_session(user_id="test_user")
            assert session_id.startswith("SESSION-")
            assert agent.current_session is not None
            assert agent.current_session.user_id == "test_user"
        
        # После выхода из контекста сессия должна быть закрыта
        assert agent.current_session is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
