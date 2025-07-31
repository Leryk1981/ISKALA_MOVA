#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import os

# Конфігурація
RAG_API_URL = "http://localhost:50084"

def test_rag_api():
    """Тестування RAG API"""
    print("=== Тестування RAG API ===\n")
    
    # 1. Перевірка здоров'я системи
    print("1. Перевірка стану системи...")
    try:
        response = requests.get(f"{RAG_API_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Система працює: {health}")
        else:
            print(f"❌ Помилка стану: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Не вдалося підключитися до API: {e}")
        return False
    
    # 2. Завантаження тестового файлу
    print("\n2. Завантаження тестового файлу...")
    test_file = "test_chat.txt"
    if not os.path.exists(test_file):
        print(f"❌ Тестовий файл {test_file} не знайдено")
        return False
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'theme': 'RAG система'}
            response = requests.post(f"{RAG_API_URL}/process-file", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Файл оброблено: {result['data']['capsule_id']}")
            capsule_id = result['data']['capsule_id']
        else:
            print(f"❌ Помилка обробки: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Помилка завантаження: {e}")
        return False
    
    # 3. Тестування пошуку
    print("\n3. Тестування пошуку...")
    search_queries = [
        "як працює індексація",
        "семантичний пошук",
        "покращення якості",
        "meaning capsule"
    ]
    
    for query in search_queries:
        print(f"\n   Пошук: '{query}'")
        try:
            search_data = {
                "query": query,
                "search_type": "both",
                "n_results": 3
            }
            response = requests.post(f"{RAG_API_URL}/search", json=search_data)
            
            if response.status_code == 200:
                results = response.json()
                qa_results = results['results']['qa_results']
                capsule_results = results['results']['capsule_results']
                
                if qa_results:
                    print(f"   Q&A результати: {len(qa_results)} знайдено")
                    for i, qa in enumerate(qa_results[:2]):
                        print(f"     {i+1}. {qa['question'][:50]}...")
                        print(f"        Схожість: {1 - qa['similarity']:.3f}")
                
                if capsule_results:
                    print(f"   Капсули: {len(capsule_results)} знайдено")
                    for i, capsule in enumerate(capsule_results[:2]):
                        print(f"     {i+1}. Тема: {capsule['theme']}")
                        print(f"        Q&A кількість: {capsule['qa_count']}")
            else:
                print(f"   ❌ Помилка пошуку: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Помилка пошуку: {e}")
    
    # 4. Список капсул
    print("\n4. Список капсул...")
    try:
        response = requests.get(f"{RAG_API_URL}/capsules")
        if response.status_code == 200:
            capsules = response.json()
            print(f"✅ Знайдено капсул: {capsules['count']}")
            for capsule in capsules['capsules']:
                print(f"   - {capsule['capsule_id']}: {capsule['theme']} ({capsule['qa_count']} Q&A)")
        else:
            print(f"❌ Помилка отримання списку: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка списку капсул: {e}")
    
    # 5. Деталі капсули
    print(f"\n5. Деталі капсули {capsule_id}...")
    try:
        response = requests.get(f"{RAG_API_URL}/capsules/{capsule_id}")
        if response.status_code == 200:
            details = response.json()
            capsule = details['capsule']
            print(f"✅ Тема: {capsule['theme']}")
            print(f"   Теги: {', '.join(capsule['tags'])}")
            print(f"   Q&A кількість: {capsule['qa_count']}")
            print(f"   Створено: {capsule['created_at']}")
        else:
            print(f"❌ Помилка отримання деталей: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка деталей капсули: {e}")
    
    print("\n✅ Тестування завершено!")
    return True

if __name__ == "__main__":
    print("Запуск тестування RAG API...")
    print(f"API URL: {RAG_API_URL}")
    print("Переконайтеся, що контейнер запущено: docker-compose up iskala-rag")
    print()
    
    test_rag_api() 