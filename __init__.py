"""
AbsichtLayer v2 - центральний шар виконання намірів

Цей пакет надає простий та ефективний спосіб реєстрації та виконання намірів
з підтримкою мультимовності та розширюваності.
"""

from .absicht_layer_v2 import (
    register,
    execute,
    execute_intent,
    get_registered_intents,
    unregister,
    clear_registry,
    is_intent_registered,
    adapter_registry
)

# Імпортуємо стандартні адаптери
from . import default_adapters

__version__ = "2.0.0"
__author__ = "MOVA_ISKALA Team"

__all__ = [
    "register",
    "execute", 
    "execute_intent",
    "get_registered_intents",
    "unregister",
    "clear_registry",
    "is_intent_registered",
    "adapter_registry",
    "default_adapters"
]

# Автоматично завантажуємо стандартні адаптери при імпорті пакету
def _load_default_adapters():
    """Завантажує стандартні адаптери"""
    try:
        import default_adapters
        return True
    except ImportError:
        return False

# Завантажуємо адаптери при імпорті
_load_default_adapters() 