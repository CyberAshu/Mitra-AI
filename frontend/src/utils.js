export const getThemeColor = (systemHealth) => {
  switch (systemHealth) {
    case 'Healthy': return 'green-500';
    case 'Warming': return 'yellow-500';
    case 'Overheating': return 'red-500';
    case 'Syncing': return 'blue-500';
    default: return 'gray-500';
  }
};

// More realistic metric simulation with some persistence
let previousMetrics = { cpu: 45, gpu: 60, ram: 72, temperature: 58 };

export const simulateMetrics = () => {
  // Add some randomness but keep it realistic
  const variance = 15;
  
  previousMetrics = {
    cpu: Math.max(10, Math.min(90, previousMetrics.cpu + (Math.random() - 0.5) * variance)),
    gpu: Math.max(5, Math.min(95, previousMetrics.gpu + (Math.random() - 0.5) * variance)),
    ram: Math.max(30, Math.min(85, previousMetrics.ram + (Math.random() - 0.5) * 10)),
    temperature: Math.max(35, Math.min(85, previousMetrics.temperature + (Math.random() - 0.5) * 8)),
  };
  
  return {
    cpu: Math.floor(previousMetrics.cpu),
    gpu: Math.floor(previousMetrics.gpu),
    ram: Math.floor(previousMetrics.ram),
    temperature: Math.floor(previousMetrics.temperature),
  };
};

export const simulateAIStatus = () => {
  const statuses = ['Listening', 'Processing', 'Idle'];
  const weights = [0.3, 0.2, 0.5]; // Idle is more common
  const random = Math.random();
  
  if (random < weights[0]) return statuses[0];
  if (random < weights[0] + weights[1]) return statuses[1];
  return statuses[2];
};

export const formatUptime = (seconds) => {
  const days = Math.floor(seconds / (24 * 3600));
  const hours = Math.floor((seconds % (24 * 3600)) / 3600);
  if (days > 0) return `${days} days`;
  if (hours > 0) return `${hours} hours`;
  return `${Math.floor(seconds / 60)} minutes`;
};
