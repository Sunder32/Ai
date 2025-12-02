import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { configurationAPI } from '../services/api';
import type { ConfigurationRequest } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import { FaRocket, FaUser, FaDollarSign, FaCheckCircle } from 'react-icons/fa';

const Configurator: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
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

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-5xl font-bold mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-center">
        Конфигуратор ПК
      </h1>

      {error && (
        <div className="backdrop-blur-xl bg-red-500/10 border border-red-500/30 text-red-300 px-6 py-4 rounded-2xl mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Тип пользователя */}
        <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 hover:border-white/20 transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            {React.createElement(FaUser as any, { className: "text-2xl text-blue-400" })}
            <h2 className="text-2xl font-semibold text-white">Профиль пользователя</h2>
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

        {/* Кнопка отправки */}
        <div className="flex justify-center">
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
    </div>
  );
};

export default Configurator;
