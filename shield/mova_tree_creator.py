#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ISKALA Tree Creator Module
Модуль для створення дерев сенсів у просторі ISKALA
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

class TreeCreator:
    """Клас для створення та управління деревами сенсів"""
    
    def __init__(self, trees_dir: str = "/app/trees"):
        self.trees_dir = trees_dir
        os.makedirs(trees_dir, exist_ok=True)
    
    def plant_mova_seed(self, intention: str, context: Dict[str, Any]) -> str:
        """Створює нове дерево сенсів з наміру"""
        tree_id = str(uuid.uuid4())
        
        tree_data = {
            "id": tree_id,
            "intention": intention,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "status": "growing",
            "branches": [],
            "roots": [],
            "leaves": []
        }
        
        tree_file = os.path.join(self.trees_dir, f"{tree_id}.json")
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=2)
        
        return tree_id
    
    def list_trees(self) -> List[Dict[str, Any]]:
        """Повертає список всіх дерев"""
        trees = []
        
        if not os.path.exists(self.trees_dir):
            return trees
        
        for filename in os.listdir(self.trees_dir):
            if filename.endswith('.json'):
                tree_file = os.path.join(self.trees_dir, filename)
                try:
                    with open(tree_file, 'r', encoding='utf-8') as f:
                        tree_data = json.load(f)
                    trees.append(tree_data)
                except Exception as e:
                    print(f"Помилка читання дерева {filename}: {e}")
                    continue
        
        return trees
    
    def get_tree(self, tree_id: str) -> Optional[Dict[str, Any]]:
        """Отримує конкретне дерево за ID"""
        tree_file = os.path.join(self.trees_dir, f"{tree_id}.json")
        
        if not os.path.exists(tree_file):
            return None
        
        try:
            with open(tree_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Помилка читання дерева {tree_id}: {e}")
            return None
    
    def add_branch(self, tree_id: str, branch_data: Dict[str, Any]) -> bool:
        """Додає гілку до дерева"""
        tree = self.get_tree(tree_id)
        if not tree:
            return False
        
        branch_id = str(uuid.uuid4())
        branch_data["id"] = branch_id
        branch_data["created_at"] = datetime.now().isoformat()
        
        tree["branches"].append(branch_data)
        
        tree_file = os.path.join(self.trees_dir, f"{tree_id}.json")
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree, f, ensure_ascii=False, indent=2)
        
        return True

# Глобальний екземпляр
tree_creator = TreeCreator()

def plant_mova_seed(intention: str, context: Dict[str, Any]) -> str:
    """Функція для створення дерева сенсів"""
    return tree_creator.plant_mova_seed(intention, context) 