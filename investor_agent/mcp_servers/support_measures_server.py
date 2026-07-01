"""
MCP-сервер: Реестр мер государственной поддержки
"""
import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Создание сервера
server = Server("support-measures-db")

# Путь к базе данных
DB_PATH = Path(__file__).parent / "data" / "support_measures.db"


def init_database():
    """Инициализация базы данных"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица мер поддержки
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_measures (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            max_amount REAL,
            min_amount REAL,
            description TEXT,
            eligibility TEXT,
            documents_required TEXT,
            deadline TEXT,
            contact_info TEXT,
            region TEXT,
            industry TEXT,
            business_size TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Таблица заявок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            measure_id TEXT,
            applicant_name TEXT,
            applicant_inn TEXT,
            status TEXT,
            submitted_at TEXT,
            decision_at TEXT,
            decision_reason TEXT,
            FOREIGN KEY (measure_id) REFERENCES support_measures(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Заполнение тестовыми данными
    seed_database()


def seed_database():
    """Заполнение базы тестовыми данными"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверка, есть ли уже данные
    cursor.execute("SELECT COUNT(*) FROM support_measures")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Меры поддержки для Свердловской области
    measures = [
        {
            "id": "SVE-GRANT-001",
            "name": "Грант на развитие промышленного производства",
            "type": "grant",
            "max_amount": 30000000,
            "min_amount": 5000000,
            "description": "Грант для промышленных предприятий на расширение производства и модернизацию",
            "eligibility": json.dumps([
                "Регистрация в Свердловской области",
                "Отрасль: обрабатывающее производство",
                "Создание не менее 50 рабочих мест",
                "Срок деятельности не менее 1 года"
            ], ensure_ascii=False),
            "documents_required": json.dumps([
                "Заявка по форме",
                "Бизнес-план",
                "Финансовая отчётность за 3 года",
                "Выписка из ЕГРЮЛ",
                "Документы о материально-техническом обеспечении"
            ], ensure_ascii=False),
            "deadline": "2024-12-31",
            "contact_info": "Министерство инвестиций Свердловской области, +7 (343) 312-00-00, invest@mid.ural.ru",
            "region": "Свердловская область",
            "industry": "обрабатывающее производство, металлургия, машиностроение",
            "business_size": "small, medium, large",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "SVE-SUB-002",
            "name": "Субсидия на модернизацию оборудования",
            "type": "subsidy",
            "max_amount": 15000000,
            "min_amount": 1000000,
            "description": "Компенсация до 50% затрат на приобретение нового оборудования",
            "eligibility": json.dumps([
                "МСП",
                "Действующее производство",
                "Отсутствие задолженности по налогам"
            ], ensure_ascii=False),
            "documents_required": json.dumps([
                "Заявление",
                "Договоры на оборудование",
                "Платёжные документы",
                "Акт приёма-передачи"
            ], ensure_ascii=False),
            "deadline": "2024-10-31",
            "contact_info": "Фонд развития промышленности, +7 (343) 312-00-01, frp@ural.ru",
            "region": "Свердловская область",
            "industry": "обрабатывающее производство, лёгкая промышленность",
            "business_size": "small, medium",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "SVE-TAX-003",
            "name": "Налоговые льготы для резидентов ОЭЗ",
            "type": "tax_benefit",
            "max_amount": 0,
            "min_amount": 0,
            "description": "Снижение налога на прибыль до 2% в первые 5 лет работы",
            "eligibility": json.dumps([
                "Резидент ОЭЗ 'Титановая долина'",
                "Инвестиции не менее 50 млн руб",
                "Новое производство"
            ], ensure_ascii=False),
            "documents_required": json.dumps([
                "Заявление на получение статуса резидента",
                "Инвестиционный проект",
                "Бизнес-план"
            ], ensure_ascii=False),
            "deadline": None,
            "contact_info": "Управляющая компания ОЭЗ, +7 (343) 312-00-02, info@titan-valley.ru",
            "region": "Свердловская область",
            "industry": "металлургия, машиностроение, химическая промышленность, IT",
            "business_size": "medium, large",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "SVE-GRANT-004",
            "name": "Грант на развитие IT-проектов",
            "type": "grant",
            "max_amount": 20000000,
            "min_amount": 3000000,
            "description": "Поддержка IT-стартапов и цифровых проектов",
            "eligibility": json.dumps([
                "Аккредитованная IT-компания",
                "Регистрация в Свердловской области",
                "Инновационный продукт"
            ], ensure_ascii=False),
            "documents_required": json.dumps([
                "Заявка",
                "Техническое задание",
                "Финансовая модель",
                "Презентация продукта"
            ], ensure_ascii=False),
            "deadline": "2024-11-30",
            "contact_info": "Минцифры Свердловской области, +7 (343) 312-00-03, it@mid.ural.ru",
            "region": "Свердловская область",
            "industry": "IT и цифровые технологии",
            "business_size": "small, medium",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "SVE-GUAR-005",
            "name": "Гарантийная поддержка для МСП",
            "type": "guarantee",
            "max_amount": 50000000,
            "min_amount": 5000000,
            "description": "Государственные гарантии по кредитам для МСП",
            "eligibility": json.dumps([
                "МСП",
                "Срок деятельности не менее 6 месяцев",
                "Отсутствие просрочек по кредитам"
            ], ensure_ascii=False),
            "documents_required": json.dumps([
                "Заявление",
                "Финансовая отчётность",
                "Кредитный договор",
                "Бизнес-план"
            ], ensure_ascii=False),
            "deadline": None,
            "contact_info": "Гарантийный фонд Свердловской области, +7 (343) 312-00-04, guarantee@ural.ru",
            "region": "Свердловская область",
            "industry": "все отрасли",
            "business_size": "small, medium",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "SVE-SUB-006",
            "name": "Субсидия на экспортную деятельность",
            "type": "subsidy",
            "max_amount": 10000000,
            "min_amount": 500000,
            "description": "Компенсация затрат на сертификацию, логистику, участие в выставках",
            "eligibility": json.dumps([
                "Экспортёр или планирующий экспорт",
                "Регистрация в Свердловской области"
            ], ensure_ascii=False),
            "documents_required": json.dumps([
                "Заявление",
                "Контракты с иностранными партнёрами",
                "Документы о затратах"
            ], ensure_ascii=False),
            "deadline": "2024-12-15",
            "contact_info": "Центр поддержки экспорта, +7 (343) 312-00-05, export@ural.ru",
            "region": "Свердловская область",
            "industry": "все отрасли",
            "business_size": "small, medium, large",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        }
    ]
    
    for measure in measures:
        cursor.execute("""
            INSERT OR REPLACE INTO support_measures 
            (id, name, type, max_amount, min_amount, description, eligibility, 
             documents_required, deadline, contact_info, region, industry, 
             business_size, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            measure["id"], measure["name"], measure["type"],
            measure["max_amount"], measure["min_amount"], measure["description"],
            measure["eligibility"], measure["documents_required"],
            measure["deadline"], measure["contact_info"], measure["region"],
            measure["industry"], measure["business_size"],
            measure["created_at"], measure["updated_at"]
        ))
    
    conn.commit()
    conn.close()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Список доступных инструментов"""
    return [
        Tool(
            name="query_support_measures",
            description="Поиск мер государственной поддержки по фильтрам",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Регион (например, 'Свердловская область')"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Отрасль (например, 'металлургия', 'IT')"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["grant", "subsidy", "tax_benefit", "guarantee"],
                        "description": "Тип меры поддержки"
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Минимальная сумма поддержки"
                    },
                    "business_size": {
                        "type": "string",
                        "enum": ["small", "medium", "large"],
                        "description": "Размер бизнеса"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_measure_details",
            description="Получение детальной информации о мере поддержки по ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "measure_id": {
                        "type": "string",
                        "description": "ID меры поддержки (например, 'SVE-GRANT-001')"
                    }
                },
                "required": ["measure_id"]
            }
        ),
        Tool(
            name="get_statistics",
            description="Получение статистики по мерам поддержки",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Регион для статистики"
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Вызов инструмента"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if name == "query_support_measures":
            # Формирование SQL-запроса с фильтрами
            query = "SELECT * FROM support_measures WHERE 1=1"
            params = []
            
            if arguments.get("region"):
                query += " AND region LIKE ?"
                params.append(f"%{arguments['region']}%")
            
            if arguments.get("industry"):
                query += " AND industry LIKE ?"
                params.append(f"%{arguments['industry']}%")
            
            if arguments.get("type"):
                query += " AND type = ?"
                params.append(arguments["type"])
            
            if arguments.get("min_amount"):
                query += " AND max_amount >= ?"
                params.append(arguments["min_amount"])
            
            if arguments.get("business_size"):
                query += " AND business_size LIKE ?"
                params.append(f"%{arguments['business_size']}%")
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "max_amount": row["max_amount"],
                    "min_amount": row["min_amount"],
                    "description": row["description"],
                    "eligibility": json.loads(row["eligibility"]),
                    "documents_required": json.loads(row["documents_required"]),
                    "deadline": row["deadline"],
                    "contact_info": row["contact_info"],
                    "region": row["region"],
                    "industry": row["industry"]
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(results),
                    "data": results
                }, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_measure_details":
            measure_id = arguments.get("measure_id")
            if not measure_id:
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": "measure_id required"}, ensure_ascii=False)
                )]
            
            cursor.execute("SELECT * FROM support_measures WHERE id = ?", (measure_id,))
            row = cursor.fetchone()
            
            if row:
                result = {
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "max_amount": row["max_amount"],
                    "min_amount": row["min_amount"],
                    "description": row["description"],
                    "eligibility": json.loads(row["eligibility"]),
                    "documents_required": json.loads(row["documents_required"]),
                    "deadline": row["deadline"],
                    "contact_info": row["contact_info"],
                    "region": row["region"]
                }
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": "Measure not found"}, ensure_ascii=False)
                )]
        
        elif name == "get_statistics":
            region = arguments.get("region", "Свердловская область")
            
            cursor.execute("""
                SELECT 
                    type,
                    COUNT(*) as count,
                    SUM(max_amount) as total_max_amount,
                    AVG(max_amount) as avg_amount
                FROM support_measures 
                WHERE region LIKE ?
                GROUP BY type
            """, (f"%{region}%",))
            
            rows = cursor.fetchall()
            stats = {row["type"]: {"count": row["count"], "total_max": row["total_max_amount"], "avg": row["avg_amount"]} for row in rows}
            
            cursor.execute("SELECT COUNT(*) FROM support_measures WHERE region LIKE ?", (f"%{region}%",))
            total = cursor.fetchone()[0]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "region": region,
                    "total_measures": total,
                    "by_type": stats
                }, ensure_ascii=False, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}, ensure_ascii=False)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
        )]
    finally:
        conn.close()


async def main():
    """Запуск сервера"""
    # Инициализация БД
    init_database()
    
    # Запуск сервера
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
