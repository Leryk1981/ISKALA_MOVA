from fastapi import FastAPI, HTTPException
from .schemas import EncryptRequest, EncryptResponse, DecryptRequest, DecryptResponse, VerifyRequest, VerifyResponse
from .crypto import encrypt_chacha20, decrypt_chacha20, hmac_sha256, verify_hmac_sha256
from .utils import hex_to_bytes, bytes_to_hex
from cryptography.exceptions import InvalidTag

app = FastAPI()

@app.post('/encrypt', response_model=EncryptResponse)
def encrypt(req: EncryptRequest):
    key = hex_to_bytes(req.key)
    nonce = hex_to_bytes(req.nonce)
    plaintext = req.plaintext.encode('utf-8')
    ciphertext = encrypt_chacha20(plaintext, key, nonce)
    tag = hmac_sha256(ciphertext, key)
    return EncryptResponse(ciphertext=bytes_to_hex(ciphertext), nonce=req.nonce, hmac=bytes_to_hex(tag))

@app.post('/decrypt', response_model=DecryptResponse)
def decrypt(req: DecryptRequest):
    key = hex_to_bytes(req.key)
    nonce = hex_to_bytes(req.nonce)
    ciphertext = hex_to_bytes(req.ciphertext)
    try:
        plaintext = decrypt_chacha20(ciphertext, key, nonce)
    except InvalidTag:
        raise HTTPException(status_code=400, detail="Ошибка расшифровки: неверный ключ или повреждённые данные")
    return DecryptResponse(plaintext=plaintext.decode('utf-8'))

@app.post('/verify', response_model=VerifyResponse)
def verify(req: VerifyRequest):
    key = hex_to_bytes(req.key)
    tag = hex_to_bytes(req.hmac)
    valid = verify_hmac_sha256(req.message.encode('utf-8'), key, tag)
    return VerifyResponse(valid=valid) 