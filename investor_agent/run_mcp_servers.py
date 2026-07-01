"""
Скрипт для запуска MCP-серверов
Использование:
    python run_mcp_servers.py all         - запустить все серверы
    python run_mcp_servers.py support     - только сервер мер поддержки
    python run_mcp_servers.py investment  - только сервер инвестобъектов
    python run_mcp_servers.py business    - только реестр предприятий
"""
import asyncio
import sys
import subprocess
from pathlib import Path

MCP_SERVERS = {
    "support": "mcp_servers/support_measures_server.py",
    "investment": "mcp_servers/investment_objects_server.py",
    "business": "mcp_servers/business_registry_server.py"
}


async def run_server(name: str, filepath: str):
    """Запуск одного MCP-сервера"""
    print(f"🚀 Запуск сервера: {name}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Чтение вывода
        async def read_stream(stream, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                print(f"[{prefix}] {line.decode().strip()}")
        
        await asyncio.gather(
            read_stream(process.stdout, name),
            read_stream(process.stderr, name)
        )
        
        await process.wait()
        
    except Exception as e:
        print(f"❌ Ошибка сервера {name}: {e}")


async def run_all_servers():
    """Запуск всех серверов параллельно"""
    tasks = []
    
    for name, filepath in MCP_SERVERS.items():
        full_path = Path(__file__).parent / filepath
        tasks.append(run_server(name, str(full_path)))
    
    await asyncio.gather(*tasks, return_exceptions=True)


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python run_mcp_servers.py all         - все серверы")
        print("  python run_mcp_servers.py support     - меры поддержки")
        print("  python run_mcp_servers.py investment  - инвестобъекты")
        print("  python run_mcp_servers.py business    - реестр предприятий")
        return
    
    command = sys.argv[1].lower()
    
    if command == "all":
        print("🚀 Запуск всех MCP-серверов...")
        asyncio.run(run_all_servers())
    
    elif command in MCP_SERVERS:
        filepath = Path(__file__).parent / MCP_SERVERS[command]
        asyncio.run(run_server(command, str(filepath)))
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        print(f"Доступные: {', '.join(MCP_SERVERS.keys())}, all")


if __name__ == "__main__":
    main()
