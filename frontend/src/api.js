import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('devflow_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred.';
    if (error.response?.data?.error) {
      message = error.response.data.error;
    } else if (typeof error.response?.data?.detail === 'string') {
      message = error.response.data.detail;
    } else if (Array.isArray(error.response?.data?.detail)) {
      message = "Validation Error: Please check your input.";
    }
    
    // Dispatch custom event for the Toast component
    window.dispatchEvent(new CustomEvent('devflow-toast', { detail: message }));
    
    return Promise.reject(error);
  }
);

export default api;
