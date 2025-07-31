#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ISKALA RAG System з all-MiniLM-L6-v2
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import uuid
from datetime import datetime

# Add paths
sys.path.append('/app')

from chat_processor.processor import ChatProcessor
from embeddings.system import EmbeddingSystem

class ISKALARAGSystem:
    """ISKALA RAG System"""
    
    def __init__(self):
        self.processor = ChatProcessor()
        self.embedding_system = EmbeddingSystem()
        self.capsules_path = "/app/capsules"
        
        # Створюємо директорії
        os.makedirs(self.capsules_path, exist_ok=True)
        os.makedirs("/app/vector_store", exist_ok=True)
        os.makedirs("/app/uploads", exist_ok=True)
    
    def process_chat_file(self, file_path: str, theme: str = None) -> Dict[str, Any]:
        """Process a chat file and create indexed meaning capsules"""
        try:
            # Parse chat file
            qa_pairs = self.processor.parse_chat_file(file_path)

            if not qa_pairs:
                return {"error": "No Q&A pairs found in file"}

            # Create meaning capsule
            capsule = self.processor.create_meaning_capsule(qa_pairs, theme)

            # Index Q&A pairs
            qa_ids = self.embedding_system.index_qa_pairs(qa_pairs)

            # Index meaning capsule
            capsule_id = self.embedding_system.index_meaning_capsule(capsule)

            # Save capsule to file
            capsule_file = os.path.join(self.capsules_path, f"{capsule_id}.json")
            with open(capsule_file, 'w', encoding='utf-8') as f:
                json.dump(capsule, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "capsule_id": capsule_id,
                "qa_count": len(qa_pairs),
                "qa_ids": qa_ids,
                "capsule_file": capsule_file
            }

        except Exception as e:
            return {"error": str(e)}

    def search_knowledge(self, query: str, search_type: str = "both", n_results: int = 5) -> Dict[str, Any]:
        """Search through indexed knowledge"""
        results = {
            "query": query,
            "qa_results": [],
            "capsule_results": []
        }

        if search_type in ["qa", "both"]:
            results["qa_results"] = self.embedding_system.search_similar_qa(query, n_results)

        if search_type in ["capsules", "both"]:
            results["capsule_results"] = self.embedding_system.search_similar_capsules(query, n_results)

        return results

    def list_capsules(self) -> List[Dict[str, Any]]:
        """List all created meaning capsules"""
        capsules = []
        for file_path in Path(self.capsules_path).glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                capsule = json.load(f)
                capsules.append({
                    "capsule_id": capsule["capsule_id"],
                    "theme": capsule["theme"],
                    "qa_count": capsule["qa_count"],
                    "created_at": capsule["created_at"],
                    "tags": capsule["tags"]
                })

        return sorted(capsules, key=lambda x: x["created_at"], reverse=True)
    
    def get_capsule_details(self, capsule_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific capsule"""
        capsule_file = os.path.join(self.capsules_path, f"{capsule_id}.json")
        if os.path.exists(capsule_file):
            with open(capsule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "Capsule not found"}

# Global instance
rag_system = ISKALARAGSystem()
