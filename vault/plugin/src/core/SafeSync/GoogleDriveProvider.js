export class GoogleDriveProvider {
    async connect() {
      // TODO: OAuth2 flow or token handling
    }
  
    async listFiles() {
      // TODO: implement listing files from Google Drive
      return [];
    }
  
    async uploadFile(file, path) {
      // TODO: implement upload logic
    }
  
    async downloadFile(fileId) {
      // TODO: implement download logic
    }
  
    async watchChanges(callback) {
      // TODO: setup polling (every 5s)
      setInterval(async () => {
        const changes = await this.listFiles();
        callback(changes);
      }, 5000);
    }
  }