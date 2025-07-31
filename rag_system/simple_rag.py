#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простий RAG без huggingface_hub залежностей
Використовує TF-IDF для семантичного пошуку
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimpleRAGSystem:
    """Простий RAG без нейромереж"""
    
    def __init__(self, data_path: str = "/app/data"):
        self.data_path = data_path
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.documents = []
        self.metadata = []
        self.tfidf_matrix = None
        
    def process_chat_file(self, file_path: str, theme: str = None) -> Dict[str, Any]:
        """Обробка чат файлу"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг Q&A пар
            qa_pairs = self._parse_qa_pairs(content)
            
            # Створення капсули
            capsule = self._create_capsule(qa_pairs, theme or "General")
            
            # Індексація
            self._index_qa_pairs(qa_pairs)
            
            return {
                "success": True,
                "capsule": capsule,
                "qa_pairs_count": len(qa_pairs)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_qa_pairs(self, content: str) -> List[Dict[str, Any]]:
        """Парсинг Q&A пар з тексту"""
        qa_pairs = []
        
        # Регулярний вираз для пошуку Q&A
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
    
    def _create_capsule(self, qa_pairs: List[Dict], theme: str) -> Dict[str, Any]:
        """Створення капсули сенсу"""
        capsule_id = f"capsule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Створення контексту
        questions = [qa['question'] for qa in qa_pairs]
        answers = [qa['answer'] for qa in qa_pairs]
        
        semantic_context = f"Theme: {theme}. Questions: {' '.join(questions[:3])}. Answers: {' '.join(answers[:3])}"
        
        # Генерація тегів
        tags = self._generate_tags(questions + answers)
        
        return {
            'capsule_id': capsule_id,
            'theme': theme,
            'semantic_context': semantic_context,
            'qa_count': len(qa_pairs),
            'tags': tags,
            'created_at': datetime.now().isoformat(),
            'qa_pairs': qa_pairs
        }
    
    def _generate_tags(self, texts: List[str]) -> List[str]:
        """Генерація тегів на основі тексту"""
        # Простий алгоритм генерації тегів
        all_text = ' '.join(texts).lower()
        
        # Пошук ключових слів
        keywords = ['python', 'code', 'programming', 'ai', 'machine learning', 
                   'data', 'analysis', 'web', 'api', 'database', 'docker']
        
        found_tags = []
        for keyword in keywords:
            if keyword in all_text:
                found_tags.append(keyword)
        
        return found_tags[:5]  # Максимум 5 тегів
    
    def _index_qa_pairs(self, qa_pairs: List[Dict]):
        """Індексація Q&A пар"""
        for qa in qa_pairs:
            # Комбінуємо питання та відповідь
            combined_text = f"{qa['question']} {qa['answer']}"
            
            self.documents.append(combined_text)
            self.metadata.append({
                'id': qa['id'],
                'question': qa['question'],
                'answer': qa['answer'],
                'timestamp': qa['timestamp']
            })
        
        # Оновлюємо TF-IDF матрицю
        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
    
    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Пошук знань"""
        if not self.documents or self.tfidf_matrix is None:
            return []
        
        # Трансформуємо запит
        query_vector = self.vectorizer.transform([query])
        
        # Обчислюємо схожість
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Знаходимо топ результати
        top_indices = similarities.argsort()[-n_results:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Мінімальна схожість
                results.append({
                    'id': self.metadata[idx]['id'],
                    'question': self.metadata[idx]['question'],
                    'answer': self.metadata[idx]['answer'],
                    'similarity': float(similarities[idx]),
                    'timestamp': self.metadata[idx]['timestamp']
                })
        
        return results
    
    def list_capsules(self) -> List[Dict[str, Any]]:
        """Список капсул"""
        # В реальній системі це було б з бази даних
        return []
    
    def get_capsule_details(self, capsule_id: str) -> Dict[str, Any]:
        """Деталі капсули"""
        # В реальній системі це було б з бази даних
        return {}

# Глобальний екземпляр
simple_rag = SimpleRAGSystem() 