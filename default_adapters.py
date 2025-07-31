"""
Default Adapters - стандартні адаптери для AbsichtLayer

Цей файл містить базові дії, які можуть виконуватися через AbsichtLayer.
Всі функції реєструються через декоратор @register.
"""

import json
import logging
import os
import httpx
from typing import Dict, Any, Optional
from absicht_layer_v2 import register

logger = logging.getLogger(__name__)

# LLM конфігурація
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "moonshotai/kimi-k2")

async def call_llm(prompt: str, max_tokens: int = 1000) -> Optional[str]:
    """Викликає LLM через OpenRouter API"""
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY не налаштовано")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://iskala-mova.local",
                    "X-Title": "Iskala/MOVA"
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Помилка виклику LLM: {e}")
        return None

logger = logging.getLogger(__name__)

# ============================================================================
# КОМУНІКАЦІЯ
# ============================================================================

@register("надіслати_email")
def send_email(context: Dict[str, Any]) -> str:
    """
    Надсилає email
    
    Args:
        context: Словник з ключами:
            - to: email адреса отримувача
            - subject: тема листа
            - body: тіло листа
            - from_email: email відправника (опціонально)
    
    Returns:
        Повідомлення про успішне надсилання
    """
    to = context.get("to")
    subject = context.get("subject")
    body = context.get("body")
    from_email = context.get("from_email", "system@mova-iskala.com")
    
    if not all([to, subject, body]):
        raise ValueError("Потрібні параметри: to, subject, body")
    
    # Тут буде реальна логіка надсилання email
    logger.info(f"Надсилання email до {to}: {subject}")
    
    return f"[OK] Email надіслано до {to} з темою '{subject}'"

@register("send_email")
def send_email_en(context: Dict[str, Any]) -> str:
    """Англійська версія надсилання email"""
    return send_email(context)

@register("отправить_письмо")
def send_email_ru(context: Dict[str, Any]) -> str:
    """Російська версія надсилання email"""
    return send_email(context)

# ============================================================================
# ПЕРЕКЛАД
# ============================================================================

@register("перекласти_текст")
def translate_text(context: Dict[str, Any]) -> str:
    """
    Перекладає текст
    
    Args:
        context: Словник з ключами:
            - text: текст для перекладу
            - from_lang: мова оригіналу (опціонально)
            - to_lang: мова перекладу
            - format: формат виводу (опціонально)
    
    Returns:
        Перекладений текст
    """
    text = context.get("text")
    from_lang = context.get("from_lang", "auto")
    to_lang = context.get("to_lang", "en")
    format_type = context.get("format", "text")
    
    if not text:
        raise ValueError("Параметр 'text' обов'язковий")
    
    # Тут буде реальна логіка перекладу
    logger.info(f"Переклад тексту з {from_lang} на {to_lang}")
    
    # Симуляція перекладу
    translated = f"Translated({to_lang}): {text}"
    
    if format_type == "json":
        return json.dumps({
            "original": text,
            "translated": translated,
            "from_lang": from_lang,
            "to_lang": to_lang
        })
    
    return translated

@register("translate_text")
def translate_text_en(context: Dict[str, Any]) -> str:
    """Англійська версія перекладу"""
    return translate_text(context)

@register("перевести_текст")
def translate_text_ru(context: Dict[str, Any]) -> str:
    """Російська версія перекладу"""
    return translate_text(context)

# ============================================================================
# ФАЙЛИ ТА ДОКУМЕНТИ
# ============================================================================

@register("зберегти_файл")
def save_file(context: Dict[str, Any]) -> str:
    """
    Зберігає файл
    
    Args:
        context: Словник з ключами:
            - content: вміст файлу
            - filename: назва файлу
            - path: шлях для збереження (опціонально)
            - format: формат файлу (опціонально)
    
    Returns:
        Повідомлення про успішне збереження
    """
    content = context.get("content")
    filename = context.get("filename")
    path = context.get("path", "./")
    format_type = context.get("format", "txt")
    
    if not all([content, filename]):
        raise ValueError("Потрібні параметри: content, filename")
    
    # Тут буде реальна логіка збереження файлу
    logger.info(f"Збереження файлу {filename} в {path}")
    
    return f"[OK] Файл {filename} збережено в {path}"

@register("save_file")
def save_file_en(context: Dict[str, Any]) -> str:
    """Англійська версія збереження файлу"""
    return save_file(context)

@register("сохранить_файл")
def save_file_ru(context: Dict[str, Any]) -> str:
    """Російська версія збереження файлу"""
    return save_file(context)

@register("читати_файл")
def read_file(context: Dict[str, Any]) -> str:
    """
    Читає файл
    
    Args:
        context: Словник з ключами:
            - filename: назва файлу
            - path: шлях до файлу (опціонально)
            - encoding: кодування (опціонально)
    
    Returns:
        Вміст файлу
    """
    filename = context.get("filename")
    path = context.get("path", "./")
    encoding = context.get("encoding", "utf-8")
    
    if not filename:
        raise ValueError("Параметр 'filename' обов'язковий")
    
    # Тут буде реальна логіка читання файлу
    logger.info(f"Читання файлу {filename} з {path}")
    
    return f"[CONTENT] Вміст файлу {filename} (симуляція)"

@register("read_file")
def read_file_en(context: Dict[str, Any]) -> str:
    """Англійська версія читання файлу"""
    return read_file(context)

# ============================================================================
# АНАЛІЗ ТА ОБРОБКА
# ============================================================================

@register("аналізувати_текст")
def analyze_text(context: Dict[str, Any]) -> str:
    """
    Аналізує текст
    
    Args:
        context: Словник з ключами:
            - text: текст для аналізу
            - analysis_type: тип аналізу (sentiment, keywords, summary)
            - language: мова тексту (опціонально)
    
    Returns:
        Результат аналізу
    """
    text = context.get("text")
    analysis_type = context.get("analysis_type", "general")
    language = context.get("language", "uk")
    
    if not text:
        raise ValueError("Параметр 'text' обов'язковий")
    
    # Тут буде реальна логіка аналізу
    logger.info(f"Аналіз тексту типу {analysis_type}")
    
    return f"[ANALYSIS] Результат аналізу тексту ({analysis_type}): {text[:50]}..."

@register("analyze_text")
def analyze_text_en(context: Dict[str, Any]) -> str:
    """Англійська версія аналізу тексту"""
    return analyze_text(context)

@register("проаналізуровать_текст")
def analyze_text_ru(context: Dict[str, Any]) -> str:
    """Російська версія аналізу тексту"""
    return analyze_text(context)

# ============================================================================
# СИСТЕМНІ ДІЇ
# ============================================================================

@register("системна_інформація")
def system_info(context: Dict[str, Any]) -> str:
    """
    Повертає системну інформацію
    
    Args:
        context: Словник з ключами:
            - info_type: тип інформації (memory, performance, status)
    
    Returns:
        Системна інформація
    """
    info_type = context.get("info_type", "general")
    
    # Тут буде реальна логіка отримання системної інформації
    logger.info(f"Отримання системної інформації типу {info_type}")
    
    return f"[SYSTEM] Системна інформація ({info_type}): статус OK"

@register("system_info")
def system_info_en(context: Dict[str, Any]) -> str:
    """Англійська версія системної інформації"""
    return system_info(context)

@register("системная_информация")
def system_info_ru(context: Dict[str, Any]) -> str:
    """Російська версія системної інформації"""
    return system_info(context)

@register("очистити_кеш")
def clear_cache(context: Dict[str, Any]) -> str:
    """
    Очищає кеш
    
    Args:
        context: Словник з ключами:
            - cache_type: тип кешу для очищення (all, memory, temp)
    
    Returns:
        Повідомлення про очищення
    """
    cache_type = context.get("cache_type", "all")
    
    # Тут буде реальна логіка очищення кешу
    logger.info(f"Очищення кешу типу {cache_type}")
    
    return f"[OK] Кеш типу {cache_type} очищено"

@register("clear_cache")
def clear_cache_en(context: Dict[str, Any]) -> str:
    """Англійська версія очищення кешу"""
    return clear_cache(context)

# ============================================================================
# КОРИСТУВАЧСЬКІ ДІЇ
# ============================================================================

@register("привітання")
def greeting(context: Dict[str, Any]) -> str:
    """
    Привітання користувача
    
    Args:
        context: Словник з ключами:
            - name: ім'я користувача
            - time: час доби (опціонально)
            - language: мова привітання (опціонально)
    
    Returns:
        Привітання
    """
    name = context.get("name", "користувач")
    time = context.get("time", "день")
    language = context.get("language", "uk")
    
    greetings = {
        "uk": f"Привіт, {name}! Добрий {time}!"
    }
    
    return greetings.get(language, greetings["uk"])

@register("greeting")
def greeting_en(context: Dict[str, Any]) -> str:
    """Англійська версія привітання"""
    name = context.get("name", "user")
    time = context.get("time", "day")
    return f"Hello, {name}! Good {time}!"

@register("приветствие")
def greeting_ru(context: Dict[str, Any]) -> str:
    """Російська версія привітання"""
    name = context.get("name", "пользователь")
    time = context.get("time", "день")
    return f"Привет, {name}! Добрый {time}!"

# ============================================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================================

def get_available_intents() -> Dict[str, str]:
    """
    Повертає список доступних намірів з описом
    
    Returns:
        Словник {намір: опис}
    """
    return {
        "надіслати_email": "Надсилає email",
        "перекласти_текст": "Перекладає текст",
        "зберегти_файл": "Зберігає файл",
        "читати_файл": "Читає файл",
        "аналізувати_текст": "Аналізує текст",
        "системна_інформація": "Повертає системну інформацію",
        "очистити_кеш": "Очищає кеш",
        "привітання": "Привітання користувача",
        "llm_генерація": "Генерує контент через LLM",
        "llm_переклад": "Перекладає текст через LLM",
        "llm_аналіз": "Аналізує текст через LLM"
    }

# ============================================================================
# LLM ФУНКЦІЇ
# ============================================================================

@register("llm_генерація")
async def llm_generate(context: Dict[str, Any]) -> str:
    """
    Генерує контент через LLM
    
    Args:
        context: Словник з ключами:
            - prompt: запит для генерації
            - max_tokens: максимальна кількість токенів (опціонально)
    
    Returns:
        Згенерований контент
    """
    prompt = context.get("prompt")
    max_tokens = context.get("max_tokens", 1000)
    
    if not prompt:
        raise ValueError("Параметр 'prompt' обов'язковий")
    
    result = await call_llm(prompt, max_tokens)
    if result:
        return f"[LLM] {result}"
    else:
        return "[ERROR] LLM недоступний"

@register("llm_generate")
async def llm_generate_en(context: Dict[str, Any]) -> str:
    """Англійська версія LLM генерації"""
    return await llm_generate(context)

@register("llm_переклад")
async def llm_translate(context: Dict[str, Any]) -> str:
    """
    Перекладає текст через LLM
    
    Args:
        context: Словник з ключами:
            - text: текст для перекладу
            - target_lang: мова перекладу
            - source_lang: мова оригіналу (опціонально)
    
    Returns:
        Перекладений текст
    """
    text = context.get("text")
    target_lang = context.get("target_lang", "en")
    source_lang = context.get("source_lang", "auto")
    
    if not text:
        raise ValueError("Параметр 'text' обов'язковий")
    
    prompt = f"Переклади текст з {source_lang} на {target_lang}: {text}"
    result = await call_llm(prompt, 500)
    
    if result:
        return f"[LLM Translate] {result}"
    else:
        return "[ERROR] LLM недоступний"

@register("llm_translate")
async def llm_translate_en(context: Dict[str, Any]) -> str:
    """Англійська версія LLM перекладу"""
    return await llm_translate(context)

@register("llm_аналіз")
async def llm_analyze(context: Dict[str, Any]) -> str:
    """
    Аналізує текст через LLM
    
    Args:
        context: Словник з ключами:
            - text: текст для аналізу
            - analysis_type: тип аналізу (sentiment, summary, etc.)
    
    Returns:
        Результат аналізу
    """
    text = context.get("text")
    analysis_type = context.get("analysis_type", "general")
    
    if not text:
        raise ValueError("Параметр 'text' обов'язковий")
    
    prompt = f"Проаналізуй текст (тип: {analysis_type}): {text}"
    result = await call_llm(prompt, 800)
    
    if result:
        return f"[LLM Analysis] {result}"
    else:
        return "[ERROR] LLM недоступний"

@register("llm_analyze")
async def llm_analyze_en(context: Dict[str, Any]) -> str:
    """Англійська версія LLM аналізу"""
    return await llm_analyze(context)

if __name__ == "__main__":
    # Демонстрація роботи адаптерів
    from absicht_layer_v2 import execute, get_registered_intents
    
    print("=== Default Adapters Demo ===")
    
    # Тестуємо різні наміри
    test_cases = [
        {
            "намір": "привітання",
            "контекст": {"name": "Іван", "time": "ранок"}
        },
        {
            "намір": "перекласти_текст",
            "контекст": {"text": "Привіт світ", "to_lang": "en"}
        },
        {
            "намір": "greeting",
            "контекст": {"name": "John", "time": "morning"}
        },
        {
            "намір": "приветствие",
            "контекст": {"name": "Иван", "time": "утро"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = execute(test_case)
            print(f"Тест {i}: {result}")
        except Exception as e:
            print(f"Тест {i}: Помилка - {e}")
    
    print(f"\nЗареєстровані наміри: {list(get_registered_intents().keys())}") 