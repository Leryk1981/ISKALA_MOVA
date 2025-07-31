"""
AbsichtLayer v2 - центральний шар виконання намірів

🎯 Мета:
- Приймає намір у вигляді структури MOVA (dict із ключем "намір" і "контекст")
- Викликає відповідну дію, зареєстровану у внутрішньому реєстрі функцій
- Повертає результат виконання або помилку
- Підтримує мультимовність (назви намірів можуть бути в різних мовах)
"""

import json
import logging
import asyncio
from typing import Dict, Any, Callable, Optional, Union
from datetime import datetime
from pathlib import Path

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальний реєстр адаптерів
adapter_registry: Dict[str, Union[Callable, Any]] = {}

def register(absicht_name: str):
    """
    Декоратор для реєстрації дії
    
    Args:
        absicht_name: Назва наміру (може бути на будь-якій мові)
    
    Returns:
        Декоратор функції
    """
    def wrapper(func: Callable) -> Callable:
        adapter_registry[absicht_name] = func
        logger.info(f"Зареєстровано намір: {absicht_name} -> {func.__name__}")
        return func
    return wrapper

def execute(absicht_dict: Dict[str, Any]) -> Any:
    """
    Основний виконавець намірів
    
    Args:
        absicht_dict: Словник з ключами "намір" та "контекст"
    
    Returns:
        Результат виконання дії
    
    Raises:
        ValueError: Якщо намір не знайдено в реєстрі
        Exception: Помилки виконання дії
    """
    absicht = absicht_dict.get("намір")
    context = absicht_dict.get("контекст", {})
    
    if not absicht:
        raise ValueError("Ключ 'намір' відсутній в словнику")
    
    if absicht not in adapter_registry:
        # Логуємо невідомий намір
        logger.warning(f"Невідомий намір: {absicht}")
        logger.info(f"Доступні наміри: {list(adapter_registry.keys())}")
        raise ValueError(f"Невідомий намір: {absicht}")
    
    try:
        # Виконуємо зареєстровану дію
        func = adapter_registry[absicht]
        
        # Перевіряємо чи це асинхронна функція
        if asyncio.iscoroutinefunction(func):
            # Запускаємо асинхронну функцію
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(func(context))
        else:
            # Виконуємо синхронну функцію
            result = func(context)
            
        logger.info(f"Намір '{absicht}' виконано успішно")
        return result
    except Exception as e:
        logger.error(f"Помилка виконання наміру '{absicht}': {e}")
        raise

def get_registered_intents() -> Dict[str, str]:
    """
    Повертає список зареєстрованих намірів з їх функціями
    
    Returns:
        Словник {намір: назва_функції}
    """
    return {
        intent: func.__name__ 
        for intent, func in adapter_registry.items()
    }

def unregister(absicht_name: str) -> bool:
    """
    Видаляє намір з реєстру
    
    Args:
        absicht_name: Назва наміру для видалення
    
    Returns:
        True якщо намір був видалений, False якщо не знайдено
    """
    if absicht_name in adapter_registry:
        del adapter_registry[absicht_name]
        logger.info(f"Намір '{absicht_name}' видалено з реєстру")
        return True
    return False

def clear_registry():
    """Очищає весь реєстр намірів"""
    adapter_registry.clear()
    logger.info("Реєстр намірів очищено")

# Зручні функції для роботи з намірами
def execute_intent(intent_name: str, context: Dict[str, Any] = None) -> Any:
    """
    Зручна функція для виконання наміру
    
    Args:
        intent_name: Назва наміру
        context: Контекст виконання
    
    Returns:
        Результат виконання
    """
    absicht_dict = {
        "намір": intent_name,
        "контекст": context or {}
    }
    return execute(absicht_dict)

def is_intent_registered(intent_name: str) -> bool:
    """
    Перевіряє чи зареєстрований намір
    
    Args:
        intent_name: Назва наміру
    
    Returns:
        True якщо намір зареєстрований
    """
    return intent_name in adapter_registry

# Приклади використання (будуть імпортовані з default_adapters.py)
if __name__ == "__main__":
    # Демонстрація роботи
    print("=== AbsichtLayer v2 Demo ===")
    
    # Реєструємо тестові наміри
    @register("тестовий_намір")
    def test_intent(context):
        return f"Тестовий намір виконано з контекстом: {context}"
    
    @register("привітання")
    def greeting_intent(context):
        name = context.get("ім'я", "незнайомець")
        return f"Привіт, {name}! Радий тебе бачити!"
    
    # Виконуємо наміри
    try:
        # Тестовий намір
        result1 = execute({
            "намір": "тестовий_намір",
            "контекст": {"параметр": "значення"}
        })
        print(f"Результат 1: {result1}")
        
        # Привітання
        result2 = execute({
            "намір": "привітання",
            "контекст": {"ім'я": "Іван"}
        })
        print(f"Результат 2: {result2}")
        
        # Невідомий намір
        result3 = execute({
            "намір": "неіснуючий_намір",
            "контекст": {}
        })
    except ValueError as e:
        print(f"Очікувана помилка: {e}")
    
    # Показуємо зареєстровані наміри
    print(f"\nЗареєстровані наміри: {get_registered_intents()}") 