"""
MCP-сервер: База инвестиционных объектов и площадок
"""
import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("investment-objects-db")

DB_PATH = Path(__file__).parent / "data" / "investment_objects.db"


def init_database():
    """Инициализация базы данных"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_objects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            location TEXT,
            region TEXT,
            area REAL,
            area_unit TEXT,
            price REAL,
            price_unit TEXT,
            infrastructure TEXT,
            description TEXT,
            status TEXT,
            contacts TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS object_photos (
            id TEXT PRIMARY KEY,
            object_id TEXT,
            url TEXT,
            description TEXT,
            FOREIGN KEY (object_id) REFERENCES investment_objects(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    seed_database()


def seed_database():
    """Заполнение тестовыми данными"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM investment_objects")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    objects = [
        {
            "id": "INV-SVE-001",
            "name": "Индустриальный парк 'Титановая долина'",
            "type": "industrial_park",
            "location": "Верхняя Салда",
            "region": "Свердловская область",
            "area": 500.0,
            "area_unit": "га",
            "price": None,
            "price_unit": "руб/га",
            "infrastructure": json.dumps([
                "Электричество 35 кВ",
                "Газоснабжение",
                "Водоснабжение",
                "Ж/Д подъездные пути",
                "Автомобильные дороги",
                "Оптоволоконная связь"
            ], ensure_ascii=False),
            "description": "ОЭЗ промышленно-производственного типа. Готовые площадки для производств в области титана, металлургии, машиностроения.",
            "status": "available",
            "contacts": json.dumps({
                "phone": "+7 (3434) 55-55-55",
                "email": "info@titan-valley.ru",
                "website": "https://titan-valley.ru"
            }, ensure_ascii=False),
            "latitude": 58.0469,
            "longitude": 60.5536,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "INV-SVE-002",
            "name": "Бизнес-инкубатор 'Технопарк'",
            "type": "business_incubator",
            "location": "Екатеринбург",
            "region": "Свердловская область",
            "area": 2500.0,
            "area_unit": "м²",
            "price": 500,
            "price_unit": "руб/м²/мес",
            "infrastructure": json.dumps([
                "Офисные помещения",
                "Конференц-залы",
                "Высокоскоростной интернет",
                "Переговорные комнаты",
                "Коворкинг",
                "Парковка"
            ], ensure_ascii=False),
            "description": "Бизнес-инкубатор для IT-стартапов и инновационных проектов. Предоставляет помещения и услуги поддержки.",
            "status": "available",
            "contacts": json.dumps({
                "phone": "+7 (343) 200-00-01",
                "email": "info@technopark-ekb.ru",
                "website": "https://technopark-ekb.ru"
            }, ensure_ascii=False),
            "latitude": 56.8389,
            "longitude": 60.6057,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "INV-SVE-003",
            "name": "Производственная площадка 'Нижний Тагил'",
            "type": "facility",
            "location": "Нижний Тагил",
            "region": "Свердловская область",
            "area": 15000.0,
            "area_unit": "м²",
            "price": 100000000,
            "price_unit": "руб",
            "infrastructure": json.dumps([
                "Электричество 10 кВ",
                "Газоснабжение",
                "Водоснабжение",
                "Крановое оборудование",
                "Ж/Д ветка",
                "Охраняемая территория"
            ], ensure_ascii=False),
            "description": "Готовый производственный корпус с возможностью размещения металлургического или машиностроительного производства.",
            "status": "available",
            "contacts": json.dumps({
                "phone": "+7 (3435) 00-00-01",
                "email": "invest@nt-plant.ru"
            }, ensure_ascii=False),
            "latitude": 57.9197,
            "longitude": 59.9659,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "INV-SVE-004",
            "name": "Агропромышленный парк 'Асбест'",
            "type": "agricultural_park",
            "location": "Асбест",
            "region": "Свердловская область",
            "area": 200.0,
            "area_unit": "га",
            "price": None,
            "price_unit": "руб/га",
            "infrastructure": json.dumps([
                "Ирригационная система",
                "Хранилища",
                "Перерабатывающие мощности",
                "Логистический центр"
            ], ensure_ascii=False),
            "description": "Площадка для развития агропромышленного комплекса. Выращивание и переработка сельхозпродукции.",
            "status": "available",
            "contacts": json.dumps({
                "phone": "+7 (34365) 0-00-01",
                "email": "agro@asbest.ru"
            }, ensure_ascii=False),
            "latitude": 57.0144,
            "longitude": 61.4594,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "INV-SVE-005",
            "name": "Логистический центр 'Кольцово'",
            "type": "logistics_center",
            "location": "Кольцово",
            "region": "Свердловская область",
            "area": 50000.0,
            "area_unit": "м²",
            "price": 500000000,
            "price_unit": "руб",
            "infrastructure": json.dumps([
                "Складские помещения",
                "Холодильные камеры",
                "Погрузочная техника",
                "Таможенный терминал",
                "Близость к аэропорту"
            ], ensure_ascii=False),
            "description": "Современный логистический комплекс рядом с аэропортом Кольцово. Идеально для дистрибьюторских центров.",
            "status": "available",
            "contacts": json.dumps({
                "phone": "+7 (343) 200-00-02",
                "email": "logistic@koltsovo.ru"
            }, ensure_ascii=False),
            "latitude": 56.7444,
            "longitude": 60.8078,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        },
        {
            "id": "INV-SVE-006",
            "name": "Земельный участок 'Полевской'",
            "type": "land_plot",
            "location": "Полевской",
            "region": "Свердловская область",
            "area": 50.0,
            "area_unit": "га",
            "price": 25000000,
            "price_unit": "руб",
            "infrastructure": json.dumps([
                "Электричество рядом",
                "Подъездная дорога",
                "Возможность подключения к газу"
            ], ensure_ascii=False),
            "description": "Свободный земельный участок под промышленное или складское строительство.",
            "status": "available",
            "contacts": json.dumps({
                "phone": "+7 (34369) 0-00-01",
                "email": "land@polevskoy.ru"
            }, ensure_ascii=False),
            "latitude": 56.4433,
            "longitude": 60.2211,
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        }
    ]
    
    for obj in objects:
        cursor.execute("""
            INSERT OR REPLACE INTO investment_objects 
            (id, name, type, location, region, area, area_unit, price, price_unit,
             infrastructure, description, status, contacts, latitude, longitude,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            obj["id"], obj["name"], obj["type"], obj["location"], obj["region"],
            obj["area"], obj["area_unit"], obj["price"], obj["price_unit"],
            obj["infrastructure"], obj["description"], obj["status"], obj["contacts"],
            obj["latitude"], obj["longitude"], obj["created_at"], obj["updated_at"]
        ))
    
    conn.commit()
    conn.close()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_investment_objects",
            description="Поиск инвестиционных объектов и площадок",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Регион"},
                    "type": {
                        "type": "string",
                        "enum": ["industrial_park", "business_incubator", "facility", "agricultural_park", "logistics_center", "land_plot"],
                        "description": "Тип объекта"
                    },
                    "location": {"type": "string", "description": "Город/район"},
                    "min_area": {"type": "number", "description": "Минимальная площадь"},
                    "max_price": {"type": "number", "description": "Максимальная цена"},
                    "status": {"type": "string", "enum": ["available", "reserved", "sold"], "description": "Статус"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_object_details",
            description="Детальная информация об объекте",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_id": {"type": "string", "description": "ID объекта"}
                },
                "required": ["object_id"]
            }
        ),
        Tool(
            name="get_available_objects_summary",
            description="Сводка по доступным объектам в регионе",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Регион"}
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if name == "query_investment_objects":
            query = "SELECT * FROM investment_objects WHERE 1=1"
            params = []
            
            if arguments.get("region"):
                query += " AND region LIKE ?"
                params.append(f"%{arguments['region']}%")
            
            if arguments.get("type"):
                query += " AND type = ?"
                params.append(arguments["type"])
            
            if arguments.get("location"):
                query += " AND location LIKE ?"
                params.append(f"%{arguments['location']}%")
            
            if arguments.get("min_area"):
                query += " AND area >= ?"
                params.append(arguments["min_area"])
            
            if arguments.get("max_price"):
                query += " AND (price IS NULL OR price <= ?)"
                params.append(arguments["max_price"])
            
            if arguments.get("status"):
                query += " AND status = ?"
                params.append(arguments["status"])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "location": row["location"],
                    "region": row["region"],
                    "area": row["area"],
                    "area_unit": row["area_unit"],
                    "price": row["price"],
                    "price_unit": row["price_unit"],
                    "infrastructure": json.loads(row["infrastructure"]),
                    "description": row["description"],
                    "status": row["status"],
                    "contacts": json.loads(row["contacts"]),
                    "coordinates": {"lat": row["latitude"], "lon": row["longitude"]}
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "count": len(results), "data": results}, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_object_details":
            object_id = arguments.get("object_id")
            if not object_id:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "object_id required"}))]
            
            cursor.execute("SELECT * FROM investment_objects WHERE id = ?", (object_id,))
            row = cursor.fetchone()
            
            if row:
                result = {
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "location": row["location"],
                    "region": row["region"],
                    "area": f"{row['area']} {row['area_unit']}",
                    "price": f"{row['price']} {row['price_unit']}" if row['price'] else "По запросу",
                    "infrastructure": json.loads(row["infrastructure"]),
                    "description": row["description"],
                    "status": row["status"],
                    "contacts": json.loads(row["contacts"]),
                    "coordinates": {"lat": row["latitude"], "lon": row["longitude"]}
                }
                return [TextContent(type="text", text=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=2))]
            else:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Object not found"}))]
        
        elif name == "get_available_objects_summary":
            region = arguments.get("region", "Свердловская область")
            
            cursor.execute("""
                SELECT type, COUNT(*) as count, SUM(area) as total_area, AVG(price) as avg_price
                FROM investment_objects 
                WHERE region LIKE ? AND status = 'available'
                GROUP BY type
            """, (f"%{region}%",))
            
            rows = cursor.fetchall()
            summary = {row["type"]: {"count": row["count"], "total_area": row["total_area"], "avg_price": row["avg_price"]} for row in rows}
            
            cursor.execute("SELECT COUNT(*), SUM(area) FROM investment_objects WHERE region LIKE ? AND status = 'available'", (f"%{region}%",))
            row = cursor.fetchone()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "region": region,
                    "total_objects": row[0],
                    "total_area": f"{row[1]} (разные ед.)",
                    "by_type": summary
                }, ensure_ascii=False, indent=2)
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
