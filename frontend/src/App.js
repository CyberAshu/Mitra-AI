import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import AiCoreDisplay from './components/AiCoreDisplay';
import SystemMetrics from './components/SystemMetrics';
import SystemInfo from './components/SystemInfo';
import VoiceOverlay from './components/VoiceOverlay';
import AlertsStrip from './components/AlertsStrip';
import LeftPanel from './components/LeftPanel';
import RightPanel from './components/RightPanel';
import DataLogs from './components/DataLogs';
import { getThemeColor, simulateAIStatus } from './utils';

function App() {
  const [aiStatus, setAiStatus] = useState('Idle');
  const [systemHealth, setSystemHealth] = useState('Healthy');
  const [metrics, setMetrics] = useState({ cpu: 45, gpu: 60, ram: 72, temperature: 58 });
  const [systemInfo, setSystemInfo] = useState({
    networkUp: 100,
    networkDown: 50,
    latency: 12,
    uptime: '24 days',
    activeServices: 5,
    processes: ['AI Core: Active', 'Data Sync: 80% Complete', 'Voice Recognition: Ready'],
  });
  const [alerts, setAlerts] = useState(['System Healthy', 'AI Core Online', 'All Services Running']);
  const [logs, setLogs] = useState([
    '[15:30:45] AI Core initialized successfully',
    '[15:30:46] Voice recognition module loaded',
    '[15:30:47] Camera feed connected',
    '[15:30:48] Network status: Connected',
    '[15:30:49] System ready for commands',
  ]);
  const [services] = useState([
    { service: 'AI Core', status: 'Running' },
    { service: 'Voice Recognition', status: 'Running' },
    { service: 'Camera Service', status: 'Running' },
    { service: 'Network Monitor', status: 'Running' },
    { service: 'Data Sync', status: 'Stopped' },
  ]);
  const [storageUsed] = useState(67);
  const [aiCoreLoad] = useState(60);
  const [backgroundJobs] = useState(['Data Sync: Running', 'Model Training: Queued']);
  const [taskQueue] = useState(['Voice Command: Awaiting', 'Process Audio: Ready']);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [isElectron] = useState(typeof window !== 'undefined' && window.electronAPI);

  // Function to fetch real system metrics from Electron
  const fetchSystemMetrics = useCallback(async () => {
    if (isElectron && window.electronAPI) {
      try {
        const data = await window.electronAPI.getSystemMetrics();
        if (data) {
          setMetrics({
            cpu: data.cpu.usage,
            gpu: data.gpu ? 50 : 0, // GPU usage not directly available
            ram: data.memory.usage,
            temperature: data.temperature.main || 40
          });

          // Update system health based on real temperature
          const temp = data.temperature.main || 40;
          if (temp > 75) {
            setSystemHealth('Overheating');
            setAlerts(prev => [...prev.slice(-2), 'High Temperature Detected!']);
          } else if (temp > 65) {
            setSystemHealth('Warming');
          } else {
            setSystemHealth('Healthy');
          }
        }
      } catch (error) {
        console.error('Error fetching system metrics:', error);
      }
    }
  }, [isElectron]);

  // Function to fetch system info from Electron
  const fetchSystemInfo = useCallback(async () => {
    if (isElectron && window.electronAPI) {
      try {
        const data = await window.electronAPI.getSystemInfo();
        if (data) {
          setSystemInfo({
            networkUp: Math.round((data.network.tx_sec || 0) / 1024), // Convert to KB/s
            networkDown: Math.round((data.network.rx_sec || 0) / 1024),
            latency: 12, // Placeholder
            uptime: formatUptime(data.uptime),
            activeServices: 5,
            processes: data.processes.slice(0, 3).map(p => `${p.name}: ${p.cpu.toFixed(1)}%`)
          });
        }
      } catch (error) {
        console.error('Error fetching system info:', error);
      }
    }
  }, [isElectron]);

  // Helper function to format uptime
  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / (24 * 60 * 60));
    const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60));
    return `${days}d ${hours}h`;
  };

  useEffect(() => {
   
    const statusInterval = setInterval(() => {
      setAiStatus(simulateAIStatus());
    }, 5000);

    // Fetch real system metrics if in Electron, otherwise simulate
    const metricsInterval = setInterval(() => {
      if (isElectron) {
        fetchSystemMetrics();
        fetchSystemInfo();
      } else {
        // Fallback simulation for web browser
        const simulatedMetrics = {
          cpu: Math.floor(Math.random() * 40) + 20,
          gpu: Math.floor(Math.random() * 30) + 40,
          ram: Math.floor(Math.random() * 30) + 50,
          temperature: Math.floor(Math.random() * 20) + 40
        };
        setMetrics(simulatedMetrics);
      }
    }, 2000);

    // System logs simulation
    const logsInterval = setInterval(() => {
      const logMessages = [
        'System check completed',
        'Processing voice command',
        'AI model updated',
        'Network ping: 12ms',
        'Storage cleanup initiated',
        'Memory usage optimized',
        'Background sync completed',
        'Security scan passed'
      ];
      
      const newLog = `[${new Date().toTimeString().split(' ')[0]}] ${logMessages[Math.floor(Math.random() * logMessages.length)]}`;
      setLogs(prev => [...prev.slice(-9), newLog]);
    }, 10000);

    // Initial fetch
    if (isElectron) {
      fetchSystemMetrics();
      fetchSystemInfo();
    }

    // Electron event listeners
    if (isElectron && window.electronAPI) {
      const cleanup1 = window.electronAPI.onSystemMetricsUpdate(() => {
        fetchSystemMetrics();
        fetchSystemInfo();
      });

      const cleanup2 = window.electronAPI.onToggleLogs(() => {
        setIsLogsOpen(prev => !prev);
      });

      return () => {
        clearInterval(statusInterval);
        clearInterval(metricsInterval);
        clearInterval(logsInterval);
        cleanup1();
        cleanup2();
      };
    }

    return () => {
      clearInterval(statusInterval);
      clearInterval(metricsInterval);
      clearInterval(logsInterval);
    };
  }, [fetchSystemMetrics, fetchSystemInfo, isElectron]);

  return (
    <div className="h-screen w-screen bg-gray-900 text-white font-sans overflow-hidden relative">
      
      {/* Desktop Layout */}
      <div className="hidden lg:flex lg:flex-row lg:h-full lg:p-2 lg:gap-2 xl:p-4 xl:gap-4 relative z-10">
        <LeftPanel 
          logs={logs}
          services={services}
          storageUsed={storageUsed}
          getThemeColor={getThemeColor}
          systemHealth={systemHealth}
          systemInfo={systemInfo}
        />
        
        <div className="flex-1 flex flex-col">
          <AlertsStrip alerts={alerts} getThemeColor={getThemeColor} systemHealth={systemHealth} />
          <SystemMetrics metrics={metrics} getThemeColor={getThemeColor} systemHealth={systemHealth} />
          <div className="flex-1 flex items-center justify-center">
            <AiCoreDisplay aiStatus={aiStatus} systemHealth={systemHealth} getThemeColor={getThemeColor} />
          </div>
          <SystemInfo systemInfo={systemInfo} getThemeColor={getThemeColor} systemHealth={systemHealth} />
        </div>
        
        <RightPanel 
          aiCoreLoad={aiCoreLoad}
          backgroundJobs={backgroundJobs}
          taskQueue={taskQueue}
          getThemeColor={getThemeColor}
          systemHealth={systemHealth}
        />
      </div>

      {/* Mobile/Tablet Layout */}
      <div className="lg:hidden flex flex-col min-h-screen p-4 gap-4 relative z-10">
        <AlertsStrip alerts={alerts} getThemeColor={getThemeColor} systemHealth={systemHealth} />
        <SystemMetrics metrics={metrics} getThemeColor={getThemeColor} systemHealth={systemHealth} />
        <div className="flex-1 flex items-center justify-center py-8">
          <AiCoreDisplay aiStatus={aiStatus} systemHealth={systemHealth} getThemeColor={getThemeColor} />
        </div>
        <SystemInfo systemInfo={systemInfo} getThemeColor={getThemeColor} systemHealth={systemHealth} />
      </div>

      <VoiceOverlay aiStatus={aiStatus} getThemeColor={getThemeColor} systemHealth={systemHealth} />
      
      {/* Data Logs Modal/Overlay */}
      <div className="relative z-50">
        <DataLogs 
          isOpen={isLogsOpen}
          onClose={() => setIsLogsOpen(false)}
          logs={logs}
          getThemeColor={getThemeColor}
          systemHealth={systemHealth}
        />
      </div>
    </div>
  );
}

export default App;
