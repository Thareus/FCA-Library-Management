import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { api, clearAuthToken } from '../api/apiClient';
import { API_PATHS } from '../utils/apiPaths';

export const ProtectedRoute = ({ children, requireStaff = false }: { 
  children: React.ReactNode;
  requireStaff?: boolean;
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isStaff, setIsStaff] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }

      try {
        const response = await api.get(API_PATHS.CURRENT_USER);

        setIsAuthenticated(true);
        setIsStaff(response.is_staff || false);
      } catch (error) {
        console.error('Authentication check failed:', error);
        clearAuthToken();
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>; // Or a loading spinner
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireStaff && !isStaff) {
    return <Navigate to="/" replace />; // Or to a 'not authorized' page
  }

  return <>{children}</>;
};
