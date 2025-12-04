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
  surround_sound: boolean;
  noise_cancellation: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Webcam {
  id: number;
  name: string;
  manufacturer: string;
  resolution: string;
  fps: number;
  autofocus: boolean;
  microphone: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Microphone {
  id: number;
  name: string;
  manufacturer: string;
  mic_type: 'condenser' | 'dynamic' | 'usb';
  polar_pattern?: string;
  frequency_response?: string;
  connection_type: string;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Desk {
  id: number;
  name: string;
  manufacturer: string;
  width: number;
  depth: number;
  height_adjustable: boolean;
  material?: string;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Chair {
  id: number;
  name: string;
  manufacturer: string;
  ergonomic: boolean;
  lumbar_support: boolean;
  armrests_adjustable: boolean;
  max_weight?: number;
  material?: string;
  price: string;
  created_at: string;
  updated_at: string;
}

// Новые типы периферии
export interface Speakers {
  id: number;
  name: string;
  manufacturer: string;
  speaker_type: '2.0' | '2.1' | '5.1' | 'soundbar';
  total_power: number;
  frequency_response?: string;
  bluetooth: boolean;
  rgb: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Mousepad {
  id: number;
  name: string;
  manufacturer: string;
  size: 'small' | 'medium' | 'large' | 'xl' | 'desk';
  width: number;
  height: number;
  thickness: number;
  rgb: boolean;
  material: string;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface MonitorArm {
  id: number;
  name: string;
  manufacturer: string;
  mount_type: 'single' | 'dual' | 'triple' | 'quad';
  max_screen_size: number;
  max_weight: string;
  vesa_pattern: string;
  gas_spring: boolean;
  cable_management: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface USBHub {
  id: number;
  name: string;
  manufacturer: string;
  usb3_ports: number;
  usbc_ports: number;
  usb2_ports: number;
  card_reader: boolean;
  hdmi_port: boolean;
  ethernet_port: boolean;
  power_delivery?: number;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface DeskLighting {
  id: number;
  name: string;
  manufacturer: string;
  lighting_type: 'led_strip' | 'desk_lamp' | 'monitor_bar' | 'ambient' | 'ring_light';
  rgb: boolean;
  dimmable: boolean;
  color_temperature?: string;
  smart_control: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface StreamDeck {
  id: number;
  name: string;
  manufacturer: string;
  keys_count: number;
  lcd_keys: boolean;
  dials: number;
  touchscreen: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface CaptureCard {
  id: number;
  name: string;
  manufacturer: string;
  max_resolution: string;
  max_fps: number;
  connection: string;
  passthrough: boolean;
  internal: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface Gamepad {
  id: number;
  name: string;
  manufacturer: string;
  platform: 'pc' | 'xbox' | 'playstation' | 'universal';
  wireless: boolean;
  vibration: boolean;
  rgb: boolean;
  extra_buttons: number;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface HeadphoneStand {
  id: number;
  name: string;
  manufacturer: string;
  usb_hub: boolean;
  usb_ports: number;
  rgb: boolean;
  wireless_charging: boolean;
  price: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceSetup {
  id: number;
  configuration: number;
  monitor_primary?: Monitor | number;
  monitor_primary_detail?: Monitor;
  monitor_secondary?: Monitor | number;
  monitor_secondary_detail?: Monitor;
  keyboard?: Keyboard | number;
  keyboard_detail?: Keyboard;
  mouse?: Mouse | number;
  mouse_detail?: Mouse;
  headset?: Headset | number;
  headset_detail?: Headset;
  webcam?: Webcam | number;
  webcam_detail?: Webcam;
  microphone?: Microphone | number;
  microphone_detail?: Microphone;
  desk?: Desk | number;
  desk_detail?: Desk;
  chair?: Chair | number;
  chair_detail?: Chair;
  lighting_recommendation?: string;
  total_price: string | number;
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
  workspace?: WorkspaceSetup;
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
  include_workspace?: boolean;
  use_ai?: boolean;
  ai_generation_mode?: 'database' | 'generative' | 'full_ai';

  // Расширенные параметры PC
  preferred_cpu_manufacturer?: 'intel' | 'amd' | 'any';
  preferred_gpu_manufacturer?: 'nvidia' | 'amd' | 'any';
  min_cpu_cores?: number;
  min_gpu_vram?: number;
  min_ram_capacity?: number;
  storage_type_preference?: 'nvme' | 'sata' | 'hdd' | 'any';
  min_storage_capacity?: number;
  cooling_preference?: 'air' | 'aio' | 'custom' | 'any';
  rgb_preference?: boolean;
  case_size_preference?: 'mini' | 'mid' | 'full' | 'any';
  overclocking_support?: boolean;

  // Настройки периферии
  peripheral_budget_percent?: number;
  need_monitor?: boolean;
  need_keyboard?: boolean;
  need_mouse?: boolean;
  need_headset?: boolean;
  need_webcam?: boolean;
  need_microphone?: boolean;
  need_desk?: boolean;
  need_chair?: boolean;

  // Расширенные параметры периферии
  monitor_min_refresh_rate?: number;
  monitor_min_resolution?: string;
  monitor_size_preference?: number;
  monitor_panel_type?: 'ips' | 'va' | 'tn' | 'oled' | 'any';
  keyboard_type_preference?: 'mechanical' | 'membrane' | 'any';
  keyboard_switch_type?: 'linear' | 'tactile' | 'clicky' | 'any';
  keyboard_rgb?: boolean;
  mouse_min_dpi?: number;
  mouse_sensor_type?: 'optical' | 'laser' | 'any';
  mouse_wireless?: boolean;
  headset_wireless?: boolean;
  headset_noise_cancellation?: boolean;
  webcam_min_resolution?: '720p' | '1080p' | '4k' | 'any';
  microphone_type?: 'condenser' | 'dynamic' | 'usb' | 'any';

  // Расширенные параметры workspace
  desk_min_width?: number;
  desk_min_depth?: number;
  desk_height_adjustable?: boolean;
  desk_material_preference?: 'wood' | 'metal' | 'glass' | 'any';
  desk_cable_management?: boolean;
  chair_ergonomic?: boolean;
  chair_lumbar_support?: boolean;
  chair_armrests_adjustable?: boolean;
  chair_max_weight?: number;
  chair_material_preference?: 'leather' | 'fabric' | 'mesh' | 'any';
  workspace_rgb_lighting?: boolean;
  workspace_lighting_type?: 'warm' | 'neutral' | 'cold' | 'adjustable' | 'any';
  workspace_sound_dampening?: boolean;
  monitor_arm?: boolean;
  cable_management_accessories?: boolean;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
