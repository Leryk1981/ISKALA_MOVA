// src/core/crypto/libsodiumWrapper.js
import sodium from 'libsodium-wrappers';

let isReady = false;

export async function initSodium() {
  if (!isReady) {
    await sodium.ready;
    isReady = true;
  }
  return sodium;
}
