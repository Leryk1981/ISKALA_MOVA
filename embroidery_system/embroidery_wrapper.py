#!/usr/bin/env python3
"""
Ukrainian Embroidery Tree Integration
Python wrapper for integrating embroidery system with ISKALA tree
"""

import json
import os
from datetime import datetime

class EmbroideryTreeWrapper:
    def __init__(self, tree_data_path="/a0/instruments/custom/iskala/trees"):
        self.tree_data_path = tree_data_path
        self.embroidery_data = {}
        self.load_data()

    def load_data(self):
        """Load existing embroidery data"""
        embroidery_file = os.path.join(self.tree_data_path, "embroidery_signatures.json")
        if os.path.exists(embroidery_file):
            with open(embroidery_file, 'r', encoding='utf-8') as f:
                self.embroidery_data = json.load(f)

    def save_data(self):
        """Save embroidery data"""
        embroidery_file = os.path.join(self.tree_data_path, "embroidery_signatures.json")
        with open(embroidery_file, 'w', encoding='utf-8') as f:
            json.dump(self.embroidery_data, f, ensure_ascii=False, indent=2)

    def add_signature(self, node_id, signature_data):
        """Add embroidery signature to tree node"""
        signature = {
            'node_id': node_id,
            'text': signature_data.get('text', ''),
            'color_scheme': signature_data.get('color_scheme', 'traditional'),
            'pattern_type': signature_data.get('pattern_type', 'default'),
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }

        self.embroidery_data[node_id] = signature
        self.save_data()

        return signature

    def get_signature(self, node_id):
        """Get embroidery signature for node"""
        return self.embroidery_data.get(node_id)

    def list_signatures(self):
        """List all embroidery signatures"""
        return self.embroidery_data

    def generate_pattern_data(self, text, color_scheme, pattern_type):
        """Generate pattern data for frontend"""
        # This would integrate with the JavaScript generator
        return {
            'text': text,
            'color_scheme': color_scheme,
            'pattern_type': pattern_type,
            'pattern': self.create_pattern(text, pattern_type),
            'colors': self.get_colors(color_scheme)
        }

    def create_pattern(self, text, pattern_type):
        """Create pattern based on text and type"""
        patterns = {
            'мова': [
                [0,1,1,1,0],
                [1,0,1,0,1],
                [1,1,1,1,1],
                [1,0,1,0,1],
                [0,1,1,1,0]
            ],
            'дім': [
                [0,1,1,1,0],
                [1,1,0,1,1],
                [1,0,0,0,1],
                [1,1,1,1,1],
                [1,0,0,0,1]
            ]
        }

        return patterns.get(pattern_type, self.generate_from_text(text))

    def generate_from_text(self, text):
        """Generate pattern from text hash"""
        import hashlib
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()

        pattern = []
        for i in range(5):
            row = []
            for j in range(5):
                index = (i * 5 + j) % len(hash_hex)
                row.append(1 if int(hash_hex[index], 16) > 7 else 0)
            pattern.append(row)

        return pattern

    def get_colors(self, color_scheme):
        """Get color scheme"""
        schemes = {
            'traditional': ['#bd1136', '#1a0709', '#ffffff'],
            'nature': ['#58a34a', '#2fa6c7', '#feca32'],
            'warm': ['#bd1136', '#ff6b35', '#feca32'],
            'cool': ['#2fa6c7', '#58a34a', '#ffffff'],
            'monochrome': ['#1a0709', '#666666', '#cccccc']
        }

        return schemes.get(color_scheme, schemes['traditional'])

    def export_data(self):
        """Export all embroidery data"""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'signatures': self.embroidery_data,
            'total_signatures': len(self.embroidery_data)
        }

    def import_data(self, data):
        """Import embroidery data"""
        if 'signatures' in data:
            self.embroidery_data.update(data['signatures'])
            self.save_data()
            return {'imported': len(data['signatures'])}
        return {'imported': 0}

# Usage example
if __name__ == "__main__":
    wrapper = EmbroideryTreeWrapper()

    # Example usage
    signature = wrapper.add_signature("mova-001", {
        'text': 'створити гармонійний простір',
        'color_scheme': 'traditional',
        'pattern_type': 'мова'
    })

    print("✅ Підпис створено:", signature)
