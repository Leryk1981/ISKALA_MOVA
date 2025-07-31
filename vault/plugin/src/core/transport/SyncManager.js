// src/core/transport/SyncManager.js
import { decryptFile, verifyHMAC } from '@core/crypto/CryptoEngine';
import { downloadFile, uploadFile } from '@core/cloud/GoogleDriveProvider';
import { v4 as uuidv4 } from 'uuid';

export default class SyncManager {
  constructor(cryptoEngine) {
    this.cryptoEngine = cryptoEngine;
    this.syncedFiles = new Map(); // fileId → { lastModified, hash }
  }

  async syncFiles(localFiles = [], remoteFiles = []) {
    for (const remote of remoteFiles) {
      const local = localFiles.find(f => f.id === remote.id);
      if (!local) {
        await this.downloadAndStore(remote);
      } else if (remote.lastModified > local.lastModified) {
        await this.resolveConflict(local, remote);
      }
    }

    for (const local of localFiles) {
      const remote = remoteFiles.find(f => f.id === local.id);
      if (!remote || local.lastModified > remote.lastModified) {
        await this.upload(local);
      }
    }
  }

  async resolveConflict(local, remote) {
    console.warn(`Конфликт версий для файла ${local.name}, сохраняем обе версии.`);

    const remoteDecrypted = await this.cryptoEngine.decryptFile(await downloadFile(remote.id));
    const conflictName = `${local.name}.conflict.${Date.now()}`;

    await uploadFile(conflictName, remoteDecrypted);
    // При необходимости сохранить оба файла или показать пользователю выбор
  }

  async downloadAndStore(remoteFile) {
    const encrypted = await downloadFile(remoteFile.id);
    const decrypted = await this.cryptoEngine.decryptFile(encrypted);

    // Здесь можно сохранить файл в локальное хранилище (IndexedDB, FS API)
    console.log(`Файл ${remoteFile.name} скачан и расшифрован`);
  }

  async upload(file) {
    const encrypted = await this.cryptoEngine.encryptFile(file.content);
    await uploadFile(file.name, encrypted);
    this.syncedFiles.set(file.id, {
      lastModified: Date.now(),
      hash: await this.cryptoEngine.getHash(encrypted),
    });
    console.log(`Файл ${file.name} загружен`);
  }

  updateSyncStatus(fileId, status) {
    console.log(`Статус синхронизации ${fileId}: ${status}`);
    // Можно обновлять UI или статус в IndexedDB
  }
}
