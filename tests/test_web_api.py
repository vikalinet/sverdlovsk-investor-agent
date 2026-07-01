"""
Тесты для Web API
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from web.app import app


@pytest.fixture
def client():
    """Тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Тесты endpoints здоровья"""
    
    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data
        assert data['region'] == 'Свердловская область'
    
    def test_region_info(self, client):
        response = client.get('/api/region')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['name'] == 'Свердловская область'
        assert data['code'] == '66'


class TestPracticesAPI:
    """Тесты API лучших практик"""
    
    def test_find_practices(self, client):
        response = client.post('/api/practices',
            json={'industry': 'металлургия'},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        assert 'count' in data


class TestOpportunitiesAPI:
    """Тесты API инвествозможностей"""
    
    def test_find_opportunities(self, client):
        response = client.post('/api/opportunities',
            json={'industry': 'металлургия', 'min_investment': 10000000},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data


class TestSupportMeasuresAPI:
    """Тесты API мер поддержки"""
    
    def test_find_support_measures(self, client):
        response = client.post('/api/support-measures',
            json={'industry': 'металлургия', 'business_size': 'medium'},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'count' in data
        assert len(data['data']) > 0


class TestDocumentsAPI:
    """Тесты API документов"""
    
    def test_get_checklist(self, client):
        response = client.get('/api/documents/checklist?measure_type=grant')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'checklist' in data
        assert len(data['checklist']) > 0
    
    def test_prepare_documents(self, client):
        project_data = {
            'applicant_name': 'ООО "Тест"',
            'inn': '6601000001',
            'project_name': 'Тестовый проект',
            'investment_amount': 50000000,
            'grant_amount': 15000000,
            'jobs_created': 25
        }
        
        response = client.post('/api/documents/package',
            json={
                'measure_name': 'Грант на развитие',
                'measure_type': 'grant',
                'project_data': project_data
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'package_id' in data['data']


class TestAnalysisAPI:
    """Тесты API анализа"""
    
    def test_full_analysis(self, client):
        response = client.post('/api/analysis/full',
            json={'industry': 'металлургия', 'min_investment': 50000000},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        assert 'sections' in data['data']


class TestMCPEndpoints:
    """Тесты MCP endpoints"""
    
    def test_mcp_status(self, client):
        response = client.get('/api/mcp/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'databases' in data


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_404(self, client):
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] == False
    
    def test_invalid_method(self, client):
        response = client.put('/api/health')
        assert response.status_code == 405


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
