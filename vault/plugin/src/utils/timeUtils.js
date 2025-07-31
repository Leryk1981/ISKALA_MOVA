// plugin/src/utils/timeUtils.js

export function getCurrentTimestamp() {
    return Math.floor(Date.now() / 1000);
  }
  
  export function getBlockNumber(secondsPerBlock = 60) {
    return Math.floor(Date.now() / 1000 / secondsPerBlock);
  }
  
  export function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toISOString();
  }
  