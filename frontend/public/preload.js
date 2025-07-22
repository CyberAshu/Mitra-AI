const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // System metrics
  getSystemMetrics: () => ipcRenderer.invoke('get-system-metrics'),
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Event listeners
  onSystemMetricsUpdate: (callback) => {
    ipcRenderer.on('system-metrics-update', callback);
    return () => ipcRenderer.removeListener('system-metrics-update', callback);
  },
  
  onToggleLogs: (callback) => {
    ipcRenderer.on('toggle-logs', callback);
    return () => ipcRenderer.removeListener('toggle-logs', callback);
  },
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// Prevent the default context menu from appearing
window.addEventListener('contextmenu', (e) => {
  e.preventDefault();
});

// Handle window drag functionality for frameless window
window.addEventListener('DOMContentLoaded', () => {
  // Create a draggable area at the top of the window
  const dragArea = document.createElement('div');
  dragArea.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 30px;
    -webkit-app-region: drag;
    z-index: 1000;
    pointer-events: auto;
  `;
  document.body.appendChild(dragArea);
});
