import React from 'react';

const AlertsStrip = ({ alerts, getThemeColor, systemHealth }) => {
  const themeColor = getThemeColor(systemHealth);

  if (!alerts || alerts.length === 0) return null;

  const getAlertType = (alert) => {
    const lowerAlert = alert.toLowerCase();
    if (lowerAlert.includes('error') || lowerAlert.includes('failed') || lowerAlert.includes('high temperature')) {
      return 'error';
    }
    if (lowerAlert.includes('warning') || lowerAlert.includes('warming')) {
      return 'warning';
    }
    if (lowerAlert.includes('info') || lowerAlert.includes('sync') || lowerAlert.includes('update')) {
      return 'info';
    }
    return 'success';
  };

  const getAlertIcon = (type) => {
    const icons = {
      error: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      warning: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
      ),
      info: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      success: (
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      )
    };
    return icons[type] || icons.success;
  };

  const getAlertStyling = (type) => {
    const styles = {
      error: 'bg-red-500/10 border-red-500/30 text-red-400',
      warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
      info: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
      success: `bg-${themeColor}/10 border-${themeColor}/30 text-${themeColor.replace('500', '400')}`
    };
    return styles[type] || styles.success;
  };

  return (
    <div className="w-full mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white">System Notifications</h3>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className={`w-2 h-2 rounded-full bg-${themeColor} animate-pulse`}></div>
          <span>Live</span>
        </div>
      </div>
      
      <div className="relative">
        {/* Background blur effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/50 via-gray-800/30 to-gray-900/50 rounded-xl blur-sm"></div>
        
        {/* Main alerts container */}
        <div className="relative bg-gray-800/60 backdrop-blur-sm rounded-xl border border-gray-700/50 p-4 overflow-hidden">
          <div className="flex gap-3 overflow-x-auto scrollbar-hide">
            {alerts.slice(-5).map((alert, index) => {
              const alertType = getAlertType(alert);
              const alertStyling = getAlertStyling(alertType);
              
              return (
                <div 
                  key={index} 
                  className={`flex-shrink-0 flex items-center gap-3 px-4 py-2 rounded-lg border ${alertStyling} backdrop-blur-sm transition-all duration-300 hover:scale-105 cursor-pointer group`}
                >
                  <div className="flex-shrink-0">
                    {getAlertIcon(alertType)}
                  </div>
                  <span className="text-sm font-medium whitespace-nowrap">
                    {alert}
                  </span>
                  <div className={`w-2 h-2 rounded-full bg-current opacity-60 animate-pulse`}></div>
                </div>
              );
            })}
          </div>
          
          {/* Scroll indicator */}
          {alerts.length > 3 && (
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400">
              <svg className="w-4 h-4 animate-bounce" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertsStrip;
