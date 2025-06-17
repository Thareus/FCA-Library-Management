import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// Create a base axios instance with common configuration
const createApiClient = (): AxiosInstance => {
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add a request interceptor to include the auth token if it exists
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Token ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) { // Unauthorised
        // Redirect to login
        clearAuthToken();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return api;
};

// Export the api client instance
export const apiClient = createApiClient();

// Helper to set the auth token in both localStorage and axios defaults
export const setAuthToken = (token: string) => {
  localStorage.setItem('token', token);
  apiClient.defaults.headers.Authorization = `Token ${token}`;
};

// Helper to clear the auth token from storage and axios defaults
export const clearAuthToken = () => {
  localStorage.removeItem('token');
  delete apiClient.defaults.headers.Authorization;
};

// Custom hook to use the API client
export const useApi = () => {
  return apiClient;
};

// Types for our API responses
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: any;
  config: any;
}

// Helper functions for common CRUD operations with proper typing
export const api = {
  /**
   * GET request
   * @template T - Expected response type
   * @param {string} url - The URL to send the request to
   * @param {AxiosRequestConfig} [config] - Optional axios config
   * @returns {Promise<T>} - The response data
   */
  get: async <T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  },
  
  /**
   * POST request
   * @template T - Expected response type
   * @template D - Request data type
   * @param {string} url - The URL to send the request to
   * @param {D} data - The data to send with the request
   * @param {AxiosRequestConfig} [config] - Optional axios config
   * @returns {Promise<T>} - The response data
   */
  post: async <T = any, D = any>(
    url: string, 
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.post<T>(url, data, config);
    return response.data;
  },
  
  /**
   * PUT request
   * @template T - Expected response type
   * @template D - Request data type
   * @param {string} url - The URL to send the request to
   * @param {D} data - The data to send with the request
   * @param {AxiosRequestConfig} [config] - Optional axios config
   * @returns {Promise<T>} - The response data
   */
  put: async <T = any, D = any>(
    url: string, 
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    console.log(url)
    const response = await apiClient.put<T>(url, data, config);
    return response.data;
  },
  
  /**
   * DELETE request
   * @template T - Expected response type
   * @param {string} url - The URL to send the request to
   * @param {AxiosRequestConfig} [config] - Optional axios config
   * @returns {Promise<T>} - The response data
   */
  delete: async <T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.delete<T>(url, config);
    return response.data;
  },
  
  /**
   * PATCH request
   * @template T - Expected response type
   * @template D - Request data type
   * @param {string} url - The URL to send the request to
   * @param {D} data - The data to send with the request
   * @param {AxiosRequestConfig} [config] - Optional axios config
   * @returns {Promise<T>} - The response data
   */
  patch: async <T = any, D = any>(
    url: string, 
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.patch<T>(url, data, config);
    return response.data;
  },
};
