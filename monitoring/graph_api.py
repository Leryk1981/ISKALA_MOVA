"""
MOVA Graph API - Comprehensive graph operations and queries
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

class MOVAGraphAPI:
    def __init__(self, db_path: str = "/a0/instruments/custom/iskala/database/mova_graph.db"):
        self.db_path = db_path
        
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def create_node(self, node_type: str, content: str, metadata: Dict = None) -> str:
        """Create a new graph node"""
        node_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata or {})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO graph_nodes (node_id, node_type, content, metadata)
                VALUES (?, ?, ?, ?)
            ''', (node_id, node_type, content, metadata_json))
        
        return node_id
    
    def create_edge(self, source_node: str, target_node: str, 
                   edge_type: str, weight: float = 1.0, metadata: Dict = None) -> int:
        """Create a new graph edge"""
        metadata_json = json.dumps(metadata or {})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO graph_edges (source_node, target_node, edge_type, weight, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_node, target_node, edge_type, weight, metadata_json))
            return cursor.lastrowid
    
    def store_intention(self, intention_text: str, language: str = "uk", 
                       context: Dict = None) -> str:
        """Store an intention and create corresponding graph nodes"""
        intention_hash = str(uuid.uuid4())
        context_json = json.dumps(context or {})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO intentions (intention_text, intention_hash, language, context_data)
                VALUES (?, ?, ?, ?)
            ''', (intention_text, intention_hash, language, context_json))
            
            # Create corresponding graph node
            node_id = self.create_node("intention", intention_text, {
                "hash": intention_hash,
                "language": language,
                "context": context
            })
            
            return intention_hash
    
    def create_tree(self, root_content: str, tree_data: Dict) -> str:
        """Create a new tree structure"""
        tree_id = str(uuid.uuid4())
        
        # Create root node
        root_node = self.create_node("tree_root", root_content, {"tree_id": tree_id})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trees (tree_id, root_node, tree_data)
                VALUES (?, ?, ?)
            ''', (tree_id, root_node, json.dumps(tree_data)))
        
        return tree_id
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT node_id, node_type, content, metadata, created_at
                FROM graph_nodes WHERE node_id = ?
            ''', (node_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "node_id": row[0],
                    "node_type": row[1],
                    "content": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {},
                    "created_at": row[4]
                }
        return None
    
    def get_neighbors(self, node_id: str) -> List[Dict]:
        """Get all neighbors of a node"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT gn.node_id, gn.node_type, gn.content, ge.edge_type, ge.weight
                FROM graph_nodes gn
                JOIN graph_edges ge ON gn.node_id = ge.target_node
                WHERE ge.source_node = ?
                UNION
                SELECT gn.node_id, gn.node_type, gn.content, ge.edge_type, ge.weight
                FROM graph_nodes gn
                JOIN graph_edges ge ON gn.node_id = ge.source_node
                WHERE ge.target_node = ?
            ''', (node_id, node_id))
            
            return [
                {
                    "node_id": row[0],
                    "node_type": row[1],
                    "content": row[2],
                    "edge_type": row[3],
                    "weight": row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def traverse_graph(self, start_node: str, depth: int = 3) -> Dict:
        """Traverse graph from start node"""
        visited = set()
        result = {"nodes": [], "edges": []}
        
        def traverse(node_id: str, current_depth: int):
            if current_depth <= 0 or node_id in visited:
                return
            
            visited.add(node_id)
            node = self.get_node(node_id)
            if node:
                result["nodes"].append(node)
                
                neighbors = self.get_neighbors(node_id)
                for neighbor in neighbors:
                    if neighbor["node_id"] not in visited:
                        result["edges"].append({
                            "source": node_id,
                            "target": neighbor["node_id"],
                            "type": neighbor["edge_type"],
                            "weight": neighbor["weight"]
                        })
                        traverse(neighbor["node_id"], current_depth - 1)
        
        traverse(start_node, depth)
        return result
    
    def search_nodes(self, query: str, node_type: str = None) -> List[Dict]:
        """Search nodes by content"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            sql = '''
                SELECT node_id, node_type, content, metadata, created_at
                FROM graph_nodes
                WHERE content LIKE ?
            '''
            params = [f"%{query}%"]
            
            if node_type:
                sql += " AND node_type = ?"
                params.append(node_type)
            
            cursor.execute(sql, params)
            
            return [
                {
                    "node_id": row[0],
                    "node_type": row[1],
                    "content": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {},
                    "created_at": row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def get_tree(self, tree_id: str) -> Optional[Dict]:
        """Get tree by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tree_id, root_node, tree_data, status, created_at
                FROM trees WHERE tree_id = ?
            ''', (tree_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "tree_id": row[0],
                    "root_node": row[1],
                    "tree_data": json.loads(row[2]) if row[2] else {},
                    "status": row[3],
                    "created_at": row[4]
                }
        return None
    
    def get_all_trees(self) -> List[Dict]:
        """Get all trees"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tree_id, root_node, tree_data, status, created_at
                FROM trees ORDER BY created_at DESC
            ''')
            
            return [
                {
                    "tree_id": row[0],
                    "root_node": row[1],
                    "tree_data": json.loads(row[2]) if row[2] else {},
                    "status": row[3],
                    "created_at": row[4]
                }
                for row in cursor.fetchall()
            ]

# Global API instance
graph_api = MOVAGraphAPI()
