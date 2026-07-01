"""
MCP-сервер: Реестр предприятий Свердловской области
"""
import asyncio
import json
import sqlite3
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("business-registry-db")

DB_PATH = Path(__file__).parent / "data" / "business_registry.db"


def init_database():
    """Инициализация базы данных"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            inn TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            full_name TEXT,
            ogrn TEXT,
            kpp TEXT,
            address TEXT,
            region TEXT,
            city TEXT,
            industry TEXT,
            industry_code TEXT,
            employees INTEGER,
            revenue REAL,
            revenue_year INTEGER,
            status TEXT,
            registration_date TEXT,
            director TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inn TEXT,
            activity_type TEXT,
            activity_description TEXT,
            okved_code TEXT,
            is_primary INTEGER,
            FOREIGN KEY (inn) REFERENCES businesses(inn)
        )
    """)
    
    conn.commit()
    conn.close()
    seed_database()


def seed_database():
    """Заполнение тестовыми данными"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM businesses")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    businesses = [
        {
            "inn": "6601000001",
            "name": "Уральский металлургический завод",
            "full_name": "ООО 'Уральский металлургический завод'",
            "ogrn": "1026600000001",
            "kpp": "660101001",
            "address": "620000, Свердловская обл, г. Екатеринбург, ул. Заводская, 1",
            "region": "Свердловская область",
            "city": "Екатеринбург",
            "industry": "металлургия",
            "industry_code": "24.10",
            "employees": 1500,
            "revenue": 5000000000,
            "revenue_year": 2023,
            "status": "active",
            "registration_date": "2005-03-15",
            "director": "Иванов Иван Иванович",
            "phone": "+7 (343) 100-00-01",
            "email": "info@uralmetall.ru",
            "website": "https://uralmetall.ru"
        },
        {
            "inn": "6601000002",
            "name": "Свердловский машиностроитель",
            "full_name": "АО 'Свердловский машиностроительный завод'",
            "ogrn": "1026600000002",
            "kpp": "660101002",
            "address": "620000, Свердловская обл, г. Екатеринбург, ул. Машинная, 15",
            "region": "Свердловская область",
            "city": "Екатеринбург",
            "industry": "машиностроение",
            "industry_code": "28.11",
            "employees": 800,
            "revenue": 2500000000,
            "revenue_year": 2023,
            "status": "active",
            "registration_date": "1998-07-20",
            "director": "Петров Пётр Петрович",
            "phone": "+7 (343) 100-00-02",
            "email": "info@sv-mash.ru",
            "website": "https://sv-mash.ru"
        },
        {
            "inn": "6601000003",
            "name": "УралХимПласт",
            "full_name": "ООО 'УралХимПласт'",
            "ogrn": "1026600000003",
            "kpp": "660101003",
            "address": "623000, Свердловская обл, г. Первоуральск, ул. Химиков, 10",
            "region": "Свердловская область",
            "city": "Первоуральск",
            "industry": "химическая промышленность",
            "industry_code": "20.14",
            "employees": 450,
            "revenue": 1200000000,
            "revenue_year": 2023,
            "status": "active",
            "registration_date": "2010-05-12",
            "director": "Сидоров Сидор Сидорович",
            "phone": "+7 (3439) 00-00-01",
            "email": "info@uralhimplast.ru",
            "website": "https://uralhimplast.ru"
        },
        {
            "inn": "6601000004",
            "name": "Урал IT Решения",
            "full_name": "ООО 'Урал IT Решения'",
            "ogrn": "1026600000004",
            "kpp": "660101004",
            "address": "620000, Свердловская обл, г. Екатеринбург, ул. Ленина, 50, оф. 301",
            "region": "Свердловская область",
            "city": "Екатеринбург",
            "industry": "IT и цифровые технологии",
            "industry_code": "62.01",
            "employees": 120,
            "revenue": 300000000,
            "revenue_year": 2023,
            "status": "active",
            "registration_date": "2015-09-01",
            "director": "Козлов Алексей Дмитриевич",
            "phone": "+7 (343) 100-00-04",
            "email": "info@ural-it.ru",
            "website": "https://ural-it.ru"
        },
        {
            "inn": "6601000005",
            "name": "СвердловскАгро",
            "full_name": "ООО 'СвердловскАгро'",
            "ogrn": "1026600000005",
            "kpp": "660101005",
            "address": "623000, Свердловская обл, с. Белоярское, ул. Аграрная, 5",
            "region": "Свердловская область",
            "city": "Белоярский",
            "industry": "сельское хозяйство",
            "industry_code": "01.11",
            "employees": 350,
            "revenue": 800000000,
            "revenue_year": 2023,
            "status": "active",
            "registration_date": "2008-02-28",
            "director": "Морозов Николай Николаевич",
            "phone": "+7 (34368) 0-00-01",
            "email": "info@sverdagro.ru",
            "website": "https://sverdagro.ru"
        },
        {
            "inn": "6601000006",
            "name": "ТагилЛесПром",
            "full_name": "ООО 'ТагилЛесПром'",
            "ogrn": "1026600000006",
            "kpp": "660201001",
            "address": "622000, Свердловская обл, г. Нижний Тагил, ул. Лесная, 20",
            "region": "Свердловская область",
            "city": "Нижний Тагил",
            "industry": "лесная промышленность",
            "industry_code": "16.10",
            "employees": 600,
            "revenue": 1500000000,
            "revenue_year": 2023,
            "status": "active",
            "registration_date": "2003-11-10",
            "director": "Волков Владимир Владимирович",
            "phone": "+7 (3435) 00-00-06",
            "email": "info@tagillesprom.ru",
            "website": "https://tagillesprom.ru"
        }
    ]
    
    for biz in businesses:
        cursor.execute("""
            INSERT OR REPLACE INTO businesses 
            (inn, name, full_name, ogrn, kpp, address, region, city, industry,
             industry_code, employees, revenue, revenue_year, status, registration_date,
             director, phone, email, website, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            biz["inn"], biz["name"], biz["full_name"], biz["ogrn"], biz["kpp"],
            biz["address"], biz["region"], biz["city"], biz["industry"],
            biz["industry_code"], biz["employees"], biz["revenue"], biz["revenue_year"],
            biz["status"], biz["registration_date"], biz["director"], biz["phone"],
            biz["email"], biz["website"], "2024-01-01", "2024-01-01"
        ))
        
        # Деятельность
        cursor.execute("""
            INSERT INTO business_activities (inn, activity_type, activity_description, okved_code, is_primary)
            VALUES (?, ?, ?, ?, 1)
        """, (biz["inn"], "Основная", f"Производство в отрасли: {biz['industry']}", biz["industry_code"]))
    
    conn.commit()
    conn.close()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_businesses",
            description="Поиск предприятий по фильтрам",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Регион"},
                    "city": {"type": "string", "description": "Город"},
                    "industry": {"type": "string", "description": "Отрасль"},
                    "min_employees": {"type": "integer", "description": "Мин. количество сотрудников"},
                    "max_employees": {"type": "integer", "description": "Макс. количество сотрудников"},
                    "min_revenue": {"type": "number", "description": "Мин. выручка"},
                    "status": {"type": "string", "enum": ["active", "liquidated"], "description": "Статус"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_business_details",
            description="Детальная информация о предприятии по ИНН",
            inputSchema={
                "type": "object",
                "properties": {
                    "inn": {"type": "string", "description": "ИНН предприятия"}
                },
                "required": ["inn"]
            }
        ),
        Tool(
            name="get_industry_statistics",
            description="Статистика по отрасли в регионе",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Регион"},
                    "industry": {"type": "string", "description": "Отрасль"}
                },
                "required": []
            }
        ),
        Tool(
            name="search_partners",
            description="Поиск потенциальных партнёров по отрасли",
            inputSchema={
                "type": "object",
                "properties": {
                    "industry": {"type": "string", "description": "Отрасль"},
                    "min_employees": {"type": "integer", "description": "Мин. сотрудники"}
                },
                "required": ["industry"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if name == "query_businesses":
            query = "SELECT * FROM businesses WHERE 1=1"
            params = []
            
            if arguments.get("region"):
                query += " AND region LIKE ?"
                params.append(f"%{arguments['region']}%")
            
            if arguments.get("city"):
                query += " AND city LIKE ?"
                params.append(f"%{arguments['city']}%")
            
            if arguments.get("industry"):
                query += " AND industry LIKE ?"
                params.append(f"%{arguments['industry']}%")
            
            if arguments.get("min_employees"):
                query += " AND employees >= ?"
                params.append(arguments["min_employees"])
            
            if arguments.get("max_employees"):
                query += " AND employees <= ?"
                params.append(arguments["max_employees"])
            
            if arguments.get("min_revenue"):
                query += " AND revenue >= ?"
                params.append(arguments["min_revenue"])
            
            if arguments.get("status"):
                query += " AND status = ?"
                params.append(arguments["status"])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "inn": row["inn"],
                    "name": row["name"],
                    "city": row["city"],
                    "region": row["region"],
                    "industry": row["industry"],
                    "employees": row["employees"],
                    "revenue": row["revenue"],
                    "revenue_year": row["revenue_year"],
                    "status": row["status"],
                    "contacts": {
                        "phone": row["phone"],
                        "email": row["email"],
                        "website": row["website"]
                    }
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "count": len(results), "data": results}, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_business_details":
            inn = arguments.get("inn")
            if not inn:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "inn required"}))]
            
            cursor.execute("SELECT * FROM businesses WHERE inn = ?", (inn,))
            row = cursor.fetchone()
            
            if row:
                result = {
                    "inn": row["inn"],
                    "name": row["name"],
                    "full_name": row["full_name"],
                    "ogrn": row["ogrn"],
                    "kpp": row["kpp"],
                    "address": row["address"],
                    "region": row["region"],
                    "city": row["city"],
                    "industry": row["industry"],
                    "industry_code": row["industry_code"],
                    "employees": row["employees"],
                    "revenue": f"{row['revenue']:,.0f} руб. ({row['revenue_year']})",
                    "status": row["status"],
                    "registration_date": row["registration_date"],
                    "director": row["director"],
                    "contacts": {
                        "phone": row["phone"],
                        "email": row["email"],
                        "website": row["website"]
                    }
                }
                
                cursor.execute("SELECT * FROM business_activities WHERE inn = ?", (inn,))
                activities = [dict(row) for row in cursor.fetchall()]
                result["activities"] = activities
                
                return [TextContent(type="text", text=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=2))]
            else:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Business not found"}))]
        
        elif name == "get_industry_statistics":
            region = arguments.get("region", "Свердловская область")
            industry = arguments.get("industry")
            
            query = """
                SELECT 
                    industry,
                    COUNT(*) as companies_count,
                    SUM(employees) as total_employees,
                    SUM(revenue) as total_revenue,
                    AVG(employees) as avg_employees,
                    AVG(revenue) as avg_revenue
                FROM businesses 
                WHERE region LIKE ? AND status = 'active'
            """
            params = [f"%{region}%"]
            
            if industry:
                query += " AND industry LIKE ?"
                params.append(f"%{industry}%")
            
            query += " GROUP BY industry"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            stats = {}
            for row in rows:
                stats[row["industry"]] = {
                    "companies": row["companies_count"],
                    "total_employees": row["total_employees"],
                    "total_revenue": row["total_revenue"],
                    "avg_employees": row["avg_employees"],
                    "avg_revenue": row["avg_revenue"]
                }
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "region": region,
                    "industry_filter": industry,
                    "statistics": stats
                }, ensure_ascii=False, indent=2)
            )]
        
        elif name == "search_partners":
            industry = arguments.get("industry")
            if not industry:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "industry required"}))]
            
            query = """
                SELECT inn, name, city, industry, employees, revenue, phone, email
                FROM businesses 
                WHERE industry LIKE ? AND status = 'active'
            """
            params = [f"%{industry}%"]
            
            if arguments.get("min_employees"):
                query += " AND employees >= ?"
                params.append(arguments["min_employees"])
            
            query += " ORDER BY revenue DESC LIMIT 20"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            partners = []
            for row in rows:
                partners.append({
                    "inn": row["inn"],
                    "name": row["name"],
                    "city": row["city"],
                    "industry": row["industry"],
                    "employees": row["employees"],
                    "revenue": row["revenue"],
                    "contacts": {"phone": row["phone"], "email": row["email"]}
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "count": len(partners), "data": partners}, ensure_ascii=False, indent=2)
            )]
        
        else:
            return [TextContent(type="text", text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}))]
    finally:
        conn.close()


async def main():
    init_database()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
