import axios from 'axios';
import router from '../router';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

const token = localStorage.getItem('token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else {
    delete config.headers.Authorization;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const currentPath = router.currentRoute.value.path;
      const isAuthPage = currentPath.startsWith('/auth/');
      const isPublicPage = currentPath === '/' || isAuthPage;
      
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      
      if (!isPublicPage) {
        router.push('/auth/login');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
