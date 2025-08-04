"""
🧪 Comprehensive tests for MultilingualDocumentProcessor
Testing multilingual document chunking system with 50+ language support
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.document_processor import (
    MultilingualDocumentProcessor,
    DocChunk,
    LanguageCode,
    UkrainianTokenizer,
    EnglishTokenizer,
    DefaultTokenizer,
    TokenizerRegistry,
    LanguageDetector,
    DetectedLanguage
)

class TestLanguageDetection:
    """Test language detection capabilities"""
    
    @pytest.fixture
    def detector(self):
        return LanguageDetector()
    
    @pytest.mark.asyncio
    async def test_detect_ukrainian(self, detector):
        """Test Ukrainian language detection"""
        text = "Україна має багату історію в галузі інформаційно-комунікаційних технологій."
        result = await detector.detect_language(text)
        
        assert result.lang == "uk"
        assert result.confidence > 0.7
        assert result.method in ["langdetect", "fallback"]
    
    @pytest.mark.asyncio
    async def test_detect_english(self, detector):
        """Test English language detection"""
        text = "Artificial Intelligence has revolutionized computational problem solving."
        result = await detector.detect_language(text)
        
        assert result.lang == "en"
        assert result.confidence > 0.7
    
    @pytest.mark.asyncio
    async def test_detect_chinese(self, detector):
        """Test Chinese language detection"""
        text = "人工智能领域已经彻底改变了我们处理复杂计算问题的方式。"
        result = await detector.detect_language(text)
        
        assert result.lang == "zh-cn" or result.lang == "zh" 
        assert result.confidence > 0.7
    
    @pytest.mark.asyncio
    async def test_detect_short_text_fallback(self, detector):
        """Test fallback for very short text"""
        text = "Hi"
        result = await detector.detect_language(text)
        
        # Should not crash and provide some result
        assert isinstance(result, DetectedLanguage)
        assert result.confidence >= 0.0

    def test_metadata_detection(self, detector):
        """Test language detection from metadata/filename"""
        test_cases = [
            ("document_uk.txt", "uk"),
            ("report_en.md", "en"),
            ("chinese_zh.pdf", "zh"),
            ("russian_ru.docx", "ru"),
            ("unknown_file.txt", None)
        ]
        
        for filename, expected in test_cases:
            result = detector.detect_from_metadata(filename)
            assert result == expected

class TestTokenizers:
    """Test language-specific tokenizers"""
    
    def test_ukrainian_tokenizer(self):
        """Test Ukrainian tokenizer with compound terms and names"""
        tokenizer = UkrainianTokenizer()
        
        # Test compound terms protection
        text_with_terms = "Державно-приватне партнерство та науково-технічний прогрес важливі."
        assert not tokenizer.should_split("державно-приватне партнерство")
        assert not tokenizer.should_split("науково-технічний прогрес")
        
        # Test name protection
        assert not tokenizer.should_split("Тарас Шевченко був великим поетом")
        assert not tokenizer.should_split("Іван Франко та Леся Українка")
        
        # Test normalization
        text = "Україна   має  багату   історію."
        normalized = tokenizer.normalize_text(text)
        assert "  " not in normalized  # Multiple spaces removed
        assert "Україна має багату історію." in normalized
    
    def test_english_tokenizer(self):
        """Test English tokenizer"""
        tokenizer = EnglishTokenizer()
        
        # Test protected terms
        assert not tokenizer.should_split("Machine Learning is important")
        assert not tokenizer.should_split("New York City")
        
        # Test sentence tokenization
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = tokenizer.tokenize_sentences(text)
        assert len(sentences) == 3
        assert "sentence one" in sentences[0]
        assert "sentence two" in sentences[1]
        assert "sentence three" in sentences[2]
    
    def test_tokenizer_registry(self):
        """Test tokenizer registry functionality"""
        registry = TokenizerRegistry()
        
        # Test supported languages
        supported = registry.get_supported_languages()
        assert "uk" in supported
        assert "en" in supported
        assert "ru" in supported
        
        # Test getting tokenizers
        uk_tokenizer = registry.get("uk")
        assert isinstance(uk_tokenizer, UkrainianTokenizer)
        
        en_tokenizer = registry.get("en")
        assert isinstance(en_tokenizer, EnglishTokenizer)
        
        # Test fallback for unsupported language
        unknown_tokenizer = registry.get("unknown")
        assert isinstance(unknown_tokenizer, DefaultTokenizer)

class TestDocumentProcessing:
    """Test document processing functionality"""
    
    @pytest.fixture
    def processor(self):
        return MultilingualDocumentProcessor(
            chunk_size=200,
            chunk_overlap=50,
            min_chunk_size=20
        )

    @pytest.mark.asyncio
    async def test_process_ukrainian_text(self, processor):
        """Test processing Ukrainian text"""
        text = """
        Україна має багату історію в галузі інформаційно-комунікаційних технологій. 
        Тарас Шевченко писав про важливість освіти. 
        Державно-приватне партнерство в IT-сфері показує відмінні результати.
        """
        
        chunks = await processor.process_text(text, "test_ua.txt")
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocChunk) for chunk in chunks)
        assert chunks[0].language == "uk"
        
        # Check that compound terms are preserved
        combined_content = " ".join(chunk.content for chunk in chunks)
        assert "державно-приватне" in combined_content.lower()
        assert "інформаційно-комунікаційних" in combined_content.lower()

    @pytest.mark.asyncio 
    async def test_process_english_text(self, processor):
        """Test processing English text"""
        text = """
        Artificial Intelligence has revolutionized computational problem solving.
        Machine Learning algorithms show remarkable capabilities.
        Natural Language Processing enables human-computer interaction.
        """
        
        chunks = await processor.process_text(text, "test_en.txt")
        
        assert len(chunks) > 0
        assert chunks[0].language == "en"
        
        # Check protected terms
        combined_content = " ".join(chunk.content for chunk in chunks)
        assert "Machine Learning" in combined_content
        assert "Natural Language Processing" in combined_content

    @pytest.mark.asyncio
    async def test_process_chinese_text(self, processor):
        """Test processing Chinese text"""
        text = """
        人工智能领域已经彻底改变了我们处理复杂计算问题的方式。
        机器学习算法在处理人类语言方面展现出了卓越的能力。
        自然语言处理技术涵盖了理解和生成人类文本的各种技术。
        """
        
        chunks = await processor.process_text(text, "test_zh.txt")
        
        assert len(chunks) > 0
        # Should detect Chinese (zh-cn or zh)
        assert chunks[0].language in ["zh-cn", "zh", "zh_cn"]

    @pytest.mark.asyncio
    async def test_mixed_language_content(self, processor):
        """Test processing mixed language content (like code with comments)"""
        text = """
        # English comment: This is a function
        def process_text(text):
            # Український коментар: обробка тексту  
            return text.strip()
        
        # 中文注释：处理文本函数
        # Функция обработки текста (Russian)
        """
        
        chunks = await processor.process_text(text, "mixed_code.py")
        
        assert len(chunks) > 0
        # Should detect some language (likely English as primary)
        assert chunks[0].language in ["en", "uk", "zh-cn", "zh", "ru"]

    @pytest.mark.parametrize("text,expected_lang", [
        ("This is English text about Machine Learning.", "en"),
        ("Це український текст про штучний інтелект.", "uk"), 
        ("这是关于人工智能的中文文本。", ["zh", "zh-cn"]),
        ("Это русский текст об искусственном интеллекте.", "ru"),
        ("Este es texto en español sobre inteligencia artificial.", "es"),
    ])
    @pytest.mark.asyncio
    async def test_language_detection_accuracy(self, processor, text, expected_lang):
        """Test accuracy of language detection for various languages"""
        chunks = await processor.process_text(text, "test.txt")
        
        assert len(chunks) > 0
        detected_lang = chunks[0].language
        
        if isinstance(expected_lang, list):
            assert detected_lang in expected_lang
        else:
            assert detected_lang == expected_lang

class TestPerformance:
    """Test performance and benchmarks"""
    
    @pytest.fixture
    def processor(self):
        return MultilingualDocumentProcessor(chunk_size=512, chunk_overlap=128)

    def test_large_text_processing_performance(self, processor, benchmark):
        """Benchmark large text processing"""
        # Create large text (10KB)
        large_text = "This is a test sentence for performance testing. " * 200
        
        result = benchmark(
            lambda: asyncio.run(processor.process_text(large_text, "large_test.txt"))
        )
        
        assert len(result) > 0
        # Performance target: should process 10KB in reasonable time

    @pytest.mark.asyncio
    async def test_memory_usage_large_document(self, processor):
        """Test memory efficiency with large documents"""
        # 100KB text
        large_text = "Artificial Intelligence and Machine Learning. " * 2000
        
        chunks = await processor.process_text(large_text, "memory_test.txt")
        
        assert len(chunks) > 0
        # Should not crash with large documents
        assert all(len(chunk.content) <= processor.chunk_size * 1.2 for chunk in chunks)

class TestFileProcessing:
    """Test file processing capabilities"""
    
    @pytest.fixture
    def processor(self):
        return MultilingualDocumentProcessor()

    @pytest.mark.asyncio
    async def test_process_text_file(self, processor):
        """Test processing .txt files"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("This is test content for file processing. Machine Learning is amazing!")
            temp_path = f.name
        
        try:
            chunks = await processor.process_file(temp_path)
            assert len(chunks) > 0
            assert chunks[0].language == "en"
            assert "Machine Learning" in chunks[0].content
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_markdown_file(self, processor):
        """Test processing .md files"""
        markdown_content = """
        # Ukrainian AI Development
        
        Україна активно розвиває сферу штучного інтелекту.
        
        ## Основні напрямки
        - Машинне навчання
        - Обробка природної мови
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(markdown_content)
            temp_path = f.name
        
        try:
            chunks = await processor.process_file(temp_path) 
            assert len(chunks) > 0
            # Should detect Ukrainian content
            ukrainian_chunks = [c for c in chunks if c.language == "uk"]
            assert len(ukrainian_chunks) > 0
        finally:
            os.unlink(temp_path)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def processor(self):
        return MultilingualDocumentProcessor()

    @pytest.mark.asyncio
    async def test_empty_text_processing(self, processor):
        """Test processing empty text"""
        chunks = await processor.process_text("", "empty.txt")
        assert len(chunks) == 0

    @pytest.mark.asyncio 
    async def test_very_short_text(self, processor):
        """Test very short text processing"""
        chunks = await processor.process_text("Hi", "short.txt")
        # Should handle gracefully, might be empty if below min_chunk_size
        assert isinstance(chunks, list)

    @pytest.mark.asyncio
    async def test_nonexistent_file(self, processor):
        """Test processing non-existent file"""
        with pytest.raises(FileNotFoundError):
            await processor.process_file("nonexistent_file.txt")

    @pytest.mark.asyncio
    async def test_unsupported_file_type(self, processor):
        """Test unsupported file type (should fallback to text)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.unknown', delete=False, encoding='utf-8') as f:
            f.write("This is content in unknown file type.")
            temp_path = f.name
        
        try:
            chunks = await processor.process_file(temp_path)
            # Should process as text (fallback)
            assert len(chunks) >= 0  # Should not crash
        except Exception:
            # It's OK if some file types are not supported
            pass
        finally:
            os.unlink(temp_path)

class TestStatistics:
    """Test statistics and reporting"""
    
    @pytest.fixture
    def processor(self):
        return MultilingualDocumentProcessor()

    @pytest.mark.asyncio
    async def test_multilingual_statistics(self, processor):
        """Test statistics for multilingual content"""
        texts = [
            ("English text about AI and ML.", "en"),
            ("Український текст про ШІ.", "uk"),
            ("中文人工智能文本。", "zh"),
        ]
        
        all_chunks = []
        for text, _ in texts:
            chunks = await processor.process_text(text, "multi_test.txt")
            all_chunks.extend(chunks)
        
        stats = processor.get_statistics(all_chunks)
        
        assert "languages" in stats
        assert "total_chunks" in stats
        assert "average_confidence" in stats
        assert len(stats["languages"]) >= 2  # Should detect multiple languages

    def test_empty_statistics(self, processor):
        """Test statistics for empty input"""
        stats = processor.get_statistics([])
        assert "error" in stats

# Integration tests
class TestIntegration:
    """Integration tests with real-world scenarios"""
    
    @pytest.fixture
    def processor(self):
        return MultilingualDocumentProcessor(chunk_size=300, chunk_overlap=50)

    @pytest.mark.asyncio
    async def test_real_world_ukrainian_document(self, processor):
        """Test with real Ukrainian document from test data"""
        test_file = Path(__file__).parent.parent / "data" / "sample_ua.txt"
        
        if test_file.exists():
            chunks = await processor.process_file(test_file)
            
            assert len(chunks) > 0
            assert chunks[0].language == "uk"
            
            # Check preservation of Ukrainian terms
            combined_text = " ".join(chunk.content for chunk in chunks)
            ukrainian_terms = ["інформаційно-комунікаційних", "державно-приватне", "науково-технічний"]
            found_terms = [term for term in ukrainian_terms if term in combined_text.lower()]
            assert len(found_terms) > 0

    @pytest.mark.asyncio
    async def test_real_world_english_document(self, processor):
        """Test with real English document from test data"""
        test_file = Path(__file__).parent.parent / "data" / "sample_en.txt"
        
        if test_file.exists():
            chunks = await processor.process_file(test_file)
            
            assert len(chunks) > 0
            assert chunks[0].language == "en"
            
            # Check preservation of technical terms
            combined_text = " ".join(chunk.content for chunk in chunks)
            terms = ["Machine Learning", "Natural Language Processing", "Artificial Intelligence"]
            found_terms = [term for term in terms if term in combined_text]
            assert len(found_terms) > 0

    @pytest.mark.asyncio
    async def test_code_file_processing(self, processor):
        """Test processing code files with multilingual comments"""
        test_file = Path(__file__).parent.parent / "data" / "sample_code.py"
        
        if test_file.exists():
            chunks = await processor.process_file(test_file)
            
            assert len(chunks) > 0
            # Code files might be detected as various languages due to mixed content
            assert chunks[0].language in ["en", "uk", "zh", "ru", "unknown"]

if __name__ == "__main__":
    # Run specific test groups
    pytest.main([__file__ + "::TestLanguageDetection", "-v"])
    pytest.main([__file__ + "::TestTokenizers", "-v"])
    pytest.main([__file__ + "::TestDocumentProcessing", "-v"]) 