import type { AxiosError } from 'axios';
import api from './api';
import type { User } from '../stores/auth';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async login(credentials: { email: string; password: string }): Promise<User> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    
    const { data } = await api.post<TokenResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    localStorage.setItem('token', data.access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
    return this.getCurrentUser();
  },

  async register(userData: RegisterData): Promise<User> {
    const { data } = await api.post<User>('/auth/register', userData);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No token found');
    }
    
    // Set token in headers
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    try {
      const { data } = await api.get<User>('/user/me');
      return data;
    } catch (error: unknown) {
      // If 401, token is invalid - clear it
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as AxiosError;
        if (axiosError.response?.status === 401) {
          this.logout();
        }
      }
      throw error;
    }
  },

  async updateProfile(payload: { name: string }): Promise<User> {
    const { data } = await api.patch<User>('/user/me', payload);
    return data;
  },

  logout(): void {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },
};
