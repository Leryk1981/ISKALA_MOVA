#!/usr/bin/env python3
"""
Translation Models for ISKALA
Pydantic models for translation service layer
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes"""
    UKRAINIAN = "uk"
    ENGLISH = "en" 
    GERMAN = "de"
    POLISH = "pl"
    RUSSIAN = "ru"
    FRENCH = "fr"
    SPANISH = "es"


class UserStyle(str, Enum):
    """Translation style options"""
    NEUTRAL = "neutral"
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"


class TranslationRequest(BaseModel):
    """Request model for translation"""
    text: str = Field(min_length=1, max_length=5000, description="Text to translate")
    source_lang: LanguageCode = Field(description="Source language code")
    target_lang: LanguageCode = Field(description="Target language code")
    user_style: UserStyle = UserStyle.NEUTRAL
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Привіт, як справи?",
                "source_lang": "uk",
                "target_lang": "en",
                "user_style": "casual",
                "user_context": {"domain": "greeting"}
            }
        }
    }


class TranslationResponse(BaseModel):
    """Response model for translation"""
    translated_text: str = Field(description="Translated text")
    original_text: str = Field(description="Original input text")
    source_lang: LanguageCode = Field(description="Source language")
    target_lang: LanguageCode = Field(description="Target language")
    confidence: float = Field(ge=0.0, le=1.0, default=0.95, description="Translation confidence score")
    cached: bool = Field(default=False, description="Whether result was cached")
    translation_id: str = Field(description="Unique translation identifier")
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {
        "json_schema_extra": {
            "example": {
                "translated_text": "Hello, how are you?",
                "original_text": "Привіт, як справи?",
                "source_lang": "uk",
                "target_lang": "en",
                "confidence": 0.95,
                "cached": False,
                "translation_id": "abc123",
                "created_at": "2025-08-05T11:20:00"
            }
        }
    }


class UniversalSenseRequest(BaseModel):
    """Request model for creating universal sense"""
    text: str = Field(min_length=1, max_length=5000)
    source_lang: LanguageCode
    user_context: Optional[Dict[str, Any]] = None


class UniversalSenseResponse(BaseModel):
    """Response model for universal sense"""
    sense_id: str = Field(description="Unique sense identifier")
    universal_payload: str = Field(description="Language-agnostic content representation")
    original_lang: LanguageCode = Field(description="Original language")
    created_at: datetime = Field(default_factory=datetime.now)
    meta: Dict[str, Any] = Field(default_factory=dict)


class LanguageBubbleResponse(BaseModel):
    """Response model for user language bubble"""
    user_id: str
    preferred_lang: LanguageCode
    supported_languages: List[LanguageCode]
    translation_history: List[Dict[str, Any]] = Field(default_factory=list)


class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages"""
    languages: List[LanguageCode] = Field(description="List of supported language codes")
    total_count: int = Field(description="Total number of supported languages")

    model_config = {
        "json_schema_extra": {
            "example": {
                "languages": ["uk", "en", "de", "pl", "ru", "fr", "es"],
                "total_count": 7
            }
        }
    }


class TranslationError(BaseModel):
    """Error model for translation failures"""
    error_code: str = Field(description="Error code identifier")
    error_message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now) 