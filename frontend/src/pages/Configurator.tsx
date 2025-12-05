import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { configurationAPI } from '../services/api';
import type { ConfigurationRequest } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import { FiCpu, FiMonitor, FiSettings, FiDollarSign, FiCheck, FiArrowRight, FiCode, FiEdit3, FiBriefcase, FiBookOpen, FiVideo } from 'react-icons/fi';

type Section = 'pc' | 'workspace' | 'peripherals';
type UserType = 'gamer' | 'programmer' | 'designer' | 'office' | 'student' | 'content_creator';

// Пресеты для разных профилей пользователей
const profilePresets: Record<UserType, Partial<ConfigurationRequest>> = {
  gamer: {
    user_type: 'gamer',
    priority: 'performance',
    min_budget: 80000,
    max_budget: 150000,
    gaming: true,
    streaming: false,
    video_editing: false,
    multitasking: true,
    work_with_4k: false,
    vr_support: true,
    min_cpu_cores: 6,
    min_gpu_vram: 8,
    min_ram_capacity: 16,
    min_storage_capacity: 1000,
    storage_type_preference: 'nvme',
    rgb_preference: true,
    overclocking_support: true,
    monitor_min_refresh_rate: 144,
    monitor_min_resolution: '1440p',
    mouse_min_dpi: 16000,
    headset_wireless: true,
  },
  programmer: {
    user_type: 'programmer',
    priority: 'performance',
    min_budget: 60000,
    max_budget: 120000,
    gaming: false,
    streaming: false,
    video_editing: false,
    multitasking: true,
    work_with_4k: true,
    vr_support: false,
    min_cpu_cores: 8,
    min_gpu_vram: 4,
    min_ram_capacity: 32,
    min_storage_capacity: 1000,
    storage_type_preference: 'nvme',
    rgb_preference: false,
    overclocking_support: false,
    monitor_min_refresh_rate: 60,
    monitor_min_resolution: '1440p',
    monitor_size_preference: 27,
    keyboard_type_preference: 'mechanical',
    chair_ergonomic: true,
    chair_lumbar_support: true,
  },
  designer: {
    user_type: 'designer',
    priority: 'performance',
    min_budget: 100000,
    max_budget: 200000,
    gaming: false,
    streaming: false,
    video_editing: true,
    multitasking: true,
    work_with_4k: true,
    vr_support: false,
    min_cpu_cores: 8,
    min_gpu_vram: 8,
    min_ram_capacity: 32,
    min_storage_capacity: 2000,
    storage_type_preference: 'nvme',
    rgb_preference: false,
    overclocking_support: false,
    monitor_min_refresh_rate: 60,
    monitor_min_resolution: '4k',
    monitor_size_preference: 27,
    monitor_panel_type: 'ips',
    keyboard_type_preference: 'mechanical',
  },
  office: {
    user_type: 'office',
    priority: 'silence',
    min_budget: 30000,
    max_budget: 60000,
    gaming: false,
    streaming: false,
    video_editing: false,
    multitasking: true,
    work_with_4k: false,
    vr_support: false,
    min_cpu_cores: 4,
    min_gpu_vram: 2,
    min_ram_capacity: 8,
    min_storage_capacity: 256,
    storage_type_preference: 'sata',
    rgb_preference: false,
    overclocking_support: false,
    monitor_min_refresh_rate: 60,
    monitor_min_resolution: '1080p',
    monitor_size_preference: 24,
    case_size_preference: 'mini',
  },
  student: {
    user_type: 'student',
    priority: 'performance',
    min_budget: 40000,
    max_budget: 80000,
    gaming: true,
    streaming: false,
    video_editing: false,
    multitasking: true,
    work_with_4k: false,
    vr_support: false,
    min_cpu_cores: 6,
    min_gpu_vram: 6,
    min_ram_capacity: 16,
    min_storage_capacity: 512,
    storage_type_preference: 'nvme',
    rgb_preference: false,
    overclocking_support: false,
    monitor_min_refresh_rate: 75,
    monitor_min_resolution: '1080p',
    monitor_size_preference: 24,
  },
  content_creator: {
    user_type: 'content_creator',
    priority: 'performance',
    min_budget: 120000,
    max_budget: 250000,
    gaming: true,
    streaming: true,
    video_editing: true,
    multitasking: true,
    work_with_4k: true,
    vr_support: false,
    min_cpu_cores: 12,
    min_gpu_vram: 12,
    min_ram_capacity: 64,
    min_storage_capacity: 2000,
    storage_type_preference: 'nvme',
    rgb_preference: true,
    overclocking_support: true,
    monitor_min_refresh_rate: 144,
    monitor_min_resolution: '1440p',
    monitor_size_preference: 27,
    need_webcam: true,
    need_microphone: true,
    webcam_min_resolution: '4k',
  },
};

// Иконки и названия профилей
const profileInfo: Record<UserType, { icon: any; label: string; description: string }> = {
  gamer: { 
    icon: FiMonitor, 
    label: 'Геймер',
    description: 'Высокая производительность в играх, RGB подсветка, VR поддержка'
  },
  programmer: { 
    icon: FiCode, 
    label: 'Разработчик',
    description: 'Много ядер, большой объем RAM, качественный монитор'
  },
  designer: { 
    icon: FiEdit3, 
    label: 'Дизайнер',
    description: 'Мощная графика, 4K монитор с IPS матрицей, цветопередача'
  },
  office: { 
    icon: FiBriefcase, 
    label: 'Офис',
    description: 'Тихая работа, надежность, компактные размеры'
  },
  student: { 
    icon: FiBookOpen, 
    label: 'Студент',
    description: 'Баланс цены и производительности, универсальность'
  },
  content_creator: { 
    icon: FiVideo, 
    label: 'Стример',
    description: 'Стриминг, видеомонтаж, качественный микрофон и камера'
  },
};

const Configurator: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<Section>('pc');
  const [selectedProfile, setSelectedProfile] = useState<UserType | null>(null);

  const [formData, setFormData] = useState<ConfigurationRequest>({
    user_type: 'gamer',
    min_budget: 50000,
    max_budget: 100000,
    priority: 'performance',
    multitasking: false,
    work_with_4k: false,
    vr_support: false,
    video_editing: false,
    gaming: true,
    streaming: false,
    has_existing_components: false,
    include_workspace: true,
    use_ai: true,
    ai_generation_mode: 'full_ai',
    preferred_cpu_manufacturer: 'any',
    preferred_gpu_manufacturer: 'any',
    min_cpu_cores: 4,
    min_gpu_vram: 4,
    min_ram_capacity: 16,
    storage_type_preference: 'any',
    min_storage_capacity: 512,
    cooling_preference: 'any',
    rgb_preference: false,
    case_size_preference: 'any',
    overclocking_support: false,
    peripheral_budget_percent: 30,
    need_monitor: true,
    need_keyboard: true,
    need_mouse: true,
    need_headset: true,
    need_webcam: false,
    need_microphone: false,
    need_desk: true,
    need_chair: true,
    monitor_min_refresh_rate: 60,
    monitor_min_resolution: '1080p',
    monitor_size_preference: 24,
    monitor_panel_type: 'any',
    keyboard_type_preference: 'any',
    keyboard_switch_type: 'any',
    keyboard_rgb: false,
    mouse_min_dpi: 1000,
    mouse_sensor_type: 'any',
    mouse_wireless: false,
    headset_wireless: false,
    headset_noise_cancellation: false,
    webcam_min_resolution: 'any',
    microphone_type: 'any',
    desk_min_width: 120,
    desk_min_depth: 60,
    desk_height_adjustable: false,
    desk_material_preference: 'any',
    desk_cable_management: true,
    chair_ergonomic: true,
    chair_lumbar_support: true,
    chair_armrests_adjustable: false,
    chair_max_weight: 120,
    chair_material_preference: 'any',
    workspace_rgb_lighting: false,
    workspace_lighting_type: 'any',
    workspace_sound_dampening: false,
    monitor_arm: false,
    cable_management_accessories: true,
  });

  // Применение пресета профиля
  const applyProfile = (profileType: UserType) => {
    const preset = profilePresets[profileType];
    setFormData(prev => ({
      ...prev,
      ...preset,
    }));
    setSelectedProfile(profileType);
    // Обновляем URL
    setSearchParams({ type: profileType });
  };

  // Читаем параметр type из URL при загрузке
  useEffect(() => {
    const typeParam = searchParams.get('type') as UserType | null;
    if (typeParam && profilePresets[typeParam]) {
      applyProfile(typeParam);
    }
  }, []);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await configurationAPI.generateConfiguration(formData);
      const config = response.data as any;
      const configId = config.id;
      
      if (configId) {
        setTimeout(() => {
          navigate(`/configuration/${configId}`);
        }, 100);
      } else {
        setError('Конфигурация создана, но не удалось получить ID.');
      }
    } catch (err: any) {
      let errorMessage = 'Ошибка при генерации конфигурации';
      if (err.code === 'ECONNABORTED') {
        errorMessage = 'Превышено время ожидания. Попробуйте еще раз.';
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    { id: 'pc', name: 'Компоненты', icon: FiCpu },
    { id: 'workspace', name: 'Рабочее место', icon: FiSettings },
    { id: 'peripherals', name: 'Периферия', icon: FiMonitor },
  ];

  if (loading) {
    return (
      <div className="py-20">
        <LoadingSpinner text="Генерация конфигурации..." size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-heading text-3xl md:text-4xl text-white mb-3">
          Конфигуратор ПК
        </h1>
        <p className="text-gray-500">
          Настройте параметры и получите оптимальную конфигурацию
        </p>
      </div>

      {/* Profile Cards - Quick Selection */}
      <div className="mb-8">
        <div className="text-center mb-4">
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
            Быстрый выбор профиля
          </h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {(Object.keys(profilePresets) as UserType[]).map((profileKey) => {
            const profile = profileInfo[profileKey];
            const isSelected = selectedProfile === profileKey;
            return (
              <button
                key={profileKey}
                type="button"
                onClick={() => applyProfile(profileKey)}
                className={`group relative p-4 text-center transition-all duration-300 border-2 ${
                  isSelected
                    ? 'bg-primary/10 border-primary shadow-lg shadow-primary/20'
                    : 'bg-bg-card border-border-dark hover:border-primary/50 hover:bg-bg-surface'
                }`}
              >
                {/* Selected indicator */}
                {isSelected && (
                  <div className="absolute top-2 right-2">
                    {React.createElement(FiCheck as any, { className: "w-4 h-4 text-primary" })}
                  </div>
                )}
                
                <div className={`w-12 h-12 mx-auto flex items-center justify-center mb-3 transition-colors duration-300 ${
                  isSelected 
                    ? 'bg-primary/20' 
                    : 'bg-bg-surface group-hover:bg-primary/10'
                }`}>
                  {React.createElement(profile.icon as any, { 
                    className: `text-xl ${isSelected ? 'text-primary' : 'text-gray-400 group-hover:text-primary'} transition-colors duration-300` 
                  })}
                </div>
                
                <span className={`text-sm font-medium transition-colors duration-300 ${
                  isSelected ? 'text-primary' : 'text-gray-400 group-hover:text-white'
                }`}>
                  {profile.label}
                </span>

                {/* Tooltip on hover */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 border border-gray-700 
                  text-xs text-gray-300 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible 
                  transition-all duration-200 whitespace-nowrap z-10 pointer-events-none shadow-lg">
                  {profile.description}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></div>
                </div>
              </button>
            );
          })}
        </div>
        
        {/* Selected profile info */}
        {selectedProfile && (
          <div className="mt-4 p-4 bg-primary/5 border border-primary/20 flex items-center gap-3 animate-fade-in">
            {React.createElement(profileInfo[selectedProfile].icon as any, { className: "text-xl text-primary flex-shrink-0" })}
            <div>
              <span className="text-primary font-medium">{profileInfo[selectedProfile].label}:</span>
              <span className="text-gray-400 ml-2 text-sm">{profileInfo[selectedProfile].description}</span>
            </div>
          </div>
        )}
      </div>

      {/* Section Tabs */}
      <div className="flex gap-2 mb-8 p-1 bg-bg-card border border-border-dark">
        {sections.map((section) => {
          const isActive = activeSection === section.id;
          return (
            <button
              key={section.id}
              type="button"
              onClick={() => setActiveSection(section.id as Section)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-400 hover:text-white hover:bg-bg-surface'
              }`}
            >
              {React.createElement(section.icon as any, { className: "text-lg" })}
              <span className="hidden sm:inline">{section.name}</span>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* PC Section */}
        {activeSection === 'pc' && (
          <div className="space-y-6 animate-fade-in">
            {/* Profile */}
            <div className="card p-6">
              <h2 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
                {React.createElement(FiSettings as any, { className: "text-primary" })}
                Профиль использования
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Тип пользователя</label>
                  <select
                    name="user_type"
                    value={formData.user_type}
                    onChange={handleInputChange}
                    className="input"
                  >
                    <option value="gamer">Геймер</option>
                    <option value="designer">Дизайнер</option>
                    <option value="programmer">Программист</option>
                    <option value="content_creator">Контент-криэйтор</option>
                    <option value="office">Офис</option>
                    <option value="student">Студент</option>
                  </select>
                </div>
                <div>
                  <label className="label">Приоритет</label>
                  <select
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                    className="input"
                  >
                    <option value="performance">Производительность</option>
                    <option value="silence">Тишина работы</option>
                    <option value="compactness">Компактность</option>
                    <option value="aesthetics">Эстетика</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Budget */}
            <div className="card p-6">
              <h2 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
                {React.createElement(FiDollarSign as any, { className: "text-primary" })}
                Бюджет
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Минимум (₽)</label>
                  <input
                    type="number"
                    name="min_budget"
                    value={formData.min_budget}
                    onChange={handleInputChange}
                    min="10000"
                    step="1000"
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Максимум (₽)</label>
                  <input
                    type="number"
                    name="max_budget"
                    value={formData.max_budget}
                    onChange={handleInputChange}
                    min="20000"
                    step="1000"
                    className="input"
                  />
                </div>
              </div>
            </div>

            {/* Requirements */}
            <div className="card p-6">
              <h2 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
                {React.createElement(FiCheck as any, { className: "text-primary" })}
                Требования
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { name: 'multitasking', label: 'Многозадачность' },
                  { name: 'work_with_4k', label: 'Работа с 4K' },
                  { name: 'vr_support', label: 'Поддержка VR' },
                  { name: 'video_editing', label: 'Видеомонтаж' },
                  { name: 'gaming', label: 'Гейминг' },
                  { name: 'streaming', label: 'Стриминг' },
                ].map((item) => (
                  <label
                    key={item.name}
                    className="flex items-center gap-2 p-3 bg-bg-surface border border-border-dark cursor-pointer hover:border-primary/30 transition-colors"
                  >
                    <input
                      type="checkbox"
                      name={item.name}
                      checked={(formData as any)[item.name]}
                      onChange={handleInputChange}
                      className="w-4 h-4 accent-primary"
                    />
                    <span className="text-sm text-gray-400">{item.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="card p-6">
              <h2 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
                {React.createElement(FiCpu as any, { className: "text-primary" })}
                Расширенные параметры
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* CPU */}
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Процессор</h3>
                  <div>
                    <label className="label">Производитель</label>
                    <select
                      name="preferred_cpu_manufacturer"
                      value={formData.preferred_cpu_manufacturer}
                      onChange={handleInputChange}
                      className="input"
                    >
                      <option value="any">Любой</option>
                      <option value="intel">Intel</option>
                      <option value="amd">AMD</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Минимум ядер: {formData.min_cpu_cores}</label>
                    <input
                      type="range"
                      name="min_cpu_cores"
                      value={formData.min_cpu_cores}
                      onChange={handleInputChange}
                      min="2"
                      max="32"
                      step="2"
                      className="w-full accent-primary"
                    />
                  </div>
                </div>

                {/* GPU */}
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Видеокарта</h3>
                  <div>
                    <label className="label">Производитель</label>
                    <select
                      name="preferred_gpu_manufacturer"
                      value={formData.preferred_gpu_manufacturer}
                      onChange={handleInputChange}
                      className="input"
                    >
                      <option value="any">Любой</option>
                      <option value="nvidia">NVIDIA</option>
                      <option value="amd">AMD</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Минимум VRAM: {formData.min_gpu_vram} GB</label>
                    <input
                      type="range"
                      name="min_gpu_vram"
                      value={formData.min_gpu_vram}
                      onChange={handleInputChange}
                      min="2"
                      max="24"
                      step="2"
                      className="w-full accent-primary"
                    />
                  </div>
                </div>

                {/* RAM */}
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Память</h3>
                  <div>
                    <label className="label">Минимум RAM: {formData.min_ram_capacity} GB</label>
                    <input
                      type="range"
                      name="min_ram_capacity"
                      value={formData.min_ram_capacity}
                      onChange={handleInputChange}
                      min="8"
                      max="128"
                      step="8"
                      className="w-full accent-primary"
                    />
                  </div>
                </div>

                {/* Storage */}
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Накопитель</h3>
                  <div>
                    <label className="label">Тип</label>
                    <select
                      name="storage_type_preference"
                      value={formData.storage_type_preference}
                      onChange={handleInputChange}
                      className="input"
                    >
                      <option value="any">Любой</option>
                      <option value="nvme">NVMe SSD</option>
                      <option value="sata">SATA SSD</option>
                      <option value="hdd">HDD</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Минимум: {formData.min_storage_capacity} GB</label>
                    <input
                      type="range"
                      name="min_storage_capacity"
                      value={formData.min_storage_capacity}
                      onChange={handleInputChange}
                      min="256"
                      max="4096"
                      step="256"
                      className="w-full accent-primary"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Workspace Section */}
        {activeSection === 'workspace' && (
          <div className="space-y-6 animate-fade-in">
            <div className="card p-6">
              <h2 className="text-lg font-heading font-semibold text-white mb-4">
                Настройки рабочего места
              </h2>
              
              <label className="flex items-center gap-3 p-4 bg-bg-surface border border-border-dark cursor-pointer hover:border-primary/30 transition-colors mb-4">
                <input
                  type="checkbox"
                  name="include_workspace"
                  checked={formData.include_workspace}
                  onChange={handleInputChange}
                  className="w-5 h-5 accent-primary"
                />
                <div>
                  <span className="text-white font-medium">Включить рабочее место</span>
                  <p className="text-sm text-gray-500">Добавить стол и кресло в конфигурацию</p>
                </div>
              </label>

              {formData.include_workspace && (
                <div className="grid grid-cols-2 gap-3 mt-4">
                  <label className="flex items-center gap-2 p-3 bg-bg-surface border border-border-dark cursor-pointer hover:border-primary/30 transition-colors">
                    <input
                      type="checkbox"
                      name="need_desk"
                      checked={formData.need_desk}
                      onChange={handleInputChange}
                      className="w-4 h-4 accent-primary"
                    />
                    <span className="text-sm text-gray-400">Стол</span>
                  </label>
                  <label className="flex items-center gap-2 p-3 bg-bg-surface border border-border-dark cursor-pointer hover:border-primary/30 transition-colors">
                    <input
                      type="checkbox"
                      name="need_chair"
                      checked={formData.need_chair}
                      onChange={handleInputChange}
                      className="w-4 h-4 accent-primary"
                    />
                    <span className="text-sm text-gray-400">Кресло</span>
                  </label>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Peripherals Section */}
        {activeSection === 'peripherals' && (
          <div className="space-y-6 animate-fade-in">
            <div className="card p-6">
              <h2 className="text-lg font-heading font-semibold text-white mb-4">
                Периферийные устройства
              </h2>
              
              <div className="mb-4">
                <label className="label">Бюджет на периферию: {formData.peripheral_budget_percent}%</label>
                <input
                  type="range"
                  name="peripheral_budget_percent"
                  value={formData.peripheral_budget_percent}
                  onChange={handleInputChange}
                  min="10"
                  max="50"
                  step="5"
                  className="w-full accent-primary"
                />
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { name: 'need_monitor', label: 'Монитор' },
                  { name: 'need_keyboard', label: 'Клавиатура' },
                  { name: 'need_mouse', label: 'Мышь' },
                  { name: 'need_headset', label: 'Гарнитура' },
                  { name: 'need_webcam', label: 'Веб-камера' },
                  { name: 'need_microphone', label: 'Микрофон' },
                ].map((item) => (
                  <label
                    key={item.name}
                    className="flex items-center gap-2 p-3 bg-bg-surface border border-border-dark cursor-pointer hover:border-primary/30 transition-colors"
                  >
                    <input
                      type="checkbox"
                      name={item.name}
                      checked={(formData as any)[item.name]}
                      onChange={handleInputChange}
                      className="w-4 h-4 accent-primary"
                    />
                    <span className="text-sm text-gray-400">{item.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* AI Configuration Section */}
        <div className="card p-6 border-2 border-primary/30 bg-gradient-to-br from-primary/5 to-transparent">
          <h2 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 16a6 6 0 1 1 6-6 6 6 0 0 1-6 6z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            Сборка с помощью AI
          </h2>
          
          <div className="space-y-4">
            <div className="p-4 bg-primary/10 border border-primary/30">
              <p className="text-sm text-gray-300">
                <strong className="text-primary">AI DeepSeek</strong> создаст оптимальную конфигурацию 
                на основе актуальных данных о комплектующих (декабрь 2025). Модель учитывает совместимость 
                компонентов, ваш бюджет и требования.
              </p>
              <ul className="mt-3 text-xs text-gray-400 space-y-1">
                <li>✓ Процессор, видеокарта, материнская плата, RAM, SSD, БП, корпус, охлаждение</li>
                <li>✓ Монитор, клавиатура, мышь, гарнитура</li>
                <li>✓ Стол и кресло для рабочего места</li>
                <li>✓ Актуальные цены на декабрь 2025</li>
              </ul>
            </div>
            
            {/* Include workspace toggle */}
            <label className="flex items-center gap-3 p-4 bg-bg-surface border border-border-dark cursor-pointer hover:border-primary/30 transition-colors">
              <input
                type="checkbox"
                name="include_workspace"
                checked={formData.include_workspace}
                onChange={handleInputChange}
                className="w-5 h-5 accent-primary"
              />
              <div>
                <span className="text-white font-medium">Включить рабочее место</span>
                <p className="text-sm text-gray-500">Стол и кресло в дополнение к ПК и периферии</p>
              </div>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-6">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-4 text-base flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 16a6 6 0 1 1 6-6 6 6 0 0 1-6 6z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            <span>Собрать с AI</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default Configurator;
