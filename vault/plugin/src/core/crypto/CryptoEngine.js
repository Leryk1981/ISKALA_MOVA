// src/core/crypto/CryptoEngine.js
import { initSodium } from './libsodiumWrapper';

export class CryptoEngine {
  constructor() {
    this.sodium = null;
  }

  async init() {
    if (!this.sodium) {
      this.sodium = await initSodium();
    }
  }

  async deriveKey(password, salt) {
    await this.init();
    return this.sodium.crypto_pwhash(
      32,
      password,
      salt,
      this.sodium.crypto_pwhash_OPSLIMIT_INTERACTIVE,
      this.sodium.crypto_pwhash_MEMLIMIT_INTERACTIVE,
      this.sodium.crypto_pwhash_ALG_DEFAULT
    );
  }

  async encryptData(message, key, nonce) {
    await this.init();
    const cipher = this.sodium.crypto_aead_chacha20poly1305_ietf_encrypt(
      message,
      null,
      null,
      nonce,
      key
    );
    return cipher;
  }

  async decryptData(ciphertext, key, nonce) {
    await this.init();
    try {
      return this.sodium.crypto_aead_chacha20poly1305_ietf_decrypt(
        null,
        ciphertext,
        null,
        nonce,
        key
      );
    } catch (e) {
      console.error("Ошибка расшифровки:", e);
      return null;
    }
  }

  async generateKey() {
    await this.init();
    return this.sodium.randombytes_buf(32);
  }

  async generateNonce() {
    await this.init();
    return this.sodium.randombytes_buf(this.sodium.crypto_aead_chacha20poly1305_ietf_NPUBBYTES);
  }
}
export default CryptoEngine;
