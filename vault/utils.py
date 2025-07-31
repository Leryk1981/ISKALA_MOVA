import os
import hashlib

def hex_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)

def bytes_to_hex(b: bytes) -> str:
    return b.hex()

def generate_nonce(size: int = 12) -> bytes:
    return os.urandom(size)

def build_seed(key: str, word: str, gesture: str, timestamp: str) -> bytes:
    data = (key + word + gesture + timestamp).encode('utf-8')
    return hashlib.sha256(data).digest() 