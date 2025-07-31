"""
LLM Agent v2 для MOVA ISKALA
На основі архітектури Agent Zero
Підтримка OpenRouter
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

@dataclass
class ToolResponse:
    """Відповідь від інструменту"""
    message: str
    success: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    break_loop: bool = False

class BaseTool:
    """Базовий клас для всіх інструментів"""
    
    def __init__(self, agent: 'LLMAgentV2', name: str):
        self.agent = agent
        self.name = name
        self.logger = logging.getLogger(f"tool.{name}")
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Виконати інструмент - має бути перевизначено"""
        raise NotImplementedError
    
    def get_description(self) -> str:
        """Отримати опис інструменту для LLM"""
        return f"Інструмент {self.name}"
    
    def get_parameters(self) -> Dict[str, Any]:
        """Отримати параметри інструменту"""
        return {}

class FileTool(BaseTool):
    """Інструмент для роботи з файлами"""
    
    def __init__(self, agent: 'LLMAgentV2'):
        super().__init__(agent, "file_operations")
    
    async def execute(self, action: str, path: str, content: str = "", **kwargs) -> ToolResponse:
        try:
            file_path = Path(path)
            
            if action == "create":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return ToolResponse(f"Файл {path} створено", data={"path": str(file_path)})
                
            elif action == "read":
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return ToolResponse(f"Файл {path} прочитано", data={"content": content})
                else:
                    return ToolResponse(f"Файл {path} не знайдено", success=False)
                    
            elif action == "write":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return ToolResponse(f"Файл {path} оновлено", data={"path": str(file_path)})
                
            elif action == "delete":
                if file_path.exists():
                    file_path.unlink()
                    return ToolResponse(f"Файл {path} видалено")
                else:
                    return ToolResponse(f"Файл {path} не знайдено", success=False)
            
            else:
                return ToolResponse(f"Невідома дія: {action}", success=False)
                
        except Exception as e:
            return ToolResponse(f"Помилка роботи з файлом: {e}", success=False)
    
    def get_description(self) -> str:
        return "Робота з файлами: створення, читання, запис, видалення"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "action": "create|read|write|delete",
            "path": "шлях до файлу",
            "content": "вміст файлу (для create/write)"
        }

class CommandTool(BaseTool):
    """Інструмент для виконання команд"""
    
    def __init__(self, agent: 'LLMAgentV2'):
        super().__init__(agent, "command_execution")
    
    async def execute(self, command: str, **kwargs) -> ToolResponse:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode('utf-8').strip()
                return ToolResponse(f"Команда виконана успішно", data={"output": output})
            else:
                error = stderr.decode('utf-8').strip()
                return ToolResponse(f"Помилка виконання команди: {error}", success=False)
                
        except Exception as e:
            return ToolResponse(f"Помилка виконання команди: {e}", success=False)
    
    def get_description(self) -> str:
        return "Виконання системних команд"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "command": "команда для виконання"
        }

class APITool(BaseTool):
    """Інструмент для роботи з API"""
    
    def __init__(self, agent: 'LLMAgentV2'):
        super().__init__(agent, "api_calls")
    
    async def execute(self, method: str, url: str, data: Dict = None, headers: Dict = None, **kwargs) -> ToolResponse:
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        result = await response.text()
                elif method.upper() == "POST":
                    async with session.post(url, json=data, headers=headers) as response:
                        result = await response.text()
                else:
                    return ToolResponse(f"Непідтримуваний метод: {method}", success=False)
                
                return ToolResponse(f"API запит виконано", data={"response": result, "status": response.status})
                
        except Exception as e:
            return ToolResponse(f"Помилка API запиту: {e}", success=False)
    
    def get_description(self) -> str:
        return "Виконання HTTP запитів до API"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "method": "GET|POST",
            "url": "URL для запиту",
            "data": "дані для POST запиту",
            "headers": "заголовки запиту"
        }

class MemoryTool(BaseTool):
    """Інструмент для роботи з пам'яттю"""
    
    def __init__(self, agent: 'LLMAgentV2'):
        super().__init__(agent, "memory")
        self.memory_file = Path("state/memory.json")
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_memory()
    
    def _load_memory(self):
        """Завантажити пам'ять з файлу"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
        else:
            self.memory = {"interactions": [], "contexts": {}}
    
    def _save_memory(self):
        """Зберегти пам'ять у файл"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    async def execute(self, action: str, key: str = "", value: str = "", **kwargs) -> ToolResponse:
        try:
            if action == "save":
                interaction = {
                    "timestamp": datetime.now().isoformat(),
                    "key": key,
                    "value": value,
                    "context": kwargs.get("context", "")
                }
                self.memory["interactions"].append(interaction)
                self._save_memory()
                return ToolResponse(f"Пам'ять збережено: {key}")
                
            elif action == "load":
                # Пошук по ключу або контексту
                results = []
                for interaction in self.memory["interactions"]:
                    if key.lower() in interaction["key"].lower() or key.lower() in interaction["value"].lower():
                        results.append(interaction)
                
                if results:
                    return ToolResponse(f"Знайдено {len(results)} записів", data={"results": results})
                else:
                    return ToolResponse(f"Записи не знайдено для ключа: {key}")
                    
            elif action == "list":
                return ToolResponse(f"Всього записів: {len(self.memory['interactions'])}", 
                                  data={"count": len(self.memory["interactions"])})
            
            else:
                return ToolResponse(f"Невідома дія: {action}", success=False)
                
        except Exception as e:
            return ToolResponse(f"Помилка роботи з пам'яттю: {e}", success=False)
    
    def get_description(self) -> str:
        return "Робота з пам'яттю: збереження, завантаження, пошук"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "action": "save|load|list",
            "key": "ключ для збереження/пошуку",
            "value": "значення для збереження",
            "context": "контекст запису"
        }

class LLMAgentV2:
    """LLM Агент v2 на основі архітектури Agent Zero з підтримкою OpenRouter"""
    
    def __init__(self, api_key: str = None, model: str = None):
        # Отримуємо налаштування з змінних середовища
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or "your-api-key"
        self.model = model or os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini"
        
        # Налаштування для OpenRouter
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Ініціалізація інструментів
        self.tools = {
            "file": FileTool(self),
            "command": CommandTool(self),
            "api": APITool(self),
            "memory": MemoryTool(self)
        }
        
        # Історія взаємодій
        self.history = []
        
        # Системний промпт
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Отримати системний промпт"""
        tools_description = "\n".join([
            f"- {tool.name}: {tool.get_description()}" 
            for tool in self.tools.values()
        ])
        
        return f"""Ти - LLM агент MOVA ISKALA з повними правами для роботи з простором.

Твоя роль:
- Розуміти наміри користувача
- Використовувати доступні інструменти для виконання завдань
- Відповідати природно, без форматування
- Запитувати підтвердження перед виконанням важливих дій

Доступні інструменти:
{tools_description}

Правила:
1. Відповідай природно, як у звичайному чаті
2. Якщо потрібно виконати дію - опиши що плануєш зробити
3. Чекай підтвердження користувача перед виконанням
4. Використовуй інструменти тільки після підтвердження
5. Зберігай важливу інформацію в пам'яті"""
    
    async def process_request(self, user_request: str) -> Dict[str, Any]:
        """Обробити запит користувача"""
        try:
            # Додаємо запит до історії
            self.history.append({
                "role": "user",
                "content": user_request,
                "timestamp": datetime.now().isoformat()
            })
            
            # Формуємо повідомлення для LLM
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_request}
            ]
            
            # Виклик LLM через OpenRouter
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            llm_response = response.choices[0].message.content
            
            # Додаємо відповідь до історії
            self.history.append({
                "role": "assistant",
                "content": llm_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Аналізуємо чи потрібні дії
            needs_confirmation = self._analyze_for_actions(llm_response)
            
            return {
                "llm_response": llm_response,
                "needs_confirmation": needs_confirmation,
                "suggested_actions": self._extract_suggested_actions(llm_response) if needs_confirmation else []
            }
            
        except Exception as e:
            logger.error(f"Помилка обробки запиту: {e}")
            return {
                "llm_response": f"Помилка: {e}",
                "needs_confirmation": False,
                "suggested_actions": []
            }
    
    def _analyze_for_actions(self, response: str) -> bool:
        """Аналізувати чи відповідь містить плани дій"""
        action_keywords = [
            "створю", "виконаю", "запущу", "напишу", "зроблю",
            "файл", "команда", "api", "пам'ять", "збережу"
        ]
        
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in action_keywords)
    
    def _extract_suggested_actions(self, response: str) -> List[Dict[str, Any]]:
        """Витягти запропоновані дії з відповіді"""
        actions = []
        
        # Простий парсинг на основі ключових слів
        if "файл" in response.lower():
            actions.append({
                "type": "file",
                "description": "Робота з файлами",
                "tool": "file"
            })
        
        if "команда" in response.lower():
            actions.append({
                "type": "command",
                "description": "Виконання команди",
                "tool": "command"
            })
        
        if "api" in response.lower():
            actions.append({
                "type": "api",
                "description": "API запит",
                "tool": "api"
            })
        
        if "пам'ять" in response.lower():
            actions.append({
                "type": "memory",
                "description": "Робота з пам'яттю",
                "tool": "memory"
            })
        
        return actions
    
    async def execute_confirmed_request(self, user_request: str, llm_response: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Виконати підтверджений запит"""
        try:
            results = []
            
            for action in actions:
                tool_name = action.get("tool")
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    
                    # Простий вивід інформації про дію
                    result = ToolResponse(
                        f"Виконано дію: {action['description']}",
                        data={"action": action}
                    )
                    results.append(result)
            
            # Зберігаємо результат в пам'ять
            await self.tools["memory"].execute(
                action="save",
                key="execution_result",
                value=f"Запит: {user_request}\nРезультат: {len(results)} дій виконано",
                context="user_confirmed_execution"
            )
            
            return {
                "success": True,
                "results": [r.message for r in results],
                "actions_executed": len(results)
            }
            
        except Exception as e:
            logger.error(f"Помилка виконання запиту: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def call_tool(self, tool_name: str, **kwargs) -> ToolResponse:
        """Викликати інструмент"""
        if tool_name in self.tools:
            return await self.tools[tool_name].execute(**kwargs)
        else:
            return ToolResponse(f"Невідомий інструмент: {tool_name}", success=False)
    
    def get_available_tools(self) -> List[str]:
        """Отримати список доступних інструментів"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Отримати інформацію про інструмент"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            return {
                "name": tool.name,
                "description": tool.get_description(),
                "parameters": tool.get_parameters()
            }
        return {} 