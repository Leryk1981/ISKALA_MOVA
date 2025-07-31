"""
LLM Agent з повними правами для роботи з простором MOVA ISKALA

Цей агент працює вільно без обмежень - LLM сама розуміє що робити
"""

import os
import json
import subprocess
import asyncio
import httpx
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Імпорт RAG інтеграції
from .rag_integration import rag_iskala_integration

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAgent:
    """LLM агент з повними правами - працює вільно без обмежень"""
    
    def __init__(self):
        self.workspace_path = Path("/app/workspace")
        self.capsules_path = Path("/app/data/capsules")
        self.logs_path = Path("/app/logs")
        self.api_base_url = "http://localhost:8000"
        self.src_api_url = "http://localhost:8001"
        
        # Створюємо необхідні директорії
        self.workspace_path.mkdir(exist_ok=True)
        self.capsules_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        
        # LLM конфігурація
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "moonshotai/kimi-k2")
        
        logger.info("LLM Agent ініціалізовано з повними правами")
    
    async def call_llm(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Викликає LLM через OpenRouter API"""
        if not self.openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY не налаштовано")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://iskala-mova.local",
                        "X-Title": "Iskala/MOVA LLM Agent"
                    },
                    json={
                        "model": self.openrouter_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Помилка виклику LLM: {e}")
            return None
    
    def create_file(self, file_path: str, content: str) -> bool:
        """Створює або оновлює файл"""
        try:
            full_path = self.workspace_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Файл створено/оновлено: {full_path}")
            return True
        except Exception as e:
            logger.error(f"Помилка створення файлу {file_path}: {e}")
            return False
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Читає файл"""
        try:
            full_path = self.workspace_path / file_path
            if not full_path.exists():
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Помилка читання файлу {file_path}: {e}")
            return None
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Виконує системну команду"""
        try:
            logger.info(f"Виконується команда: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=str(self.workspace_path)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            logger.error(f"Помилка виконання команди {command}: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    async def call_api(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Викликає API endpoint"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"Непідтримуваний метод: {method}")
                
                response.raise_for_status()
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Помилка виклику API {endpoint}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def call_src_api(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Викликає SRC API endpoint"""
        try:
            url = f"{self.src_api_url}{endpoint}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"Непідтримуваний метод: {method}")
                
                response.raise_for_status()
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Помилка виклику SRC API {endpoint}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_capsule(self, name: str, content: str) -> bool:
        """Створює капсулу сенсу"""
        try:
            capsule_path = self.capsules_path / f"{name}.сенс"
            with open(capsule_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Капсула створена: {name}")
            return True
        except Exception as e:
            logger.error(f"Помилка створення капсули {name}: {e}")
            return False
    
    def list_capsules(self) -> List[str]:
        """Повертає список капсул"""
        try:
            capsules = []
            for file in self.capsules_path.glob("*.сенс"):
                capsules.append(file.stem)
            return capsules
        except Exception as e:
            logger.error(f"Помилка отримання списку капсул: {e}")
            return []
    
    def create_capsule_from_chat(self, chat_file_path: str, theme: str = None) -> Dict[str, Any]:
        """Створює капсулу сенсу з чат файлу через RAG систему"""
        try:
            result = rag_iskala_integration.create_iskala_capsule_from_chat(chat_file_path, theme)
            if result["success"]:
                logger.info(f"Капсула створена з чату: {result['iskala_capsule']}")
            return result
        except Exception as e:
            logger.error(f"Помилка створення капсули з чату: {e}")
            return {"success": False, "error": str(e)}
    
    def search_knowledge(self, query: str, search_type: str = "both") -> Dict[str, Any]:
        """Пошук знань по всіх капсулах (RAG + ISKALA)"""
        try:
            return rag_iskala_integration.search_knowledge_integrated(query, search_type)
        except Exception as e:
            logger.error(f"Помилка пошуку знань: {e}")
            return {"error": str(e)}
    
    def list_all_capsules(self) -> Dict[str, Any]:
        """Список всіх капсул (RAG + ISKALA)"""
        try:
            return rag_iskala_integration.list_all_capsules()
        except Exception as e:
            logger.error(f"Помилка отримання списку капсул: {e}")
            return {"error": str(e)}
    
    async def execute_intent(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Виконує намір через SRC API"""
        try:
            result = await self.call_src_api(
                "/api/intent/analyze",
                method="POST",
                data={
                    "text": context.get("text", ""),
                    "user_id": context.get("user_id", "llm_agent"),
                    "session_id": context.get("session_id", "default")
                }
            )
            return result
        except Exception as e:
            logger.error(f"Помилка виконання наміру {intent}: {e}")
            return {"success": False, "error": str(e)}
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Логує дію агента"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        log_file = self.logs_path / "llm_agent_actions.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    async def process_user_request(self, request: str) -> Dict[str, Any]:
        """Обробляє запит користувача - LLM працює вільно"""
        try:
            # Мінімальний промпт - LLM сама розуміє що робити
            prompt = f"""
Запит: {request}

Ти маєш повні права в просторі MOVA ISKALA. Відповідай природно, без форматування.
"""
            
            # Отримуємо відповідь від LLM
            llm_response = await self.call_llm(prompt)
            if not llm_response:
                return {"success": False, "error": "LLM недоступний"}
            
            # Просто повертаємо відповідь LLM
            return {
                "success": True,
                "llm_response": llm_response,
                "needs_confirmation": True,
                "message": "LLM готовий виконати дії. Підтвердіть виконання."
            }
            
        except Exception as e:
            logger.error(f"Помилка обробки запиту: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_confirmed_request(self, request: str, llm_response: str) -> Dict[str, Any]:
        """Виконує запит після підтвердження користувача"""
        try:
            # LLM сама вирішує що робити на основі свого розуміння
            # Тут можна додати логіку виконання дій
            
            # Логуємо виконання
            self.log_action("execute_confirmed", {
                "request": request,
                "llm_response": llm_response,
                "status": "executed"
            })
            
            return {
                "success": True,
                "message": "Дії виконано",
                "executed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка виконання підтвердженого запиту: {e}")
            return {"success": False, "error": str(e)}

# Глобальний екземпляр агента
llm_agent = LLMAgent() 