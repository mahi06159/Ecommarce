import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (res) => {
    if (res.data && typeof res.data.success !== 'undefined') {
      res.data = res.data.data;
    }
    return res.data;
  },
  async (error) => {
    const originalRequest = error.config;
    // Prevent infinite loop if refreshing fails
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/token/refresh/')) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          // Request refresh using standard axios instance to avoid infinite loop
          const res = await axios.post('/api/auth/token/refresh/', { refresh: refreshToken });
          
          let newAccess = null;
          if (res.data) {
            if (typeof res.data.success !== 'undefined') {
              newAccess = res.data.data?.access;
            } else {
              newAccess = res.data.access;
            }
          }
          
          if (newAccess) {
            localStorage.setItem('access_token', newAccess);
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
          // Refresh token is expired or invalid, log out
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.dispatchEvent(new Event('auth-logout'));
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
export { api };
