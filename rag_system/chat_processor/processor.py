
import re
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import uuid

class ChatProcessor:
    def __init__(self):
        self.qa_pattern = re.compile(r'(?:User|Користувач|user):\s*(.+?)\n(?:Assistant|AI|assistant):\s*(.+?)(?=\n(?:User|Користувач|user):|$)', re.DOTALL)

    def parse_chat_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse chat file and extract Q&A pairs"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        qa_pairs = []
        matches = self.qa_pattern.findall(content)

        for i, (question, answer) in enumerate(matches):
            qa_pairs.append({
                'id': str(uuid.uuid4()),
                'question': question.strip(),
                'answer': answer.strip(),
                'timestamp': datetime.now().isoformat(),
                'source_file': os.path.basename(file_path),
                'pair_index': i
            })

        return qa_pairs

    def create_meaning_capsule(self, qa_pairs: List[Dict[str, Any]], theme: str = None) -> Dict[str, Any]:
        """Create a meaning capsule from Q&A pairs"""
        capsule = {
            'capsule_id': str(uuid.uuid4()),
            'theme': theme or 'general_conversation',
            'created_at': datetime.now().isoformat(),
            'qa_count': len(qa_pairs),
            'qa_pairs': qa_pairs,
            'semantic_context': self._extract_context(qa_pairs),
            'tags': self._generate_tags(qa_pairs),
            'connections': []
        }
        return capsule

    def _extract_context(self, qa_pairs: List[Dict[str, Any]]) -> str:
        """Extract semantic context from Q&A pairs"""
        contexts = []
        for pair in qa_pairs[:5]:  # Take first 5 pairs for context
            contexts.append(f"Q: {pair['question'][:100]}...")
        return ' '.join(contexts)

    def _generate_tags(self, qa_pairs: List[Dict[str, Any]]) -> List[str]:
        """Generate tags from Q&A content"""
        tags = []
        all_text = ' '.join([f"{p['question']} {p['answer']}" for p in qa_pairs])

        # Simple keyword extraction
        keywords = ['мова', 'кодування', 'алгоритм', 'система', 'інтенція', 'значення', 'граф', 'дерево']
        for keyword in keywords:
            if keyword.lower() in all_text.lower():
                tags.append(keyword)

        return tags[:10]  # Limit to 10 tags
