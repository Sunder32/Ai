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
  Webcam,
  Microphone,
  Desk,
  Chair,
  Speakers,
  Mousepad,
  MonitorArm,
  USBHub,
  DeskLighting,
  StreamDeck,
  CaptureCard,
  Gamepad,
  HeadphoneStand,
  PCConfiguration,
  ConfigurationRequest,
  PaginatedResponse,
} from '../types';

// Увеличен таймаут для AI генерации (5 минут)
const API_TIMEOUT = 300000;

const api = axios.create({
  // baseURL будет установлен динамически через interceptor
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Интерсептор для динамического определения baseURL и токена
api.interceptors.request.use(
  (config) => {
    // Динамически определяем baseURL при каждом запросе
    let baseURL = '/api'; // по умолчанию относительный путь
    
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      // Для localhost используем локальный бэкенд
      if (hostname === 'localhost' || hostname === '127.0.0.1') {
        baseURL = 'http://localhost:8001/api';
      }
      // Для CloudPub фронтенда - используем CloudPub бэкенд
      else if (hostname.includes('cloudpub.ru')) {
        // Бэкенд на illicitly-frank-bulbul.cloudpub.ru
        baseURL = 'https://illicitly-frank-bulbul.cloudpub.ru/api';
      }
    }
    
    config.baseURL = baseURL;
    
    // Добавляем токен авторизации
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
  
  getWebcams: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Webcam>>('/peripherals/webcams/', { params }),
  
  getMicrophones: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Microphone>>('/peripherals/microphones/', { params }),
  
  getDesks: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Desk>>('/peripherals/desks/', { params }),
  
  getChairs: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Chair>>('/peripherals/chairs/', { params }),
  
  getSpeakers: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Speakers>>('/peripherals/speakers/', { params }),
  
  getMousepads: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Mousepad>>('/peripherals/mousepads/', { params }),
  
  getMonitorArms: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<MonitorArm>>('/peripherals/monitor-arms/', { params }),
  
  getUSBHubs: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<USBHub>>('/peripherals/usb-hubs/', { params }),
  
  getLighting: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<DeskLighting>>('/peripherals/lighting/', { params }),
  
  getStreamDecks: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<StreamDeck>>('/peripherals/stream-decks/', { params }),
  
  getCaptureCards: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<CaptureCard>>('/peripherals/capture-cards/', { params }),
  
  getGamepads: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Gamepad>>('/peripherals/gamepads/', { params }),
  
  getHeadphoneStands: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<HeadphoneStand>>('/peripherals/headphone-stands/', { params }),
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
  
  // Новые методы для Build Yourself
  saveBuild: (data: BuildRequest) =>
    api.post<PCConfiguration & { share_url?: string }>('/recommendations/configurations/save_build/', data),
  
  getPublicBuild: (shareCode: string) =>
    api.get<PCConfiguration>(`/recommendations/configurations/public/${shareCode}/`),
  
  getMyBuilds: () =>
    api.get<PCConfiguration[]>('/recommendations/configurations/my_builds/'),
  
  compareBuilds: (ids: number[]) =>
    api.get<PCConfiguration[]>('/recommendations/configurations/compare/', { 
      params: { ids: ids.join(',') },
      paramsSerializer: () => ids.map(id => `ids=${id}`).join('&')
    }),
};

// Тип запроса для сохранения сборки
export interface BuildRequest {
  name: string;
  is_public?: boolean;
  // PC компоненты
  cpu?: number | null;
  gpu?: number | null;
  motherboard?: number | null;
  ram?: number | null;
  storage_primary?: number | null;
  storage_secondary?: number | null;
  psu?: number | null;
  case?: number | null;
  cooling?: number | null;
  // Периферия
  monitor_primary?: number | null;
  monitor_secondary?: number | null;
  keyboard?: number | null;
  mouse?: number | null;
  headset?: number | null;
  webcam?: number | null;
  microphone?: number | null;
  desk?: number | null;
  chair?: number | null;
  speakers?: number | null;
  mousepad?: number | null;
  monitor_arm?: number | null;
  usb_hub?: number | null;
  lighting?: number | null;
  stream_deck?: number | null;
  capture_card?: number | null;
  gamepad?: number | null;
  headphone_stand?: number | null;
}

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
  
  register: (data: { username: string; email: string; password: string; password2: string }) =>
    api.post<{ token: string; user: User }>('/accounts/register/', data),
  
  logout: () => api.post('/accounts/logout/'),
};

export default api;
