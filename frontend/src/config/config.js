// Configuration file for environment variables
// This file centralizes all environment variable access

const config = {
  // Backend API Configuration
  backendUrl: process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000',
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api',
  
  // Frontend Configuration
  frontendUrl: process.env.REACT_APP_FRONTEND_URL || 'http://localhost:3000',
  
  // Application Configuration
  appName: process.env.REACT_APP_APP_NAME || 'Your Stock.ai',
  version: process.env.REACT_APP_VERSION || '1.0.0',
  
  // Feature Flags
  enableAnalytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
  enableMockData: process.env.REACT_APP_ENABLE_MOCK_DATA === 'true',
  
  // Chart Configuration
  chartAnimationDuration: parseInt(process.env.REACT_APP_CHART_ANIMATION_DURATION) || 1000,
  chartUpdateInterval: parseInt(process.env.REACT_APP_CHART_UPDATE_INTERVAL) || 30000,
  
  // Authentication Configuration
  googleClientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || '',
  authRedirectUrl: process.env.REACT_APP_AUTH_REDIRECT_URL || 'http://localhost:3000'
};

// Helper function to build API URLs
config.buildApiUrl = (endpoint) => {
  const baseUrl = config.apiBaseUrl.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.replace(/^\//, ''); // Remove leading slash
  return `${baseUrl}/${cleanEndpoint}`;
};

export default config; 