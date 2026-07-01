"""
Тесты для MCP-серверов
"""
import pytest
import sqlite3
from pathlib import Path

# Тесты инициализации баз данных
class TestSupportMeasuresDB:
    """Тесты сервера мер поддержки"""
    
    @pytest.fixture
    def db_path(self):
        return Path(__file__).parent.parent / "mcp_servers" / "data" / "support_measures.db"
    
    def test_database_exists(self, db_path):
        assert db_path.exists(), "База данных мер поддержки не найдена"
    
    def test_measures_table_exists(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='support_measures'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "Таблица support_measures не найдена"
    
    def test_measures_data_exists(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM support_measures")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "Таблица support_measures пуста"
    
    def test_measures_types(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT type FROM support_measures")
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert "grant" in types, "Нет мер типа 'grant'"
        assert "subsidy" in types, "Нет мер типа 'subsidy'"


class TestInvestmentObjectsDB:
    """Тесты сервера инвестиционных объектов"""
    
    @pytest.fixture
    def db_path(self):
        return Path(__file__).parent.parent / "mcp_servers" / "data" / "investment_objects.db"
    
    def test_database_exists(self, db_path):
        assert db_path.exists(), "База данных инвестобъектов не найдена"
    
    def test_objects_count(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM investment_objects")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "Таблица investment_objects пуста"
    
    def test_object_types(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT type FROM investment_objects")
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert "industrial_park" in types, "Нет индустриальных парков"
        assert "business_incubator" in types, "Нет бизнес-инкубаторов"


class TestBusinessRegistryDB:
    """Тесты сервера реестра предприятий"""
    
    @pytest.fixture
    def db_path(self):
        return Path(__file__).parent.parent / "mcp_servers" / "data" / "business_registry.db"
    
    def test_database_exists(self, db_path):
        assert db_path.exists(), "База данных реестра не найдена"
    
    def test_businesses_count(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM businesses")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "Таблица businesses пуста"
    
    def test_industries_present(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT industry FROM businesses")
        industries = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert len(industries) > 0, "Нет отраслей в реестре"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
