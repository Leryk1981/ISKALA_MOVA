#!/usr/bin/env python3
"""
ISKALA Universal Translator Core
Центральний модуль перекладу для мультимовної підтримки
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any

class UniversalSense:
    """Універсальна структура сенсу для мультимовного зберігання"""

    def __init__(self, payload: str, original_lang: str, meta: Dict[str, Any] = None):
        self.payload = payload  # Універсальний зміст/намір
        self.original_lang = original_lang  # Мова оригіналу
        self.meta = meta or {}  # Службова інформація
        self.embedding = None  # Вектор змісту
        self.history = []  # Історія перекладів
        self.created_at = datetime.now().isoformat()
        self.id = hashlib.md5(f"{payload}{original_lang}{self.created_at}".encode()).hexdigest()

    def add_translation(self, lang: str, text: str, translator: str = "llm"):
        """Додати переклад до історії"""
        self.history.append({
            "lang": lang,
            "text": text,
            "translator": translator,
            "timestamp": datetime.now().isoformat()
        })

    def to_dict(self) -> Dict[str, Any]:
        """Конвертувати в словник для зберігання"""
        return {
            "id": self.id,
            "payload": self.payload,
            "original_lang": self.original_lang,
            "meta": self.meta,
            "embedding": self.embedding,
            "history": self.history,
            "created_at": self.created_at
        }

class ISKALATranslator:
    """Універсальний перекладач для ISKALA"""

    def __init__(self):
        self.name = "ISKALA Universal Translator"
        self.cache = {}
        self.supported_languages = ["uk", "en", "de", "pl", "ru", "fr", "es"]

    def create_universal_sense(self, original_text: str, source_lang: str, 
                             user_context: Dict[str, Any] = None) -> UniversalSense:
        """Створити універсальний сенс з оригінального тексту"""

        # Трансформуємо в універсальний payload
        universal_payload = self._text_to_universal(original_text, source_lang)

        # Створюємо універсальний сенс
        sense = UniversalSense(
            payload=universal_payload,
            original_lang=source_lang,
            meta={
                "user_context": user_context,
                "transformation_method": "semantic_embedding",
                "confidence": 0.95
            }
        )

        # Додаємо оригінал до історії
        sense.add_translation(source_lang, original_text, "original")

        return sense

    def translate_sense(self, sense: UniversalSense, target_lang: str, 
                       user_style: str = "neutral") -> str:
        """Перекласти сенс на цільову мову"""

        # Перевіряємо кеш
        cache_key = f"{sense.id}_{target_lang}_{user_style}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Перекладаємо payload на цільову мову
        translated = self._universal_to_text(
            sense.payload, 
            target_lang, 
            user_style,
            context=sense.meta
        )

        # Додаємо до історії
        sense.add_translation(target_lang, translated, "llm")

        # Кешуємо результат
        self.cache[cache_key] = translated

        return translated

    def _text_to_universal(self, text: str, source_lang: str) -> str:
        """Трансформувати текст в універсальний формат"""
        # Спрощена реалізація - використовуємо семантичне представлення
        return f"[UNIVERSAL:{source_lang}]{text}[/UNIVERSAL]"

    def _universal_to_text(self, universal_payload: str, target_lang: str, 
                          user_style: str, context: Dict[str, Any] = None) -> str:
        """Перекласти універсальний payload на цільову мову"""
        # Спрощена реалізація - у реальному середовищі тут буде LLM

        # Витягуємо текст з універсального формату
        if universal_payload.startswith("[UNIVERSAL:"):
            text = universal_payload.split("]")[1].split("[/UNIVERSAL]")[0]
        else:
            text = universal_payload

        # Адаптуємо стиль
        style_adaptations = {
            "formal": f"[Формально] {text}",
            "casual": f"[Повсякденно] {text}",
            "poetic": f"[Поетично] {text}",
            "neutral": text
        }

        return style_adaptations.get(user_style, text)

    def get_user_language_bubble(self, user_id: str, preferred_lang: str) -> Dict[str, Any]:
        """Отримати мовну бульбашку для користувача"""
        return {
            "user_id": user_id,
            "language": preferred_lang,
            "style": "neutral",
            "cultural_context": "ukrainian",
            "translation_preferences": {
                "preserve_cultural_references": True,
                "adapt_local_expressions": True,
                "maintain_author_style": True
            }
        }

# Глобальний екземпляр перекладача
translator = ISKALATranslator()
