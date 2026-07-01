"""
Тесты для middleware (rate limiting, auth)

Запуск:
    pytest tests/unit/test_middleware.py -v
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from flask import Flask


class TestRateLimiter:
    """Тесты для RateLimiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Создание rate limiter для тестов"""
        from web.middleware.rate_limiter import RateLimiter
        return RateLimiter(
            max_requests=5,
            window_seconds=1,
            block_duration=1
        )
    
    def test_is_allowed_under_limit(self, rate_limiter):
        """Тест разрешений под лимитом"""
        for i in range(5):
            assert rate_limiter.is_allowed("test_client") is True
    
    def test_is_allowed_over_limit(self, rate_limiter):
        """Тест превышения лимита"""
        # 5 запросов разрешены
        for i in range(5):
            rate_limiter.is_allowed("test_client")
        
        # 6-й должен быть заблокирован
        assert rate_limiter.is_allowed("test_client") is False
    
    def test_get_remaining(self, rate_limiter):
        """Тест получения оставшихся запросов"""
        assert rate_limiter.get_remaining("test_client") == 5
        
        rate_limiter.is_allowed("test_client")
        assert rate_limiter.get_remaining("test_client") == 4
        
        rate_limiter.is_allowed("test_client")
        assert rate_limiter.get_remaining("test_client") == 3
    
    def test_reset(self, rate_limiter):
        """Тест сброса счётчиков"""
        # Несколько запросов
        for i in range(3):
            rate_limiter.is_allowed("test_client")
        
        # Сброс
        rate_limiter.reset("test_client")
        
        # Должно быть снова 5
        assert rate_limiter.get_remaining("test_client") == 5
    
    def test_block_duration(self):
        """Тест длительности блокировки"""
        from web.middleware.rate_limiter import RateLimiter
        
        limiter = RateLimiter(
            max_requests=2,
            window_seconds=1,
            block_duration=2
        )
        
        # Превышение лимита
        limiter.is_allowed("client")
        limiter.is_allowed("client")
        assert limiter.is_allowed("client") is False
        
        # Сразу после блокировки - всё ещё заблокирован
        assert limiter._is_blocked("client") is True
        
        # Ждём окончания блокировки
        time.sleep(2.1)
        assert limiter._is_blocked("client") is False
    
    def test_get_stats(self, rate_limiter):
        """Тест получения статистики"""
        # Несколько запросов
        rate_limiter.is_allowed("client1")
        rate_limiter.is_allowed("client2")
        
        stats = rate_limiter.get_stats()
        
        assert "active_clients" in stats
        assert "blocked_clients" in stats
        assert "config" in stats
        assert stats["config"]["max_requests"] == 5


class TestAPIKeyStore:
    """Тесты для APIKeyStore"""
    
    @pytest.fixture
    def key_store(self):
        """Создание хранилища ключей"""
        from web.middleware.auth import APIKeyStore
        return APIKeyStore()
    
    def test_add_and_validate_key(self, key_store):
        """Тест добавления и валидации ключа"""
        key_store.add_key(
            key="test-key-123",
            owner="test_user",
            permissions=["read", "write"]
        )
        
        result = key_store.validate("test-key-123")
        
        assert result is not None
        assert result["owner"] == "test_user"
        assert "read" in result["permissions"]
    
    def test_validate_invalid_key(self, key_store):
        """Тест валидации невалидного ключа"""
        result = key_store.validate("nonexistent-key")
        assert result is None
    
    def test_has_permission(self, key_store):
        """Тест проверки разрешений"""
        key_store.add_key(
            key="test-key-perm",
            owner="test_user",
            permissions=["read"]
        )
        
        assert key_store.has_permission("test-key-perm", "read") is True
        assert key_store.has_permission("test-key-perm", "write") is False
    
    def test_expired_key(self, key_store):
        """Тест истёкшего ключа"""
        from datetime import datetime, timedelta
        
        key_store.add_key(
            key="expired-key",
            owner="test_user",
            permissions=["read"],
            expires=datetime.now() - timedelta(days=1)
        )
        
        result = key_store.validate("expired-key")
        assert result is None
    
    def test_revoke_key(self, key_store):
        """Тест отзыва ключа"""
        key_store.add_key(
            key="to-revoke",
            owner="test_user",
            permissions=["read"]
        )
        
        # До отзыва
        assert key_store.validate("to-revoke") is not None
        
        # Отзыв
        result = key_store.revoke_key("to-revoke")
        assert result is True
        
        # После отзыва
        assert key_store.validate("to-revoke") is None
    
    def test_get_stats(self, key_store):
        """Тест статистики"""
        stats = key_store.get_stats()
        
        assert "total_keys" in stats
        assert "active_keys" in stats
        assert "total_usage" in stats


class TestRateLimitDecorator:
    """Тесты для декоратора rate_limit"""
    
    @pytest.fixture
    def flask_app(self):
        """Flask приложение для тестов"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    def test_rate_limit_decorator(self, flask_app):
        """Тест декоратора rate_limit"""
        from web.middleware.rate_limiter import rate_limit, RateLimiter
        
        test_limiter = RateLimiter(max_requests=2, window_seconds=10)
        
        @flask_app.route('/test')
        @rate_limit(test_limiter)
        def test_endpoint():
            return "OK"
        
        with flask_app.test_client() as client:
            # Первые 2 запроса успешны
            resp1 = client.get('/test')
            assert resp1.status_code == 200
            
            resp2 = client.get('/test')
            assert resp2.status_code == 200
            
            # 3-й запрос заблокирован
            resp3 = client.get('/test')
            assert resp3.status_code == 429


class TestAuthDecorator:
    """Тесты для декораторов аутентификации"""
    
    @pytest.fixture
    def flask_app(self):
        """Flask приложение для тестов"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    def test_require_api_key_success(self, flask_app):
        """Тест успешной аутентификации"""
        from web.middleware.auth import require_api_key
        
        @flask_app.route('/protected')
        @require_api_key
        def protected_endpoint():
            return "OK"
        
        with flask_app.test_client() as client:
            # С валидным ключом
            resp = client.get(
                '/protected',
                headers={'X-API-Key': 'demo-api-key-12345'}
            )
            assert resp.status_code == 200
    
    def test_require_api_key_missing(self, flask_app):
        """Тест отсутствия ключа"""
        from web.middleware.auth import require_api_key
        
        @flask_app.route('/protected')
        @require_api_key
        def protected_endpoint():
            return "OK"
        
        with flask_app.test_client() as client:
            # Без ключа
            resp = client.get('/protected')
            assert resp.status_code == 401
    
    def test_require_api_key_invalid(self, flask_app):
        """Тест невалидного ключа"""
        from web.middleware.auth import require_api_key
        
        @flask_app.route('/protected')
        @require_api_key
        def protected_endpoint():
            return "OK"
        
        with flask_app.test_client() as client:
            # С невалидным ключом
            resp = client.get(
                '/protected',
                headers={'X-API-Key': 'invalid-key'}
            )
            assert resp.status_code == 401
    
    def test_require_permission_success(self, flask_app):
        """Тест проверки разрешения"""
        from web.middleware.auth import require_api_key, require_permission
        
        @flask_app.route('/admin')
        @require_api_key
        @require_permission('read')
        def admin_endpoint():
            return "OK"
        
        with flask_app.test_client() as client:
            resp = client.get(
                '/admin',
                headers={'X-API-Key': 'demo-api-key-12345'}
            )
            assert resp.status_code == 200
    
    def test_require_permission_denied(self, flask_app):
        """Тест недостаточных прав"""
        from web.middleware.auth import require_api_key, require_permission
        
        @flask_app.route('/admin')
        @require_api_key
        @require_permission('superadmin')
        def admin_endpoint():
            return "OK"
        
        with flask_app.test_client() as client:
            resp = client.get(
                '/admin',
                headers={'X-API-Key': 'readonly-key-67890'}
            )
            assert resp.status_code == 403


class TestGenerateAPIKey:
    """Тесты для генерации API ключей"""
    
    def test_generate_api_key(self):
        """Тест генерации ключа"""
        from web.middleware.auth import generate_api_key
        
        key = generate_api_key()
        
        assert isinstance(key, str)
        assert len(key) >= 32
    
    def test_create_api_key(self):
        """Тест создания ключа с информацией"""
        from web.middleware.auth import create_api_key
        
        result = create_api_key(
            owner="test_user",
            permissions=["read", "write"],
            expires_days=30
        )
        
        assert "key" in result
        assert "owner" in result
        assert "permissions" in result
        assert "expires" in result
        assert result["owner"] == "test_user"
        assert "read" in result["permissions"]
