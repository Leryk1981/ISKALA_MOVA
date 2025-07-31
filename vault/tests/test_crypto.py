import pytest
from vault.crypto import encrypt_chacha20, decrypt_chacha20, hmac_sha256, verify_hmac_sha256, pbkdf2_sha256
from vault.utils import generate_nonce
import os

def test_chacha20_encrypt_decrypt():
    key = os.urandom(32)
    nonce = generate_nonce()
    plaintext = b"test message"
    ciphertext = encrypt_chacha20(plaintext, key, nonce)
    decrypted = decrypt_chacha20(ciphertext, key, nonce)
    assert decrypted == plaintext

def test_hmac_sha256():
    key = os.urandom(32)
    msg = b"hello"
    tag = hmac_sha256(msg, key)
    assert verify_hmac_sha256(msg, key, tag)
    assert not verify_hmac_sha256(b"bad", key, tag)

def test_pbkdf2_sha256():
    password = "pass"
    salt = os.urandom(16)
    key1 = pbkdf2_sha256(password, salt)
    key2 = pbkdf2_sha256(password, salt)
    assert key1 == key2
    assert len(key1) == 32

def test_chacha20_wrong_key():
    key = os.urandom(32)
    nonce = generate_nonce()
    plaintext = b"secret"
    ciphertext = encrypt_chacha20(plaintext, key, nonce)
    with pytest.raises(Exception):
        decrypt_chacha20(ciphertext, os.urandom(32), nonce) 