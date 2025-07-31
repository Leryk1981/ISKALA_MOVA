export function generateTimestamp() {
    return new Date().toISOString();
  }
  
  export function compareMetadata(localMeta, remoteMeta) {
    return new Date(remoteMeta.modifiedTime) > new Date(localMeta.modifiedTime);
  }