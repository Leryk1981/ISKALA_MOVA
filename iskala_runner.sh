#!/bin/bash

# ISKALA Module Runner
# Цей скрипт дозволяє Agent Zero запускати функції ISKALA модуля

ISKALA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Функція для запуску ISKALA агента
run_iskala_agent() {
    cd "$ISKALA_DIR"
    python3 llm_agent_v2.py "$@"
}

# Функція для роботи з файлами
iskala_file_operation() {
    local action="$1"
    local path="$2"
    local content="$3"
    
    cd "$ISKALA_DIR"
    python3 -c "
import asyncio
from llm_agent_v2 import FileTool, LLMAgentV2

async def main():
    agent = LLMAgentV2()
    tool = FileTool(agent)
    result = await tool.execute(action='$action', path='$path', content='$content')
    print(result.message)

asyncio.run(main())
"
}

# Функція для виконання команд
iskala_command_execution() {
    local command="$1"
    
    cd "$ISKALA_DIR"
    python3 -c "
import asyncio
from llm_agent_v2 import CommandTool, LLMAgentV2

async def main():
    agent = LLMAgentV2()
    tool = CommandTool(agent)
    result = await tool.execute(command='$command')
    print(result.message)

asyncio.run(main())
"
}

# Функція для роботи з пам'яттю
iskala_memory_operation() {
    local action="$1"
    local key="$2"
    local value="$3"
    
    cd "$ISKALA_DIR"
    python3 -c "
import asyncio
from llm_agent_v2 import MemoryTool, LLMAgentV2

async def main():
    agent = LLMAgentV2()
    tool = MemoryTool(agent)
    result = await tool.execute(action='$action', key='$key', value='$value')
    print(result.message)

asyncio.run(main())
"
}

# Головна логіка
case "$1" in
    "agent")
        shift
        run_iskala_agent "$@"
        ;;
    "file")
        shift
        iskala_file_operation "$@"
        ;;
    "command")
        shift
        iskala_command_execution "$@"
        ;;
    "memory")
        shift
        iskala_memory_operation "$@"
        ;;
    "help")
        echo "ISKALA Module Runner"
        echo "Використання: $0 [команда] [параметри]"
        echo ""
        echo "Команди:"
        echo "  agent [параметри]  - запуск ISKALA агента"
        echo "  file [дія] [шлях] [вміст] - робота з файлами"
        echo "  command [команда]  - виконання системної команди"
        echo "  memory [дія] [ключ] [значення] - робота з пам'яттю"
        echo "  help               - показати цю довідку"
        ;;
    *)
        echo "Невідома команда: $1"
        echo "Використайте '$0 help' для довідки"
        exit 1
        ;;
esac 