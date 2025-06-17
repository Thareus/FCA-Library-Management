import { useState, useEffect } from 'react';
import {api} from '../api/apiClient';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isStaff, setIsStaff] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [user, setUser] = useState<{
    id: number;
    email: string;
    is_staff: boolean;
  } | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await api.get('/users/me/', {
          headers: { 'Authorization': `Token ${token}` }
        });
        
        setIsAuthenticated(true);
        setIsStaff(response.is_staff || false);
        setUser({
          id: response.id,
          email: response.email,
          is_staff: response.is_staff
        });
      } catch (error) {
        console.error('Authentication check failed:', error);
        localStorage.removeItem('token');
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, []);

  return { isAuthenticated, isStaff, isLoading, user };
};
