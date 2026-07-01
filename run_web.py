"""
Скрипт для запуска веб-интерфейса
"""
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("=" * 60)
print("🚀 Запуск веб-интерфейса AI-агента «Помощник инвестора»")
print("=" * 60)
print()
print("📍 Откройте в браузере: http://localhost:5000")
print("📍 API документация: http://localhost:5000/api/health")
print()
print("Нажмите Ctrl+C для остановки сервера")
print("=" * 60)
print()

from web.app import app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
