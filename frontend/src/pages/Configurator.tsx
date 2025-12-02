import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { configurationAPI } from '../services/api';
import type { ConfigurationRequest } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import Dock from '../components/Dock';
import { FaRocket, FaUser, FaDollarSign, FaCheckCircle, FaDesktop, FaCouch, FaKeyboard, FaMicrochip, FaVideo, FaMemory, FaHdd, FaSnowflake, FaBoxOpen } from 'react-icons/fa';

type Section = 'pc' | 'workspace' | 'peripherals';

const Configurator: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<Section>('pc');
  
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
    include_workspace: false,
    use_ai: false,
    
    // Расширенные параметры PC
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
    
    // Настройки периферии
    peripheral_budget_percent: 30,
    need_monitor: true,
    need_keyboard: true,
    need_mouse: true,
    need_headset: true,
    need_webcam: false,
    need_microphone: false,
    need_desk: true,
    need_chair: true,
    
    // Расширенные параметры периферии
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
    
    // Расширенные параметры workspace
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
      const config = response.data;
      
      if (config.id) {
        navigate(`/configuration/${config.id}`);
      } else {
        setError('Не удалось получить ID конфигурации');
      }
    } catch (err: any) {
      console.error('Configuration error:', err);
      setError(err.response?.data?.error || err.response?.data?.message || 'Ошибка при генерации конфигурации');
    } finally {
      setLoading(false);
    }
  };

  const dockItems = [
    {
      icon: React.createElement(FaDesktop as any, { className: "text-2xl" }),
      label: 'Компоненты ПК',
      onClick: () => setActiveSection('pc'),
      active: activeSection === 'pc',
    },
    {
      icon: React.createElement(FaCouch as any, { className: "text-2xl" }),
      label: 'Рабочее место',
      onClick: () => setActiveSection('workspace'),
      active: activeSection === 'workspace',
    },
    {
      icon: React.createElement(FaKeyboard as any, { className: "text-2xl" }),
      label: 'Периферия',
      onClick: () => setActiveSection('peripherals'),
      active: activeSection === 'peripherals',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto pb-24">
      <h1 className="text-5xl font-bold mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 text-center">
        Конфигуратор ПК
      </h1>

      {error && (
        <div className="backdrop-blur-xl bg-red-500/10 border border-red-500/30 text-red-300 px-6 py-4 rounded-2xl mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* PC Section */}
        {activeSection === 'pc' && (
          <div className="space-y-6 animate-fadeIn">
            {/* Тип пользователя */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/5 to-blue-500/5 rounded-2xl border border-blue-500/20 p-8 hover:border-blue-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10">
              <div className="flex items-center gap-3 mb-6">
                {React.createElement(FaUser as any, { className: "text-3xl text-blue-400" })}
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">Профиль пользователя</h2>
              </div>
          
          <div className="mb-6">
            <label className="block text-white/90 font-medium mb-3">
              Для каких задач нужен компьютер?
            </label>
            <select
              name="user_type"
              value={formData.user_type}
              onChange={handleInputChange}
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 transition-all backdrop-blur-sm"
            >
              <option value="gamer" className="bg-gray-900">Геймер</option>
              <option value="designer" className="bg-gray-900">Дизайнер</option>
              <option value="programmer" className="bg-gray-900">Программист</option>
              <option value="content_creator" className="bg-gray-900">Контент-криэйтор</option>
              <option value="office" className="bg-gray-900">Офисный работник</option>
              <option value="student" className="bg-gray-900">Студент</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-white/90 font-medium mb-3">
              Приоритет
            </label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 transition-all backdrop-blur-sm"
            >
              <option value="performance" className="bg-gray-900">Производительность</option>
              <option value="silence" className="bg-gray-900">Тишина работы</option>
              <option value="compactness" className="bg-gray-900">Компактность</option>
              <option value="aesthetics" className="bg-gray-900">Эстетика</option>
            </select>
          </div>
        </div>

        {/* Бюджет */}
        <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 hover:border-white/20 transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            {React.createElement(FaDollarSign as any, { className: "text-2xl text-green-400" })}
            <h2 className="text-2xl font-semibold text-white">Бюджет</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-white/90 font-medium mb-3">
                Минимальный бюджет (₽)
              </label>
              <input
                type="number"
                name="min_budget"
                value={formData.min_budget}
                onChange={handleInputChange}
                min="10000"
                step="1000"
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-green-500/50 focus:border-green-400 transition-all backdrop-blur-sm"
              />
            </div>
            <div>
              <label className="block text-white/90 font-medium mb-3">
                Максимальный бюджет (₽)
              </label>
              <input
                type="number"
                name="max_budget"
                value={formData.max_budget}
                onChange={handleInputChange}
                min="20000"
                step="1000"
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-green-500/50 focus:border-green-400 transition-all backdrop-blur-sm"
              />
            </div>
          </div>
        </div>

        {/* Специфические требования */}
        <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 hover:border-white/20 transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            {React.createElement(FaCheckCircle as any, { className: "text-2xl text-purple-400" })}
            <h2 className="text-2xl font-semibold text-white">Специфические требования</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="multitasking"
                checked={formData.multitasking}
                onChange={handleInputChange}
                className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
              />
              <span className="text-white/90 group-hover:text-white transition-colors">Многозадачность</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="work_with_4k"
                checked={formData.work_with_4k}
                onChange={handleInputChange}
                className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
              />
              <span className="text-white/90 group-hover:text-white transition-colors">Работа с 4K</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="vr_support"
                checked={formData.vr_support}
                onChange={handleInputChange}
                className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
              />
              <span className="text-white/90 group-hover:text-white transition-colors">Поддержка VR</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="video_editing"
                checked={formData.video_editing}
                onChange={handleInputChange}
                className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
              />
              <span className="text-white/90 group-hover:text-white transition-colors">Видеомонтаж</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="gaming"
                checked={formData.gaming}
                onChange={handleInputChange}
                className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
              />
              <span className="text-white/90 group-hover:text-white transition-colors">Гейминг</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="streaming"
                checked={formData.streaming}
                onChange={handleInputChange}
                className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
              />
              <span className="text-white/90 group-hover:text-white transition-colors">Стриминг</span>
            </label>
          </div>
        </div>

            {/* Расширенные параметры PC */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/5 to-purple-500/5 rounded-2xl border border-purple-500/20 p-8 hover:border-purple-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10">
              <div className="flex items-center gap-3 mb-6">
                {React.createElement(FaMicrochip as any, { className: "text-3xl text-purple-400" })}
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Расширенные параметры</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Процессор */}
                <div className="space-y-4 p-6 bg-purple-500/5 border border-purple-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-purple-300 flex items-center gap-2">
                    {React.createElement(FaMicrochip as any, { className: "text-xl" })}
                    Процессор
                  </h3>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">Производитель</label>
                    <select
                      name="preferred_cpu_manufacturer"
                      value={formData.preferred_cpu_manufacturer}
                      onChange={handleInputChange}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 transition-all backdrop-blur-sm"
                    >
                      <option value="any" className="bg-gray-900">Любой</option>
                      <option value="intel" className="bg-gray-900">Intel</option>
                      <option value="amd" className="bg-gray-900">AMD</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">
                      Минимум ядер: {formData.min_cpu_cores}
                    </label>
                    <input
                      type="range"
                      name="min_cpu_cores"
                      value={formData.min_cpu_cores}
                      onChange={handleInputChange}
                      min="2"
                      max="32"
                      step="2"
                      className="w-full h-2 bg-purple-500/20 rounded-lg appearance-none cursor-pointer slider-purple"
                    />
                    <div className="flex justify-between text-xs text-white/60 mt-1">
                      <span>2</span>
                      <span>8</span>
                      <span>16</span>
                      <span>32</span>
                    </div>
                  </div>

                  <label className="flex items-center space-x-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      name="overclocking_support"
                      checked={formData.overclocking_support}
                      onChange={handleInputChange}
                      className="w-5 h-5 text-purple-600 rounded border-white/30 bg-white/10 focus:ring-purple-500/50"
                    />
                    <span className="text-white/90 group-hover:text-white transition-colors">Разгон (OC)</span>
                  </label>
                </div>

                {/* Видеокарта */}
                <div className="space-y-4 p-6 bg-green-500/5 border border-green-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-green-300 flex items-center gap-2">
                    {React.createElement(FaVideo as any, { className: "text-xl" })}
                    Видеокарта
                  </h3>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">Производитель</label>
                    <select
                      name="preferred_gpu_manufacturer"
                      value={formData.preferred_gpu_manufacturer}
                      onChange={handleInputChange}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-green-500/50 focus:border-green-400 transition-all backdrop-blur-sm"
                    >
                      <option value="any" className="bg-gray-900">Любой</option>
                      <option value="nvidia" className="bg-gray-900">NVIDIA</option>
                      <option value="amd" className="bg-gray-900">AMD</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">
                      Минимум VRAM: {formData.min_gpu_vram} GB
                    </label>
                    <input
                      type="range"
                      name="min_gpu_vram"
                      value={formData.min_gpu_vram}
                      onChange={handleInputChange}
                      min="2"
                      max="24"
                      step="2"
                      className="w-full h-2 bg-green-500/20 rounded-lg appearance-none cursor-pointer slider-green"
                    />
                    <div className="flex justify-between text-xs text-white/60 mt-1">
                      <span>2 GB</span>
                      <span>8 GB</span>
                      <span>16 GB</span>
                      <span>24 GB</span>
                    </div>
                  </div>
                </div>

                {/* Память */}
                <div className="space-y-4 p-6 bg-yellow-500/5 border border-yellow-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-yellow-300 flex items-center gap-2">
                    {React.createElement(FaMemory as any, { className: "text-xl" })}
                    Память
                  </h3>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">
                      Минимум RAM: {formData.min_ram_capacity} GB
                    </label>
                    <input
                      type="range"
                      name="min_ram_capacity"
                      value={formData.min_ram_capacity}
                      onChange={handleInputChange}
                      min="8"
                      max="128"
                      step="8"
                      className="w-full h-2 bg-yellow-500/20 rounded-lg appearance-none cursor-pointer slider-yellow"
                    />
                    <div className="flex justify-between text-xs text-white/60 mt-1">
                      <span>8 GB</span>
                      <span>32 GB</span>
                      <span>64 GB</span>
                      <span>128 GB</span>
                    </div>
                  </div>
                </div>

                {/* Накопитель */}
                <div className="space-y-4 p-6 bg-cyan-500/5 border border-cyan-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-cyan-300 flex items-center gap-2">
                    {React.createElement(FaHdd as any, { className: "text-xl" })}
                    Накопитель
                  </h3>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">Тип накопителя</label>
                    <select
                      name="storage_type_preference"
                      value={formData.storage_type_preference}
                      onChange={handleInputChange}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-400 transition-all backdrop-blur-sm"
                    >
                      <option value="any" className="bg-gray-900">Любой</option>
                      <option value="nvme" className="bg-gray-900">NVMe SSD (быстрый)</option>
                      <option value="sata" className="bg-gray-900">SATA SSD</option>
                      <option value="hdd" className="bg-gray-900">HDD (дешевый)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">
                      Минимум: {formData.min_storage_capacity} GB
                    </label>
                    <input
                      type="range"
                      name="min_storage_capacity"
                      value={formData.min_storage_capacity}
                      onChange={handleInputChange}
                      min="256"
                      max="4096"
                      step="256"
                      className="w-full h-2 bg-cyan-500/20 rounded-lg appearance-none cursor-pointer slider-cyan"
                    />
                    <div className="flex justify-between text-xs text-white/60 mt-1">
                      <span>256 GB</span>
                      <span>1 TB</span>
                      <span>2 TB</span>
                      <span>4 TB</span>
                    </div>
                  </div>
                </div>

                {/* Охлаждение и корпус */}
                <div className="space-y-4 p-6 bg-blue-500/5 border border-blue-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-blue-300 flex items-center gap-2">
                    {React.createElement(FaSnowflake as any, { className: "text-xl" })}
                    Охлаждение
                  </h3>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">Тип охлаждения</label>
                    <select
                      name="cooling_preference"
                      value={formData.cooling_preference}
                      onChange={handleInputChange}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 transition-all backdrop-blur-sm"
                    >
                      <option value="any" className="bg-gray-900">Любое</option>
                      <option value="air" className="bg-gray-900">Воздушное</option>
                      <option value="aio" className="bg-gray-900">Водяное (AIO)</option>
                      <option value="custom" className="bg-gray-900">Кастомное СВО</option>
                    </select>
                  </div>
                </div>

                {/* Корпус */}
                <div className="space-y-4 p-6 bg-pink-500/5 border border-pink-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-pink-300 flex items-center gap-2">
                    {React.createElement(FaBoxOpen as any, { className: "text-xl" })}
                    Корпус
                  </h3>

                  <div>
                    <label className="block text-white/90 font-medium mb-2 text-sm">Размер</label>
                    <select
                      name="case_size_preference"
                      value={formData.case_size_preference}
                      onChange={handleInputChange}
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-pink-500/50 focus:border-pink-400 transition-all backdrop-blur-sm"
                    >
                      <option value="any" className="bg-gray-900">Любой</option>
                      <option value="mini" className="bg-gray-900">Mini-ITX (компактный)</option>
                      <option value="mid" className="bg-gray-900">Mid-Tower (стандарт)</option>
                      <option value="full" className="bg-gray-900">Full-Tower (большой)</option>
                    </select>
                  </div>

                  <label className="flex items-center space-x-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      name="rgb_preference"
                      checked={formData.rgb_preference}
                      onChange={handleInputChange}
                      className="w-5 h-5 text-pink-600 rounded border-white/30 bg-white/10 focus:ring-pink-500/50"
                    />
                    <span className="text-white/90 group-hover:text-white transition-colors">RGB подсветка</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Navigation Hint */}
            <div className="text-center text-white/60 text-sm">
              Переключайтесь между секциями внизу экрана ↓
            </div>
          </div>
        )}

        {/* Workspace Section */}
        {activeSection === 'workspace' && (
          <div className="space-y-6 animate-fadeIn">
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/5 to-emerald-500/5 rounded-2xl border border-emerald-500/20 p-8 hover:border-emerald-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10">
              <div className="flex items-center gap-3 mb-6">
                {React.createElement(FaCouch as any, { className: "text-3xl text-emerald-400" })}
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">Рабочее место</h2>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Стол */}
                <div className="space-y-4 p-6 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-2 border-emerald-500/30 rounded-xl">
                  <label className="flex items-center space-x-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      name="need_desk"
                      checked={formData.need_desk}
                      onChange={handleInputChange}
                      className="w-6 h-6 text-emerald-600 rounded border-white/30 bg-white/10 focus:ring-emerald-500/50"
                    />
                    <span className="text-xl font-bold text-emerald-200 group-hover:text-emerald-100 transition-colors">🪑 Стол</span>
                  </label>

                  {formData.need_desk && (
                    <div className="space-y-4 ml-2 mt-4 pt-4 border-t border-emerald-500/20">
                      <div>
                        <label className="block text-white/90 font-semibold mb-3">
                          Минимальная ширина: {formData.desk_min_width} см
                        </label>
                        <input
                          type="range"
                          name="desk_min_width"
                          value={formData.desk_min_width}
                          onChange={handleInputChange}
                          min="100"
                          max="200"
                          step="10"
                          className="w-full h-3 bg-emerald-500/20 rounded-lg appearance-none cursor-pointer slider-emerald"
                        />
                        <div className="flex justify-between text-xs text-white/60 mt-2">
                          <span>100 см</span>
                          <span>150 см</span>
                          <span>200 см</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-white/90 font-semibold mb-3">
                          Минимальная глубина: {formData.desk_min_depth} см
                        </label>
                        <input
                          type="range"
                          name="desk_min_depth"
                          value={formData.desk_min_depth}
                          onChange={handleInputChange}
                          min="50"
                          max="90"
                          step="5"
                          className="w-full h-3 bg-emerald-500/20 rounded-lg appearance-none cursor-pointer slider-emerald"
                        />
                        <div className="flex justify-between text-xs text-white/60 mt-2">
                          <span>50 см</span>
                          <span>70 см</span>
                          <span>90 см</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-white/90 font-semibold mb-2">Материал</label>
                        <select
                          name="desk_material_preference"
                          value={formData.desk_material_preference}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-emerald-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-400 transition-all backdrop-blur-sm"
                        >
                          <option value="any" className="bg-gray-900">Любой</option>
                          <option value="wood" className="bg-gray-900">Дерево (классика)</option>
                          <option value="metal" className="bg-gray-900">Металл (прочность)</option>
                          <option value="glass" className="bg-gray-900">Стекло (стиль)</option>
                        </select>
                      </div>

                      <div className="space-y-2">
                        <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-emerald-500/5 transition-all">
                          <input
                            type="checkbox"
                            name="desk_height_adjustable"
                            checked={formData.desk_height_adjustable}
                            onChange={handleInputChange}
                            className="w-5 h-5 text-emerald-600 rounded border-white/30 bg-white/10 focus:ring-emerald-500/50"
                          />
                          <span className="text-white/90 font-medium group-hover:text-white transition-colors">Регулируемая высота</span>
                        </label>

                        <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-emerald-500/5 transition-all">
                          <input
                            type="checkbox"
                            name="desk_cable_management"
                            checked={formData.desk_cable_management}
                            onChange={handleInputChange}
                            className="w-5 h-5 text-emerald-600 rounded border-white/30 bg-white/10 focus:ring-emerald-500/50"
                          />
                          <span className="text-white/90 font-medium group-hover:text-white transition-colors">Кабель-менеджмент</span>
                        </label>
                      </div>
                    </div>
                  )}
                </div>

                {/* Кресло */}
                <div className="space-y-4 p-6 bg-gradient-to-br from-teal-500/10 to-cyan-500/10 border-2 border-teal-500/30 rounded-xl">
                  <label className="flex items-center space-x-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      name="need_chair"
                      checked={formData.need_chair}
                      onChange={handleInputChange}
                      className="w-6 h-6 text-teal-600 rounded border-white/30 bg-white/10 focus:ring-teal-500/50"
                    />
                    <span className="text-xl font-bold text-teal-200 group-hover:text-teal-100 transition-colors">💺 Кресло</span>
                  </label>

                  {formData.need_chair && (
                    <div className="space-y-4 ml-2 mt-4 pt-4 border-t border-teal-500/20">
                      <div>
                        <label className="block text-white/90 font-semibold mb-3">
                          Максимальная нагрузка: {formData.chair_max_weight} кг
                        </label>
                        <input
                          type="range"
                          name="chair_max_weight"
                          value={formData.chair_max_weight}
                          onChange={handleInputChange}
                          min="90"
                          max="200"
                          step="10"
                          className="w-full h-3 bg-teal-500/20 rounded-lg appearance-none cursor-pointer slider-emerald"
                        />
                        <div className="flex justify-between text-xs text-white/60 mt-2">
                          <span>90 кг</span>
                          <span>150 кг</span>
                          <span>200 кг</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-white/90 font-semibold mb-2">Материал обивки</label>
                        <select
                          name="chair_material_preference"
                          value={formData.chair_material_preference}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-teal-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-teal-500/50 focus:border-teal-400 transition-all backdrop-blur-sm"
                        >
                          <option value="any" className="bg-gray-900">Любой</option>
                          <option value="leather" className="bg-gray-900">Кожа (премиум)</option>
                          <option value="fabric" className="bg-gray-900">Ткань (комфорт)</option>
                          <option value="mesh" className="bg-gray-900">Сетка (вентиляция)</option>
                        </select>
                      </div>

                      <div className="space-y-2">
                        <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-teal-500/5 transition-all">
                          <input
                            type="checkbox"
                            name="chair_ergonomic"
                            checked={formData.chair_ergonomic}
                            onChange={handleInputChange}
                            className="w-5 h-5 text-teal-600 rounded border-white/30 bg-white/10 focus:ring-teal-500/50"
                          />
                          <span className="text-white/90 font-medium group-hover:text-white transition-colors">Эргономичное</span>
                        </label>

                        <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-teal-500/5 transition-all">
                          <input
                            type="checkbox"
                            name="chair_lumbar_support"
                            checked={formData.chair_lumbar_support}
                            onChange={handleInputChange}
                            className="w-5 h-5 text-teal-600 rounded border-white/30 bg-white/10 focus:ring-teal-500/50"
                          />
                          <span className="text-white/90 font-medium group-hover:text-white transition-colors">Поясничная поддержка</span>
                        </label>

                        <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-teal-500/5 transition-all">
                          <input
                            type="checkbox"
                            name="chair_armrests_adjustable"
                            checked={formData.chair_armrests_adjustable}
                            onChange={handleInputChange}
                            className="w-5 h-5 text-teal-600 rounded border-white/30 bg-white/10 focus:ring-teal-500/50"
                          />
                          <span className="text-white/90 font-medium group-hover:text-white transition-colors">Регулируемые подлокотники</span>
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Освещение и Аксессуары */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                {/* Освещение */}
                <div className="p-6 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-2 border-yellow-500/30 rounded-xl">
                  <label className="flex items-center space-x-3 cursor-pointer group mb-4">
                    <input
                      type="checkbox"
                      name="workspace_rgb_lighting"
                      checked={formData.workspace_rgb_lighting}
                      onChange={handleInputChange}
                      className="w-6 h-6 text-yellow-600 rounded border-white/30 bg-white/10 focus:ring-yellow-500/50"
                    />
                    <div>
                      <span className="text-xl font-bold text-yellow-200 group-hover:text-yellow-100 transition-colors block">💡 Освещение</span>
                      <span className="text-white/60 text-sm">Профессиональная подсветка</span>
                    </div>
                  </label>

                  {formData.workspace_rgb_lighting && (
                    <div className="ml-2 mt-4 pt-4 border-t border-yellow-500/20">
                      <div>
                        <label className="block text-white/90 font-semibold mb-2">Температура света</label>
                        <select
                          name="workspace_lighting_type"
                          value={formData.workspace_lighting_type}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-yellow-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-400 transition-all backdrop-blur-sm"
                        >
                          <option value="any" className="bg-gray-900">Любая</option>
                          <option value="warm" className="bg-gray-900">Тёплый (расслабляющий)</option>
                          <option value="neutral" className="bg-gray-900">Нейтральный (универсальный)</option>
                          <option value="cold" className="bg-gray-900">Холодный (для концентрации)</option>
                          <option value="adjustable" className="bg-gray-900">Регулируемый (RGB)</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>

                {/* Аксессуары */}
                <div className="p-6 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-2 border-blue-500/30 rounded-xl">
                  <p className="text-xl font-bold text-blue-200 mb-4">🔧 Аксессуары</p>
                  
                  <div className="space-y-2">
                    <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-blue-500/5 transition-all">
                      <input
                        type="checkbox"
                        name="monitor_arm"
                        checked={formData.monitor_arm}
                        onChange={handleInputChange}
                        className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
                      />
                      <div>
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors block">Кронштейн для монитора</span>
                        <span className="text-white/60 text-xs">Эргономичная установка монитора</span>
                      </div>
                    </label>

                    <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-blue-500/5 transition-all">
                      <input
                        type="checkbox"
                        name="cable_management_accessories"
                        checked={formData.cable_management_accessories}
                        onChange={handleInputChange}
                        className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
                      />
                      <div>
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors block">Органайзеры для кабелей</span>
                        <span className="text-white/60 text-xs">Держатели, стяжки, каналы</span>
                      </div>
                    </label>

                    <label className="flex items-center space-x-3 cursor-pointer group p-2 rounded-lg hover:bg-blue-500/5 transition-all">
                      <input
                        type="checkbox"
                        name="workspace_sound_dampening"
                        checked={formData.workspace_sound_dampening}
                        onChange={handleInputChange}
                        className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
                      />
                      <div>
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors block">Звукопоглощение</span>
                        <span className="text-white/60 text-xs">Панели для улучшения акустики</span>
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              {/* Итоговая информация */}
              <div className="mt-6 p-6 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border-2 border-emerald-500/30 rounded-xl">
                <p className="text-emerald-200 font-bold text-lg mb-2">
                  ✓ {formData.need_desk && formData.need_chair ? 'Будет подобран полный комплект для рабочего места' : 
                       formData.need_desk ? 'Будет подобран только стол' :
                       formData.need_chair ? 'Будет подобрано только кресло' :
                       'Выберите элементы рабочего места'}
                </p>
                <p className="text-white/70 text-sm mt-1">
                  + Персональные рекомендации по освещению и эргономике
                </p>
                {(formData.monitor_arm || formData.cable_management_accessories || formData.workspace_sound_dampening) && (
                  <p className="text-cyan-300 text-sm mt-2">
                    + Дополнительные аксессуары: {[
                      formData.monitor_arm && 'кронштейн',
                      formData.cable_management_accessories && 'органайзеры',
                      formData.workspace_sound_dampening && 'звукопоглощение'
                    ].filter(Boolean).join(', ')}
                  </p>
                )}
              </div>
            </div>

            {/* Navigation Hint */}
            <div className="text-center text-white/60 text-sm">
              Переключайтесь между секциями внизу экрана ↓
            </div>
          </div>
        )}

        {/* Peripherals Section */}
        {activeSection === 'peripherals' && (
          <div className="space-y-6 animate-fadeIn">
            {/* Включение периферии */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-white/5 to-cyan-500/5 rounded-2xl border border-cyan-500/20 p-8 hover:border-cyan-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10">
              <div className="flex items-center gap-3 mb-6">
                {React.createElement(FaKeyboard as any, { className: "text-3xl text-cyan-400" })}
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">Периферия</h2>
              </div>
              
              <label className="flex items-start space-x-3 cursor-pointer group p-4 rounded-xl hover:bg-cyan-500/5 transition-all">
                <input
                  type="checkbox"
                  name="include_workspace"
                  checked={formData.include_workspace}
                  onChange={handleInputChange}
                  className="w-6 h-6 mt-1 text-cyan-600 rounded border-white/30 bg-white/10 focus:ring-cyan-500/50"
                />
                <div>
                  <span className="text-lg font-semibold text-white group-hover:text-cyan-300 transition-colors block mb-1">
                    Включить подбор периферии
                  </span>
                  <span className="text-white/70 text-sm block">
                    Настройте параметры периферийных устройств для вашей конфигурации
                  </span>
                </div>
              </label>
            </div>

            {/* Настройки периферии */}
            {formData.include_workspace && (
              <div className="backdrop-blur-xl bg-gradient-to-br from-white/5 to-cyan-500/5 rounded-2xl border border-cyan-500/20 p-8 hover:border-cyan-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10">
                <div className="flex items-center gap-3 mb-6">
                  {React.createElement(FaCheckCircle as any, { className: "text-3xl text-cyan-400" })}
                  <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">Детальные настройки</h2>
                </div>
                
                <div className="space-y-6">
                {/* Бюджет на периферию */}
                <div className="p-6 backdrop-blur-xl bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-xl">
                  <label className="block text-cyan-200 font-bold text-lg mb-4">
                    💰 Бюджет на периферию: {formData.peripheral_budget_percent}%
                  </label>
                  <input
                    type="range"
                    name="peripheral_budget_percent"
                    value={formData.peripheral_budget_percent}
                    onChange={handleInputChange}
                    min="10"
                    max="50"
                    step="5"
                    className="w-full h-3 bg-cyan-500/20 rounded-lg appearance-none cursor-pointer slider-cyan"
                  />
                  <div className="flex justify-between mt-3">
                    <span className="text-sm text-white/60">10%</span>
                    <span className="text-lg font-bold text-cyan-300">
                      ~₽{Math.round((formData.max_budget * (formData.peripheral_budget_percent || 30)) / 100).toLocaleString()}
                    </span>
                    <span className="text-sm text-white/60">50%</span>
                  </div>
                </div>

                {/* Выбор устройств по категориям */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Базовые устройства */}
                  <div className="p-6 bg-cyan-500/5 border border-cyan-500/20 rounded-xl">
                    <p className="text-cyan-300 font-bold text-lg mb-4">🖥️ Базовые устройства</p>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-cyan-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="need_monitor"
                          checked={formData.need_monitor}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-cyan-600 rounded border-white/30 bg-white/10 focus:ring-cyan-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Монитор</span>
                      </label>

                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-cyan-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="need_keyboard"
                          checked={formData.need_keyboard}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-cyan-600 rounded border-white/30 bg-white/10 focus:ring-cyan-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Клавиатура</span>
                      </label>

                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-cyan-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="need_mouse"
                          checked={formData.need_mouse}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-cyan-600 rounded border-white/30 bg-white/10 focus:ring-cyan-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Мышь</span>
                      </label>

                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-cyan-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="need_headset"
                          checked={formData.need_headset}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-cyan-600 rounded border-white/30 bg-white/10 focus:ring-cyan-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Гарнитура</span>
                      </label>
                    </div>
                  </div>

                  {/* Дополнительно */}
                  <div className="p-6 bg-purple-500/5 border border-purple-500/20 rounded-xl">
                    <p className="text-purple-300 font-bold text-lg mb-4">📹 Дополнительно</p>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-purple-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="need_webcam"
                          checked={formData.need_webcam}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-purple-600 rounded border-white/30 bg-white/10 focus:ring-purple-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Веб-камера</span>
                      </label>

                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-purple-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="need_microphone"
                          checked={formData.need_microphone}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-purple-600 rounded border-white/30 bg-white/10 focus:ring-purple-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Микрофон</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Расширенные параметры монитора */}
                {formData.need_monitor && (
                  <div className="p-6 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border-2 border-cyan-500/30 rounded-xl">
                    <p className="text-cyan-200 font-bold text-xl mb-5 flex items-center gap-2">
                      🖥️ Параметры монитора
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      <div>
                        <label className="block text-white/90 font-medium mb-2">Частота обновления</label>
                        <select
                          name="monitor_min_refresh_rate"
                          value={formData.monitor_min_refresh_rate}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-cyan-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-400 transition-all backdrop-blur-sm"
                        >
                          <option value="60" className="bg-gray-900">60 Hz (стандарт)</option>
                          <option value="75" className="bg-gray-900">75 Hz</option>
                          <option value="120" className="bg-gray-900">120 Hz</option>
                          <option value="144" className="bg-gray-900">144 Hz (игровой)</option>
                          <option value="165" className="bg-gray-900">165 Hz</option>
                          <option value="240" className="bg-gray-900">240 Hz (pro)</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-white/90 font-medium mb-2">Разрешение</label>
                        <select
                          name="monitor_min_resolution"
                          value={formData.monitor_min_resolution}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-cyan-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-400 transition-all backdrop-blur-sm"
                        >
                          <option value="1920x1080" className="bg-gray-900">Full HD (1920x1080)</option>
                          <option value="2560x1440" className="bg-gray-900">2K (2560x1440)</option>
                          <option value="3840x2160" className="bg-gray-900">4K (3840x2160)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-white/90 font-medium mb-2">
                          Диагональ: {formData.monitor_size_preference}"
                        </label>
                        <input
                          type="range"
                          name="monitor_size_preference"
                          value={formData.monitor_size_preference}
                          onChange={handleInputChange}
                          min="21"
                          max="34"
                          step="1"
                          className="w-full h-2 bg-cyan-500/20 rounded-lg appearance-none cursor-pointer slider-cyan"
                        />
                        <div className="flex justify-between text-xs text-white/60 mt-1">
                          <span>21"</span>
                          <span>27"</span>
                          <span>34"</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-white/90 font-medium mb-2">Тип матрицы</label>
                        <select
                          name="monitor_panel_type"
                          value={formData.monitor_panel_type}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-cyan-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-400 transition-all backdrop-blur-sm"
                        >
                          <option value="any" className="bg-gray-900">Любая</option>
                          <option value="ips" className="bg-gray-900">IPS (лучшие углы обзора)</option>
                          <option value="va" className="bg-gray-900">VA (высокая контрастность)</option>
                          <option value="tn" className="bg-gray-900">TN (быстрый отклик)</option>
                          <option value="oled" className="bg-gray-900">OLED (премиум)</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Расширенные параметры клавиатуры */}
                {formData.need_keyboard && (
                  <div className="p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-2 border-purple-500/30 rounded-xl">
                    <p className="text-purple-200 font-bold text-xl mb-5 flex items-center gap-2">
                      ⌨️ Параметры клавиатуры
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      <div>
                        <label className="block text-white/90 font-medium mb-2">Тип клавиатуры</label>
                        <select
                          name="keyboard_type_preference"
                          value={formData.keyboard_type_preference}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-purple-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 transition-all backdrop-blur-sm"
                        >
                          <option value="any" className="bg-gray-900">Любая</option>
                          <option value="mechanical" className="bg-gray-900">Механическая (быстрый отклик)</option>
                          <option value="membrane" className="bg-gray-900">Мембранная (тихая)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-white/90 font-medium mb-2">Тип переключателей</label>
                        <select
                          name="keyboard_switch_type"
                          value={formData.keyboard_switch_type}
                          onChange={handleInputChange}
                          className="w-full bg-white/10 border border-purple-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 transition-all backdrop-blur-sm"
                        >
                          <option value="any" className="bg-gray-900">Любой</option>
                          <option value="linear" className="bg-gray-900">Linear (плавные)</option>
                          <option value="tactile" className="bg-gray-900">Tactile (с откликом)</option>
                          <option value="clicky" className="bg-gray-900">Clicky (с щелчком)</option>
                        </select>
                      </div>

                      <div className="md:col-span-2">
                        <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-purple-500/5 transition-all">
                          <input
                            type="checkbox"
                            name="keyboard_rgb"
                            checked={formData.keyboard_rgb}
                            onChange={handleInputChange}
                            className="w-5 h-5 text-purple-600 rounded border-white/30 bg-white/10 focus:ring-purple-500/50"
                          />
                          <span className="text-white/90 font-medium group-hover:text-white transition-colors">RGB подсветка</span>
                        </label>
                      </div>
                    </div>
                  </div>
                )}

                {/* Расширенные параметры мыши */}
                {formData.need_mouse && (
                  <div className="p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-2 border-blue-500/30 rounded-xl">
                    <p className="text-blue-200 font-bold text-xl mb-5 flex items-center gap-2">
                      🖱️ Параметры мыши
                    </p>
                    <div className="space-y-5">
                      <div>
                        <label className="block text-white/90 font-medium mb-3">
                          Минимальный DPI: {formData.mouse_min_dpi}
                        </label>
                        <input
                          type="range"
                          name="mouse_min_dpi"
                          value={formData.mouse_min_dpi}
                          onChange={handleInputChange}
                          min="800"
                          max="25600"
                          step="400"
                          className="w-full h-3 bg-blue-500/20 rounded-lg appearance-none cursor-pointer slider-cyan"
                        />
                        <div className="flex justify-between text-xs text-white/60 mt-2">
                          <span>800 (офис)</span>
                          <span>6400 (стандарт)</span>
                          <span>25600 (pro)</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-white/90 font-medium mb-2">Тип сенсора</label>
                          <select
                            name="mouse_sensor_type"
                            value={formData.mouse_sensor_type}
                            onChange={handleInputChange}
                            className="w-full bg-white/10 border border-blue-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 transition-all backdrop-blur-sm"
                          >
                            <option value="any" className="bg-gray-900">Любой</option>
                            <option value="optical" className="bg-gray-900">Optical (точный)</option>
                            <option value="laser" className="bg-gray-900">Laser (универсальный)</option>
                          </select>
                        </div>

                        <div className="flex items-end">
                          <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-blue-500/5 transition-all w-full">
                            <input
                              type="checkbox"
                              name="mouse_wireless"
                              checked={formData.mouse_wireless}
                              onChange={handleInputChange}
                              className="w-5 h-5 text-blue-600 rounded border-white/30 bg-white/10 focus:ring-blue-500/50"
                            />
                            <span className="text-white/90 font-medium group-hover:text-white transition-colors">Беспроводная</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Параметры гарнитуры */}
                {formData.need_headset && (
                  <div className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-2 border-green-500/30 rounded-xl">
                    <p className="text-green-200 font-bold text-xl mb-5 flex items-center gap-2">
                      🎧 Параметры гарнитуры
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-green-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="headset_wireless"
                          checked={formData.headset_wireless}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-green-600 rounded border-white/30 bg-white/10 focus:ring-green-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Беспроводная</span>
                      </label>

                      <label className="flex items-center space-x-3 cursor-pointer group p-3 rounded-lg hover:bg-green-500/5 transition-all">
                        <input
                          type="checkbox"
                          name="headset_noise_cancellation"
                          checked={formData.headset_noise_cancellation}
                          onChange={handleInputChange}
                          className="w-5 h-5 text-green-600 rounded border-white/30 bg-white/10 focus:ring-green-500/50"
                        />
                        <span className="text-white/90 font-medium group-hover:text-white transition-colors">Шумоподавление</span>
                      </label>
                    </div>
                  </div>
                )}

                {/* Параметры веб-камеры */}
                {formData.need_webcam && (
                  <div className="p-6 bg-gradient-to-br from-orange-500/10 to-yellow-500/10 border-2 border-orange-500/30 rounded-xl">
                    <p className="text-orange-200 font-bold text-xl mb-5 flex items-center gap-2">
                      📹 Параметры веб-камеры
                    </p>
                    <div>
                      <label className="block text-white/90 font-medium mb-2">Минимальное разрешение</label>
                      <select
                        name="webcam_min_resolution"
                        value={formData.webcam_min_resolution}
                        onChange={handleInputChange}
                        className="w-full bg-white/10 border border-orange-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-orange-500/50 focus:border-orange-400 transition-all backdrop-blur-sm"
                      >
                        <option value="any" className="bg-gray-900">Любое</option>
                        <option value="720p" className="bg-gray-900">720p HD</option>
                        <option value="1080p" className="bg-gray-900">1080p Full HD</option>
                        <option value="4k" className="bg-gray-900">4K Ultra HD</option>
                      </select>
                    </div>
                  </div>
                )}

                {/* Параметры микрофона */}
                {formData.need_microphone && (
                  <div className="p-6 bg-gradient-to-br from-pink-500/10 to-rose-500/10 border-2 border-pink-500/30 rounded-xl">
                    <p className="text-pink-200 font-bold text-xl mb-5 flex items-center gap-2">
                      🎤 Параметры микрофона
                    </p>
                    <div>
                      <label className="block text-white/90 font-medium mb-2">Тип микрофона</label>
                      <select
                        name="microphone_type"
                        value={formData.microphone_type}
                        onChange={handleInputChange}
                        className="w-full bg-white/10 border border-pink-500/30 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-pink-500/50 focus:border-pink-400 transition-all backdrop-blur-sm"
                      >
                        <option value="any" className="bg-gray-900">Любой</option>
                        <option value="condenser" className="bg-gray-900">Condenser (студийный)</option>
                        <option value="dynamic" className="bg-gray-900">Dynamic (универсальный)</option>
                        <option value="usb" className="bg-gray-900">USB (удобный)</option>
                      </select>
                    </div>
                  </div>
                )}

                {/* Итоговая информация */}
                <div className="p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-2 border-green-500/30 rounded-xl">
                  <p className="text-green-200 font-bold text-lg mb-2">
                    ✓ Будет подобрано: {[
                      formData.need_monitor && 'монитор',
                      formData.need_keyboard && 'клавиатура',
                      formData.need_mouse && 'мышь',
                      formData.need_headset && 'гарнитура',
                      formData.need_webcam && 'веб-камера',
                      formData.need_microphone && 'микрофон',
                      formData.need_desk && 'стол',
                      formData.need_chair && 'кресло'
                    ].filter(Boolean).join(', ')}
                  </p>
                  <p className="text-white/70 text-sm mt-1">
                    + Персональные рекомендации по освещению рабочего места
                  </p>
                </div>
                </div>
              </div>
            )}

            {/* Navigation Hint */}
            <div className="text-center text-white/60 text-sm">
              Переключайтесь между секциями внизу экрана ↓
            </div>
          </div>
        )}

        {/* Кнопка отправки - показывается во всех секциях */}
        <div className="flex justify-center animate-fadeIn">
          <button
            type="submit"
            disabled={loading}
            className="group relative px-12 py-4 rounded-2xl text-lg font-bold text-white overflow-hidden transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 transition-opacity group-hover:opacity-90"></div>
            <div className="relative flex items-center gap-3">
              {loading ? (
                <LoadingSpinner />
              ) : (
                <>
                  {React.createElement(FaRocket as any, { className: "text-xl" })}
                  <span>Подобрать конфигурацию</span>
                </>
              )}
            </div>
          </button>
        </div>
      </form>

      {/* Dock Navigation */}
      <Dock items={dockItems} />
    </div>
  );
};

export default Configurator;
