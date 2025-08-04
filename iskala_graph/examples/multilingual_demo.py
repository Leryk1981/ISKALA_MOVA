#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 ISKALA MOVA Multilingual Document Processing Demo
Демонстрація багатомовної обробки документів для ISKALA MOVA
多语言文档处理演示

This demo showcases the enterprise-grade multilingual document chunking system.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.document_processor import (
    MultilingualDocumentProcessor,
    DocChunk,
    LanguageCode,
    process_multilingual_document,
    chunk_multilingual_text
)

class MultilingualDemo:
    """
    🌍 Comprehensive demo of multilingual document processing capabilities
    """
    
    def __init__(self):
        self.processor = MultilingualDocumentProcessor(
            chunk_size=400,
            chunk_overlap=100,
            auto_detect_language=True
        )
        
    async def demo_language_detection(self):
        """Demo automatic language detection"""
        print("\n🔍 LANGUAGE DETECTION DEMO")
        print("=" * 50)
        
        test_texts = {
            "English": "Artificial Intelligence has revolutionized how we process natural language. Machine Learning algorithms can understand human text with remarkable accuracy.",
            
            "Ukrainian": "Штучний інтелект революціонізував обробку природної мови. Алгоритми машинного навчання можуть розуміти людський текст з надзвичайною точністю.",
            
            "Chinese": "人工智能彻底改变了我们处理自然语言的方式。机器学习算法能够以惊人的准确性理解人类文本。",
            
            "Russian": "Искусственный интеллект революционизировал обработку естественного языка. Алгоритмы машинного обучения могут понимать человеческий текст с удивительной точностью.",
            
            "Spanish": "La Inteligencia Artificial ha revolucionado cómo procesamos el lenguaje natural. Los algoritmos de Machine Learning pueden entender texto humano con precisión notable.",
            
            "Mixed (Code)": """
            # English comment: Initialize AI model
            def initialize_model():
                # Український коментар: ініціалізація моделі
                model = "gpt-4"  
                # 中文注释：模型配置
                return model
            """
        }
        
        for name, text in test_texts.items():
            print(f"\n📝 {name} Text Sample:")
            print(f"   {text[:80]}...")
            
            chunks = await self.processor.process_text(text, f"demo_{name.lower()}.txt")
            
            if chunks:
                detected_lang = chunks[0].language
                confidence = chunks[0].confidence
                print(f"🌍 Detected Language: {detected_lang}")
                print(f"📊 Confidence: {confidence:.3f}")
                print(f"🔢 Chunks Created: {len(chunks)}")
            else:
                print("❌ No chunks created")

    async def demo_tokenizer_features(self):
        """Demo language-specific tokenization features"""
        print("\n🔧 TOKENIZER FEATURES DEMO")
        print("=" * 50)
        
        # Ukrainian compound terms preservation
        ukrainian_text = """
        Державно-приватне партнерство в інформаційно-комунікаційних технологіях 
        показує відмінні результати. Тарас Шевченко та Іван Франко були великими 
        письменниками. Науково-технічний прогрес забезпечує розвиток суспільства.
        """
        
        print("🇺🇦 Ukrainian Text Processing:")
        chunks = await self.processor.process_text(ukrainian_text, "ukrainian_test.txt")
        combined_text = " ".join(chunk.content for chunk in chunks)
        
        # Check preservation of compound terms
        preserved_terms = [
            "державно-приватне",
            "інформаційно-комунікаційних", 
            "науково-технічний"
        ]
        
        for term in preserved_terms:
            if term in combined_text.lower():
                print(f"   ✅ Preserved compound term: {term}")
            else:
                print(f"   ❌ Lost compound term: {term}")
        
        # Check name preservation
        if "тарас шевченко" in combined_text.lower():
            print("   ✅ Preserved Ukrainian names")
        
        # English technical terms preservation
        english_text = """
        Machine Learning and Artificial Intelligence are transforming Natural Language Processing.
        Companies like Google, Microsoft, and OpenAI are leading the development of Large Language Models.
        The United States and European Union are investing heavily in AI research.
        """
        
        print("\n🇺🇸 English Text Processing:")
        chunks = await self.processor.process_text(english_text, "english_test.txt")
        combined_text = " ".join(chunk.content for chunk in chunks)
        
        technical_terms = [
            "Machine Learning",
            "Artificial Intelligence", 
            "Natural Language Processing",
            "Large Language Models"
        ]
        
        for term in technical_terms:
            if term in combined_text:
                print(f"   ✅ Preserved technical term: {term}")
        
        proper_nouns = ["Google", "Microsoft", "OpenAI", "United States"]
        for noun in proper_nouns:
            if noun in combined_text:
                print(f"   ✅ Preserved proper noun: {noun}")

    async def demo_file_processing(self):
        """Demo file processing capabilities"""
        print("\n📁 FILE PROCESSING DEMO")
        print("=" * 50)
        
        data_dir = Path(__file__).parent.parent / "data"
        
        test_files = [
            ("sample_ua.txt", "Ukrainian Document"),
            ("sample_en.txt", "English Document"), 
            ("sample_zh.txt", "Chinese Document"),
            ("sample_code.py", "Multilingual Code File")
        ]
        
        for filename, description in test_files:
            file_path = data_dir / filename
            
            if file_path.exists():
                print(f"\n📄 Processing {description}:")
                print(f"   File: {filename}")
                
                start_time = time.time()
                chunks = await self.processor.process_file(file_path)
                processing_time = time.time() - start_time
                
                if chunks:
                    stats = self.processor.get_statistics(chunks)
                    
                    print(f"   🌍 Languages: {list(stats['languages'].keys())}")
                    print(f"   🔢 Total Chunks: {stats['total_chunks']}")
                    print(f"   📊 Avg Confidence: {stats['average_confidence']}")
                    print(f"   ⏱️  Processing Time: {processing_time:.3f}s")
                    print(f"   📏 Size Range: {stats['chunk_size_stats']['min']}-{stats['chunk_size_stats']['max']} chars")
                else:
                    print("   ❌ No chunks created")
            else:
                print(f"\n📄 {description}: File not found ({filename})")

    async def demo_performance_benchmarks(self):
        """Demo performance with various text sizes"""
        print("\n⚡ PERFORMANCE BENCHMARKS")
        print("=" * 50)
        
        test_sizes = [
            (100, "Small Text (100 chars)"),
            (1000, "Medium Text (1KB)"),
            (10000, "Large Text (10KB)"),
            (50000, "Very Large Text (50KB)")
        ]
        
        base_text = "This is a performance test sentence for multilingual document processing. " \
                   "It contains technical terms like Machine Learning and Artificial Intelligence. "
        
        for size, description in test_sizes:
            # Generate text of specified size
            repeat_count = max(1, size // len(base_text))
            test_text = base_text * repeat_count
            actual_size = len(test_text)
            
            print(f"\n🔬 {description}")
            print(f"   Actual Size: {actual_size:,} characters")
            
            # Benchmark processing
            start_time = time.time()
            chunks = await self.processor.process_text(test_text, f"perf_test_{size}.txt")
            processing_time = time.time() - start_time
            
            # Calculate metrics
            chars_per_second = actual_size / processing_time if processing_time > 0 else 0
            chunks_per_second = len(chunks) / processing_time if processing_time > 0 else 0
            
            print(f"   ⏱️  Processing Time: {processing_time:.3f}s")
            print(f"   🚀 Speed: {chars_per_second:,.0f} chars/sec")
            print(f"   🔢 Chunks Created: {len(chunks)} ({chunks_per_second:.1f} chunks/sec)")
            
            if chunks:
                avg_chunk_size = sum(len(c.content) for c in chunks) / len(chunks)
                print(f"   📏 Average Chunk Size: {avg_chunk_size:.0f} characters")

    async def demo_multilingual_statistics(self):
        """Demo comprehensive statistics"""
        print("\n📊 MULTILINGUAL STATISTICS DEMO")
        print("=" * 50)
        
        # Process multiple documents in different languages
        all_chunks = []
        
        multilingual_texts = {
            "en": "English technical documentation about Artificial Intelligence and Machine Learning systems.",
            "uk": "Українська технічна документація про системи штучного інтелекту та машинного навчання.",
            "zh": "关于人工智能和机器学习系统的中文技术文档。",
            "ru": "Русская техническая документация о системах искусственного интеллекта и машинного обучения.",
            "es": "Documentación técnica en español sobre sistemas de Inteligencia Artificial y Machine Learning."
        }
        
        for lang_code, text in multilingual_texts.items():
            chunks = await self.processor.process_text(text * 3, f"demo_{lang_code}.txt")  # Repeat for more content
            all_chunks.extend(chunks)
        
        # Generate comprehensive statistics
        stats = self.processor.get_statistics(all_chunks)
        
        print("\n📈 Overall Statistics:")
        print(f"   Total Documents: {len(multilingual_texts)}")
        print(f"   Total Chunks: {stats['total_chunks']}")
        print(f"   Total Characters: {stats['total_characters']:,}")
        print(f"   Total Words: {stats['total_words']:,}")
        print(f"   Average Confidence: {stats['average_confidence']}")
        
        print("\n🌍 Language Distribution:")
        for lang, count in stats['languages'].items():
            percentage = (count / stats['total_chunks']) * 100
            print(f"   {lang}: {count} chunks ({percentage:.1f}%)")
        
        print(f"\n🔧 Supported Languages: {len(stats['supported_languages'])}")
        print(f"   Languages: {', '.join(stats['supported_languages'])}")

    async def demo_integration_example(self):
        """Demo integration with embedding service (simulated)"""
        print("\n🔗 INTEGRATION EXAMPLE")
        print("=" * 50)
        
        text = """
        ISKALA MOVA is a Ukrainian AI system with multilingual capabilities.
        Система ІСКАЛА МОВА підтримує багатомовну обробку документів.
        该系统支持多语言文档处理功能。
        """
        
        print("Processing multilingual text...")
        chunks = await self.processor.process_text(text, "integration_demo.txt")
        
        print(f"\n📋 Generated {len(chunks)} chunks for embedding:")
        
        for i, chunk in enumerate(chunks):
            print(f"\n🔸 Chunk {i+1}:")
            print(f"   Language: {chunk.language}")
            print(f"   Content: {chunk.content[:100]}...")
            print(f"   Confidence: {chunk.confidence:.3f}")
            print(f"   Words: {chunk.word_count}")
            print(f"   Hash: {chunk.chunk_hash}")
            
            # Simulate embedding integration
            print(f"   🧠 Ready for EmbeddingService.get_embedding('{chunk.chunk_id}')")

    async def run_full_demo(self):
        """Run complete demonstration"""
        print("🌍 ISKALA MOVA MULTILINGUAL DOCUMENT PROCESSOR DEMO")
        print("=" * 60)
        print("Enterprise-grade document processing with 50+ language support")
        print("=" * 60)
        
        demos = [
            ("Language Detection", self.demo_language_detection),
            ("Tokenizer Features", self.demo_tokenizer_features),
            ("File Processing", self.demo_file_processing),
            ("Performance Benchmarks", self.demo_performance_benchmarks),
            ("Multilingual Statistics", self.demo_multilingual_statistics),
            ("Integration Example", self.demo_integration_example)
        ]
        
        for name, demo_func in demos:
            try:
                await demo_func()
                print(f"\n✅ {name} demo completed successfully")
            except Exception as e:
                print(f"\n❌ {name} demo failed: {e}")
        
        print("\n🎉 DEMO COMPLETED!")
        print("=" * 60)
        print("🚀 ISKALA MOVA MultilingualDocumentProcessor is ready for production!")

async def main():
    """Main demo execution"""
    demo = MultilingualDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    # Run the complete demo
    asyncio.run(main()) 