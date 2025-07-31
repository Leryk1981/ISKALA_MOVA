#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG система з OpenRouter LLM
Використовує вашу LLM для створення embeddings та семантичного пошуку
"""

import json
import os
import re
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

class OpenRouterRAGSystem:
    """RAG система з OpenRouter LLM"""
    
    def __init__(self, openrouter_api_key: str = None, model: str = "moonshotai/kimi-k2"):
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        
        # ChromaDB клієнт
        self.client = chromadb.PersistentClient(
            path="/app/vector_store",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Колекції
        self.qa_collection = self.client.get_or_create_collection(
            name="qa_pairs",
            metadata={"description": "Q&A pairs from chat conversations"}
        )
        
        self.capsules_collection = self.client.get_or_create_collection(
            name="meaning_capsules",
            metadata={"description": "Semantic meaning capsules"}
        )
        
    def call_openrouter_embedding(self, text: str) -> Optional[List[float]]:
        """Отримує embeddings через OpenRouter"""
        if not self.openrouter_api_key:
            return None
            
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://iskala-mova.local",
                    "X-Title": "Iskala/MOVA RAG System"
                },
                json={
                    "model": "text-embedding-ada-002",  # Використовуємо OpenAI embeddings
                    "input": text
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"Помилка отримання embeddings: {e}")
            return None
    
    def call_openrouter_llm(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Викликає LLM через OpenRouter"""
        if not self.openrouter_api_key:
            return None
            
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://iskala-mova.local",
                    "X-Title": "Iskala/MOVA RAG System"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Помилка виклику LLM: {e}")
            return None
    
    def process_chat_file(self, file_path: str, theme: str = None) -> Dict[str, Any]:
        """Обробка чат файлу"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг Q&A пар
            qa_pairs = self._parse_qa_pairs(content)
            
            if not qa_pairs:
                return {"success": False, "error": "Не знайдено Q&A пар"}
            
            # Створення капсули через LLM
            capsule = self._create_capsule_with_llm(qa_pairs, theme or "General")
            
            # Індексація
            self._index_qa_pairs(qa_pairs)
            
            return {
                "success": True,
                "capsule": capsule,
                "qa_pairs_count": len(qa_pairs)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_qa_pairs(self, content: str) -> List[Dict[str, Any]]:
        """Парсинг Q&A пар з тексту"""
        qa_pairs = []
        
        pattern = r'(?:User|Користувач|user):\s*(.+?)\n(?:Assistant|AI|assistant):\s*(.+?)(?=\n(?:User|Користувач|user):|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (question, answer) in enumerate(matches):
            qa_pairs.append({
                'id': f"qa_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'question': question.strip(),
                'answer': answer.strip(),
                'timestamp': datetime.now().isoformat()
            })
        
        return qa_pairs
    
    def _create_capsule_with_llm(self, qa_pairs: List[Dict], theme: str) -> Dict[str, Any]:
        """Створення капсули сенсу через LLM"""
        capsule_id = f"capsule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Формуємо промпт для LLM
        qa_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs[:5]])
        
        prompt = f"""
        Створи капсулу сенсу на основі наступних Q&A пар:
        
        Тема: {theme}
        
        Q&A пари:
        {qa_text}
        
        Проаналізуй та створи:
        1. Короткий опис теми (1-2 речення)
        2. Семантичний контекст (3-4 речення)
        3. Ключові теги (5-7 слів)
        
        Відповідь в форматі JSON:
        {{
            "short_description": "...",
            "semantic_context": "...",
            "tags": ["tag1", "tag2", "tag3"]
        }}
        """
        
        # Викликаємо LLM
        llm_response = self.call_openrouter_llm(prompt)
        
        if llm_response:
            try:
                # Парсимо JSON відповідь
                analysis = json.loads(llm_response)
                
                return {
                    'capsule_id': capsule_id,
                    'theme': theme,
                    'short_description': analysis.get('short_description', ''),
                    'semantic_context': analysis.get('semantic_context', ''),
                    'tags': analysis.get('tags', []),
                    'qa_count': len(qa_pairs),
                    'created_at': datetime.now().isoformat(),
                    'qa_pairs': qa_pairs
                }
            except json.JSONDecodeError:
                # Якщо LLM не повернув JSON, створюємо просту капсулу
                pass
        
        # Fallback - проста капсула
        return {
            'capsule_id': capsule_id,
            'theme': theme,
            'short_description': f"Капсула на тему: {theme}",
            'semantic_context': f"Містить {len(qa_pairs)} Q&A пар на тему {theme}",
            'tags': [theme, "chat", "qa"],
            'qa_count': len(qa_pairs),
            'created_at': datetime.now().isoformat(),
            'qa_pairs': qa_pairs
        }
    
    def _index_qa_pairs(self, qa_pairs: List[Dict]):
        """Індексація Q&A пар"""
        for qa in qa_pairs:
            # Комбінуємо питання та відповідь
            combined_text = f"Question: {qa['question']} Answer: {qa['answer']}"
            
            # Отримуємо embeddings
            embedding = self.call_openrouter_embedding(combined_text)
            
            if embedding:
                # Додаємо до колекції
                self.qa_collection.add(
                    ids=[qa['id']],
                    documents=[combined_text],
                    metadatas=[{
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'timestamp': qa['timestamp'],
                        'type': 'qa_pair'
                    }],
                    embeddings=[embedding]
                )
    
    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Пошук знань"""
        # Отримуємо embeddings для запиту
        query_embedding = self.call_openrouter_embedding(query)
        
        if not query_embedding:
            return []
        
        # Шукаємо в колекції
        results = self.qa_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return [
            {
                'id': results['ids'][0][i],
                'question': results['metadatas'][0][i]['question'],
                'answer': results['metadatas'][0][i]['answer'],
                'similarity': results['distances'][0][i],
                'timestamp': results['metadatas'][0][i]['timestamp']
            }
            for i in range(len(results['ids'][0]))
        ]
    
    def list_capsules(self) -> List[Dict[str, Any]]:
        """Список капсул"""
        # В реальній системі це було б з бази даних
        return []
    
    def get_capsule_details(self, capsule_id: str) -> Dict[str, Any]:
        """Деталі капсули"""
        # В реальній системі це було б з бази даних
        return {}

# Глобальний екземпляр
openrouter_rag = OpenRouterRAGSystem() 