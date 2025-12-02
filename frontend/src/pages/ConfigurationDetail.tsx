import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { configurationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import type { PCConfiguration } from '../types';
import { FaMicrochip, FaVideo, FaMemory, FaHdd, FaBolt, FaBoxOpen, FaSnowflake, FaServer, FaCheckCircle, FaExclamationTriangle, FaLightbulb } from 'react-icons/fa';

const ConfigurationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [config, setConfig] = useState<PCConfiguration | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadConfiguration(parseInt(id));
    }
  }, [id]);

  const loadConfiguration = async (configId: number) => {
    try {
      const response = await configurationAPI.getConfiguration(configId);
      setConfig(response.data);
    } catch (error) {
      console.error('Ошибка загрузки конфигурации:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!config) return (
    <div className="backdrop-blur-xl bg-red-500/10 border border-red-500/30 rounded-2xl p-8 text-center">
      <p className="text-2xl font-semibold text-red-300">Конфигурация не найдена</p>
    </div>
  );

  const getCPU = () => typeof config.cpu === 'object' ? config.cpu : config.cpu_detail;
  const getGPU = () => typeof config.gpu === 'object' ? config.gpu : config.gpu_detail;
  const getMB = () => typeof config.motherboard === 'object' ? config.motherboard : config.motherboard_detail;
  const getRAM = () => typeof config.ram === 'object' ? config.ram : config.ram_detail;
  const getStorage = () => typeof config.storage === 'object' ? config.storage : config.storage_primary_detail;
  const getPSU = () => typeof config.psu === 'object' ? config.psu : config.psu_detail;
  const getCase = () => typeof config.case === 'object' ? config.case : config.case_detail;
  const getCooling = () => typeof config.cooling === 'object' ? config.cooling : config.cooling_detail;

  const chartData = [
    { name: 'Процессор', value: parseFloat(String(getCPU()?.price || 0)), color: '#3B82F6' },
    { name: 'Видеокарта', value: parseFloat(String(getGPU()?.price || 0)), color: '#10B981' },
    { name: 'Материнская плата', value: parseFloat(String(getMB()?.price || 0)), color: '#F59E0B' },
    { name: 'Память', value: parseFloat(String(getRAM()?.price || 0)), color: '#EF4444' },
    { name: 'Накопитель', value: parseFloat(String(getStorage()?.price || 0)), color: '#8B5CF6' },
    { name: 'Блок питания', value: parseFloat(String(getPSU()?.price || 0)), color: '#EC4899' },
    { name: 'Корпус', value: parseFloat(String(getCase()?.price || 0)), color: '#14B8A6' },
    { name: 'Охлаждение', value: parseFloat(String(getCooling()?.price || 0)), color: '#6366F1' },
  ].filter((item) => item.value > 0);

  const ComponentSection: React.FC<{ title: string; component: any; specs: Record<string, any>; icon: any }> = ({
    title,
    component,
    specs,
    icon,
  }) => (
    <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 mb-4 hover:border-white/20 transition-all duration-300">
      <div className="flex items-center gap-3 mb-4">
        {React.createElement(icon as any, { className: "text-2xl text-blue-400" })}
        <h3 className="text-xl font-bold text-white">{title}</h3>
      </div>
      {component ? (
        <>
          <div className="mb-4">
            <p className="text-2xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">{component.name}</p>
            <p className="text-white/70">{component.manufacturer}</p>
            <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400 mt-2">₽{component.price.toLocaleString()}</p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(specs).map(([key, value]) => (
              <div key={key} className="flex justify-between border-b border-white/10 pb-2">
                <span className="text-white/70">{key}:</span>
                <span className="font-semibold text-white">{value}</span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="text-white/50 italic">Не выбран</p>
      )}
    </div>
  );

  return (
    <div>
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 mb-8">
        <h1 className="text-5xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
          Конфигурация #{config.id}
        </h1>
        <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
          <div className="space-y-2">
            <p className="text-white/80">
              Тип: <span className="font-semibold text-white capitalize">{config.user_type?.replace('_', ' ')}</span>
            </p>
            <p className="text-white/80">
              Приоритет: <span className="font-semibold text-white capitalize">{config.priority}</span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-white/80 mb-1">Итого:</p>
            <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
              ₽{config.total_price.toLocaleString()}
            </p>
          </div>
        </div>

        {config.is_compatible === false && (
          <div className="backdrop-blur-xl bg-red-500/10 border-l-4 border-red-500 rounded-xl p-5 mb-6">
            <div className="flex items-center gap-3 mb-2">
              {React.createElement(FaExclamationTriangle as any, { className: "text-2xl text-red-400" })}
              <p className="font-bold text-red-300">Обнаружены проблемы совместимости</p>
            </div>
            {config.compatibility_issues && (
              <ul className="list-disc list-inside mt-3 text-red-200 space-y-1">
                {config.compatibility_issues.map((issue, idx) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {config.is_compatible && (
          <div className="backdrop-blur-xl bg-green-500/10 border-l-4 border-green-500 rounded-xl p-5 mb-6">
            <div className="flex items-center gap-3">
              {React.createElement(FaCheckCircle as any, { className: "text-2xl text-green-400" })}
              <p className="font-bold text-green-300">Все компоненты совместимы</p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Components List */}
        <div>
          <h2 className="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
            Компоненты
          </h2>

          <ComponentSection
            title="Процессор"
            component={getCPU()}
            icon={FaMicrochip}
            specs={{
              Сокет: getCPU()?.socket,
              'Ядра/Потоки': `${getCPU()?.cores}/${getCPU()?.threads}`,
              Частота: `${getCPU()?.base_clock} - ${getCPU()?.boost_clock} ГГц`,
              TDP: `${getCPU()?.tdp} Вт`,
            }}
          />

          <ComponentSection
            title="Видеокарта"
            component={getGPU()}
            icon={FaVideo}
            specs={{
              Чипсет: getGPU()?.chipset,
              Память: `${getGPU()?.memory} GB ${getGPU()?.memory_type}`,
              'Частота ядра': `${getGPU()?.core_clock} MHz`,
              TDP: `${getGPU()?.tdp} Вт`,
            }}
          />

          <ComponentSection
            title="Материнская плата"
            component={getMB()}
            icon={FaServer}
            specs={{
              Сокет: getMB()?.socket,
              Чипсет: getMB()?.chipset,
              'Форм-фактор': getMB()?.form_factor,
              'Слотов памяти': getMB()?.memory_slots,
            }}
          />

          <ComponentSection
            title="Оперативная память"
            component={getRAM()}
            icon={FaMemory}
            specs={{
              Тип: getRAM()?.memory_type,
              Объем: `${getRAM()?.capacity} GB`,
              Частота: `${getRAM()?.speed} MHz`,
              Модулей: getRAM()?.modules,
            }}
          />

          <ComponentSection
            title="Накопитель"
            component={getStorage()}
            icon={FaHdd}
            specs={{
              Тип: getStorage()?.storage_type?.toUpperCase(),
              Объем: `${getStorage()?.capacity} GB`,
              Чтение: getStorage()?.read_speed ? `${getStorage()?.read_speed} MB/s` : 'N/A',
              Запись: getStorage()?.write_speed ? `${getStorage()?.write_speed} MB/s` : 'N/A',
            }}
          />

          <ComponentSection
            title="Блок питания"
            component={getPSU()}
            icon={FaBolt}
            specs={{
              Мощность: `${getPSU()?.wattage} Вт`,
              Сертификат: getPSU()?.efficiency_rating,
              Модульный: getPSU()?.modular ? 'Да' : 'Нет',
            }}
          />

          <ComponentSection
            title="Корпус"
            component={getCase()}
            icon={FaBoxOpen}
            specs={{
              'Форм-фактор': getCase()?.form_factor,
              'Макс. GPU': `${getCase()?.max_gpu_length} мм`,
              'Макс. длина GPU': `${getCase()?.max_gpu_length} мм`,
            }}
          />

          <ComponentSection
            title="Охлаждение"
            component={getCooling()}
            icon={FaSnowflake}
            specs={{
              Тип: getCooling()?.cooling_type,
              Сокеты: getCooling()?.socket_compatibility,
              TDP: `${getCooling()?.max_tdp} Вт`,
            }}
          />
        </div>

        {/* Chart and Recommendations */}
        <div>
          <h2 className="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
            Распределение бюджета
          </h2>
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 mb-8">
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => `₽${value.toLocaleString()}`}
                  contentStyle={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                  labelStyle={{ color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend wrapperStyle={{ color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {config.recommendations && config.recommendations.length > 0 && (
            <div>
              <h2 className="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                Рекомендации
              </h2>
              {config.recommendations.map((rec) => (
                <div key={rec.id} className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 mb-4 hover:border-white/20 transition-all duration-300">
                  <div className="flex items-center gap-3 mb-3">
                    {React.createElement(FaLightbulb as any, { className: "text-2xl text-yellow-400" })}
                    <h3 className="text-lg font-semibold text-white">{rec.title}</h3>
                  </div>
                  <p className="text-white/80 mb-4">{rec.description}</p>
                  <div className="flex flex-wrap justify-between items-center gap-3">
                    <span
                      className={`px-4 py-2 rounded-xl text-sm font-semibold backdrop-blur-sm ${
                        rec.priority === 'high'
                          ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                          : rec.priority === 'medium'
                          ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                          : 'bg-green-500/20 text-green-300 border border-green-500/30'
                      }`}
                    >
                      {rec.priority === 'high' ? 'Высокий' : rec.priority === 'medium' ? 'Средний' : 'Низкий'}
                    </span>
                    {rec.estimated_cost && (
                      <span className="text-white/70 font-semibold">Стоимость: ₽{rec.estimated_cost.toLocaleString()}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfigurationDetail;
