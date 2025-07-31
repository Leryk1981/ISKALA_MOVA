export class SafeSync {
    constructor(cloudProvider) {
      this.cloudProvider = cloudProvider;
      this.trackedFiles = new Map();
    }
  
    trackFile(fileMeta) {
      this.trackedFiles.set(fileMeta.id, fileMeta);
    }
  
    untrackFile(fileId) {
      this.trackedFiles.delete(fileId);
    }
  
    getTrackedFiles() {
      return Array.from(this.trackedFiles.values());
    }
  
    async syncFiles() {
      const remoteFiles = await this.cloudProvider.listFiles();
      for (const fileMeta of remoteFiles) {
        const localMeta = this.trackedFiles.get(fileMeta.id);
        if (!localMeta || new Date(fileMeta.modifiedTime) > new Date(localMeta.modifiedTime)) {
          const file = await this.cloudProvider.downloadFile(fileMeta.id);
          // TODO: decrypt and store locally
          this.trackedFiles.set(fileMeta.id, fileMeta);
        }
      }
    }
  
    updateSyncStatus(fileId, status) {
      const meta = this.trackedFiles.get(fileId);
      if (meta) meta.syncStatus = status;
    }
  }