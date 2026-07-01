"""
Flask API для агента-помощника инвестора
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from loguru import logger

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent import InvestorAgent
from config import REGION
from web.schemas import (
    PracticeRequest,
    OpportunityRequest,
    SupportMeasuresRequest,
    DocumentsPackageRequest,
    AnalysisRequest,
    ProposalRequest,
    success_response,
    error_response
)
from web.error_handlers import (
    handle_api_errors,
    validate_json,
    register_error_handlers,
    APIError,
    ValidationError,
    NotFoundError
)

# Создание Flask приложения
app = Flask(__name__, static_folder='static', static_url_path='')

# Настройка CORS с безопасными настройками
CORS(
    app,
    origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Ограничить в production
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    supports_credentials=True,
    max_age=3600
)

# Настройка JSON для корректной кодировки UTF-8 (Flask 3.x)
app.json.ensure_ascii = False  # Разрешаем Unicode символы
app.json.sort_keys = False  # Сохраняем порядок ключей

# Регистрация глобальных обработчиков ошибок
register_error_handlers(app)

# Настройка логирования
logger.add(
    "logs/web_api.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)

# Инициализация агента
agent = InvestorAgent()
logger.info("Агент инициализирован")


# ==================== API Endpoints ====================

@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья API"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "region": REGION["name"],
        "version": "1.0.0"
    }), 200


@app.route('/api/region', methods=['GET'])
def get_region_info():
    """Информация о регионе"""
    return jsonify({
        "name": REGION["name"],
        "code": REGION.get("code", "66"),
        "capital": REGION.get("capital", "Екатеринбург")
    })


@app.route('/api/practices', methods=['POST'])
@validate_json
@handle_api_errors
def find_best_practices():
    """
    Поиск лучших отраслевых практик
    
    Request:
    {
        "industry": "металлургия",
        "practice_type": "all"
    }
    """
    data = request.get_json()
    
    # Валидация через Pydantic
    try:
        validated = PracticeRequest(**data)
    except ValueError as e:
        raise ValidationError(str(e))
    
    logger.info(f"Поиск практик: industry={validated.industry}, type={validated.practice_type}")
    
    # Запуск асинхронного запроса
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        practices = loop.run_until_complete(
            agent.find_best_practices(validated.industry, validated.practice_type)
        )
    finally:
        loop.close()
        
    # Форматирование результатов
    results = []
    for p in practices[:10]:  # Топ-10
        results.append({
            "name": p.practice.name,
            "region": p.practice.region,
            "industry": p.practice.industry,
            "description": p.practice.description[:200] if p.practice.description else "",
            "results": p.practice.results,
            "applicability_score": round(p.applicability_score, 3),
            "implementation_cost": p.practice.implementation_cost,
            "recommendations": p.adaptation_recommendations[:3],
            "risks": p.risks[:3] if hasattr(p, 'risks') else []
        })
    
    return jsonify(success_response({
        "count": len(results),
        "practices": results
    }))


@app.route('/api/opportunities', methods=['POST'])
@validate_json
@handle_api_errors
def find_investment_opportunities():
    """
    Поиск инвестиционных возможностей
    
    Request:
    {
        "industry": "металлургия",
        "min_investment": 10000000,
        "location": "Екатеринбург"
    }
    """
    data = request.get_json()
    
    # Валидация через Pydantic
    try:
        validated = OpportunityRequest(**data)
    except ValueError as e:
        raise ValidationError(str(e))
    
    logger.info(f"Поиск возможностей: industry={validated.industry}, min={validated.min_investment}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        opportunities = loop.run_until_complete(
            agent.find_investment_opportunities(
                industry=validated.industry,
                min_investment=validated.min_investment,
                location=validated.location
            )
        )
    finally:
        loop.close()
        
    results = []
    for opp in opportunities:
        results.append({
            "title": opp.title,
            "type": opp.type,
            "location": opp.location,
            "industry": opp.industry,
            "investment_required": opp.investment_required,
            "description": opp.description,
            "potential_return": opp.potential_return,
            "status": opp.status
        })
    
    return jsonify(success_response({
        "count": len(results),
        "opportunities": results
    }))


@app.route('/api/support-measures', methods=['POST'])
@validate_json
@handle_api_errors
def find_support_measures():
    """
    Поиск мер господдержки
    
    Request:
    {
        "industry": "металлургия",
        "business_size": "medium"
    }
    """
    data = request.get_json()
    
    # Валидация через Pydantic
    try:
        validated = SupportMeasuresRequest(**data)
    except ValueError as e:
        raise ValidationError(str(e))
    
    logger.info(f"Поиск мер поддержки: industry={validated.industry}, size={validated.business_size}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        measures = loop.run_until_complete(
            agent.find_support_measures(validated.industry, validated.business_size)
        )
    finally:
        loop.close()
        
    results = []
    for m in measures:
        results.append({
            "id": m.id,
            "name": m.name,
            "type": m.type,
            "max_amount": m.max_amount,
            "min_amount": m.min_amount,
            "description": m.description,
            "eligibility": m.eligibility,
            "documents_required": m.documents_required,
            "deadline": m.deadline,
            "contact_info": m.contact_info
        })
    
    return jsonify(success_response({
        "count": len(results),
        "measures": results
    }))


@app.route('/api/proposal', methods=['POST'])
@validate_json
@handle_api_errors
def create_investment_proposal():
    """
    Создание инвестиционного предложения
    
    Request:
    {
        "opportunity_id": "INV-SVE-001",
        "industry": "металлургия"
    }
    """
    data = request.get_json()
    
    # Валидация через Pydantic
    try:
        validated = ProposalRequest(**data)
    except ValueError as e:
        raise ValidationError(str(e))
    
    logger.info(f"Создание предложения: industry={validated.industry}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Получаем возможность
        opportunities = loop.run_until_complete(
            agent.find_investment_opportunities(industry=validated.industry)
        )
        
        if not opportunities:
            raise NotFoundError("Инвестиционные возможности не найдены")
        
        opportunity = opportunities[0]  # Берём первую
        
        proposal = loop.run_until_complete(
            agent.create_investment_proposal(opportunity, validated.industry)
        )
    finally:
        loop.close()
        
    result = {
        "id": proposal.id,
        "title": proposal.title,
        "total_investment": proposal.total_investment,
        "own_funds_required": proposal.own_funds_required,
        "support_funds_available": proposal.support_funds_available,
        "payback_period": round(proposal.payback_period, 2),
        "roi": round(proposal.roi, 2),
        "implementation_plan": proposal.implementation_plan,
        "risks": proposal.risks,
        "recommendations": proposal.recommendations
    }
    
    return jsonify(success_response(result))


@app.route('/api/documents/package', methods=['POST'])
@validate_json
@handle_api_errors
def prepare_documents_package():
    """
    Подготовка пакета документов
    
    Request:
    {
        "measure_name": "Грант на развитие производства",
        "measure_type": "grant",
        "project_data": {
            "applicant_name": "ООО 'Пример'",
            "inn": "6601000001",
            ...
        }
    }
    """
    data = request.get_json()
    
    # Валидация через Pydantic
    try:
        validated = DocumentsPackageRequest(**data)
    except ValueError as e:
        raise ValidationError(str(e), details={"field": "project_data"})
    
    logger.info(f"Подготовка документов: {validated.measure_name}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        package = loop.run_until_complete(
            agent.prepare_documents_package(
                measure_name=validated.measure_name,
                measure_type=validated.measure_type,
                project_data=validated.project_data.model_dump()
            )
        )
        
        verification = loop.run_until_complete(
            agent.verify_documents(package)
        )
    finally:
        loop.close()
        
    result = {
        "package_id": package.id,
        "measure_name": package.measure_name,
        "measure_type": package.measure_type,
        "status": package.status,
        "created_at": package.created_at,
        "documents": package.documents,
        "validation": verification
    }
    
    return jsonify(success_response(result))


@app.route('/api/documents/checklist', methods=['GET'])
def get_documents_checklist():
    """
    Получение чек-листа документов
    
    Query:
    measure_type=grant
    """
    try:
        measure_type = request.args.get('measure_type', 'grant')
        
        checklist = agent.get_documents_checklist(measure_type)
        
        return jsonify({
            "success": True,
            "measure_type": measure_type,
            "checklist": checklist
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения чек-листа: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/analysis/full', methods=['POST'])
@validate_json
@handle_api_errors
def full_investment_analysis():
    """
    Комплексный анализ отрасли
    
    Request:
    {
        "industry": "металлургия",
        "min_investment": 50000000
    }
    """
    data = request.get_json()
    
    # Валидация через Pydantic
    try:
        validated = AnalysisRequest(**data)
    except ValueError as e:
        raise ValidationError(str(e))
    
    logger.info(f"Комплексный анализ: industry={validated.industry}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        analysis = loop.run_until_complete(
            agent.full_investment_analysis(validated.industry, validated.min_investment)
        )
    finally:
        loop.close()
    
    return jsonify(success_response(analysis))


@app.route('/api/mcp/status', methods=['GET'])
def get_mcp_status():
    """Статус MCP-серверов"""
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = Path(__file__).parent.parent / "mcp_servers" / "data"
        
        databases = {
            "support_measures": db_path / "support_measures.db",
            "investment_objects": db_path / "investment_objects.db",
            "business_registry": db_path / "business_registry.db"
        }
        
        status = {}
        for name, path in databases.items():
            if path.exists():
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchone()[0]
                conn.close()
                status[name] = {
                    "exists": True,
                    "tables": tables,
                    "path": str(path)
                }
            else:
                status[name] = {
                    "exists": False,
                    "path": str(path)
                }
        
        return jsonify({
            "success": True,
            "databases": status
        })
        
    except Exception as e:
        logger.error(f"Ошибка проверки MCP: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ==================== Middleware ====================

@app.before_request
def before_request():
    """Логирование запросов"""
    from web.error_handlers import log_request_info
    log_request_info()


@app.after_request
def add_security_headers(response):
    """Добавление security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


# ==================== Main ====================

if __name__ == '__main__':
    # Создание директорий
    Path("logs").mkdir(exist_ok=True)
    Path("web/static").mkdir(exist_ok=True)
    Path("output/documents").mkdir(parents=True, exist_ok=True)
    Path("output/reports").mkdir(parents=True, exist_ok=True)
    
    logger.info("Запуск Flask API...")
    logger.info(f"Регион: {REGION['name']}")
    logger.info(f"API доступно на: http://0.0.0.0:5000")
    logger.info(f"Health check: http://localhost:5000/api/health")
    
    # Инициализация агента
    agent = InvestorAgent()
    
    # Запуск сервера
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
