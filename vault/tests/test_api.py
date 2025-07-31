import pytest
from fastapi.testclient import TestClient
from vault.api import app
import os
from vault.utils import bytes_to_hex, generate_nonce
from cryptography.exceptions import InvalidTag

client = TestClient(app)

def test_encrypt_decrypt():
    key = os.urandom(32)
    nonce = generate_nonce()
    plaintext = "секретное сообщение"
    resp = client.post("/encrypt", json={
        "plaintext": plaintext,
        "key": bytes_to_hex(key),
        "nonce": bytes_to_hex(nonce)
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "ciphertext" in data and "hmac" in data
    # Дешифруем
    resp2 = client.post("/decrypt", json={
        "ciphertext": data["ciphertext"],
        "key": bytes_to_hex(key),
        "nonce": bytes_to_hex(nonce)
    })
    assert resp2.status_code == 200
    assert resp2.json()["plaintext"] == plaintext

def test_verify():
    key = os.urandom(32)
    msg = "test"
    from vault.crypto import hmac_sha256
    tag = hmac_sha256(msg.encode(), key)
    resp = client.post("/verify", json={
        "message": msg,
        "key": bytes_to_hex(key),
        "hmac": bytes_to_hex(tag)
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is True
    # Неверный HMAC
    resp2 = client.post("/verify", json={
        "message": msg,
        "key": bytes_to_hex(key),
        "hmac": bytes_to_hex(os.urandom(32))
    })
    assert resp2.status_code == 200
    assert resp2.json()["valid"] is False

def test_decrypt_wrong_key():
    key = os.urandom(32)
    nonce = generate_nonce()
    plaintext = "fail"
    resp = client.post("/encrypt", json={
        "plaintext": plaintext,
        "key": bytes_to_hex(key),
        "nonce": bytes_to_hex(nonce)
    })
    data = resp.json()
    # Дешифруем с другим ключом, ожидаем ошибку
    resp2 = client.post("/decrypt", json={
        "ciphertext": data["ciphertext"],
        "key": bytes_to_hex(os.urandom(32)),
        "nonce": bytes_to_hex(nonce)
    })
    assert resp2.status_code == 500 or resp2.status_code == 422 or resp2.status_code == 400 