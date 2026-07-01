"""
Единый обработчик ошибок для API
"""
from flask import jsonify, request
from loguru import logger
from functools import wraps
from datetime import datetime
from typing import Optional, Dict, Any


# ============================================================
# Классы исключений
# ============================================================

class APIError(Exception):
    """
    Базовый класс для API ошибок
    
    Usage:
        raise APIError("Сообщение ошибки", status_code=400)
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "success": False,
            "error": self.message,
            "details": self.details,
            "timestamp": datetime.now().isoformat()
        }


class NotFoundError(APIError):
    """Ресурс не найден (404)"""
    def __init__(self, message: str = "Ресурс не найден", details: dict = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(APIError):
    """Ошибка валидации данных (400)"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)


class AuthenticationError(APIError):
    """Ошибка аутентификации (401)"""
    def __init__(self, message: str = "Требуется аутентификация", details: dict = None):
        super().__init__(message, status_code=401, details=details)


class PermissionError(APIError):
    """Ошибка авторизации (403)"""
    def __init__(self, message: str = "Недостаточно прав", details: dict = None):
        super().__init__(message, status_code=403, details=details)


class RateLimitError(APIError):
    """Превышен лимит запросов (429)"""
    def __init__(self, message: str = "Превышен лимит запросов", details: dict = None):
        super().__init__(message, status_code=429, details=details)


class ServiceUnavailableError(APIError):
    """Сервис временно недоступен (503)"""
    def __init__(self, message: str = "Сервис временно недоступен", details: dict = None):
        super().__init__(message, status_code=503, details=details)


class DatabaseError(APIError):
    """Ошибка базы данных (500)"""
    def __init__(self, message: str = "Ошибка базы данных", details: dict = None):
        super().__init__(message, status_code=500, details=details)


class ExternalServiceError(APIError):
    """Ошибка внешнего сервиса (502)"""
    def __init__(self, message: str = "Ошибка внешнего сервиса", details: dict = None):
        super().__init__(message, status_code=502, details=details)


# ============================================================
# Декораторы
# ============================================================

def handle_api_errors(f):
    """
    Декоратор для автоматической обработки ошибок API
    
    Usage:
        @app.route('/api/example')
        @handle_api_errors
        def example():
            raise ValidationError("Неверные данные")
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API ошибка [{e.status_code}]: {e.message}")
            return jsonify(e.to_dict()), e.status_code
        except ValueError as e:
            logger.warning(f"Ошибка значения: {e}")
            error = ValidationError(str(e))
            return jsonify(error.to_dict()), error.status_code
        except Exception as e:
            logger.exception(f"Необработанная ошибка: {e}")
            error = APIError(
                message="Внутренняя ошибка сервера",
                status_code=500,
                details={"type": type(e).__name__}
            )
            return jsonify(error.to_dict()), error.status_code
    return wrapper


def validate_json(f):
    """
    Декоратор для проверки JSON в запросе
    
    Usage:
        @app.route('/api/example', methods=['POST'])
        @validate_json
        def example():
            data = request.get_json()
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                raise ValidationError(
                    "Content-Type должен быть application/json",
                    details={"received": request.content_type}
                )
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# Flask error handlers
# ============================================================

def register_error_handlers(app):
    """
    Регистрация глобальных обработчиков ошибок для Flask приложения
    
    Usage:
        app = Flask(__name__)
        register_error_handlers(app)
    """
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Endpoint не найден",
            "path": request.path,
            "timestamp": datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": f"Метод {request.method} не поддерживается",
            "allowed_methods": error.get_allowed_methods() if hasattr(error, 'get_allowed_methods') else [],
            "timestamp": datetime.now().isoformat()
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.exception(f"Внутренняя ошибка: {error}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "timestamp": datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        return jsonify({
            "success": False,
            "error": "Ошибка шлюза",
            "timestamp": datetime.now().isoformat()
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            "success": False,
            "error": "Сервис временно недоступен",
            "timestamp": datetime.now().isoformat()
        }), 503


# ============================================================
# Утилиты
# ============================================================

def log_request_info():
    """Логирование информации о запросе"""
    logger.info(
        f"{request.method} {request.path} | "
        f"IP: {request.remote_addr} | "
        f"User-Agent: {request.headers.get('User-Agent', 'N/A')}"
    )


def log_response_info(status_code: int, response_time_ms: float):
    """Логирование информации об ответе"""
    log_level = logger.level("WARNING" if status_code >= 400 else "INFO")
    logger.log(
        log_level.name,
        f"Response: {status_code} | Time: {response_time_ms:.2f}ms"
    )
