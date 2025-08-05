#!/usr/bin/env python3
"""
Translation Repository for ISKALA
Data access layer for translation operations
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from translation.core.translator import ISKALATranslator, UniversalSense
from iskala_basis.models.translation_models import (
    LanguageCode, 
    TranslationRequest, 
    TranslationResponse,
    UniversalSenseResponse
)


class TranslationRepositoryInterface(ABC):
    """Abstract interface for translation repository"""
    
    @abstractmethod
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using the translation engine"""
        pass
    
    @abstractmethod
    async def create_universal_sense(self, text: str, source_lang: LanguageCode, 
                                   context: Optional[Dict[str, Any]] = None) -> UniversalSenseResponse:
        """Create universal sense from text"""
        pass
    
    @abstractmethod
    async def get_cached_translation(self, cache_key: str) -> Optional[str]:
        """Get cached translation if exists"""
        pass
    
    @abstractmethod
    async def cache_translation(self, cache_key: str, translation: str) -> None:
        """Cache translation result"""
        pass
    
    @abstractmethod
    async def get_supported_languages(self) -> List[LanguageCode]:
        """Get list of supported languages"""
        pass


class TranslationRepository(TranslationRepositoryInterface):
    """Concrete implementation of translation repository"""
    
    def __init__(self):
        self.translator = ISKALATranslator()
        self.cache: Dict[str, str] = {}
        self.sense_cache: Dict[str, UniversalSense] = {}
    
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using ISKALA translator"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(
                request.text, 
                request.source_lang, 
                request.target_lang, 
                request.user_style
            )
            
            # Check cache first
            cached_result = await self.get_cached_translation(cache_key)
            if cached_result:
                return TranslationResponse(
                    translated_text=cached_result,
                    original_text=request.text,
                    source_lang=request.source_lang,
                    target_lang=request.target_lang,
                    cached=True,
                    translation_id=cache_key[:8],
                    created_at=datetime.now()
                )
            
            # Create universal sense
            sense = self.translator.create_universal_sense(
                request.text,
                request.source_lang.value,
                request.user_context
            )
            
            # Translate using sense
            translated_text = self.translator.translate_sense(
                sense,
                request.target_lang.value,
                request.user_style.value
            )
            
            # Cache the result
            await self.cache_translation(cache_key, translated_text)
            
            # Store sense for future use
            self.sense_cache[sense.id] = sense
            
            return TranslationResponse(
                translated_text=translated_text,
                original_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                confidence=sense.meta.get("confidence", 0.95),
                cached=False,
                translation_id=sense.id[:8],
                created_at=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    async def create_universal_sense(self, text: str, source_lang: LanguageCode, 
                                   context: Optional[Dict[str, Any]] = None) -> UniversalSenseResponse:
        """Create universal sense from text"""
        try:
            sense = self.translator.create_universal_sense(
                text,
                source_lang.value,
                context
            )
            
            # Cache the sense
            self.sense_cache[sense.id] = sense
            
            return UniversalSenseResponse(
                sense_id=sense.id,
                universal_payload=sense.payload,
                original_lang=source_lang,
                created_at=datetime.fromisoformat(sense.created_at),
                meta=sense.meta
            )
            
        except Exception as e:
            raise Exception(f"Universal sense creation failed: {str(e)}")
    
    async def get_cached_translation(self, cache_key: str) -> Optional[str]:
        """Get cached translation if exists"""
        return self.cache.get(cache_key)
    
    async def cache_translation(self, cache_key: str, translation: str) -> None:
        """Cache translation result"""
        self.cache[cache_key] = translation
    
    async def get_supported_languages(self) -> List[LanguageCode]:
        """Get list of supported languages"""
        return [LanguageCode(lang) for lang in self.translator.supported_languages]
    
    async def get_user_language_bubble(self, user_id: str, preferred_lang: LanguageCode) -> Dict[str, Any]:
        """Get user's language bubble configuration"""
        return self.translator.get_user_language_bubble(user_id, preferred_lang.value)
    
    def _generate_cache_key(self, text: str, source_lang: LanguageCode, 
                          target_lang: LanguageCode, user_style: str) -> str:
        """Generate cache key for translation"""
        content = f"{text}_{source_lang.value}_{target_lang.value}_{user_style}"
        return hashlib.md5(content.encode()).hexdigest()


class MockTranslationRepository(TranslationRepositoryInterface):
    """Mock implementation for testing"""
    
    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.supported_langs = [lang for lang in LanguageCode]
    
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """Mock translation - returns reversed text"""
        translated = f"[MOCK] {request.text[::-1]}"
        
        return TranslationResponse(
            translated_text=translated,
            original_text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            cached=False,
            translation_id="mock123",
            created_at=datetime.now()
        )
    
    async def create_universal_sense(self, text: str, source_lang: LanguageCode, 
                                   context: Optional[Dict[str, Any]] = None) -> UniversalSenseResponse:
        """Mock universal sense creation"""
        sense_id = hashlib.md5(f"{text}{source_lang.value}".encode()).hexdigest()
        
        return UniversalSenseResponse(
            sense_id=sense_id,
            universal_payload=f"[UNIVERSAL] {text}",
            original_lang=source_lang,
            created_at=datetime.now(),
            meta={"mock": True}
        )
    
    async def get_cached_translation(self, cache_key: str) -> Optional[str]:
        """Mock cache lookup"""
        return self.cache.get(cache_key)
    
    async def cache_translation(self, cache_key: str, translation: str) -> None:
        """Mock cache storage"""
        self.cache[cache_key] = translation
    
    async def get_supported_languages(self) -> List[LanguageCode]:
        """Mock supported languages"""
        return self.supported_langs 