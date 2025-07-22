import React, { useState } from 'react';

const RightPanel = ({ aiCoreLoad, backgroundJobs, taskQueue, getThemeColor, systemHealth }) => {
  const themeColor = getThemeColor(systemHealth);
  const [cameraEnabled, setCameraEnabled] = useState(false);

  return (
    <div className="w-1/5 xl:w-1/4 flex flex-col gap-2 lg:gap-3 xl:gap-4 hidden lg:flex">
      {/* Camera Section */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-2 lg:p-3 border border-gray-700/50">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1">
            <div className={`text-${themeColor}`}>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4zM14 13h-3v3H9v-3H6v-2h3V8h2v3h3v2z"/>
              </svg>
            </div>
            <h3 className="text-sm lg:text-base font-semibold text-white">Camera</h3>
          </div>
          <button 
            onClick={() => setCameraEnabled(!cameraEnabled)}
            className={`px-2 py-1 rounded text-xs font-semibold transition-all duration-300 ${
              cameraEnabled 
                ? `bg-${themeColor}/20 text-${themeColor} border border-${themeColor}/30` 
                : 'bg-gray-700 text-gray-400 hover:text-gray-300'
            }`}
          >
            {cameraEnabled ? 'ON' : 'OFF'}
          </button>
        </div>
        
        {/* Camera Feed */}
        <div className={`relative bg-black rounded-lg h-20 lg:h-24 flex items-center justify-center border border-dashed transition-all duration-500 overflow-hidden group ${
          cameraEnabled ? `border-${themeColor}/50` : 'border-gray-700/50'
        }`}>
          {cameraEnabled ? (
            <>
              <div className={`absolute inset-0 bg-${themeColor}/10 animate-pulse`}></div>
              <div className="z-10 text-center">
                <div className={`w-12 h-12 mx-auto mb-2 rounded-full bg-${themeColor} flex items-center justify-center animate-pulse`}>
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                  </svg>
                </div>
                <span className={`text-sm text-${themeColor} font-medium`}>Camera Active</span>
              </div>
            </>
          ) : (
            <div className="z-10 text-center">
              <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-gray-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                </svg>
              </div>
              <span className="text-sm text-gray-400">Camera Offline</span>
            </div>
          )}
        </div>
      </div>

      {/* AI Core Load */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-4 border border-gray-700/50">
        <div className="flex items-center gap-2 mb-4">
          <div className={`text-${themeColor}`}>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white">AI Core Load</h3>
        </div>
        
        <div className="space-y-3">
          <div className="flex justify-between items-baseline">
            <span className="text-sm text-gray-300">Processing</span>
            <div className="text-right">
              <span className={`text-2xl font-bold text-${themeColor}`}>{aiCoreLoad}%</span>
              <div className="text-xs text-gray-400">CPU Usage</div>
            </div>
          </div>
          
          <div className="relative w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-700 bg-gradient-to-r from-${themeColor} to-${themeColor}/70 ${aiCoreLoad > 80 ? 'animate-pulse' : ''}`}
              style={{ width: `${aiCoreLoad}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between text-xs text-gray-400">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>
      </div>

      {/* Background Jobs */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-4 border border-gray-700/50">
        <div className="flex items-center gap-2 mb-4">
          <div className={`text-${themeColor}`}>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white">Background Jobs</h3>
          <span className="text-xs bg-gray-700 px-2 py-1 rounded-full text-gray-300">
            {backgroundJobs.length}
          </span>
        </div>
        
        <div className="space-y-2">
          {backgroundJobs.map((job, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-gray-900/40 rounded-lg border border-gray-700/30 hover:border-gray-600/50 transition-all duration-300 group">
              <div className={`w-3 h-3 rounded-full bg-${themeColor} animate-pulse group-hover:animate-bounce`}></div>
              <span className="text-sm text-gray-300 group-hover:text-gray-200 transition-colors">{job}</span>
              <div className={`ml-auto text-${themeColor} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Task Queue */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg p-2 border border-gray-700/50">
        <div className="flex items-center gap-1 mb-2">
          <div className={`text-${themeColor}`}>
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM9 16H7v-2h2v2zm0-4H7v-2h2v2zm0-4H7V6h2v2zm7 8h-5v-2h5v2zm0-4h-5v-2h5v2zm-2-4V4.5l1.5 1.5H14z"/>
            </svg>
          </div>
          <h3 className="text-xs lg:text-sm font-semibold text-white">Tasks</h3>
          <span className="text-[10px] bg-gray-700 px-1.5 py-0.5 rounded text-gray-300">
            {taskQueue.length}
          </span>
        </div>
        
        <div className="space-y-1">
          {taskQueue.slice(0, 2).map((task, index) => (
            <div key={index} className="flex items-center gap-2 p-1.5 bg-gray-900/40 rounded border border-gray-700/30 hover:border-gray-600/50 transition-all duration-300 group">
              <div className={`w-1.5 h-1.5 rounded-full bg-${themeColor} animate-pulse`}></div>
              <span className="text-xs text-gray-300 group-hover:text-gray-200 transition-colors flex-1">{task}</span>
              <div className={`text-[10px] px-1.5 py-0.5 rounded bg-${themeColor}/10 text-${themeColor} font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300`}>
                Pending
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RightPanel;
