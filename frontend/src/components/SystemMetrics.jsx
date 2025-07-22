import React from 'react';

const SystemMetrics = ({ metrics, getThemeColor, systemHealth }) => {
  const themeColor = getThemeColor(systemHealth);

  const getMetricIcon = (type) => {
    const icons = {
      CPU: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M9 3V1h2v2h2V1h2v2h3c1.1 0 2 .9 2 2v3h2v2h-2v2h2v2h-2v3c0 1.1-.9 2-2 2h-3v2h-2v-2h-2v2H9v-2H6c-1.1 0-2-.9-2-2v-3H2v-2h2v-2H2V9h2V6c0-1.1.9-2 2-2h3zm0 6v6h6V9H9z"/>
        </svg>
      ),
      GPU: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6 2h12c1.1 0 2 .9 2 2v16c0 1.1-.9 2-2 2H6c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2zm0 2v16h12V4H6zm2 2h8v2H8V6zm0 4h8v2H8v-2zm0 4h5v2H8v-2z"/>
        </svg>
      ),
      RAM: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M15 10H9v4h6v-4zM4 8h2v8H4V8zm14 0h2v8h-2V8zm-8-4h4v2h-4V4zm0 16h4v2h-4v-2z"/>
        </svg>
      ),
      Temperature: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M15 13V5c0-1.66-1.34-3-3-3S9 3.34 9 5v8.28A4.51 4.51 0 005.5 18c0 2.49 2.01 4.5 4.5 4.5s4.5-2.01 4.5-4.5c0-1.67-.91-3.13-2.27-3.94L15 13zM12 4c.55 0 1 .45 1 1v8.72l.5.28A2.5 2.5 0 0115 18c0 1.38-1.12 2.5-2.5 2.5S10 19.38 10 18c0-1.18.82-2.18 1.93-2.45L12 15.28V5c0-.55.45-1 1-1z"/>
        </svg>
      )
    };
    return icons[type] || icons.CPU;
  };

  const getStatusColor = (value, type) => {
    if (type === 'Temperature') {
      if (value > 75) return 'text-red-400';
      if (value > 65) return 'text-yellow-400';
      return 'text-green-400';
    }
    if (value > 85) return 'text-red-400';
    if (value > 70) return 'text-yellow-400';
    return 'text-green-400';
  };

  const MetricCard = ({ title, value, unit = '%', type }) => {
    const statusColor = getStatusColor(value, type);
    const progressWidth = type === 'Temperature' ? Math.min((value / 100) * 100, 100) : Math.min(value, 100);
    
    return (
      <div className="flex-1 bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg p-2 lg:p-3 border border-gray-700/50 hover:border-gray-600/50 transition-all duration-300 group">
        {/* Header */}
        <div className="flex items-center justify-between mb-1 lg:mb-2">
          <div className="flex items-center gap-1">
            <div className={`text-${themeColor}`}>
              <svg className="w-3 h-3 lg:w-4 lg:h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 3V1h2v2h2V1h2v2h3c1.1 0 2 .9 2 2v3h2v2h-2v2h2v2h-2v3c0 1.1-.9 2-2 2h-3v2h-2v-2h-2v2H9v-2H6c-1.1 0-2-.9-2-2v-3H2v-2h2v-2H2V9h2V6c0-1.1.9-2 2-2h3zm0 6v6h6V9H9z"/>
              </svg>
            </div>
            <span className="text-xs lg:text-sm font-medium text-gray-300">{title}</span>
          </div>
          <div className={`text-[10px] lg:text-xs px-1 lg:px-2 py-0.5 lg:py-1 rounded ${statusColor.replace('text-', 'bg-')}/10 ${statusColor} font-semibold`}>
            {value > 85 ? 'H' : value > 70 ? 'N' : 'O'}
          </div>
        </div>

        {/* Value Display */}
        <div className="mb-1 lg:mb-2">
          <div className="flex items-baseline gap-1">
            <span className={`text-lg lg:text-xl font-bold ${statusColor} transition-colors duration-300`}>
              {value}
            </span>
            <span className="text-xs text-gray-400 font-medium">
              {unit}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative">
          <div className="w-full bg-gray-700 rounded-full h-1 lg:h-1.5 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ease-out bg-gradient-to-r ${statusColor.replace('text-', 'from-')} ${statusColor.replace('text-', 'to-')}/70`}
              style={{ width: `${progressWidth}%` }}
            ></div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full mb-3 lg:mb-4 xl:mb-6">
      <div className="mb-2 lg:mb-3 xl:mb-4">
        <h3 className="text-sm lg:text-lg font-semibold text-white mb-1">System Metrics</h3>
        <p className="text-xs lg:text-sm text-gray-400">Real-time performance monitoring</p>
      </div>
      <div className="flex gap-2 lg:gap-3 xl:gap-4">
        <MetricCard title="CPU Usage" value={metrics.cpu} type="CPU" />
        <MetricCard title="GPU Usage" value={metrics.gpu} type="GPU" />
        <MetricCard title="Memory" value={metrics.ram} type="RAM" />
        <MetricCard title="Temperature" value={metrics.temperature} unit="°C" type="Temperature" />
      </div>
    </div>
  );
};

export default SystemMetrics;
