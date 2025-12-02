import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { configurationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import type { PCConfiguration } from '../types';
import { FaPlus, FaMicrochip, FaVideo, FaMemory, FaEye, FaTrash, FaExclamationTriangle, FaList } from 'react-icons/fa';

const MyConfigurations: React.FC = () => {
  const [configurations, setConfigurations] = useState<PCConfiguration[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConfigurations();
  }, []);

  const loadConfigurations = async () => {
    try {
      const response = await configurationAPI.getConfigurations();
      setConfigurations(response.data.results);
    } catch (error) {
      console.error('Ошибка загрузки конфигураций:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить эту конфигурацию?')) {
      try {
        await configurationAPI.deleteConfiguration(id);
        setConfigurations(configurations.filter((c) => c.id !== id));
      } catch (error) {
        console.error('Ошибка удаления:', error);
      }
    }
  };

  const formatPrice = (price: string | number): string => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return numPrice.toLocaleString();
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex flex-wrap justify-between items-center gap-4 mb-12">
        <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400">
          Мои конфигурации
        </h1>
        <Link
          to="/configurator"
          className="group relative px-6 py-3 rounded-xl font-bold text-white overflow-hidden transition-all duration-300 hover:scale-105"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 transition-opacity group-hover:opacity-90"></div>
          <div className="relative flex items-center gap-2">
            {React.createElement(FaPlus as any, { className: "text-lg" })}
            <span>Создать новую</span>
          </div>
        </Link>
      </div>

      {configurations.length === 0 ? (
        <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-16 text-center">
          {React.createElement(FaList as any, { className: "text-8xl text-white/20 mx-auto mb-6" })}
          <h2 className="text-3xl font-semibold text-white mb-3">Конфигурации не найдены</h2>
          <p className="text-white/70 text-lg mb-8">Создайте свою первую конфигурацию ПК</p>
          <Link
            to="/configurator"
            className="group relative inline-block px-10 py-4 rounded-2xl font-bold text-white text-lg overflow-hidden transition-all duration-300 hover:scale-105"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600"></div>
            <div className="relative flex items-center gap-3">
              {React.createElement(FaPlus as any, { className: "text-xl" })}
              <span>Начать подбор</span>
            </div>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {configurations.map((config) => (
            <div key={config.id} className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 overflow-hidden hover:border-white/20 hover:scale-[1.02] transition-all duration-300">
              <div className="bg-gradient-to-r from-blue-500 to-cyan-600 p-5">
                <h3 className="text-xl font-bold text-white">
                  {config.name || `Конфигурация #${config.id}`}
                </h3>
                <p className="text-blue-100 text-sm mt-1">
                  {new Date(config.created_at).toLocaleDateString('ru-RU')}
                </p>
              </div>

              <div className="p-6">
                {config.user_type && (
                  <div className="mb-4 flex flex-wrap gap-2">
                    <span className="inline-block bg-blue-500/20 text-blue-300 border border-blue-500/30 px-3 py-1 rounded-xl text-sm font-semibold backdrop-blur-sm">
                      {config.user_type.replace('_', ' ')}
                    </span>
                    {config.priority && (
                      <span className="inline-block bg-purple-500/20 text-purple-300 border border-purple-500/30 px-3 py-1 rounded-xl text-sm font-semibold backdrop-blur-sm">
                        {config.priority}
                      </span>
                    )}
                  </div>
                )}

                <div className="space-y-3 text-sm mb-4">
                  {(typeof config.cpu === 'object' ? config.cpu : config.cpu_detail) && (
                    <div className="flex items-center gap-3">
                      {React.createElement(FaMicrochip as any, { className: "text-blue-400" })}
                      <span className="text-white/70">CPU:</span>
                      <span className="font-semibold text-white truncate ml-auto">
                        {(typeof config.cpu === 'object' ? config.cpu : config.cpu_detail)?.name}
                      </span>
                    </div>
                  )}
                  {(typeof config.gpu === 'object' ? config.gpu : config.gpu_detail) && (
                    <div className="flex items-center gap-3">
                      {React.createElement(FaVideo as any, { className: "text-green-400" })}
                      <span className="text-white/70">GPU:</span>
                      <span className="font-semibold text-white truncate ml-auto">
                        {(typeof config.gpu === 'object' ? config.gpu : config.gpu_detail)?.name}
                      </span>
                    </div>
                  )}
                  {(typeof config.ram === 'object' ? config.ram : config.ram_detail) && (
                    <div className="flex items-center gap-3">
                      {React.createElement(FaMemory as any, { className: "text-purple-400" })}
                      <span className="text-white/70">RAM:</span>
                      <span className="font-semibold text-white ml-auto">
                        {(typeof config.ram === 'object' ? config.ram : config.ram_detail)?.capacity} GB
                      </span>
                    </div>
                  )}
                </div>

                <div className="border-t border-white/10 pt-4 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-white/70">Итого:</span>
                    <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
                      ₽{formatPrice(config.total_price)}
                    </span>
                  </div>
                </div>

                {config.is_compatible === false && (
                  <div className="backdrop-blur-xl bg-red-500/10 border border-red-500/30 text-red-300 px-3 py-2 rounded-xl text-sm mb-4 flex items-center gap-2">
                    {React.createElement(FaExclamationTriangle as any, { className: "" })}
                    <span>Проблемы совместимости</span>
                  </div>
                )}

                <div className="flex gap-3">
                  <Link
                    to={`/configuration/${config.id}`}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-center py-3 rounded-xl hover:opacity-90 transition font-semibold flex items-center justify-center gap-2"
                  >
                    {React.createElement(FaEye as any, {})}
                    <span>Подробнее</span>
                  </Link>
                  <button
                    onClick={() => handleDelete(config.id)}
                    className="px-4 py-3 bg-red-500/20 border border-red-500/30 text-red-300 rounded-xl hover:bg-red-500/30 transition backdrop-blur-sm flex items-center justify-center"
                  >
                    {React.createElement(FaTrash as any, {})}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyConfigurations;
