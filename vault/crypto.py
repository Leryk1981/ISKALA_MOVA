from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .utils import hex_to_bytes, bytes_to_hex
import os
import base64

# Ключ только импортируется!
def encrypt_chacha20(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    cipher = ChaCha20Poly1305(key)
    return cipher.encrypt(nonce, plaintext, None)

def decrypt_chacha20(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    cipher = ChaCha20Poly1305(key)
    return cipher.decrypt(nonce, ciphertext, None)

def hmac_sha256(message: bytes, key: bytes) -> bytes:
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(message)
    return h.finalize()

def verify_hmac_sha256(message: bytes, key: bytes, tag: bytes) -> bool:
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(message)
    try:
        h.verify(tag)
        return True
    except Exception:
        return False

def pbkdf2_sha256(password: str, salt: bytes, length: int = 32, iterations: int = 100_000) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode())

def sign_cid(cid: str, privkey: bytes) -> str:
    """
    Подписывает cid с помощью HMAC-SHA256 и возвращает base64-подпись.
    """
    tag = hmac_sha256(cid.encode('utf-8'), privkey)
    return base64.b64encode(tag).decode('utf-8')


def verify_signature(cid: str, signature: str, pubkey: bytes) -> bool:
    """
    Проверяет подпись (base64) для cid с помощью HMAC-SHA256.
    """
    try:
        tag = base64.b64decode(signature)
    except Exception:
        return False
    return verify_hmac_sha256(cid.encode('utf-8'), pubkey, tag) 