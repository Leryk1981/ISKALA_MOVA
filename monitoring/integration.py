"""
MOVA → Graph Integration Layer
Connects MOVA intentions to the graph system
"""

import json
from datetime import datetime
from typing import Dict, Any
from graph_api import graph_api

class MOVAGraphIntegration:
    def __init__(self):
        self.api = graph_api

    def process_mova_intention(self, intention_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MOVA intention and create graph structure"""

        # Extract intention components
        intention_text = intention_data.get('intention', '')
        context = intention_data.get('context', {})
        language = intention_data.get('language', 'uk')

        # Store intention in graph
        intention_hash = self.api.store_intention(
            intention_text=intention_text,
            language=language,
            context=context
        )

        # Create tree structure for the intention
        tree_data = {
            'intention': intention_text,
            'context': context,
            'language': language,
            'created_at': datetime.now().isoformat(),
            'nodes': [],
            'edges': []
        }

        tree_id = self.api.create_tree(intention_text, tree_data)

        # Create semantic nodes
        semantic_nodes = self._create_semantic_nodes(intention_text, context)

        # Create edges between nodes
        self._create_semantic_edges(semantic_nodes)

        return {
            'intention_hash': intention_hash,
            'tree_id': tree_id,
            'semantic_nodes': semantic_nodes,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }

    def _create_semantic_nodes(self, intention: str, context: Dict) -> Dict[str, str]:
        """Create semantic nodes from intention"""
        nodes = {}

        # Create root intention node
        nodes['intention'] = self.api.create_node(
            node_type="mova_intention",
            content=intention,
            metadata={
                'type': 'root',
                'context': context
            }
        )

        # Create context nodes
        for key, value in context.items():
            if isinstance(value, str):
                nodes[f'context_{key}'] = self.api.create_node(
                    node_type="context",
                    content=str(value),
                    metadata={'key': key, 'parent': nodes['intention']}
                )

        return nodes

    def _create_semantic_edges(self, nodes: Dict[str, str]):
        """Create edges between semantic nodes"""
        if 'intention' in nodes:
            for key, node_id in nodes.items():
                if key != 'intention':
                    self.api.create_edge(
                        source_node=nodes['intention'],
                        target_node=node_id,
                        edge_type="has_context",
                        weight=1.0
                    )

    def get_mova_graph(self, intention_hash: str) -> Dict[str, Any]:
        """Get complete MOVA graph for an intention"""

        # Find the intention node
        intention_nodes = self.api.search_nodes(intention_hash, "mova_intention")
        if not intention_nodes:
            return {'error': 'Intention not found'}

        intention_node = intention_nodes[0]

        # Traverse the graph
        graph_data = self.api.traverse_graph(intention_node['node_id'], depth=3)

        return {
            'intention': intention_hash,
            'graph': graph_data,
            'metadata': {
                'node_count': len(graph_data['nodes']),
                'edge_count': len(graph_data['edges']),
                'timestamp': datetime.now().isoformat()
            }
        }

    def update_tree_with_nodes(self, tree_id: str, nodes: List[Dict], edges: List[Dict]):
        """Update tree with new nodes and edges"""
        tree = self.api.get_tree(tree_id)
        if not tree:
            return {'error': 'Tree not found'}

        tree_data = tree['tree_data']
        tree_data['nodes'] = nodes
        tree_data['edges'] = edges
        tree_data['updated_at'] = datetime.now().isoformat()

        return {'status': 'updated', 'tree_id': tree_id}

# Global integration instance
mova_integration = MOVAGraphIntegration()
