import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { configurationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import type { PCConfiguration } from '../types';
import { FiPlus, FiCpu, FiMonitor, FiDatabase, FiEye, FiTrash2, FiAlertCircle } from 'react-icons/fi';

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
    <div className="py-8">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-8">
        <div>
          <h1 className="text-heading text-3xl md:text-4xl text-white mb-2">
            Мои конфигурации
          </h1>
          <p className="text-gray-500">
            {configurations.length} сохраненных сборок
          </p>
        </div>
        
        <Link
          to="/configurator"
          className="btn-primary flex items-center gap-2 px-5 py-3"
        >
          {React.createElement(FiPlus as any, { className: "text-lg" })}
          <span>Создать новую</span>
        </Link>
      </div>

      {configurations.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 mx-auto flex items-center justify-center bg-bg-surface mb-4">
            {React.createElement(FiDatabase as any, { className: "text-3xl text-gray-500" })}
          </div>
          <h3 className="text-xl font-heading font-semibold text-white mb-2">
            Нет сохраненных конфигураций
          </h3>
          <p className="text-gray-500 mb-6">
            Создайте свою первую сборку с помощью конфигуратора
          </p>
          <Link
            to="/configurator"
            className="btn-primary inline-flex items-center gap-2"
          >
            {React.createElement(FiPlus as any, {})}
            <span>Создать конфигурацию</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {configurations.map((config) => (
            <div key={config.id} className="card-accent p-5 group">
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-heading font-semibold text-white mb-1">
                    {config.name || `Сборка #${config.id}`}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {new Date(config.created_at).toLocaleDateString('ru-RU')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-heading font-bold text-primary">
                    {formatPrice(config.total_price)} ₽
                  </p>
                </div>
              </div>

              {/* Components */}
              <div className="space-y-2 text-sm mb-4">
                {config.cpu && (
                  <div className="flex items-center gap-2 text-gray-400">
                    {React.createElement(FiCpu as any, { className: "text-primary flex-shrink-0" })}
                    <span className="truncate">{typeof config.cpu === 'object' ? config.cpu.name : ''}</span>
                  </div>
                )}
                {config.gpu && (
                  <div className="flex items-center gap-2 text-gray-400">
                    {React.createElement(FiMonitor as any, { className: "text-primary flex-shrink-0" })}
                    <span className="truncate">{typeof config.gpu === 'object' ? config.gpu.name : ''}</span>
                  </div>
                )}
                {config.ram && (
                  <div className="flex items-center gap-2 text-gray-400">
                    {React.createElement(FiDatabase as any, { className: "text-primary flex-shrink-0" })}
                    <span className="truncate">{typeof config.ram === 'object' ? config.ram.name : ''}</span>
                  </div>
                )}
              </div>

              {/* Warnings */}
              {config.compatibility_issues && (
                <div className="flex items-center gap-2 p-2 bg-yellow-500/10 border border-yellow-500/30 mb-4">
                  {React.createElement(FiAlertCircle as any, { className: "text-yellow-500" })}
                  <span className="text-xs text-yellow-400">Проблемы совместимости</span>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-border-dark">
                <Link
                  to={`/configuration/${config.id}`}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 py-2 text-sm"
                >
                  {React.createElement(FiEye as any, {})}
                  <span>Открыть</span>
                </Link>
                <button
                  onClick={() => handleDelete(config.id)}
                  className="btn-secondary px-4 py-2 text-red-400 hover:text-red-300 hover:border-red-500/50"
                >
                  {React.createElement(FiTrash2 as any, {})}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyConfigurations;
