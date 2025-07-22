import React from 'react';

const AiCoreDisplay = ({ aiStatus, systemHealth, getThemeColor }) => {
  const themeColor = getThemeColor(systemHealth);
  
  const statusIcon = {
    'Listening': (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
    ),
    'Processing': (
      <svg className="w-8 h-8 animate-spin" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        <path d="M12 6c3.79 0 7 2.96 7 6.71-.74-.16-1.39-.49-1.93-.99A4.93 4.93 0 0012 8c-1.54 0-2.96.66-3.93 1.72-.54.5-1.19.83-1.93.99C6.14 8.96 8.21 6 12 6z"/>
      </svg>
    ),
    'Idle': (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.1 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
      </svg>
    )
  };

  return (
    <div className="flex flex-col items-center justify-center relative">
      {/* Main AI Core Container */}
      <div className="relative">
        {/* Outer glow ring */}
        <div className={`absolute -inset-4 rounded-full bg-gradient-to-r from-${themeColor}/20 via-${themeColor}/10 to-transparent blur-xl animate-pulse`}></div>
        
        {/* Main core circle */}
        <div className={`relative w-24 h-24 lg:w-32 lg:h-32 xl:w-40 xl:h-40 rounded-full bg-gradient-to-br from-gray-800 via-gray-900 to-black border-2 border-${themeColor}/30 flex items-center justify-center shadow-2xl overflow-hidden`}>
          
          {/* Rotating outer ring */}
          <div className={`absolute inset-3 lg:inset-6 rounded-full border border-dashed border-${themeColor}/40 animate-spin-slow`}></div>
          
          {/* Center content container */}
          <div className="relative z-20 text-center px-2 lg:px-4">
            {/* Logo/Brand */}
            <div className="mb-1 lg:mb-2">
              <div className={`w-6 h-6 lg:w-8 lg:h-8 xl:w-10 xl:h-10 mx-auto mb-1 lg:mb-2 rounded-lg bg-gradient-to-br from-${themeColor} to-${themeColor}/70 flex items-center justify-center shadow-lg`}>
                <span className="text-white font-bold text-xs lg:text-sm xl:text-base">M</span>
              </div>
              <h1 className="text-sm lg:text-lg xl:text-xl font-light text-white mb-0.5 tracking-wider">MITRA</h1>
              <div className="text-[10px] lg:text-xs text-gray-400 font-medium tracking-wide">AI ASSISTANT</div>
            </div>
            
            {/* Status indicator */}
            <div className="flex items-center justify-center gap-1 lg:gap-2 mb-2">
              <div className={`text-${themeColor} transition-all duration-500`}>
                <svg className="w-3 h-3 lg:w-4 lg:h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.1 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
                </svg>
              </div>
              <div className={`text-${themeColor} text-xs lg:text-sm font-semibold transition-all duration-300`}>
                {aiStatus}
              </div>
            </div>
            
            {/* Status bar */}
            <div className="w-full h-0.5 lg:h-1 bg-gray-700 rounded-full overflow-hidden">
              <div className={`h-full bg-gradient-to-r from-${themeColor} to-${themeColor}/70 rounded-full transition-all duration-1000 ${aiStatus === 'Processing' ? 'animate-pulse' : ''}`} 
                   style={{ width: aiStatus === 'Processing' ? '100%' : aiStatus === 'Listening' ? '60%' : '30%' }}></div>
            </div>
          </div>
          
          {/* Animated background pattern */}
          <div className="absolute inset-0 opacity-5">
            <div className={`absolute top-1/4 left-1/4 w-2 h-2 bg-${themeColor} rounded-full animate-ping`} style={{ animationDelay: '0s' }}></div>
            <div className={`absolute top-3/4 right-1/4 w-1 h-1 bg-${themeColor} rounded-full animate-ping`} style={{ animationDelay: '1s' }}></div>
            <div className={`absolute bottom-1/4 left-1/3 w-1.5 h-1.5 bg-${themeColor} rounded-full animate-ping`} style={{ animationDelay: '2s' }}></div>
          </div>
        </div>
      </div>
      
      {/* System health indicator */}
      <div className="mt-3 lg:mt-4 flex items-center gap-2">
        <div className={`w-2 h-2 lg:w-3 lg:h-3 rounded-full bg-${themeColor} animate-pulse`}></div>
        <span className="text-xs lg:text-sm text-gray-400 font-medium">Status: </span>
        <span className={`text-${themeColor} text-xs lg:text-sm font-semibold capitalize`}>{systemHealth}</span>
      </div>
    </div>
  );
};

export default AiCoreDisplay;
