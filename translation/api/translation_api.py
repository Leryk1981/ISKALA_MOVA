#!/usr/bin/env python3
"""
ISKALA Universal Translation API
REST API для мультимовної підтримки ISKALA
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os

# Додаємо шлях до ISKALA
import sys
sys.path.append('/a0/instruments/custom/iskala')

from translation.core.translator import ISKALATranslator, UniversalSense

app = FastAPI(title="ISKALA Translation API", version="1.0")
translator = ISKALATranslator()

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    user_style: str = "neutral"
    user_context: Optional[Dict[str, Any]] = None

class UniversalSenseRequest(BaseModel):
    text: str
    source_lang: str
    user_context: Optional[Dict[str, Any]] = None

class TranslationResponse(BaseModel):
    translated_text: str
    original_text: str
    source_lang: str
    target_lang: str
    confidence: float = 0.95
    cached: bool = False

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Перекласти текст між мовами"""
    try:
        # Створюємо універсальний сенс
        sense = translator.create_universal_sense(
            request.text, 
            request.source_lang, 
            request.user_context
        )

        # Перекладаємо
        translated = translator.translate_sense(
            sense, 
            request.target_lang, 
            request.user_style
        )

        # Перевіряємо кеш
        cached = any(
            h["lang"] == request.target_lang 
            for h in sense.history[1:]  # Пропускаємо оригінал
        )

        return TranslationResponse(
            translated_text=translated,
            original_text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            cached=cached
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-sense")
async def create_universal_sense(request: UniversalSenseRequest):
    """Створити універсальний сенс"""
    try:
        sense = translator.create_universal_sense(
            request.text,
            request.source_lang,
            request.user_context
        )

        return {
            "sense_id": sense.id,
            "universal_payload": sense.payload,
            "original_lang": sense.original_lang,
            "created_at": sense.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/language-bubble/{user_id}")
async def get_language_bubble(user_id: str, preferred_lang: str):
    """Отримати мовну бульбашку для користувача"""
    bubble = translator.get_user_language_bubble(user_id, preferred_lang)
    return bubble

@app.get("/supported-languages")
async def get_supported_languages():
    """Отримати список підтримуваних мов"""
    return {"languages": translator.supported_languages}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
