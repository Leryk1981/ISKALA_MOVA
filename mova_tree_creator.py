"""
MOVA Tree Creator
Модуль для створення дерев сенсів у просторі ISKALA
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TreeSeed:
    """Зерно для дерева сенсів"""
    intention: str
    context: Dict[str, Any]
    language: str = "uk"
    creator: str = "user"
    timestamp: str = None
    seed_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.seed_id is None:
            self.seed_id = str(uuid.uuid4())

@dataclass
class TreeNode:
    """Вузол дерева сенсів"""
    node_id: str
    seed_id: str
    content: str
    meaning_type: str  # "root", "branch", "leaf", "fruit"
    parent_id: Optional[str] = None
    children: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: str = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class MOVATreeCreator:
    """Клас для створення та управління деревами сенсів"""

    def __init__(self, storage_path: str = "/a0/instruments/custom/iskala/trees"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

    def plant_seed(self, seed: TreeSeed) -> str:
        """Посадити нове зерно та створити корінь дерева"""
        tree_id = f"tree_{seed.seed_id}"
        tree_dir = self.storage_path / tree_id
        tree_dir.mkdir(exist_ok=True)

        # Створити корінь дерева
        root = TreeNode(
            node_id="root",
            seed_id=seed.seed_id,
            content=seed.intention,
            meaning_type="root",
            metadata={
                "language": seed.language,
                "creator": seed.creator,
                "context": seed.context,
                "original_seed": asdict(seed)
            }
        )

        # Зберегти дерево
        self._save_tree(tree_id, {
            "tree_id": tree_id,
            "seed": asdict(seed),
            "root": asdict(root),
            "nodes": {"root": asdict(root)},
            "created_at": datetime.now().isoformat(),
            "status": "growing"
        })

        return tree_id

    def grow_branch(self, tree_id: str, parent_id: str, content: str, 
                   meaning_type: str = "branch", metadata: Dict = None) -> str:
        """Виростити нову гілку або листок"""
        tree_data = self._load_tree(tree_id)
        if not tree_data:
            raise ValueError(f"Tree {tree_id} not found")

        node_id = str(uuid.uuid4())
        new_node = TreeNode(
            node_id=node_id,
            seed_id=tree_data["seed"]["seed_id"],
            content=content,
            meaning_type=meaning_type,
            parent_id=parent_id,
            metadata=metadata or {}
        )

        # Додати до батьківського вузла
        if parent_id in tree_data["nodes"]:
            tree_data["nodes"][parent_id]["children"].append(node_id)

        # Додати новий вузол
        tree_data["nodes"][node_id] = asdict(new_node)
        tree_data["last_modified"] = datetime.now().isoformat()

        self._save_tree(tree_id, tree_data)
        return node_id

    def harvest_fruit(self, tree_id: str, node_id: str, fruit_content: str) -> str:
        """Зібрати плід з вузла"""
        return self.grow_branch(
            tree_id, node_id, fruit_content, 
            meaning_type="fruit", 
            metadata={"harvested": True}
        )

    def get_tree_structure(self, tree_id: str) -> Dict[str, Any]:
        """Отримати структуру дерева"""
        return self._load_tree(tree_id)

    def list_trees(self) -> List[str]:
        """Отримати список всіх дерев"""
        if not self.storage_path.exists():
            return []
        return [d.name for d in self.storage_path.iterdir() if d.is_dir()]

    def _save_tree(self, tree_id: str, tree_data: Dict):
        """Зберегти дерево"""
        tree_file = self.storage_path / tree_id / "tree.json"
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=2)

    def _load_tree(self, tree_id: str) -> Optional[Dict]:
        """Завантажити дерево"""
        tree_file = self.storage_path / tree_id / "tree.json"
        if tree_file.exists():
            with open(tree_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

# Глобальний екземпляр для використання
tree_creator = MOVATreeCreator()

# Функції для прямого виклику
def plant_mova_seed(intention: str, context: Dict[str, Any], language: str = "uk") -> str:
    """Посадити зерно МОВИ"""
    seed = TreeSeed(
        intention=intention,
        context=context,
        language=language
    )
    return tree_creator.plant_seed(seed)

def grow_tree_branch(tree_id: str, parent_id: str, content: str, meaning_type: str = "branch") -> str:
    """Виростити гілку дерева"""
    return tree_creator.grow_branch(tree_id, parent_id, content, meaning_type)

def get_tree_info(tree_id: str) -> Dict[str, Any]:
    """Отримати інформацію про дерево"""
    return tree_creator.get_tree_structure(tree_id)
