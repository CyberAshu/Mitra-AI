import React from 'react';

const SystemInfo = ({ systemInfo, getThemeColor, systemHealth }) => {
  const themeColor = getThemeColor(systemHealth);

  const InfoCard = ({ title, value, unit = '', icon }) => (
    <div className="flex-1 bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg p-2 border border-gray-700/50 hover:border-gray-600/50 transition-all duration-300 group text-center">
      <div className="flex items-center justify-center gap-1 mb-1">
        <div className={`text-${themeColor}`}>
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.07 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
          </svg>
        </div>
        <div className="text-xs text-gray-400 font-medium">{title}</div>
      </div>
      <div className={`text-${themeColor} font-bold text-sm`}>
        {value}{unit}
      </div>
    </div>
  );

  const getNetworkIcon = () => (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
      <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.07 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
    </svg>
  );

  const getUptimeIcon = () => (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M16.2,16.2L11,13V7H12.5V12.2L17,14.9L16.2,16.2Z"/>
    </svg>
  );

  const getServicesIcon = () => (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
  );

  return (
    <div className="w-full mt-2">
      <div className="mb-2">
        <h3 className="text-sm lg:text-base font-semibold text-white mb-1">System Information</h3>
        <p className="text-xs text-gray-400">Network, uptime and service status</p>
      </div>
      
      {/* Info Cards */}
      <div className="flex gap-2 mb-3">
        <InfoCard 
          title="Upload" 
          value={systemInfo.networkUp} 
          unit=" Mbps" 
          icon={getNetworkIcon()}
        />
        <InfoCard 
          title="Download" 
          value={systemInfo.networkDown} 
          unit=" Mbps" 
          icon={getNetworkIcon()}
        />
        <InfoCard 
          title="Latency" 
          value={systemInfo.latency} 
          unit=" ms" 
          icon={getNetworkIcon()}
        />
        <InfoCard 
          title="Uptime" 
          value={systemInfo.uptime} 
          icon={getUptimeIcon()}
        />
        <InfoCard 
          title="Services" 
          value={systemInfo.activeServices} 
          icon={getServicesIcon()}
        />
      </div>
    </div>
  );
};

export default SystemInfo;
