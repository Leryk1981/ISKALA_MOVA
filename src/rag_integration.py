#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Інтеграційний модуль для з'єднання RAG системи з основною системою ISKALA

Цей модуль забезпечує:
1. Конвертацію RAG капсул в формат ISKALA капсул сенсу
2. Інтеграцію з основною системою капсул
3. Семантичний пошук по всіх капсулах
4. Створення капсул сенсу з чатів з ШІ
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

# Додаємо шлях до RAG системи
sys.path.append('/app/rag_system')

from rag_system.main import rag_system

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGISKALAIntegration:
    """Інтеграція RAG системи з ISKALA"""
    
    def __init__(self):
        self.capsules_path = Path("/app/data/capsules")
        self.rag_capsules_path = Path("/app/rag_system/capsules")
        self.workspace_path = Path("/app/workspace")
        
        # Створюємо необхідні директорії
        self.capsules_path.mkdir(parents=True, exist_ok=True)
        self.rag_capsules_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path.mkdir(exist_ok=True)
        
        logger.info("RAG-ISKALA інтеграція ініціалізована")
    
    def create_iskala_capsule_from_chat(self, chat_file_path: str, theme: str = None) -> Dict[str, Any]:
        """Створює ISKALA капсулу сенсу з чат файлу"""
        try:
            # Обробляємо чат через RAG систему
            rag_result = rag_system.process_chat_file(chat_file_path, theme)
            
            if "error" in rag_result:
                return {"success": False, "error": rag_result["error"]}
            
            # Отримуємо деталі капсули
            capsule_details = rag_system.get_capsule_details(rag_result["capsule_id"])
            
            if "error" in capsule_details:
                return {"success": False, "error": capsule_details["error"]}
            
            # Створюємо ISKALA капсулу сенсу
            iskala_capsule = self._convert_rag_to_iskala_capsule(capsule_details)
            
            # Зберігаємо капсулу
            capsule_name = f"rag-{rag_result['capsule_id']}"
            capsule_path = self.capsules_path / f"{capsule_name}.сенс"
            
            with open(capsule_path, 'w', encoding='utf-8') as f:
                f.write(iskala_capsule)
            
            logger.info(f"Створено ISKALA капсулу: {capsule_name}")
            
            return {
                "success": True,
                "iskala_capsule": capsule_name,
                "rag_capsule_id": rag_result["capsule_id"],
                "qa_count": rag_result["qa_count"],
                "theme": theme or "general_conversation"
            }
            
        except Exception as e:
            logger.error(f"Помилка створення ISKALA капсули: {e}")
            return {"success": False, "error": str(e)}
    
    def _convert_rag_to_iskala_capsule(self, rag_capsule: Dict[str, Any]) -> str:
        """Конвертує RAG капсулу в формат ISKALA капсули сенсу"""
        
        # Аналізуємо контент капсули
        qa_pairs = rag_capsule.get("qa_pairs", [])
        theme = rag_capsule.get("theme", "general_conversation")
        tags = rag_capsule.get("tags", [])
        
        # Створюємо короткий опис
        short_description = f"Капсула знань: {theme}"
        if tags:
            short_description += f" (теги: {', '.join(tags[:3])})"
        
        # Створюємо повний опис
        full_description = f"""Капсула сенсу створена з чату з ШІ
Тема: {theme}
Кількість Q&A пар: {len(qa_pairs)}
Теги: {', '.join(tags)}
Створено: {rag_capsule.get('created_at', 'невідомо')}

Ключові питання:
"""
        
        # Додаємо перші 3 питання
        for i, qa in enumerate(qa_pairs[:3]):
            full_description += f"{i+1}. {qa['question'][:100]}...\n"
        
        # Створюємо ISKALA капсулу з шарами
        iskala_capsule = {
            "mova": {
                "short": short_description,
                "full": full_description
            },
            "jalm": {
                "short": json.dumps({
                    "намір": "зберегти_знання",
                    "тип": "rag_капсула",
                    "тема": theme
                }, ensure_ascii=False),
                "full": json.dumps({
                    "намір": "зберегти_знання",
                    "тип": "rag_капсула",
                    "тема": theme,
                    "теги": tags,
                    "qa_кількість": len(qa_pairs),
                    "джерело": "chat_file",
                    "rag_capsule_id": rag_capsule.get("capsule_id")
                }, ensure_ascii=False, indent=2)
            },
            "code": {
                "short": f"rag_capsule.create('{rag_capsule.get('capsule_id')}')",
                "full": f"""// Створення RAG капсули
const ragCapsule = {{
    id: '{rag_capsule.get('capsule_id')}',
    theme: '{theme}',
    qaCount: {len(qa_pairs)},
    tags: {json.dumps(tags, ensure_ascii=False)},
    createdAt: '{rag_capsule.get('created_at')}',
    source: 'chat_file'
}};

// Збереження в векторну БД
await vectorDB.add(ragCapsule);

// Створення ISKALA капсули
const iskalaCapsule = await convertToISKALAFormat(ragCapsule);
await saveCapsule(iskalaCapsule);"""
            },
            "log": {
                "short": f"[{datetime.now().strftime('%H:%M')}] Створено RAG капсулу: {theme}",
                "full": f"""[{datetime.now().isoformat()}] Початок створення RAG капсули
[{datetime.now().isoformat()}] Обробка чат файлу: {len(qa_pairs)} Q&A пар
[{datetime.now().isoformat()}] Створення векторних embeddings
[{datetime.now().isoformat()}] Збереження в ChromaDB
[{datetime.now().isoformat()}] Конвертація в ISKALA формат
[{datetime.now().isoformat()}] Збереження капсули сенсу
[{datetime.now().isoformat()}] RAG капсула створена успішно: {rag_capsule.get('capsule_id')}"""
            },
            "error": {
                "short": "Помилок не виявлено",
                "full": "Система працює стабільно. Помилок під час створення капсули не виявлено."
            }
        }
        
        return json.dumps(iskala_capsule, ensure_ascii=False, indent=2)
    
    def search_knowledge_integrated(self, query: str, search_type: str = "both") -> Dict[str, Any]:
        """Інтегрований пошук по всіх капсулах (RAG + ISKALA)"""
        try:
            results = {
                "query": query,
                "rag_results": [],
                "iskala_results": [],
                "integrated_results": []
            }
            
            # Пошук в RAG системі
            if search_type in ["rag", "both"]:
                rag_results = rag_system.search_knowledge(query, search_type="both", n_results=5)
                results["rag_results"] = rag_results
            
            # Пошук в ISKALA капсулах
            if search_type in ["iskala", "both"]:
                iskala_results = self._search_iskala_capsules(query)
                results["iskala_results"] = iskala_results
            
            # Інтегровані результати
            if search_type == "both":
                results["integrated_results"] = self._merge_search_results(
                    results["rag_results"], 
                    results["iskala_results"]
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка інтегрованого пошуку: {e}")
            return {"error": str(e)}
    
    def _search_iskala_capsules(self, query: str) -> List[Dict[str, Any]]:
        """Пошук в ISKALA капсулах"""
        results = []
        
        try:
            for capsule_file in self.capsules_path.glob("*.сенс"):
                try:
                    with open(capsule_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Простий текстовий пошук
                    if query.lower() in content.lower():
                        capsule_name = capsule_file.stem
                        results.append({
                            "type": "iskala_capsule",
                            "name": capsule_name,
                            "file": str(capsule_file),
                            "relevance": "text_match",
                            "preview": content[:200] + "..."
                        })
                        
                except Exception as e:
                    logger.warning(f"Помилка читання капсули {capsule_file}: {e}")
                    continue
            
            return results[:5]  # Обмежуємо результати
            
        except Exception as e:
            logger.error(f"Помилка пошуку в ISKALA капсулах: {e}")
            return []
    
    def _merge_search_results(self, rag_results: Dict, iskala_results: List) -> List[Dict[str, Any]]:
        """Об'єднує результати пошуку з обох систем"""
        merged = []
        
        # Додаємо RAG результати
        if "qa_results" in rag_results:
            for qa in rag_results["qa_results"][:3]:
                merged.append({
                    "type": "rag_qa",
                    "source": "RAG System",
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "similarity": 1 - qa["similarity"],
                    "file": qa["source_file"]
                })
        
        if "capsule_results" in rag_results:
            for capsule in rag_results["capsule_results"][:2]:
                merged.append({
                    "type": "rag_capsule",
                    "source": "RAG System",
                    "theme": capsule["theme"],
                    "qa_count": capsule["qa_count"],
                    "similarity": 1 - capsule["similarity"],
                    "tags": capsule["tags"]
                })
        
        # Додаємо ISKALA результати
        for iskala in iskala_results[:3]:
            merged.append({
                "type": "iskala_capsule",
                "source": "ISKALA System",
                "name": iskala["name"],
                "relevance": iskala["relevance"],
                "preview": iskala["preview"]
            })
        
        # Сортуємо за релевантністю
        merged.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        
        return merged
    
    def list_all_capsules(self) -> Dict[str, Any]:
        """Список всіх капсул (RAG + ISKALA)"""
        try:
            results = {
                "rag_capsules": [],
                "iskala_capsules": [],
                "total_count": 0
            }
            
            # RAG капсули
            rag_capsules = rag_system.list_capsules()
            results["rag_capsules"] = rag_capsules
            
            # ISKALA капсули
            iskala_capsules = []
            for capsule_file in self.capsules_path.glob("*.сенс"):
                iskala_capsules.append({
                    "name": capsule_file.stem,
                    "file": str(capsule_file),
                    "type": "iskala_capsule",
                    "created": capsule_file.stat().st_mtime
                })
            
            results["iskala_capsules"] = iskala_capsules
            results["total_count"] = len(rag_capsules) + len(iskala_capsules)
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка отримання списку капсул: {e}")
            return {"error": str(e)}

# Глобальний екземпляр інтеграції
rag_iskala_integration = RAGISKALAIntegration() 