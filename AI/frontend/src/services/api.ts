import axios from 'axios';
import type {
  User,
  UserProfile,
  CPU,
  GPU,
  Motherboard,
  RAM,
  Storage,
  PSU,
  Case,
  Cooling,
  Monitor,
  Keyboard,
  Mouse,
  Headset,
  PCConfiguration,
  ConfigurationRequest,
  PaginatedResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000', 10);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Добавляем токен к каждому запросу
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

// Обработка ответов и ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Удаляем токен и перенаправляем на страницу логина
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API методы для компонентов ПК
export const computerAPI = {
  getCPUs: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<CPU>>('/computers/cpu/', { params }),
  
  getGPUs: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<GPU>>('/computers/gpu/', { params }),
  
  getMotherboards: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Motherboard>>('/computers/motherboard/', { params }),
  
  getRAM: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<RAM>>('/computers/ram/', { params }),
  
  getStorage: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Storage>>('/computers/storage/', { params }),
  
  getPSU: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<PSU>>('/computers/psu/', { params }),
  
  getCases: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Case>>('/computers/case/', { params }),
  
  getCooling: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Cooling>>('/computers/cooling/', { params }),
};

// API методы для периферии
export const peripheralAPI = {
  getMonitors: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Monitor>>('/peripherals/monitors/', { params }),
  
  getKeyboards: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Keyboard>>('/peripherals/keyboards/', { params }),
  
  getMice: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Mouse>>('/peripherals/mice/', { params }),
  
  getHeadsets: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Headset>>('/peripherals/headsets/', { params }),
};

// API методы для конфигураций
export const configurationAPI = {
  getConfigurations: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<PCConfiguration>>('/recommendations/configurations/', { params }),
  
  getConfiguration: (id: number) =>
    api.get<PCConfiguration>(`/recommendations/configurations/${id}/`),
  
  generateConfiguration: (data: ConfigurationRequest) =>
    api.post<PCConfiguration & { ai_info?: { ai_used: boolean; summary: string; reasoning?: Record<string, string> } }>(
      '/recommendations/configurations/generate/',
      data
    ),
  
  checkCompatibility: (id: number) =>
    api.post<{ is_compatible: boolean; issues: string[]; notes: string }>(
      `/recommendations/configurations/${id}/check_compatibility/`
    ),
  
  getAIStatus: () =>
    api.get<{ ai_available: boolean; model: string | null }>('/recommendations/configurations/ai_status/'),
  
  saveConfiguration: (id: number, data: Partial<PCConfiguration>) =>
    api.patch<PCConfiguration>(`/recommendations/configurations/${id}/`, data),
  
  deleteConfiguration: (id: number) =>
    api.delete(`/recommendations/configurations/${id}/`),
};

// API методы для пользователей
export const userAPI = {
  register: (data: {
    username: string;
    email: string;
    password: string;
    password2: string;
    user_type: string;
  }) => api.post<User>('/accounts/users/', data),
  
  getCurrentUser: () =>
    api.get<User>('/accounts/users/me/'),
  
  getMyProfile: () =>
    api.get<UserProfile>('/accounts/profiles/my_profile/'),
  
  updateMyProfile: (data: Partial<UserProfile>) =>
    api.patch<UserProfile>('/accounts/profiles/my_profile/', data),
};

// API методы для аутентификации
export const authAPI = {
  login: (data: { username: string; password: string }) =>
    api.post<{ token: string; user: User }>('/accounts/login/', data),
  
  register: (data: { username: string; email: string; password: string }) =>
    api.post<{ token: string; user: User }>('/accounts/register/', data),
  
  logout: () => api.post('/accounts/logout/'),
};

export default api;
