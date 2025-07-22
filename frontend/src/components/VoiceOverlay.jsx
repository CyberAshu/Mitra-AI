import React, { useState, useEffect } from 'react';

const VoiceOverlay = ({ aiStatus, getThemeColor, systemHealth }) => {
  const themeColor = getThemeColor(systemHealth);
  const [isVisible, setIsVisible] = useState(true);
  
  const getStatusIcon = () => {
    switch (aiStatus) {
      case 'Listening':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
          </svg>
        );
      case 'Processing':
        return (
          <svg className="w-5 h-5 animate-spin" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 6v3l4-4-4-4v3c-4.42 0-8 3.58-8 8 0 1.57.46 3.03 1.24 4.26L6.7 14.8c-.45-.83-.7-1.79-.7-2.8 0-3.31 2.69-6 6-6z"/>
            <path d="M18.76 7.74L17.3 9.2c.44.84.7 1.79.7 2.8 0 3.31-2.69 6-6 6v-3l-4 4 4 4v-3c4.42 0 8-3.58 8-8 0-1.57-.46-3.03-1.24-4.26z"/>
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        );
    }
  };

  const getStatusText = () => {
    switch (aiStatus) {
      case 'Listening':
        return 'Voice Input Active';
      case 'Processing':
        return 'Analyzing Command';
      default:
        return 'AI Assistant Ready';
    }
  };

  const getStatusColor = () => {
    switch (aiStatus) {
      case 'Listening':
        return 'from-blue-500 to-cyan-400';
      case 'Processing':
        return `from-${themeColor} to-yellow-400`;
      default:
        return `from-${themeColor} to-${themeColor}/70`;
    }
  };

  // Auto-hide after 3 seconds for non-active states
  useEffect(() => {
    if (aiStatus === 'Idle') {
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, 3000);
      return () => clearTimeout(timer);
    } else {
      setIsVisible(true);
    }
  }, [aiStatus]);

  if (!isVisible && aiStatus === 'Idle') {
    return (
      <div 
        className="fixed bottom-4 left-4 w-12 h-12 bg-gray-800/80 backdrop-blur-sm rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-700/80 transition-all duration-300 border border-gray-600/50"
        onClick={() => setIsVisible(true)}
      >
        <div className={`text-${themeColor} animate-pulse`}>
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-4 left-4 transition-all duration-500 transform ${
      isVisible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
    }`}>
      {/* Main overlay */}
      <div className="relative">
        {/* Glow effect */}
        <div className={`absolute -inset-1 bg-gradient-to-r ${getStatusColor()} rounded-lg blur opacity-30 animate-pulse`}></div>
        
        {/* Main content */}
        <div className="relative bg-gray-800/90 backdrop-blur-sm rounded-lg border border-gray-700/50 overflow-hidden">
          <div className="flex items-center gap-3 px-4 py-3">
            {/* Status icon */}
            <div className={`flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r ${getStatusColor()} ${
              aiStatus === 'Listening' ? 'animate-pulse' : aiStatus === 'Processing' ? 'animate-bounce' : ''
            }`}>
              <div className="text-white">
                {getStatusIcon()}
              </div>
            </div>
            
            {/* Status text */}
            <div className="flex flex-col">
              <span className="text-white font-semibold text-sm">
                {getStatusText()}
              </span>
              <span className="text-gray-400 text-xs">
                {aiStatus === 'Listening' ? 'Speak now...' : 
                 aiStatus === 'Processing' ? 'Please wait...' : 
                 'Say "Hey MITRA" to activate'}
              </span>
            </div>
            
            {/* Close button for idle state */}
            {aiStatus === 'Idle' && (
              <button 
                onClick={() => setIsVisible(false)}
                className="ml-2 text-gray-400 hover:text-white transition-colors duration-200"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            )}
          </div>
          
          {/* Activity indicator bar */}
          <div className="w-full h-1 bg-gray-700">
            <div className={`h-full bg-gradient-to-r ${getStatusColor()} transition-all duration-1000 ${
              aiStatus === 'Processing' ? 'animate-pulse' : ''
            }`} 
                 style={{ width: aiStatus === 'Processing' ? '100%' : aiStatus === 'Listening' ? '60%' : '30%' }}>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceOverlay;
