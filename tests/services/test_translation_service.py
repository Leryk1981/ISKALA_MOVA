#!/usr/bin/env python3
"""
Unit Tests for Translation Service
Comprehensive test coverage for business logic layer
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from typing import Dict, Any

from iskala_basis.services.translation_service import TranslationService, TranslationServiceError
from iskala_basis.models.translation_models import (
    LanguageCode,
    UserStyle,
    TranslationRequest,
    TranslationResponse,
    UniversalSenseRequest,
    UniversalSenseResponse,
    SupportedLanguagesResponse
)
from iskala_basis.repositories.translation_repository import MockTranslationRepository


class TestTranslationService:
    """Test suite for TranslationService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository for testing"""
        return MockTranslationRepository()
    
    @pytest.fixture
    def translation_service(self, mock_repository):
        """Create TranslationService with mock repository"""
        return TranslationService(mock_repository)
    
    @pytest.fixture
    def valid_translation_request(self):
        """Create valid translation request for testing"""
        return TranslationRequest(
            text="Привіт, як справи?",
            source_lang=LanguageCode.UKRAINIAN,
            target_lang=LanguageCode.ENGLISH,
            user_style=UserStyle.CASUAL,
            user_context={"domain": "greeting"}
        )
    
    @pytest.mark.asyncio
    async def test_translate_success(self, translation_service, valid_translation_request):
        """Test successful translation"""
        result = await translation_service.translate(valid_translation_request)
        
        assert isinstance(result, TranslationResponse)
        assert result.original_text == valid_translation_request.text
        assert result.source_lang == valid_translation_request.source_lang
        assert result.target_lang == valid_translation_request.target_lang
        assert result.translated_text is not None
        assert result.translation_id is not None
        assert isinstance(result.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_translate_same_language_error(self, translation_service):
        """Test translation with same source and target language"""
        request = TranslationRequest(
            text="Hello world",
            source_lang=LanguageCode.ENGLISH,
            target_lang=LanguageCode.ENGLISH,  # Same language
            user_style=UserStyle.NEUTRAL
        )
        
        with pytest.raises(TranslationServiceError) as exc_info:
            await translation_service.translate(request)
        
        assert exc_info.value.error_code == "SAME_LANGUAGE_ERROR"
        assert "cannot be the same" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_translate_empty_text_error(self, translation_service):
        """Test translation with empty text"""
        request = TranslationRequest(
            text="   ",  # Only whitespace
            source_lang=LanguageCode.UKRAINIAN,
            target_lang=LanguageCode.ENGLISH,
            user_style=UserStyle.NEUTRAL
        )
        
        with pytest.raises(TranslationServiceError) as exc_info:
            await translation_service.translate(request)
        
        assert exc_info.value.error_code == "EMPTY_TEXT_ERROR"
    
    @pytest.mark.asyncio
    async def test_translate_text_too_long_error(self, translation_service):
        """Test translation with text exceeding length limit - Pydantic validation"""
        from pydantic import ValidationError
        
        long_text = "a" * 5001  # Exceeds 5000 character limit
        
        # Pydantic should catch this at model validation level
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(
                text=long_text,
                source_lang=LanguageCode.UKRAINIAN,
                target_lang=LanguageCode.ENGLISH,
                user_style=UserStyle.NEUTRAL
            )
        
        assert "string_too_long" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_universal_sense_success(self, translation_service):
        """Test successful universal sense creation"""
        request = UniversalSenseRequest(
            text="Привіт світ",
            source_lang=LanguageCode.UKRAINIAN,
            user_context={"domain": "greeting"}
        )
        
        result = await translation_service.create_universal_sense(request)
        
        assert isinstance(result, UniversalSenseResponse)
        assert result.sense_id is not None
        assert result.universal_payload is not None
        assert result.original_lang == request.source_lang
        assert isinstance(result.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_create_universal_sense_empty_text_error(self, translation_service):
        """Test universal sense creation with empty text - Pydantic validation"""
        from pydantic import ValidationError
        
        # Pydantic should catch this at model validation level
        with pytest.raises(ValidationError) as exc_info:
            UniversalSenseRequest(
                text="",
                source_lang=LanguageCode.UKRAINIAN
            )
        
        assert "string_too_short" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_supported_languages_success(self, translation_service):
        """Test getting supported languages"""
        result = await translation_service.get_supported_languages()
        
        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.languages) > 0
        assert result.total_count == len(result.languages)
        assert LanguageCode.ENGLISH in result.languages
        assert LanguageCode.UKRAINIAN in result.languages
    
    @pytest.mark.asyncio
    async def test_get_language_bubble_success(self, translation_service):
        """Test getting user language bubble"""
        user_id = "test_user_123"
        preferred_lang = LanguageCode.UKRAINIAN
        
        result = await translation_service.get_language_bubble(user_id, preferred_lang)
        
        assert result.user_id == user_id
        assert result.preferred_lang == preferred_lang
        assert len(result.supported_languages) > 0
        assert isinstance(result.translation_history, list)
    
    @pytest.mark.asyncio
    async def test_get_language_bubble_empty_user_id_error(self, translation_service):
        """Test language bubble with empty user ID"""
        with pytest.raises(TranslationServiceError) as exc_info:
            await translation_service.get_language_bubble("", LanguageCode.ENGLISH)
        
        assert exc_info.value.error_code == "INVALID_USER_ID"
    
    @pytest.mark.asyncio
    async def test_get_service_health_success(self, translation_service):
        """Test service health check"""
        # Perform some operations first to generate metrics
        request = TranslationRequest(
            text="Test",
            source_lang=LanguageCode.UKRAINIAN,
            target_lang=LanguageCode.ENGLISH,
            user_style=UserStyle.NEUTRAL
        )
        await translation_service.translate(request)
        
        health = await translation_service.get_service_health()
        
        assert health["status"] == "healthy"
        assert health["service"] == "translation"
        assert "metrics" in health
        assert health["metrics"]["total_translations"] >= 1
        assert "supported_languages_count" in health
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_service_metrics_tracking(self, translation_service, valid_translation_request):
        """Test that service correctly tracks metrics"""
        initial_count = translation_service.translation_count
        
        # Perform translation
        await translation_service.translate(valid_translation_request)
        
        assert translation_service.translation_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_error_count_tracking(self, translation_service):
        """Test that service correctly tracks errors"""
        initial_error_count = translation_service.error_count
        
        # Cause an error
        invalid_request = TranslationRequest(
            text="test",
            source_lang=LanguageCode.ENGLISH,
            target_lang=LanguageCode.ENGLISH  # Same language error
        )
        
        with pytest.raises(TranslationServiceError):
            await translation_service.translate(invalid_request)
        
        assert translation_service.error_count == initial_error_count + 1
    
    def test_translation_service_error_creation(self):
        """Test TranslationServiceError creation"""
        error = TranslationServiceError(
            message="Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"key": "value"}
        assert str(error) == "Test error"
    
    @pytest.mark.asyncio
    async def test_multiple_language_combinations(self, translation_service):
        """Test translation with various language combinations"""
        language_pairs = [
            (LanguageCode.UKRAINIAN, LanguageCode.ENGLISH),
            (LanguageCode.ENGLISH, LanguageCode.GERMAN),
            (LanguageCode.GERMAN, LanguageCode.FRENCH),
            (LanguageCode.FRENCH, LanguageCode.SPANISH)
        ]
        
        for source_lang, target_lang in language_pairs:
            request = TranslationRequest(
                text="Test text",
                source_lang=source_lang,
                target_lang=target_lang,
                user_style=UserStyle.NEUTRAL
            )
            
            result = await translation_service.translate(request)
            assert result.source_lang == source_lang
            assert result.target_lang == target_lang
    
    @pytest.mark.asyncio
    async def test_different_user_styles(self, translation_service):
        """Test translation with different user styles"""
        styles = [UserStyle.NEUTRAL, UserStyle.FORMAL, UserStyle.CASUAL, UserStyle.TECHNICAL]
        
        for style in styles:
            request = TranslationRequest(
                text="Hello world",
                source_lang=LanguageCode.ENGLISH,
                target_lang=LanguageCode.UKRAINIAN,
                user_style=style
            )
            
            result = await translation_service.translate(request)
            assert result.translated_text is not None


# Integration-style tests with real-ish scenarios
class TestTranslationServiceIntegration:
    """Integration-style tests for TranslationService"""
    
    @pytest.fixture
    def translation_service(self):
        """Create service with mock repository for integration tests"""
        mock_repo = MockTranslationRepository()
        return TranslationService(mock_repo)
    
    @pytest.mark.asyncio
    async def test_complete_translation_workflow(self, translation_service):
        """Test complete translation workflow"""
        # 1. Check supported languages
        languages = await translation_service.get_supported_languages()
        assert len(languages.languages) > 0
        
        # 2. Create universal sense
        sense_request = UniversalSenseRequest(
            text="Привіт, як справи?",
            source_lang=LanguageCode.UKRAINIAN,
            user_context={"domain": "greeting"}
        )
        sense = await translation_service.create_universal_sense(sense_request)
        assert sense.sense_id is not None
        
        # 3. Perform translation
        translation_request = TranslationRequest(
            text="Привіт, як справи?",
            source_lang=LanguageCode.UKRAINIAN,
            target_lang=LanguageCode.ENGLISH,
            user_style=UserStyle.CASUAL
        )
        translation = await translation_service.translate(translation_request)
        assert translation.translated_text is not None
        
        # 4. Check health
        health = await translation_service.get_service_health()
        assert health["status"] == "healthy"
        assert health["metrics"]["total_translations"] >= 1


if __name__ == "__main__":
    pytest.main([__file__]) 