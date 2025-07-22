import React, { useState } from 'react';

const LeftPanel = ({ logs, services, storageUsed, getThemeColor, systemHealth, systemInfo }) => {
  const themeColor = getThemeColor(systemHealth);
  const [activeTab, setActiveTab] = useState('logs');

  const ServiceIndicator = ({ service, status }) => {
    const isRunning = status === 'Running';
    return (
      <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg border border-gray-600/30 hover:border-gray-500/50 transition-all duration-300 group">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500' : 'bg-red-500'} shadow-lg animate-pulse`}></div>
          <div>
            <span className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">{service}</span>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                isRunning 
                  ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                {status}
              </span>
            </div>
          </div>
        </div>
        <div className={`text-${themeColor} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}>
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
          </svg>
        </div>
      </div>
    );
  };

  const TabButton = ({ id, label, icon, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
        isActive 
          ? `bg-${themeColor}/20 text-${themeColor} border border-${themeColor}/30` 
          : 'text-gray-400 hover:text-gray-300 hover:bg-gray-700/50'
      }`}
    >
      {icon}
      <span className="text-sm">{label}</span>
    </button>
  );

  return (
    <div className="w-1/5 xl:w-1/4 flex flex-col gap-3 lg:gap-4 xl:gap-6 hidden lg:flex">
      {/* Tab Navigation */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-2 lg:p-3 border border-gray-700/50">
        <div className="flex gap-1 mb-2">
          <TabButton
            id="logs"
            label="Logs"
            icon={<svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/></svg>}
            isActive={activeTab === 'logs'}
            onClick={setActiveTab}
          />
          <TabButton
            id="services"
            label="Services"
            icon={<svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>}
            isActive={activeTab === 'services'}
            onClick={setActiveTab}
          />
          <TabButton
            id="processes"
            label="Processes"
            icon={<svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>}
            isActive={activeTab === 'processes'}
            onClick={setActiveTab}
          />
        </div>
        
        {/* Tab Content */}
        <div className="h-32 lg:h-40 overflow-hidden">
          {activeTab === 'logs' && (
            <div className="h-full">
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-sm lg:text-lg font-semibold text-white">System Logs</h3>
                <div className={`w-2 h-2 rounded-full bg-${themeColor} animate-pulse`}></div>
              </div>
              <div className="bg-black/30 rounded-lg p-2 h-24 lg:h-32 overflow-y-auto backdrop-blur-sm border border-gray-700/30">
                {logs.map((log, index) => (
                  <div key={index} className="flex items-start gap-2 mb-2 text-xs font-mono group hover:bg-gray-700/20 rounded p-1 transition-colors">
                    <span className="text-gray-500 flex-shrink-0">{String(index + 1).padStart(2, '0')}</span>
                    <span className="text-gray-300 group-hover:text-gray-200 leading-relaxed">{log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {activeTab === 'services' && (
            <div className="h-full">
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-lg font-semibold text-white">Service Status</h3>
                <span className="text-xs bg-gray-700 px-2 py-1 rounded-full text-gray-300">
                  {services.filter(s => s.status === 'Running').length}/{services.length} Active
                </span>
              </div>
              <div className="space-y-2 h-48 overflow-y-auto">
                {services.map((service, index) => (
                  <ServiceIndicator key={index} {...service} />
                ))}
              </div>
            </div>
          )}
          
          {activeTab === 'processes' && (
            <div className="h-full">
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-sm lg:text-lg font-semibold text-white">AI Processes</h3>
                <div className={`w-2 h-2 rounded-full bg-${themeColor} animate-pulse`}></div>
              </div>
              <div className="space-y-1 h-24 lg:h-32 overflow-y-auto">
                {systemInfo.processes.map((process, index) => (
                  <div key={index} className="flex items-center gap-2 p-1.5 bg-gray-900/40 rounded border border-gray-700/30 hover:border-gray-600/50 transition-all duration-300 group">
                    <div className={`w-1.5 h-1.5 rounded-full bg-${themeColor} animate-pulse`}></div>
                    <span className="text-xs text-gray-300 group-hover:text-gray-200 transition-colors flex-1">{process}</span>
                    <div className={`text-[10px] px-1.5 py-0.5 rounded bg-${themeColor}/10 text-${themeColor} font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300`}>
                      Active
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Storage Section */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-4 border border-gray-700/50">
        <div className="flex items-center gap-2 mb-4">
          <div className={`text-${themeColor}`}>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20 6h-2l-2-2H8L6 6H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zM18 18H6V8h2.83l2-2h2.34l2 2H18v10z"/>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white">Storage</h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex justify-between items-baseline">
            <span className="text-sm text-gray-300">Used Space</span>
            <div className="text-right">
              <span className={`text-2xl font-bold text-${themeColor}`}>{storageUsed}%</span>
              <div className="text-xs text-gray-400">of total capacity</div>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="relative w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-700 ease-out bg-gradient-to-r from-${themeColor} to-${themeColor}/70`}
                style={{ width: `${storageUsed}%` }}
              ></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-full flex justify-between px-1">
                  {[25, 50, 75].map(mark => (
                    <div key={mark} className="w-0.5 h-1.5 bg-gray-600 rounded-full"></div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex justify-between text-xs text-gray-400">
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
              <span>75%</span>
              <span>100%</span>
            </div>
          </div>
          
          <div className={`text-xs p-2 rounded-lg ${
            storageUsed > 85 
              ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
              : storageUsed > 70 
                ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                : `bg-${themeColor}/10 text-${themeColor.replace('500', '400')} border border-${themeColor}/20`
          }`}>
            {storageUsed > 85 ? 'Storage almost full' : storageUsed > 70 ? 'Storage getting full' : 'Storage healthy'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeftPanel;
