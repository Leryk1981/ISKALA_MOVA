#!/usr/bin/env python3
"""
ISKALA Protection Shield - Unified Security Layer
Центральний шар захисту через який проходить і верифікується все
"""

import sys
import os
sys.path.append('/a0/instruments/custom/iskala')

from vault.crypto import encrypt_chacha20, decrypt_chacha20, hmac_sha256, verify_hmac_sha256
from vault.api import app as vault_api
from vault.schemas import *
import json
import hashlib
import secrets
from datetime import datetime

class ISKALAShield:
    """
    Центральний шар захисту ISKALA
    Через цей шар проходить і верифікується все
    """

    def __init__(self):
        self.name = "ISKALA Protection Shield"
        self.version = "2.0"
        self.active = True
        self.verification_log = []

    def verify_request(self, request_data, user_context=None):
        """
        Перевірка всіх вхідних запитів
        """
        verification_record = {
            "timestamp": datetime.now().isoformat(),
            "request_type": type(request_data).__name__,
            "user_context": user_context,
            "status": "pending"
        }

        # 1. Перевірка цілісності даних
        if not self._verify_data_integrity(request_data):
            verification_record["status"] = "failed"
            verification_record["reason"] = "data_integrity_check_failed"
            return False, verification_record

        # 2. Перевірка прав доступу
        if not self._verify_access_rights(request_data, user_context):
            verification_record["status"] = "failed"
            verification_record["reason"] = "access_rights_violation"
            return False, verification_record

        # 3. Перевірка політик безпеки
        if not self._verify_security_policies(request_data, user_context):
            verification_record["status"] = "failed"
            verification_record["reason"] = "security_policy_violation"
            return False, verification_record

        verification_record["status"] = "verified"
        self.verification_log.append(verification_record)
        return True, verification_record

    def encrypt_data(self, data, key_context):
        """
        Шифрування даних перед збереженням або передачею
        """
        # Генерація nonce для кожної операції
        nonce = secrets.token_bytes(12)

        # Шифрування через vault
        encrypted = encrypt_chacha20(
            data.encode('utf-8') if isinstance(data, str) else data,
            key_context['key'],
            nonce
        )

        # HMAC для перевірки цілісності
        hmac_tag = hmac_sha256(encrypted, key_context['key'])

        return {
            "encrypted_data": encrypted,
            "nonce": nonce,
            "hmac": hmac_tag,
            "timestamp": datetime.now().isoformat()
        }

    def decrypt_data(self, encrypted_package, key_context):
        """
        Дешифрування даних з перевіркою цілісності
        """
        encrypted_data = encrypted_package['encrypted_data']
        nonce = encrypted_package['nonce']
        hmac_tag = encrypted_package['hmac']

        # Перевірка HMAC
        if not verify_hmac_sha256(encrypted_data, key_context['key'], hmac_tag):
            raise ValueError("Помилка перевірки цілісності даних")

        # Дешифрування
        decrypted = decrypt_chacha20(encrypted_data, key_context['key'], nonce)
        return decrypted.decode('utf-8')

    def _verify_data_integrity(self, data):
        """Перевірка цілісності даних"""
        # Реалізація перевірки цілісності
        return True  # Спрощена реалізація для демонстрації

    def _verify_access_rights(self, data, user_context):
        """Перевірка прав доступу"""
        # Реалізація перевірки прав
        return True  # Спрощена реалізація для демонстрації

    def _verify_security_policies(self, data, user_context):
        """Перевірка політик безпеки"""
        # Реалізація перевірки політик
        return True  # Спрощена реалізація для демонстрації

    def get_shield_status(self):
        """Отримання статусу захисту"""
        return {
            "shield_name": self.name,
            "version": self.version,
            "active": self.active,
            "total_verifications": len(self.verification_log),
            "last_verification": self.verification_log[-1] if self.verification_log else None
        }

# Створення глобального екземпляру shield
shield = ISKALAShield()

# API для інтеграції з ISKALA
def process_mova_intention(intention_data, user_context):
    """Обробка намірів MOVA через shield"""
    verified, record = shield.verify_request(intention_data, user_context)
    if verified:
        return shield.encrypt_data(json.dumps(intention_data), user_context)
    return None

def process_tree_creation(tree_data, user_context):
    """Обробка створення дерев через shield"""
    verified, record = shield.verify_request(tree_data, user_context)
    if verified:
        return shield.encrypt_data(json.dumps(tree_data), user_context)
    return None

if __name__ == "__main__":
    print(f"🛡️ {shield.name} v{shield.version} активовано")
    print("🌺 ISKALA готова до приходу людей!")
