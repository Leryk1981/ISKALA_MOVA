#!/usr/bin/env python3
"""
Translation Service for ISKALA
Business logic layer for translation operations
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from iskala_basis.models.translation_models import (
    LanguageCode,
    UserStyle,
    TranslationRequest,
    TranslationResponse,
    UniversalSenseRequest,
    UniversalSenseResponse,
    LanguageBubbleResponse,
    SupportedLanguagesResponse,
    TranslationError
)
from iskala_basis.repositories.translation_repository import TranslationRepositoryInterface


# Configure logging
logger = logging.getLogger(__name__)


class TranslationServiceError(Exception):
    """Custom exception for translation service errors"""
    
    def __init__(self, message: str, error_code: str = "TRANSLATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class TranslationService:
    """
    Translation Service - Business Logic Layer
    
    Handles all translation operations with:
    - Input validation
    - Business rules enforcement
    - Error handling and logging
    - Performance monitoring
    - Caching strategy
    """
    
    def __init__(self, repository: TranslationRepositoryInterface):
        self.repository = repository
        self.logger = logger
        
        # Performance metrics
        self.translation_count = 0
        self.cache_hits = 0
        self.error_count = 0
    
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """
        Main translation method with full business logic
        
        Args:
            request: Translation request with validated data
            
        Returns:
            TranslationResponse: Complete translation result
            
        Raises:
            TranslationServiceError: For business logic violations
        """
        start_time = datetime.now()
        
        try:
            # Business rule validation
            await self._validate_translation_request(request)
            
            # Log translation attempt
            self.logger.info(
                f"Translation request: {request.source_lang} -> {request.target_lang}, "
                f"text_length: {len(request.text)}, style: {request.user_style}"
            )
            
            # Perform translation through repository
            result = await self.repository.translate_text(request)
            
            # Update metrics
            self.translation_count += 1
            if result.cached:
                self.cache_hits += 1
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"Translation completed: {result.translation_id}, "
                f"cached: {result.cached}, time: {processing_time:.3f}s"
            )
            
            return result
            
        except TranslationServiceError:
            # Re-raise service errors without wrapping
            self.error_count += 1
            raise
        except Exception as e:
            self.error_count += 1
            error_msg = f"Translation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise TranslationServiceError(
                message=error_msg,
                error_code="TRANSLATION_FAILED",
                details={
                    "source_lang": request.source_lang.value,
                    "target_lang": request.target_lang.value,
                    "text_length": len(request.text),
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            )
    
    async def create_universal_sense(self, request: UniversalSenseRequest) -> UniversalSenseResponse:
        """
        Create universal sense with business validation
        
        Args:
            request: Universal sense creation request
            
        Returns:
            UniversalSenseResponse: Created universal sense
        """
        try:
            # Validate request
            if not request.text.strip():
                raise TranslationServiceError(
                    "Empty text cannot be converted to universal sense",
                    "INVALID_INPUT"
                )
            
            self.logger.info(f"Creating universal sense: lang={request.source_lang}, length={len(request.text)}")
            
            # Create through repository
            result = await self.repository.create_universal_sense(
                request.text,
                request.source_lang,
                request.user_context
            )
            
            self.logger.info(f"Universal sense created: {result.sense_id}")
            return result
            
        except Exception as e:
            error_msg = f"Universal sense creation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise TranslationServiceError(
                message=error_msg,
                error_code="SENSE_CREATION_FAILED",
                details={"source_lang": request.source_lang.value}
            )
    
    async def get_supported_languages(self) -> SupportedLanguagesResponse:
        """
        Get supported languages with metadata
        
        Returns:
            SupportedLanguagesResponse: List of supported languages
        """
        try:
            languages = await self.repository.get_supported_languages()
            
            return SupportedLanguagesResponse(
                languages=languages,
                total_count=len(languages)
            )
            
        except Exception as e:
            error_msg = f"Failed to get supported languages: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise TranslationServiceError(
                message=error_msg,
                error_code="LANGUAGES_FETCH_FAILED"
            )
    
    async def get_language_bubble(self, user_id: str, preferred_lang: LanguageCode) -> LanguageBubbleResponse:
        """
        Get user's language bubble configuration
        
        Args:
            user_id: User identifier
            preferred_lang: User's preferred language
            
        Returns:
            LanguageBubbleResponse: User's language configuration
        """
        try:
            # Validate inputs
            if not user_id.strip():
                raise TranslationServiceError(
                    "User ID cannot be empty",
                    "INVALID_USER_ID"
                )
            
            # Get bubble data through repository
            if hasattr(self.repository, 'get_user_language_bubble'):
                bubble_data = await self.repository.get_user_language_bubble(user_id, preferred_lang)
            else:
                # Fallback for basic implementation
                bubble_data = {
                    "user_id": user_id,
                    "preferred_lang": preferred_lang.value,
                    "supported_languages": [lang.value for lang in await self.repository.get_supported_languages()],
                    "translation_history": []
                }
            
            return LanguageBubbleResponse(
                user_id=user_id,
                preferred_lang=preferred_lang,
                supported_languages=await self.repository.get_supported_languages(),
                translation_history=bubble_data.get("translation_history", [])
            )
            
        except TranslationServiceError:
            # Re-raise service errors without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to get language bubble for user {user_id}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise TranslationServiceError(
                message=error_msg,
                error_code="LANGUAGE_BUBBLE_FAILED",
                details={"user_id": user_id, "preferred_lang": preferred_lang.value}
            )
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get service health metrics
        
        Returns:
            Dict with service health information
        """
        try:
            supported_languages = await self.repository.get_supported_languages()
            
            return {
                "status": "healthy",
                "service": "translation",
                "metrics": {
                    "total_translations": self.translation_count,
                    "cache_hits": self.cache_hits,
                    "cache_hit_ratio": self.cache_hits / max(self.translation_count, 1),
                    "error_count": self.error_count,
                    "error_rate": self.error_count / max(self.translation_count, 1)
                },
                "supported_languages_count": len(supported_languages),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return {
                "status": "unhealthy",
                "service": "translation",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _validate_translation_request(self, request: TranslationRequest) -> None:
        """
        Validate translation request business rules
        
        Args:
            request: Translation request to validate
            
        Raises:
            TranslationServiceError: For validation failures
        """
        # Check if source and target languages are the same
        if request.source_lang == request.target_lang:
            raise TranslationServiceError(
                "Source and target languages cannot be the same",
                "SAME_LANGUAGE_ERROR",
                {
                    "source_lang": request.source_lang.value,
                    "target_lang": request.target_lang.value
                }
            )
        
        # Check text length limits (additional business rule)
        if len(request.text) > 5000:
            raise TranslationServiceError(
                "Text too long for translation (max 5000 characters)",
                "TEXT_TOO_LONG",
                {"text_length": len(request.text)}
            )
        
        # Check for potentially problematic content
        if request.text.strip() == "":
            raise TranslationServiceError(
                "Cannot translate empty text",
                "EMPTY_TEXT_ERROR"
            )
        
        # Validate supported languages
        supported_languages = await self.repository.get_supported_languages()
        if request.source_lang not in supported_languages:
            raise TranslationServiceError(
                f"Source language '{request.source_lang.value}' is not supported",
                "UNSUPPORTED_SOURCE_LANGUAGE",
                {"source_lang": request.source_lang.value}
            )
        
        if request.target_lang not in supported_languages:
            raise TranslationServiceError(
                f"Target language '{request.target_lang.value}' is not supported",
                "UNSUPPORTED_TARGET_LANGUAGE",
                {"target_lang": request.target_lang.value}
            ) 