"""
API Authentication middleware

Использование:
    from web.middleware import require_api_key
    
    @app.route('/api/protected')
    @require_api_key
    def protected_endpoint():
        ...
"""
from functools import wraps
from flask import request, jsonify, g
from typing import Optional, Dict, List, Callable
from datetime import datetime, timedelta
from loguru import logger
import hashlib
import hmac
import secrets


# ============================================================
# Хранилище API ключей
# ============================================================

class APIKeyStore:
    """
    Хранилище API ключей
    
    В production использовать базу данных или Redis
    """
    
    def __init__(self):
        # In-memory хранилище (для demo)
        # Формат: {key_hash: {"owner": str, "permissions": List, "created": datetime, "expires": datetime}}
        self._keys: Dict[str, Dict] = {}
        self._init_default_keys()
        logger.info("APIKeyStore инициализирован")
    
    def _init_default_keys(self) -> None:
        """Инициализация ключами по умолчанию"""
        # Demo ключ (НЕ использовать в production!)
        self.add_key(
            key="demo-api-key-12345",
            owner="demo_user",
            permissions=["read", "write"],
            expires=datetime.now() + timedelta(days=365)
        )
        
        # Readonly ключ
        self.add_key(
            key="readonly-key-67890",
            owner="readonly_user",
            permissions=["read"],
            expires=datetime.now() + timedelta(days=365)
        )
        
        logger.info("Добавлены default API ключи")
    
    def _hash_key(self, key: str) -> str:
        """Хеширование ключа"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def add_key(
        self,
        key: str,
        owner: str,
        permissions: List[str],
        expires: Optional[datetime] = None
    ) -> str:
        """
        Добавление API ключа
        
        Args:
            key: Ключ (будет захеширован)
            owner: Владелец ключа
            permissions: Список разрешений
            expires: Срок действия
        
        Returns:
            str: Хешированный ключ
        """
        key_hash = self._hash_key(key)
        self._keys[key_hash] = {
            "owner": owner,
            "permissions": permissions,
            "created": datetime.now(),
            "expires": expires,
            "last_used": None,
            "usage_count": 0
        }
        logger.info(f"Добавлен API ключ для {owner}")
        return key_hash
    
    def validate(self, key: str) -> Optional[Dict]:
        """
        Валидация API ключа
        
        Args:
            key: Ключ для проверки
        
        Returns:
            Dict: Информация о ключе или None
        """
        key_hash = self._hash_key(key)
        
        if key_hash not in self._keys:
            return None
        
        key_info = self._keys[key_hash]
        
        # Проверка срока действия
        if key_info["expires"] and datetime.now() > key_info["expires"]:
            logger.warning(f"API ключ истёк: {key_info['owner']}")
            return None
        
        # Обновление статистики
        key_info["last_used"] = datetime.now()
        key_info["usage_count"] += 1
        
        return {
            "owner": key_info["owner"],
            "permissions": key_info["permissions"],
            "expires": key_info["expires"]
        }
    
    def has_permission(self, key: str, permission: str) -> bool:
        """Проверка наличия разрешения"""
        key_info = self.validate(key)
        if not key_info:
            return False
        return permission in key_info["permissions"]
    
    def revoke_key(self, key: str) -> bool:
        """Отзыв ключа"""
        key_hash = self._hash_key(key)
        if key_hash in self._keys:
            del self._keys[key_hash]
            logger.info(f"Отозван API ключ")
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Статистика по ключам"""
        return {
            "total_keys": len(self._keys),
            "active_keys": len([
                k for k in self._keys.values()
                if not k["expires"] or datetime.now() <= k["expires"]
            ]),
            "total_usage": sum(k["usage_count"] for k in self._keys.values())
        }


# Глобальное хранилище ключей
api_key_store = APIKeyStore()


# ============================================================
# Функции валидации
# ============================================================

def validate_api_key(api_key: str) -> bool:
    """
    Валидация API ключа
    
    Args:
        api_key: Ключ для проверки
    
    Returns:
        bool: True если ключ валиден
    """
    if not api_key:
        return False
    
    key_info = api_key_store.validate(api_key)
    return key_info is not None


def get_api_key_info(api_key: str) -> Optional[Dict]:
    """Получение информации о ключе"""
    return api_key_store.validate(api_key)


# ============================================================
# Декораторы
# ============================================================

def require_api_key(f):
    """
    Декоратор для обязательного API ключа
    
    Usage:
        @app.route('/api/protected')
        @require_api_key
        def protected_endpoint():
            # Доступ к информации о ключе через g.api_key_info
            owner = g.api_key_info["owner"]
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            logger.warning("Запрос без API ключа")
            return jsonify({
                "success": False,
                "error": "Требуется API ключ",
                "details": {
                    "header": "X-API-Key"
                }
            }), 401
        
        key_info = api_key_store.validate(api_key)
        
        if not key_info:
            logger.warning(f"Невалидный API ключ: {api_key[:8]}...")
            return jsonify({
                "success": False,
                "error": "Невалидный API ключ"
            }), 401
        
        # Сохранение информации в g
        g.api_key = api_key
        g.api_key_info = key_info
        
        return f(*args, **kwargs)
    return wrapper


def require_permission(permission: str):
    """
    Декоратор для проверки разрешения
    
    Usage:
        @app.route('/api/admin')
        @require_api_key
        @require_permission('admin')
        def admin_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        @require_api_key
        def wrapper(*args, **kwargs):
            if not api_key_store.has_permission(g.api_key, permission):
                logger.warning(
                    f"Недостаточно прав: {g.api_key_info['owner']} "
                    f"для {permission}"
                )
                return jsonify({
                    "success": False,
                    "error": "Недостаточно прав",
                    "details": {
                        "required": permission,
                        "available": g.api_key_info["permissions"]
                    }
                }), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def optional_api_key(f):
    """
    Декоратор для опционального API ключа
    
    Если ключ предоставлен - валидирует и добавляет в g
    Если нет - продолжает без ключа
    
    Usage:
        @app.route('/api/data')
        @optional_api_key
        def data_endpoint():
            if hasattr(g, 'api_key_info'):
                # Ключ предоставлен
                pass
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if api_key:
            key_info = api_key_store.validate(api_key)
            if key_info:
                g.api_key = api_key
                g.api_key_info = key_info
            else:
                logger.debug("Предоставлен невалидный API ключ")
        
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# Утилиты
# ============================================================

def generate_api_key() -> str:
    """
    Генерация нового API ключа
    
    Returns:
        str: Случайный ключ
    """
    return secrets.token_urlsafe(32)


def create_api_key(
    owner: str,
    permissions: List[str],
    expires_days: int = 365
) -> Dict:
    """
    Создание нового API ключа
    
    Args:
        owner: Владелец ключа
        permissions: Разрешения
        expires_days: Срок действия в днях
    
    Returns:
        Dict: Информация о ключе (включая сам ключ)
    """
    key = generate_api_key()
    expires = datetime.now() + timedelta(days=expires_days)
    
    api_key_store.add_key(
        key=key,
        owner=owner,
        permissions=permissions,
        expires=expires
    )
    
    logger.info(f"Создан API ключ для {owner}")
    
    return {
        "key": key,
        "owner": owner,
        "permissions": permissions,
        "expires": expires.isoformat(),
        "warning": "Сохраните ключ! Он не будет показан повторно."
    }


# ============================================================
# Flask middleware
# ============================================================

def register_auth_middleware(app, exclude_paths: List[str] = None):
    """
    Регистрация auth middleware для всего приложения
    
    Args:
        app: Flask приложение
        exclude_paths: Список путей без аутентификации
    """
    exclude_paths = exclude_paths or [
        '/api/health',
        '/api/region',
        '/',
        '/static'
    ]
    
    @app.before_request
    def check_auth():
        # Пропуск исключений
        for exclude in exclude_paths:
            if request.path.startswith(exclude):
                return None
        
        # Проверка API ключа для защищённых путей
        if request.path.startswith('/api/'):
            api_key = request.headers.get('X-API-Key')
            
            if api_key:
                key_info = api_key_store.validate(api_key)
                if key_info:
                    g.api_key = api_key
                    g.api_key_info = key_info
                else:
                    logger.warning(f"Невалидный API ключ: {request.path}")
            else:
                # Для некоторых endpoint'ов ключ опционален
                if not _is_optional_path(request.path):
                    logger.debug(f"Запрос без API ключа: {request.path}")
        
        return None
    
    logger.info(f"Auth middleware зарегистрирован (исключения: {exclude_paths})")


def _is_optional_path(path: str) -> bool:
    """Проверка является ли путь опциональным для API ключа"""
    optional_paths = [
        '/api/practices',
        '/api/opportunities',
        '/api/support-measures',
        '/api/documents/checklist',
        '/api/analysis/full'
    ]
    return any(path.startswith(p) for p in optional_paths)
