#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multilingual Code Example for ISKALA MOVA Document Processing
Приклад багатомовного коду для обробки документів ISKALA MOVA
多语言代码示例
"""

import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

# English comment: Configuration settings
CONFIG = {
    "chunk_size": 512,
    "overlap": 128,
    "supported_languages": ["en", "uk", "zh", "ru", "es"]
}

@dataclass
class ProcessingResult:
    """
    Результат обробки документа (Ukrainian comment)
    处理结果数据类 (Chinese comment)
    """
    language: str
    chunks_count: int
    confidence: float
    processing_time: float

class DocumentProcessor:
    """
    Main document processing class
    Основний клас для обробки документів
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Ініціалізація процесора (Ukrainian)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def detect_language(self, text: str) -> str:
        """
        Detect text language automatically
        Автоматичне визначення мови тексту
        自动检测文本语言
        """
        # Simple detection logic (English comment)
        if any(char in text for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            return "ru"  # Russian detected
        elif any(char in text for char in "іїєґ"):
            return "uk"  # Ukrainian detected / Виявлено українську
        elif any(char in text for char in "一二三四五六七八九十"):
            return "zh"  # Chinese detected / 检测到中文
        else:
            return "en"  # Default to English / За замовчуванням англійська
    
    def chunk_text(self, text: str, language: str) -> List[str]:
        """
        Split text into chunks based on language
        Розбиття тексту на чанки залежно від мови
        根据语言将文本分割成块
        """
        # Language-specific separators / Роздільники залежно від мови
        if language == "zh":
            separators = ["。", "！", "？", "；", "，", " "]  # Chinese punctuation
        elif language in ["uk", "ru"]:
            separators = [". ", "! ", "? ", "; ", ", ", " "]  # Cyrillic punctuation  
        else:
            separators = [". ", "! ", "? ", "; ", ", ", " "]  # Default punctuation
        
        chunks = []
        current_chunk = ""
        
        for char in text:
            current_chunk += char
            if char in separators and len(current_chunk) >= self.config["chunk_size"]:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks
    
    async def process_document(self, text: str) -> ProcessingResult:
        """
        Process document with multilingual support  
        Обробка документа з підтримкою багатьох мов
        支持多语言的文档处理
        """
        import time
        start_time = time.time()
        
        # Step 1: Detect language / Крок 1: Визначення мови / 步骤 1：检测语言
        detected_lang = await self.detect_language(text)
        
        # Step 2: Chunk text / Крок 2: Розбиття на чанки / 步骤 2：文本分块
        chunks = self.chunk_text(text, detected_lang)
        
        # Step 3: Calculate confidence / Крок 3: Розрахунок впевненості / 步骤 3：计算置信度
        confidence = len(chunks) * 0.1 if len(chunks) < 10 else 1.0
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            language=detected_lang,
            chunks_count=len(chunks),
            confidence=confidence,
            processing_time=processing_time
        )

# Usage example / Приклад використання / 使用示例
async def main():
    """
    Main function demonstrating multilingual processing
    Головна функція, що демонструє багатомовну обробку  
    演示多语言处理的主函数
    """
    processor = DocumentProcessor(CONFIG)
    
    # Test texts in different languages
    test_texts = {
        "english": "This is a test document in English language.",
        "ukrainian": "Це тестовий документ українською мовою.",
        "chinese": "这是一个中文测试文档。"
    }
    
    for name, text in test_texts.items():
        result = await processor.process_document(text)
        print(f"{name}: {result.language} detected, {result.chunks_count} chunks")
        # Виведення результату (Ukrainian comment)
        # 输出结果 (Chinese comment)

if __name__ == "__main__":
    # Run the example / Запуск прикладу / 运行示例
    asyncio.run(main()) 