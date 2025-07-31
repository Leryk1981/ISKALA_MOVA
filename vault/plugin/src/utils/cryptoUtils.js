// plugin/src/utils/cryptoUtils.js

import sodium from 'libsodium-wrappers';

export async function encryptChaCha20(message, key, nonce) {
  await sodium.ready;
  const msgBytes = sodium.from_string(message);
  const keyBytes = sodium.from_hex(key);
  const nonceBytes = sodium.from_hex(nonce);
  const ciphertext = sodium.crypto_stream_chacha20_xor(msgBytes, nonceBytes, keyBytes);
  return sodium.to_hex(ciphertext);
}

export async function decryptChaCha20(cipherHex, key, nonce) {
  await sodium.ready;
  const cipherBytes = sodium.from_hex(cipherHex);
  const keyBytes = sodium.from_hex(key);
  const nonceBytes = sodium.from_hex(nonce);
  const plainBytes = sodium.crypto_stream_chacha20_xor(cipherBytes, nonceBytes, keyBytes);
  return sodium.to_string(plainBytes);
}

export async function hmacSha256(message, key) {
  await sodium.ready;
  const msgBytes = sodium.from_string(message);
  const keyBytes = sodium.from_hex(key);
  const hmac = sodium.crypto_auth(msgBytes, keyBytes);
  return sodium.to_hex(hmac);
}
