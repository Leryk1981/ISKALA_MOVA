#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Додаємо шлях до модулів
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import rag_system

def test_rag_system():
    """Тестування RAG системи"""
    print("=== Тестування RAG системи ISKALA ===\n")
    
    # Тестовий файл
    test_file = "test_chat.txt"
    
    if not os.path.exists(test_file):
        print(f"❌ Тестовий файл {test_file} не знайдено")
        return False
    
    print(f"📁 Обробка файлу: {test_file}")
    
    try:
        # Обробка чат файлу
        result = rag_system.process_chat_file(test_file, theme="RAG система")
        
        if "error" in result:
            print(f"❌ Помилка обробки: {result['error']}")
            return False
        
        print(f"✅ Файл успішно оброблено")
        print(f"   - ID капсули: {result['capsule_id']}")
        print(f"   - Кількість Q&A пар: {result['qa_count']}")
        print(f"   - Файл капсули: {result['capsule_file']}")
        
        # Тестування пошуку
        print("\n🔍 Тестування пошуку...")
        
        search_queries = [
            "як працює індексація",
            "семантичний пошук",
            "покращення якості",
            "meaning capsule"
        ]
        
        for query in search_queries:
            print(f"\n   Пошук: '{query}'")
            search_results = rag_system.search_knowledge(query, search_type="both", n_results=3)
            
            if search_results["qa_results"]:
                print(f"   Q&A результати:")
                for i, qa in enumerate(search_results["qa_results"][:2]):
                    print(f"     {i+1}. {qa['question'][:50]}...")
                    print(f"        Відповідь: {qa['answer'][:50]}...")
                    print(f"        Схожість: {1 - qa['similarity']:.3f}")
            
            if search_results["capsule_results"]:
                print(f"   Капсули:")
                for i, capsule in enumerate(search_results["capsule_results"][:2]):
                    print(f"     {i+1}. Тема: {capsule['theme']}")
                    print(f"        Теги: {', '.join(capsule['tags'][:3])}")
                    print(f"        Q&A кількість: {capsule['qa_count']}")
        
        # Список капсул
        print("\n📋 Список створених капсул:")
        capsules = rag_system.list_capsules()
        for capsule in capsules:
            print(f"   - {capsule['capsule_id']}: {capsule['theme']} ({capsule['qa_count']} Q&A)")
        
        print("\n✅ Тестування завершено успішно!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка під час тестування: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_system() 