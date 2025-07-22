import React, { useState } from 'react';

const DataLogs = ({ isOpen, onClose, logs, getThemeColor, systemHealth }) => {
  const [activeFilter, setActiveFilter] = useState('All');
  const themeColor = getThemeColor(systemHealth);

  const filters = ['All', 'Errors', 'System', 'AI', 'Sync'];

  const filteredLogs = logs.filter(log => {
    if (activeFilter === 'All') return true;
    if (activeFilter === 'Errors') return log.toLowerCase().includes('error') || log.toLowerCase().includes('failed');
    if (activeFilter === 'System') return log.toLowerCase().includes('system') || log.toLowerCase().includes('network');
    if (activeFilter === 'AI') return log.toLowerCase().includes('ai') || log.toLowerCase().includes('voice');
    if (activeFilter === 'Sync') return log.toLowerCase().includes('sync') || log.toLowerCase().includes('data');
    return true;
  });

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
      <div className="bg-gray-800 rounded-lg p-6 w-11/12 h-4/5 max-w-4xl flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Data Logs</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors duration-200 text-xl"
            aria-label="Close logs"
          >
            ✕
          </button>
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2 mb-4 flex-wrap">
          {filters.map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-3 py-1 rounded text-sm transition-colors duration-200 ${
                activeFilter === filter
                  ? `bg-${themeColor} text-gray-900`
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Stats Bar */}
        <div className="flex gap-4 mb-4 text-sm">
          <span className="text-gray-400">Total Logs: {logs.length}</span>
          <span className="text-gray-400">Filtered: {filteredLogs.length}</span>
          <span className={`text-${themeColor}`}>Active Filter: {activeFilter}</span>
        </div>

        {/* Logs Container */}
        <div className="flex-1 bg-gray-900 rounded-lg p-4 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto font-mono text-sm">
            {filteredLogs.length > 0 ? (
              filteredLogs.map((log, index) => (
                <div
                  key={index}
                  className={`py-1 px-2 border-l-2 border-${themeColor} mb-1 hover:bg-gray-800 transition-colors duration-150`}
                >
                  <span className="text-gray-400 mr-2">{index + 1}.</span>
                  <span className="text-white">{log}</span>
                </div>
              ))
            ) : (
              <div className="text-gray-400 text-center py-8">
                No logs found for filter: {activeFilter}
              </div>
            )}
          </div>

          {/* Auto-scroll indicator */}
          <div className="mt-2 text-xs text-gray-500 text-center">
            Press Ctrl+` (or Cmd+`) to toggle this view
          </div>
        </div>

        {/* Footer */}
        <div className="mt-4 flex justify-between items-center text-sm text-gray-400">
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
          <button
            onClick={() => {
              // Simulate clearing logs
              console.log('Clear logs clicked');
            }}
            className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors duration-200"
          >
            Clear Logs
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataLogs;
