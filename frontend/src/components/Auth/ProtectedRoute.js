import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');

  // Check if user is authenticated
  if (!token || !user) {
    // Redirect to signin page with the return url
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  // Check if token is expired (you can add more sophisticated token validation here)
  try {
    const userData = JSON.parse(user);
    const tokenExpiry = userData.exp || 0;
    const currentTime = Math.floor(Date.now() / 1000);
    
    if (tokenExpiry && currentTime > tokenExpiry) {
      // Token is expired, clear storage and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return <Navigate to="/signin" state={{ from: location }} replace />;
    }
  } catch (error) {
    // Invalid user data, clear storage and redirect
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute; 