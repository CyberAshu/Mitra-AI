const { app, BrowserWindow, Tray, Menu, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const si = require('systeminformation');
const os = require('os');

let mainWindow;
let tray;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 620,
    minWidth: 800,
    minHeight: 600,
    alwaysOnTop: true,
    frame: false,
    resizable: true,
    show: false,
    icon: path.join(__dirname, 'icon.png'), // Add your icon file
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
      zoomFactor: 1.0,
      enableWebSecurity: false,
    },
  });

  // Load the app
  const startUrl = isDev 
    ? 'http://localhost:3000' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Center the window
    mainWindow.center();
    
    // Disable zoom
    mainWindow.webContents.setZoomFactor(1.0);
    mainWindow.webContents.setVisualZoomLevelLimits(1, 1);
    
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Prevent window from being closed, minimize to tray instead
  mainWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
  });
}

function createTray() {
  // Create tray icon
  tray = new Tray(path.join(__dirname, 'icon.png')); // Add your tray icon
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show MITRA AI',
      click: () => {
        mainWindow.show();
        mainWindow.focus();
      }
    },
    {
      label: 'Hide MITRA AI',
      click: () => {
        mainWindow.hide();
      }
    },
    { type: 'separator' },
    {
      label: 'Toggle Always On Top',
      click: () => {
        const isOnTop = mainWindow.isAlwaysOnTop();
        mainWindow.setAlwaysOnTop(!isOnTop);
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuiting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('MITRA AI Desktop Dashboard');
  tray.setContextMenu(contextMenu);
  
  // Double click to show/hide
  tray.on('double-click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// System metrics IPC handlers
ipcMain.handle('get-system-metrics', async () => {
  try {
    const [cpu, memory, graphics, temps] = await Promise.all([
      si.cpu(),
      si.mem(),
      si.graphics(),
      si.cpuTemperature()
    ]);

    const cpuLoad = await si.currentLoad();
    
    return {
      cpu: {
        usage: Math.round(cpuLoad.currentLoad),
        model: cpu.brand,
        cores: cpu.cores,
        speed: cpu.speed
      },
      memory: {
        total: memory.total,
        used: memory.used,
        available: memory.available,
        usage: Math.round((memory.used / memory.total) * 100)
      },
      gpu: graphics.controllers.length > 0 ? {
        model: graphics.controllers[0].model,
        vram: graphics.controllers[0].vram || 0
      } : null,
      temperature: {
        main: temps.main || 0,
        cores: temps.cores || []
      }
    };
  } catch (error) {
    console.error('Error getting system metrics:', error);
    return null;
  }
});

ipcMain.handle('get-system-info', async () => {
  try {
    const [networkStats, diskLayout, processes, uptime] = await Promise.all([
      si.networkStats(),
      si.diskLayout(),
      si.processes(),
      si.time()
    ]);

    return {
      network: networkStats[0] || {},
      disk: diskLayout[0] || {},
      processes: processes.list.slice(0, 10), // Top 10 processes
      uptime: uptime.uptime,
      platform: os.platform(),
      hostname: os.hostname()
    };
  } catch (error) {
    console.error('Error getting system info:', error);
    return null;
  }
});

// App event handlers
app.whenReady().then(() => {
  createWindow();
  createTray();

  // Register global shortcut for logs toggle
  globalShortcut.register('CmdOrCtrl+`', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('toggle-logs');
    }
  });

  // Handle app activation (macOS)
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });

  // Start periodic system metrics updates
  setInterval(() => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('system-metrics-update');
    }
  }, 2000); // Update every 2 seconds
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

// Handle certificate errors in development
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});
