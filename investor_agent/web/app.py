"""
Flask API для агента-помощника инвестора
"""
import asyncio
import json
import os
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

# Создание Flask приложения
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Разрешаем CORS для React

# Настройка JSON для корректной кодировки UTF-8 (Flask 3.x)
app.json.ensure_ascii = False  # Разрешаем Unicode символы
app.json.sort_keys = False  # Сохраняем порядок ключей

# Настройка логирования
logger.add(
    "logs/web_api.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO"
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
    })


@app.route('/api/region', methods=['GET'])
def get_region_info():
    """Информация о регионе"""
    return jsonify({
        "name": REGION["name"],
        "code": REGION.get("code", "66"),
        "capital": REGION.get("capital", "Екатеринбург")
    })


@app.route('/api/practices', methods=['POST'])
def find_best_practices():
    """
    Поиск лучших отраслевых практик
    
    Request:
    {
        "industry": "металлургия",
        "practice_type": "all"
    }
    """
    try:
        data = request.get_json()
        industry = data.get('industry', 'металлургия')
        practice_type = data.get('practice_type', 'all')
        
        logger.info(f"Поиск практик: industry={industry}")
        
        # Запуск асинхронного запроса
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        practices = loop.run_until_complete(
            agent.find_best_practices(industry, practice_type)
        )
        loop.close()
        
        # Форматирование результатов
        results = []
        for p in practices[:10]:  # Топ-10
            results.append({
                "name": p.practice.name,
                "region": p.practice.region,
                "industry": p.practice.industry,
                "description": p.practice.description[:200],
                "results": p.practice.results,
                "applicability_score": round(p.applicability_score, 3),
                "implementation_cost": p.practice.implementation_cost,
                "recommendations": p.adaptation_recommendations[:3],
                "risks": p.risks[:3]
            })
        
        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })
        
    except Exception as e:
        logger.error(f"Ошибка поиска практик: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/opportunities', methods=['POST'])
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
    try:
        data = request.get_json()
        industry = data.get('industry')
        min_investment = data.get('min_investment', 0)
        location = data.get('location')
        
        logger.info(f"Поиск возможностей: {industry}, {min_investment}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        opportunities = loop.run_until_complete(
            agent.find_investment_opportunities(
                industry=industry,
                min_investment=min_investment,
                location=location
            )
        )
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
        
        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })
        
    except Exception as e:
        logger.error(f"Ошибка поиска возможностей: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/support-measures', methods=['POST'])
def find_support_measures():
    """
    Поиск мер господдержки
    
    Request:
    {
        "industry": "металлургия",
        "business_size": "medium"
    }
    """
    try:
        data = request.get_json()
        industry = data.get('industry', 'металлургия')
        business_size = data.get('business_size', 'medium')
        
        logger.info(f"Поиск мер поддержки: {industry}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        measures = loop.run_until_complete(
            agent.find_support_measures(industry, business_size)
        )
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
        
        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })
        
    except Exception as e:
        logger.error(f"Ошибка поиска мер поддержки: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/proposal', methods=['POST'])
def create_investment_proposal():
    """
    Создание инвестиционного предложения
    
    Request:
    {
        "opportunity_id": "INV-SVE-001",
        "industry": "металлургия"
    }
    """
    try:
        data = request.get_json()
        industry = data.get('industry', 'металлургия')
        opportunity_id = data.get('opportunity_id')
        
        logger.info(f"Создание предложения: {opportunity_id}")
        
        # Получаем возможность
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        opportunities = loop.run_until_complete(
            agent.find_investment_opportunities(industry=industry)
        )
        
        if not opportunities:
            return jsonify({
                "success": False,
                "error": "Возможности не найдены"
            }), 404
        
        opportunity = opportunities[0]  # Берём первую
        
        proposal = loop.run_until_complete(
            agent.create_investment_proposal(opportunity, industry)
        )
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
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Ошибка создания предложения: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/documents/package', methods=['POST'])
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
    try:
        data = request.get_json()
        measure_name = data.get('measure_name')
        measure_type = data.get('measure_type', 'grant')
        project_data = data.get('project_data', {})
        
        logger.info(f"Подготовка документов: {measure_name}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        package = loop.run_until_complete(
            agent.prepare_documents_package(
                measure_name=measure_name,
                measure_type=measure_type,
                project_data=project_data
            )
        )
        
        verification = loop.run_until_complete(
            agent.verify_documents(package)
        )
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
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Ошибка подготовки документов: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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
def full_investment_analysis():
    """
    Комплексный анализ отрасли
    
    Request:
    {
        "industry": "металлургия",
        "min_investment": 50000000
    }
    """
    try:
        data = request.get_json()
        industry = data.get('industry', 'металлургия')
        min_investment = data.get('min_investment', 10_000_000)
        
        logger.info(f"Комплексный анализ: {industry}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(
            agent.full_investment_analysis(industry, min_investment)
        )
        loop.close()
        
        return jsonify({
            "success": True,
            "data": analysis
        })
        
    except Exception as e:
        logger.error(f"Ошибка комплексного анализа: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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


# ==================== Main ====================

if __name__ == '__main__':
    # Создание директорий
    Path("logs").mkdir(exist_ok=True)
    Path("web/static").mkdir(exist_ok=True)
    
    logger.info("Запуск Flask API...")
    logger.info(f"Регион: {REGION['name']}")
    
    # Инициализация агента
    agent = InvestorAgent()
    
    # Запуск сервера
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
