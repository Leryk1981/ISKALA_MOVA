// src/core/transport/SafeSync.js
import { v4 as uuidv4 } from 'uuid';
import SyncManager from './SyncManager';
import { listFiles } from '@core/cloud/GoogleDriveProvider';

export default class SafeSync {
  constructor(cryptoEngine) {
    this.cryptoEngine = cryptoEngine;
    this.syncManager = new SyncManager(cryptoEngine);
    this.localFiles = [];
    this.remoteFiles = [];
    this.pollingInterval = null;
  }

  async init() {
    console.log('SafeSync инициализирован');
    await this.pollCloud();
    this.startPolling(); // по умолчанию каждые 5 сек
  }

  async pollCloud() {
    try {
      this.remoteFiles = await listFiles();
      await this.syncManager.syncFiles(this.localFiles, this.remoteFiles);
    } catch (err) {
      console.error('Ошибка при синхронизации:', err);
    }
  }

  startPolling(interval = 5000) {
    this.pollingInterval = setInterval(() => {
      this.pollCloud();
    }, interval);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  trackFile(file) {
    const tracked = {
      id: uuidv4(),
      name: file.name,
      content: file.content,
      lastModified: Date.now(),
    };
    this.localFiles.push(tracked);
    console.log(`Файл ${file.name} добавлен в трекинг`);
  }

  untrackFile(fileId) {
    this.localFiles = this.localFiles.filter(f => f.id !== fileId);
    console.log(`Файл ${fileId} удалён из трекинга`);
  }

  getTrackedFiles() {
    return this.localFiles;
  }
}
