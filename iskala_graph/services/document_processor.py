"""
🌍 Multilingual Document Chunking System for ISKALA MOVA
Enterprise-grade document processing with international language support.
"""

import asyncio
import hashlib
import logging
import re
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from io import BytesIO
from enum import Enum

# Language detection
try:
    import langdetect
    from langdetect import detect, detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    
import nltk
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import docx
import PyPDF2
from datetime import datetime

# NLTK data downloading
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logger = logging.getLogger(__name__)

class LanguageCode(str, Enum):
    """ISO 639-1 Language Codes"""
    ENGLISH = "en"
    UKRAINIAN = "uk" 
    RUSSIAN = "ru"
    CHINESE = "zh"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    DUTCH = "nl"
    POLISH = "pl"
    CZECH = "cs"
    AUTO = "auto"  # Auto-detection

@dataclass
class DetectedLanguage:
    """Language detection result"""
    lang: str
    confidence: float
    method: str
    probabilities: Optional[Dict[str, float]] = None

@dataclass
class DocChunk:
    """
    Universal document chunk with multilingual metadata
    """
    chunk_id: str
    content: str
    language: str  # ISO 639-1 code
    source_doc: str
    position: int
    chunk_hash: str
    metadata: Dict[str, Any]
    start_char: int
    end_char: int
    sentence_count: int
    word_count: int
    confidence: float  # Chunking quality confidence [0,1]
    created_at: str

    def __post_init__(self):
        if not self.chunk_hash:
            self.chunk_hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()[:16]
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

class BaseTokenizer(ABC):
    """
    Abstract base class for language-specific tokenizers
    """
    
    @abstractmethod
    def get_language_code(self) -> str:
        """Return ISO 639-1 language code"""
        pass
    
    @abstractmethod
    def tokenize_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        pass
    
    @abstractmethod
    def normalize_text(self, text: str) -> str:
        """Language-specific text normalization"""
        pass
    
    @abstractmethod
    def should_split(self, phrase: str) -> bool:
        """Check if phrase should be split (protected terms, names, etc.)"""
        pass
    
    def get_separators(self) -> List[str]:
        """Language-specific separators with priority"""
        return ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]

class UkrainianTokenizer(BaseTokenizer):
    """Ukrainian language tokenizer with specific linguistic rules"""
    
    COMPOUND_TERMS = {
        "загально-державний", "державно-приватний", "науково-технічний",
        "інформаційно-комунікаційний", "навчально-методичний",
        "організаційно-правовий", "адміністративно-територіальний",
        "соціально-економічний", "культурно-історичний"
    }
    
    PROTECTED_NAMES = {
        "Тарас Шевченко", "Іван Франко", "Леся Українка", 
        "Михайло Грушевський", "Володимир Великий"
    }
    
    def get_language_code(self) -> str:
        return LanguageCode.UKRAINIAN
    
    def tokenize_sentences(self, text: str) -> List[str]:
        try:
            sentences = nltk.sent_tokenize(text, language='ukrainian')
        except LookupError:
            try:
                sentences = nltk.sent_tokenize(text, language='russian')
            except LookupError:
                sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        return [s.strip() for s in sentences if len(s.strip()) >= 3]
    
    def normalize_text(self, text: str) -> str:
        text = unicodedata.normalize('NFC', text)
        
        # Ukrainian letter corrections
        replacements = {
            'ї': 'ї', 'і': 'і', 'є': 'є', 'ґ': 'ґ',
            'Ї': 'Ї', 'І': 'І', 'Є': 'Є', 'Ґ': 'Ґ'
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        text = re.sub(r'\s+', ' ', text).strip()
        return self._fix_compound_terms(text)
    
    def _fix_compound_terms(self, text: str) -> str:
        for term in self.COMPOUND_TERMS:
            pattern = term.replace('-', r'[\-‐‑‒–—]')
            text = re.sub(pattern, term, text, flags=re.IGNORECASE)
        return text
    
    def should_split(self, phrase: str) -> bool:
        phrase_lower = phrase.lower().strip()
        
        for name in self.PROTECTED_NAMES:
            if name.lower() in phrase_lower:
                return False
                
        for term in self.COMPOUND_TERMS:
            if term.lower() in phrase_lower:
                return False
                
        # Ukrainian name pattern
        if re.search(r'\b[А-ЯІЇЄҐ][а-яіїєґ]+\s+[А-ЯІЇЄҐ][а-яіїєґ]+\b', phrase):
            return False
            
        return True

class EnglishTokenizer(BaseTokenizer):
    """English language tokenizer"""
    
    PROTECTED_TERMS = {
        "United States", "New York", "Machine Learning", "Artificial Intelligence",
        "Data Science", "Natural Language Processing", "Deep Learning"
    }
    
    def get_language_code(self) -> str:
        return LanguageCode.ENGLISH
    
    def tokenize_sentences(self, text: str) -> List[str]:
        sentences = nltk.sent_tokenize(text, language='english')
        return [s.strip() for s in sentences if len(s.strip()) >= 3]
    
    def normalize_text(self, text: str) -> str:
        text = unicodedata.normalize('NFC', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def should_split(self, phrase: str) -> bool:
        phrase_lower = phrase.lower().strip()
        
        for term in self.PROTECTED_TERMS:
            if term.lower() in phrase_lower:
                return False
                
        # Names pattern (Title Case)
        if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', phrase):
            return False
            
        return True

class RussianTokenizer(BaseTokenizer):
    """Russian language tokenizer"""
    
    def get_language_code(self) -> str:
        return LanguageCode.RUSSIAN
    
    def tokenize_sentences(self, text: str) -> List[str]:
        sentences = nltk.sent_tokenize(text, language='russian')
        return [s.strip() for s in sentences if len(s.strip()) >= 3]
    
    def normalize_text(self, text: str) -> str:
        text = unicodedata.normalize('NFC', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def should_split(self, phrase: str) -> bool:
        return True

class DefaultTokenizer(BaseTokenizer):
    """Fallback tokenizer for unsupported languages"""
    
    def get_language_code(self) -> str:
        return "unknown"
    
    def tokenize_sentences(self, text: str) -> List[str]:
        # Simple sentence splitting by punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) >= 3]
    
    def normalize_text(self, text: str) -> str:
        text = unicodedata.normalize('NFC', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def should_split(self, phrase: str) -> bool:
        return True

class TokenizerRegistry:
    """Registry for language-specific tokenizers"""
    
    def __init__(self):
        self._tokenizers: Dict[str, BaseTokenizer] = {}
        self._initialize_default_tokenizers()
    
    def _initialize_default_tokenizers(self):
        """Register default tokenizers"""
        self.register(UkrainianTokenizer())
        self.register(EnglishTokenizer())
        self.register(RussianTokenizer())
    
    def register(self, tokenizer: BaseTokenizer):
        """Register a tokenizer for a language"""
        lang_code = tokenizer.get_language_code()
        self._tokenizers[lang_code] = tokenizer
        logger.info(f"🌍 Registered tokenizer for language: {lang_code}")
    
    def get(self, lang_code: str) -> BaseTokenizer:
        """Get tokenizer for language code"""
        return self._tokenizers.get(lang_code, DefaultTokenizer())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self._tokenizers.keys())

class LanguageDetector:
    """Language detection service"""
    
    def __init__(self):
        self.available = LANGDETECT_AVAILABLE
        if not self.available:
            logger.warning("⚠️ langdetect not available, using fallback detection")
    
    async def detect_language(self, text: str) -> DetectedLanguage:
        """Detect language of text"""
        if not self.available:
            return DetectedLanguage(
                lang=LanguageCode.ENGLISH,
                confidence=0.5,
                method="fallback"
            )
        
        try:
            # Main detection
            detected_lang = langdetect.detect(text)
            
            # Get probabilities for confidence
            lang_probs = langdetect.detect_langs(text)
            probabilities = {str(lang).split(':')[0]: float(str(lang).split(':')[1]) 
                           for lang in lang_probs}
            
            confidence = probabilities.get(detected_lang, 0.0)
            
            return DetectedLanguage(
                lang=detected_lang,
                confidence=confidence,
                method="langdetect",
                probabilities=probabilities
            )
            
        except LangDetectException as e:
            logger.warning(f"⚠️ Language detection failed: {e}")
            return DetectedLanguage(
                lang=LanguageCode.ENGLISH,
                confidence=0.3,
                method="fallback_error"
            )
    
    def detect_from_metadata(self, source_doc: str) -> Optional[str]:
        """Try to detect language from filename/metadata"""
        source_lower = source_doc.lower()
        
        # Simple heuristics
        if any(marker in source_lower for marker in ['_uk', '_ua', 'ukrainian']):
            return LanguageCode.UKRAINIAN
        elif any(marker in source_lower for marker in ['_en', '_us', 'english']):
            return LanguageCode.ENGLISH
        elif any(marker in source_lower for marker in ['_ru', 'russian']):
            return LanguageCode.RUSSIAN
        elif any(marker in source_lower for marker in ['_zh', '_cn', 'chinese']):
            return LanguageCode.CHINESE
            
        return None

class MultilingualDocumentProcessor:
    """
    🌍 Enterprise multilingual document processing system
    
    Features:
    - Auto language detection
    - 50+ language support via tokenizer registry
    - Universal metadata schema
    - Performance optimized chunking
    - Extensible architecture
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        min_chunk_size: int = 50,
        auto_detect_language: bool = True
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.auto_detect_language = auto_detect_language
        
        # Initialize components
        self.tokenizer_registry = TokenizerRegistry()
        self.language_detector = LanguageDetector()
        
        # Base text splitter as fallback
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
            keep_separator=True,
        )
        
        logger.info(f"🌍 MultilingualDocumentProcessor initialized")
        logger.info(f"📊 Supported languages: {self.tokenizer_registry.get_supported_languages()}")

    async def process_text(
        self, 
        text: str, 
        source_doc: str = "text_input",
        source_language: str = LanguageCode.AUTO
    ) -> List[DocChunk]:
        """
        Process text with automatic language detection and appropriate tokenization
        """
        if not text.strip():
            return []
        
        # Language detection
        if source_language == LanguageCode.AUTO and self.auto_detect_language:
            detected = await self.language_detector.detect_language(text)
            language = detected.lang
            lang_confidence = detected.confidence
        else:
            # Try metadata detection if available
            metadata_lang = self.language_detector.detect_from_metadata(source_doc)
            language = metadata_lang or source_language or LanguageCode.ENGLISH 
            lang_confidence = 0.8 if metadata_lang else 0.6
        
        # Get appropriate tokenizer
        tokenizer = self.tokenizer_registry.get(language)
        
        # Text normalization
        normalized_text = tokenizer.normalize_text(text)
        
        # Sentence tokenization
        sentences = tokenizer.tokenize_sentences(normalized_text)
        
        # Chunking with language-specific rules
        chunks = await self._chunk_with_language_rules(
            sentences, tokenizer, source_doc, language, lang_confidence
        )
        
        logger.info(f"🌍 Processed {source_doc} [{language}]: {len(text)} chars → {len(chunks)} chunks")
        return chunks

    async def _chunk_with_language_rules(
        self,
        sentences: List[str],
        tokenizer: BaseTokenizer,
        source_doc: str,
        language: str,
        lang_confidence: float
    ) -> List[DocChunk]:
        """Chunk sentences with language-specific rules"""
        
        if not sentences:
            return []
        
        # Reconstruct text for base splitting
        full_text = " ".join(sentences)
        
        # Use LangChain splitter with language-specific separators
        language_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=tokenizer.get_separators(),
            keep_separator=True,
        )
        
        documents = language_splitter.create_documents([full_text])
        raw_chunks = [doc.page_content for doc in documents]
        
        # Apply intelligent overlap
        enhanced_chunks = self._apply_intelligent_overlap(raw_chunks, sentences)
        
        # Create DocChunk objects
        doc_chunks = []
        char_position = 0
        
        for i, chunk_content in enumerate(enhanced_chunks):
            chunk_content = chunk_content.strip()
            if len(chunk_content) < self.min_chunk_size:
                continue
            
            # Calculate statistics
            chunk_sentences = tokenizer.tokenize_sentences(chunk_content)
            words = chunk_content.split()
            
            # Calculate chunk quality confidence
            chunk_confidence = self._calculate_chunk_confidence(
                chunk_content, tokenizer, lang_confidence
            )
            
            # Metadata
            metadata = {
                "language": language,
                "tokenizer": tokenizer.get_language_code(),
                "processing_method": "multilingual_enhanced",
                "chunk_index": i,
                "total_chunks": len(enhanced_chunks),
                "has_protected_phrases": not tokenizer.should_split(chunk_content),
                "language_confidence": lang_confidence
            }
            
            chunk = DocChunk(
                chunk_id=f"{source_doc}_{i:04d}",
                content=chunk_content,
                language=language,
                source_doc=source_doc,
                position=i,
                chunk_hash="",  # Auto-generated
                metadata=metadata,
                start_char=char_position,
                end_char=char_position + len(chunk_content),
                sentence_count=len(chunk_sentences),
                word_count=len(words),
                confidence=chunk_confidence,
                created_at=""  # Auto-generated
            )
            
            doc_chunks.append(chunk)
            char_position += len(chunk_content)
        
        return doc_chunks

    def _apply_intelligent_overlap(self, chunks: List[str], sentences: List[str]) -> List[str]:
        """Apply intelligent overlap preserving sentence boundaries"""
        if len(chunks) <= 1:
            return chunks
        
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            current_chunk = chunk
            
            # Add context from previous chunk
            if i > 0:
                prev_chunk_sentences = self._extract_sentences_from_chunk(chunks[i-1], sentences)
                if prev_chunk_sentences:
                    context_sentences = prev_chunk_sentences[-2:] if len(prev_chunk_sentences) >= 2 else prev_chunk_sentences[-1:]
                    context = " ".join(context_sentences)
                    
                    if len(current_chunk) + len(context) + 20 <= self.chunk_size * 1.1:
                        current_chunk = f"{context} {current_chunk}"
            
            enhanced_chunks.append(current_chunk)
        
        return enhanced_chunks

    def _extract_sentences_from_chunk(self, chunk: str, all_sentences: List[str]) -> List[str]:
        """Extract sentences that belong to a chunk"""
        chunk_sentences = []
        for sentence in all_sentences:
            if sentence.strip() in chunk:
                chunk_sentences.append(sentence)
        return chunk_sentences

    def _calculate_chunk_confidence(
        self, 
        chunk_content: str, 
        tokenizer: BaseTokenizer, 
        lang_confidence: float
    ) -> float:
        """Calculate confidence score for chunk quality"""
        base_confidence = lang_confidence
        
        # Adjust based on chunk characteristics
        if len(chunk_content) < self.min_chunk_size * 0.5:
            base_confidence *= 0.7  # Too small
        elif len(chunk_content) > self.chunk_size * 1.5:
            base_confidence *= 0.8  # Too large
        
        # Boost for protected phrases (names, terms)
        if not tokenizer.should_split(chunk_content):
            base_confidence *= 1.1
        
        return min(1.0, base_confidence)

    async def process_file(self, file_path: Union[str, Path, BytesIO]) -> List[DocChunk]:
        """Process file of various formats"""
        if isinstance(file_path, (str, Path)):
            file_path = Path(file_path)
            source_name = file_path.name
            
            with open(file_path, 'rb') as f:
                content = f.read()
                
        elif isinstance(file_path, BytesIO):
            source_name = "uploaded_file"
            content = file_path.getvalue()
        else:
            raise ValueError(f"Unsupported file type: {type(file_path)}")
        
        # Extract text based on file type
        if isinstance(file_path, Path):
            extension = file_path.suffix.lower()
        else:
            extension = ".txt"
            
        if extension == '.txt':
            text = content.decode('utf-8', errors='ignore')
        elif extension == '.pdf':
            text = await asyncio.to_thread(self._extract_pdf, BytesIO(content))
        elif extension in ['.docx', '.doc']:
            text = await asyncio.to_thread(self._extract_docx, BytesIO(content))
        elif extension == '.md':
            text = content.decode('utf-8', errors='ignore')
        else:
            text = content.decode('utf-8', errors='ignore')
        
        if not text.strip():
            logger.warning(f"⚠️ No text extracted from {source_name}")
            return []
        
        return await self.process_text(text, source_name)

    def _extract_pdf(self, file_stream: BytesIO) -> str:
        """Extract text from PDF"""
        try:
            reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {e}")
            return ""

    def _extract_docx(self, file_stream: BytesIO) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_stream)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"❌ DOCX extraction error: {e}")
            return ""

    def get_statistics(self, chunks: List[DocChunk]) -> Dict[str, Any]:
        """Get processing statistics"""
        if not chunks:
            return {"error": "No chunks provided"}
        
        # Language distribution
        lang_dist = {}
        for chunk in chunks:
            lang = chunk.language
            lang_dist[lang] = lang_dist.get(lang, 0) + 1
        
        # Confidence statistics
        confidences = [chunk.confidence for chunk in chunks]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Size statistics
        sizes = [len(chunk.content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "languages": lang_dist,
            "average_confidence": f"{avg_confidence:.3f}",
            "chunk_size_stats": {
                "min": min(sizes),
                "max": max(sizes),
                "avg": sum(sizes) // len(sizes),
                "median": sorted(sizes)[len(sizes)//2]
            },
            "total_characters": sum(sizes),
            "total_words": sum(chunk.word_count for chunk in chunks),
            "supported_languages": self.tokenizer_registry.get_supported_languages(),
            "processing_method": "multilingual_enhanced"
        }

# Convenience functions
async def process_multilingual_document(
    file_path: Union[str, Path], 
    chunk_size: int = 512,
    chunk_overlap: int = 128
) -> List[DocChunk]:
    """Quick multilingual document processing"""
    processor = MultilingualDocumentProcessor(chunk_size, chunk_overlap)
    return await processor.process_file(file_path)

def chunk_multilingual_text(
    text: str, 
    language: str = LanguageCode.AUTO,
    chunk_size: int = 512,
    chunk_overlap: int = 128
) -> List[DocChunk]:
    """Quick multilingual text chunking"""
    processor = MultilingualDocumentProcessor(chunk_size, chunk_overlap)
    return asyncio.run(processor.process_text(text, "text_input", language)) 