import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem('access_token'); // Ensure it's a boolean

  return isAuthenticated ? children : <Navigate to="/Login_page" />;
};

export default ProtectedRoute;
