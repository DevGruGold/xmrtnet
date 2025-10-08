// API Configuration
const config = {
  // Use environment variable if available, otherwise use production URL
  API_URL: process.env.REACT_APP_API_URL || 'https://xmrt-eliza-enhanced.onrender.com',
  
  // API endpoints
  endpoints: {
    eliza: '/api/eliza',
    elizaHealth: '/api/eliza/health',
    elizaActivity: '/api/eliza/activity',
    elizaStats: '/api/eliza/stats'
  },
  
  // Polling interval for realtime updates (in milliseconds)
  ACTIVITY_POLL_INTERVAL: 30000, // 30 seconds
  
  // Feature flags
  features: {
    realtimeActivity: true,
    elizaChat: true,
    activityNotifications: true
  }
};

export default config;
