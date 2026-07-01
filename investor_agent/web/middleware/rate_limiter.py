"""
Rate Limiting middleware для ограничения количества запросов

Использование:
    from web.middleware import rate_limit
    
    @app.route('/api/endpoint')
    @rate_limit
    def endpoint():
        ...
"""
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional
from loguru import logger
import threading
import time


class RateLimiter:
    """
    Rate limiter с скользящим окном
    
    Паттерн: Token Bucket с адаптивным лимитом
    
    Attributes:
        max_requests: Максимальное количество запросов
        window_seconds: Размер окна в секундах
        requests: Хранилище запросов по клиенту
    """
    
    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
        block_duration: int = 300
    ):
        """
        Инициализация rate limiter
        
        Args:
            max_requests: Максимум запросов в окно
            window_seconds: Размер окна (секунды)
            block_duration: Длительность блокировки при превышении (секунды)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.block_duration = block_duration
        
        # Хранилища
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._blocked: Dict[str, float] = {}  # client_id -> timestamp блокировки
        
        # Блокировка для потокобезопасности
        self._lock = threading.Lock()
        
        logger.info(
            f"RateLimiter инициализирован: "
            f"{max_requests} запросов/{window_seconds}с"
        )
    
    def _get_client_id(self) -> str:
        """
        Получение идентификатора клиента
        
        Приоритет:
        1. API ключ (если есть)
        2. IP адрес
        3. User-Agent + IP
        """
        # Проверка API ключа
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"api:{api_key[:16]}"
        
        # IP адрес
        ip = request.remote_addr or "unknown"
        
        # X-Forwarded-For для прокси
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            ip = forwarded_for.split(',')[0].strip()
        
        return f"ip:{ip}"
    
    def _cleanup_old_requests(self, client_id: str) -> None:
        """Очистка старых запросов"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Фильтрация запросов в окне
        self._requests[client_id] = [
            ts for ts in self._requests[client_id]
            if ts > window_start
        ]
    
    def _is_blocked(self, client_id: str) -> bool:
        """Проверка блокировки клиента"""
        if client_id not in self._blocked:
            return False
        
        block_end = self._blocked[client_id] + self.block_duration
        if time.time() > block_end:
            # Блокировка истекла
            del self._blocked[client_id]
            return False
        
        return True
    
    def _block_client(self, client_id: str) -> None:
        """Блокировка клиента"""
        self._blocked[client_id] = time.time()
        logger.warning(f"Клиент заблокирован: {client_id}")
    
    def is_allowed(self, client_id: Optional[str] = None) -> bool:
        """
        Проверка разрешённости запроса
        
        Args:
            client_id: ID клиента (автоопределение если None)
        
        Returns:
            bool: True если запрос разрешён
        """
        if client_id is None:
            client_id = self._get_client_id()
        
        with self._lock:
            # Проверка блокировки
            if self._is_blocked(client_id):
                logger.warning(f"Запрос от заблокированного клиента: {client_id}")
                return False
            
            # Очистка старых запросов
            self._cleanup_old_requests(client_id)
            
            # Проверка лимита
            current_requests = len(self._requests[client_id])
            
            if current_requests >= self.max_requests:
                # Превышение лимита - блокируем
                self._block_client(client_id)
                logger.warning(
                    f"Rate limit превышен: {client_id} "
                    f"({current_requests}/{self.max_requests})"
                )
                return False
            
            # Добавление текущего запроса
            self._requests[client_id].append(time.time())
            
            # Логирование (только для отладки)
            if current_requests > self.max_requests * 0.8:
                logger.debug(
                    f"Rate limitwarning: {client_id} "
                    f"({current_requests}/{self.max_requests})"
                )
            
            return True
    
    def get_remaining(self, client_id: Optional[str] = None) -> int:
        """
        Получение оставшегося количества запросов
        
        Returns:
            int: Оставшиеся запросы в текущем окне
        """
        if client_id is None:
            client_id = self._get_client_id()
        
        with self._lock:
            self._cleanup_old_requests(client_id)
            return max(0, self.max_requests - len(self._requests[client_id]))
    
    def get_reset_time(self, client_id: Optional[str] = None) -> int:
        """
        Получение времени сброса лимита
        
        Returns:
            int: Секунд до сброса
        """
        if client_id is None:
            client_id = self._get_client_id()
        
        with self._lock:
            if not self._requests[client_id]:
                return 0
            
            oldest_request = min(self._requests[client_id])
            reset_time = oldest_request + self.window_seconds - time.time()
            return max(0, int(reset_time))
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        with self._lock:
            return {
                "active_clients": len(self._requests),
                "blocked_clients": len(self._blocked),
                "total_requests": sum(
                    len(reqs) for reqs in self._requests.values()
                ),
                "config": {
                    "max_requests": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "block_duration": self.block_duration
                }
            }
    
    def reset(self, client_id: Optional[str] = None) -> None:
        """
        Сброс счётчиков
        
        Args:
            client_id: ID клиента (None для сброса всех)
        """
        with self._lock:
            if client_id:
                self._requests.pop(client_id, None)
                self._blocked.pop(client_id, None)
            else:
                self._requests.clear()
                self._blocked.clear()
            logger.info(f"Rate limiter сброшен: {client_id or 'все'}")


# ============================================================
# Глобальные rate limiter'ы
# ============================================================

# Default limiter - стандартный лимит
default_limiter = RateLimiter(
    max_requests=60,
    window_seconds=60,
    block_duration=300
)

# Strict limiter - строгий лимит (для чувствительных endpoint'ов)
strict_limiter = RateLimiter(
    max_requests=10,
    window_seconds=60,
    block_duration=600
)

# Relaxed limiter - мягкий лимит (для API ключей)
relaxed_limiter = RateLimiter(
    max_requests=1000,
    window_seconds=60,
    block_duration=60
)


# ============================================================
# Декораторы
# ============================================================

def rate_limit(limiter: Optional[RateLimiter] = None):
    """
    Декоратор для rate limiting
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit()
        def endpoint():
            ...
        
        # С кастомным лимитером
        @app.route('/api/sensitive')
        @rate_limit(strict_limiter)
        def sensitive_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Выбор лимитера
            current_limiter = limiter or default_limiter
            
            # Получение ID клиента
            client_id = current_limiter._get_client_id()
            
            # Проверка лимита
            if not current_limiter.is_allowed(client_id):
                remaining = current_limiter.get_remaining(client_id)
                reset_time = current_limiter.get_reset_time(client_id)
                
                logger.warning(
                    f"Rate limit exceeded: {client_id}, "
                    f"remaining={remaining}, reset={reset_time}s"
                )
                
                response = jsonify({
                    "success": False,
                    "error": "Превышен лимит запросов",
                    "details": {
                        "limit": current_limiter.max_requests,
                        "remaining": remaining,
                        "reset_in": reset_time
                    }
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(current_limiter.max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(reset_time)
                return response
            
            # Выполнение запроса
            response = f(*args, **kwargs)
            
            # Добавление заголовков
            if hasattr(response, 'headers'):
                remaining = current_limiter.get_remaining(client_id)
                reset_time = current_limiter.get_reset_time(client_id)
                response.headers['X-RateLimit-Limit'] = str(current_limiter.max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(reset_time)
            
            return response
        return wrapper
    return decorator


# ============================================================
# Flask middleware
# ============================================================

def register_rate_limit_middleware(app):
    """
    Регистрация rate limiting middleware для всего приложения
    
    Usage:
        app = Flask(__name__)
        register_rate_limit_middleware(app)
    """
    @app.before_request
    def check_rate_limit():
        # Пропуск health check
        if request.path == '/api/health':
            return None
        
        # Проверка API ключа для relaxed лимита
        api_key = request.headers.get('X-API-Key')
        if api_key and validate_api_key(api_key):
            limiter = relaxed_limiter
        else:
            limiter = default_limiter
        
        client_id = limiter._get_client_id()
        
        if not limiter.is_allowed(client_id):
            remaining = limiter.get_remaining(client_id)
            reset_time = limiter.get_reset_time(client_id)
            
            response = jsonify({
                "success": False,
                "error": "Превышен лимит запросов",
                "details": {
                    "limit": limiter.max_requests,
                    "remaining": remaining,
                    "reset_in": reset_time
                }
            })
            response.status_code = 429
            response.headers['X-RateLimit-Limit'] = str(limiter.max_requests)
            response.headers['X-RateLimit-Remaining'] = str(remaining)
            response.headers['X-RateLimit-Reset'] = str(reset_time)
            return response
        
        # Сохранение в g для использования в endpoint'ах
        g.rate_limit_remaining = limiter.get_remaining(client_id)
        g.rate_limit_reset = limiter.get_reset_time(client_id)
        
        return None
    
    logger.info("Rate limiting middleware зарегистрирован")


# ============================================================
# Утилиты
# ============================================================

def get_client_info() -> Dict:
    """Получение информации о клиенте"""
    return {
        "ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "api_key": request.headers.get('X-API-Key', None),
        "path": request.path,
        "method": request.method
    }
