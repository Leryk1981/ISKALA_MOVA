from pydantic import BaseModel, Field
from typing import Optional, Dict

class EncryptRequest(BaseModel):
    plaintext: str
    key: str  # hex
    nonce: str  # hex
    metadata: Optional[Dict[str, str]] = None

class EncryptResponse(BaseModel):
    ciphertext: str  # hex
    nonce: str  # hex
    hmac: str  # hex

class DecryptRequest(BaseModel):
    ciphertext: str  # hex
    key: str  # hex
    nonce: str  # hex

class DecryptResponse(BaseModel):
    plaintext: str

class VerifyRequest(BaseModel):
    message: str
    key: str  # hex
    hmac: str  # hex

class VerifyResponse(BaseModel):
    valid: bool 