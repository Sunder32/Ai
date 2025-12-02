// Типы для пользователей
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'designer' | 'programmer' | 'gamer' | 'office' | 'student' | 'content_creator';
  phone?: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: number;
  user: User;
  min_budget: number;
  max_budget: number;
  priority: 'performance' | 'silence' | 'compactness' | 'aesthetics';
  multitasking: boolean;
  work_with_4k: boolean;
  vr_support: boolean;
  video_editing: boolean;
  gaming: boolean;
  streaming: boolean;
  has_existing_components: boolean;
  existing_components_description?: string;
  created_at: string;
  updated_at: string;
}

// Типы для компонентов ПК
export interface CPU {
  id: number;
  name: string;
  manufacturer: string;
  socket: string;
  cores: number;
  threads: number;
  base_clock: number;
  boost_clock?: number;
  tdp: number;
  price: string;
  performance_score: number;
  created_at: string;
  updated_at: string;
}

export interface GPU {
  id: number;
  name: string;
  manufacturer: string;
  chipset: string;
  memory: number;
  memory_type: string;
  core_clock: number;
  boost_clock?: number;
  tdp: number;
  recommended_psu: number;
  price: string;
  performance_score: number;
  created_at: string;
  updated_at: string;
}

export interface Motherboard {
  id: number;
  name: string;
  manufacturer: string;
  socket: string;
  chipset: string;
  form_factor: string;
  memory_slots: number;
  max_memory: number;
  memory_type: string;
  pcie_slots: number;
  m2_slots: number;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface RAM {
  id: number;
  name: string;
  manufacturer: string;
  memory_type: string;
  capacity: number;
  speed: number;
  modules: number;
  cas_latency?: string;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Storage {
  id: number;
  name: string;
  manufacturer: string;
  storage_type: 'ssd_nvme' | 'ssd_sata' | 'hdd';
  capacity: number;
  read_speed?: number;
  write_speed?: number;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface PSU {
  id: number;
  name: string;
  manufacturer: string;
  wattage: number;
  efficiency_rating: string;
  modular: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Case {
  id: number;
  name: string;
  manufacturer: string;
  form_factor: string;
  max_gpu_length?: number;
  fan_slots: number;
  rgb: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Cooling {
  id: number;
  name: string;
  manufacturer: string;
  cooling_type: 'air' | 'aio' | 'custom';
  socket_compatibility: string;
  max_tdp: number;
  noise_level?: number;
  price: string;
  created_at: string;
  updated_at: string;
}

// Типы для периферии
export interface Monitor {
  id: number;
  name: string;
  manufacturer: string;
  screen_size: number;
  resolution: string;
  refresh_rate: number;
  panel_type: string;
  response_time: number;
  hdr: boolean;
  curved: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Keyboard {
  id: number;
  name: string;
  manufacturer: string;
  switch_type: 'mechanical' | 'membrane' | 'optical';
  switch_model?: string;
  rgb: boolean;
  wireless: boolean;
  form_factor?: string;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Mouse {
  id: number;
  name: string;
  manufacturer: string;
  sensor_type: 'optical' | 'laser';
  dpi: number;
  buttons: number;
  wireless: boolean;
  rgb: boolean;
  weight?: number;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Headset {
  id: number;
  name: string;
  manufacturer: string;
  connection_type: string;
  wireless: boolean;
  microphone: boolean;
  surround: boolean;
  noise_cancelling: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

// Типы для конфигураций
export interface PCConfiguration {
  id: number;
  user: number;
  name?: string;
  user_type?: string;
  priority?: string;
  cpu?: CPU | number;
  cpu_detail?: CPU;
  gpu?: GPU | number;
  gpu_detail?: GPU;
  motherboard?: Motherboard | number;
  motherboard_detail?: Motherboard;
  ram?: RAM | number;
  ram_detail?: RAM;
  storage?: Storage | number;
  storage_primary?: number;
  storage_primary_detail?: Storage;
  storage_secondary?: number;
  storage_secondary_detail?: Storage;
  psu?: PSU | number;
  psu_detail?: PSU;
  case?: Case | number;
  case_detail?: Case;
  cooling?: Cooling | number;
  cooling_detail?: Cooling;
  total_price: string | number;
  compatibility_check?: boolean;
  is_compatible?: boolean;
  compatibility_notes?: string;
  compatibility_issues?: string[];
  is_saved?: boolean;
  recommendations?: Recommendation[];
  created_at: string;
  updated_at: string;
}

export interface Recommendation {
  id: number;
  configuration: number;
  component_type: string;
  component_id: number;
  reason: string;
  title?: string;
  description?: string;
  priority?: 'high' | 'medium' | 'low';
  estimated_cost?: number;
  created_at: string;
}

export interface ConfigurationRequest {
  user_type: 'designer' | 'programmer' | 'gamer' | 'office' | 'student' | 'content_creator';
  min_budget: number;
  max_budget: number;
  priority: 'performance' | 'silence' | 'compactness' | 'aesthetics';
  multitasking: boolean;
  work_with_4k: boolean;
  vr_support: boolean;
  video_editing: boolean;
  gaming: boolean;
  streaming: boolean;
  has_existing_components: boolean;
  existing_components_description?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
