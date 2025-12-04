import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { configurationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import type { PCConfiguration } from '../types';
import { FiCpu, FiMonitor, FiDatabase, FiHardDrive, FiZap, FiBox, FiThermometer, FiCheck, FiAlertTriangle, FiArrowLeft } from 'react-icons/fi';

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
    <div className="card p-12 text-center">
      {React.createElement(FiAlertTriangle as any, { className: "text-4xl text-red-400 mx-auto mb-4" })}
      <p className="text-xl text-white mb-4">Конфигурация не найдена</p>
      <Link to="/my-configurations" className="btn-primary inline-flex items-center gap-2">
        {React.createElement(FiArrowLeft as any, {})}
        <span>Назад к списку</span>
      </Link>
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
    { name: 'CPU', value: parseFloat(String(getCPU()?.price || 0)), color: '#10b981' },
    { name: 'GPU', value: parseFloat(String(getGPU()?.price || 0)), color: '#34d399' },
    { name: 'Материнская плата', value: parseFloat(String(getMB()?.price || 0)), color: '#3b82f6' },
    { name: 'RAM', value: parseFloat(String(getRAM()?.price || 0)), color: '#8b5cf6' },
    { name: 'Накопитель', value: parseFloat(String(getStorage()?.price || 0)), color: '#f59e0b' },
    { name: 'БП', value: parseFloat(String(getPSU()?.price || 0)), color: '#ec4899' },
    { name: 'Корпус', value: parseFloat(String(getCase()?.price || 0)), color: '#06b6d4' },
    { name: 'Охлаждение', value: parseFloat(String(getCooling()?.price || 0)), color: '#6366f1' },
  ].filter((item) => item.value > 0);

  interface ComponentSectionProps {
    title: string;
    component: any;
    specs: Record<string, any>;
    icon: any;
  }

  const ComponentSection: React.FC<ComponentSectionProps> = ({ title, component, specs, icon: IconComponent }) => (
    <div className="card p-5">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 flex items-center justify-center bg-primary/10">
          {React.createElement(IconComponent as any, { className: "text-xl text-primary" })}
        </div>
        <h3 className="text-lg font-heading font-semibold text-white">{title}</h3>
      </div>
      {component ? (
        <>
          <div className="mb-4">
            <p className="text-base font-medium text-white mb-1">{component.name}</p>
            <p className="text-sm text-gray-500">{component.manufacturer}</p>
            <p className="text-xl font-heading font-bold text-primary mt-2">
              {Number(component.price).toLocaleString()} ₽
            </p>
          </div>
          <div className="space-y-2 text-sm">
            {Object.entries(specs).map(([key, value]) => (
              <div key={key} className="flex justify-between py-1.5 border-b border-border-dark last:border-0">
                <span className="text-gray-500">{key}</span>
                <span className="font-medium text-white">{value}</span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="text-gray-500 italic">Не выбран</p>
      )}
    </div>
  );

  return (
    <div className="py-8">
      {/* Header */}
      <div className="mb-8">
        <Link to="/my-configurations" className="inline-flex items-center gap-2 text-gray-400 hover:text-primary transition-colors mb-4">
          {React.createElement(FiArrowLeft as any, {})}
          <span>Назад к списку</span>
        </Link>
        
        <div className="flex flex-wrap justify-between items-start gap-4">
          <div>
            <h1 className="text-heading text-3xl md:text-4xl text-white mb-2">
              {config.name || `Сборка #${config.id}`}
            </h1>
            <p className="text-gray-500">
              Создана {new Date(config.created_at).toLocaleDateString('ru-RU')}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500 mb-1">Общая стоимость</p>
            <p className="text-3xl font-heading font-bold text-primary">
              {Number(config.total_price).toLocaleString()} ₽
            </p>
          </div>
        </div>
      </div>

      {/* Compatibility Status */}
      <div className={`p-4 mb-8 flex items-center gap-3 ${
        config.compatibility_issues 
          ? 'bg-yellow-500/10 border border-yellow-500/30' 
          : 'bg-primary/10 border border-primary/30'
      }`}>
        {config.compatibility_issues ? (
          <>
            {React.createElement(FiAlertTriangle as any, { className: "text-xl text-yellow-500" })}
            <span className="text-yellow-400">Обнаружены проблемы совместимости</span>
          </>
        ) : (
          <>
            {React.createElement(FiCheck as any, { className: "text-xl text-primary" })}
            <span className="text-primary">Все компоненты совместимы</span>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Components */}
        <div className="lg:col-span-2 space-y-4">
          <ComponentSection
            title="Процессор"
            component={getCPU()}
            specs={{
              'Сокет': getCPU()?.socket,
              'Ядра': getCPU()?.cores,
              'Потоки': getCPU()?.threads,
              'Базовая частота': `${getCPU()?.base_clock} ГГц`,
              'TDP': `${getCPU()?.tdp} Вт`,
            }}
            icon={FiCpu}
          />

          <ComponentSection
            title="Видеокарта"
            component={getGPU()}
            specs={{
              'Память': `${getGPU()?.memory} GB ${getGPU()?.memory_type}`,
              'Частота': `${getGPU()?.core_clock} MHz`,
              'TDP': `${getGPU()?.tdp} Вт`,
            }}
            icon={FiMonitor}
          />

          <ComponentSection
            title="Материнская плата"
            component={getMB()}
            specs={{
              'Сокет': getMB()?.socket,
              'Чипсет': getMB()?.chipset,
              'Форм-фактор': getMB()?.form_factor,
              'Слотов RAM': getMB()?.memory_slots,
            }}
            icon={FiBox}
          />

          <ComponentSection
            title="Оперативная память"
            component={getRAM()}
            specs={{
              'Тип': getRAM()?.memory_type,
              'Объем': `${getRAM()?.capacity} GB`,
              'Частота': `${getRAM()?.speed} MHz`,
              'Модулей': getRAM()?.modules,
            }}
            icon={FiDatabase}
          />

          <ComponentSection
            title="Накопитель"
            component={getStorage()}
            specs={{
              'Тип': getStorage()?.storage_type?.toUpperCase(),
              'Объем': `${getStorage()?.capacity} GB`,
              'Чтение': getStorage()?.read_speed ? `${getStorage()?.read_speed} MB/s` : '-',
              'Запись': getStorage()?.write_speed ? `${getStorage()?.write_speed} MB/s` : '-',
            }}
            icon={FiHardDrive}
          />

          <ComponentSection
            title="Блок питания"
            component={getPSU()}
            specs={{
              'Мощность': `${getPSU()?.wattage} Вт`,
              'Сертификат': getPSU()?.efficiency_rating,
              'Модульный': getPSU()?.modular ? 'Да' : 'Нет',
            }}
            icon={FiZap}
          />

          <ComponentSection
            title="Корпус"
            component={getCase()}
            specs={{
              'Форм-фактор': getCase()?.form_factor,
            }}
            icon={FiBox}
          />

          <ComponentSection
            title="Охлаждение"
            component={getCooling()}
            specs={{
              'Тип': getCooling()?.cooling_type,
              'TDP': getCooling()?.max_tdp ? `${getCooling()?.max_tdp} Вт` : '-',
            }}
            icon={FiThermometer}
          />
        </div>

        {/* Sidebar - Chart */}
        <div className="space-y-6">
          <div className="card p-5">
            <h3 className="text-lg font-heading font-semibold text-white mb-4">
              Распределение бюджета
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`${value.toLocaleString()} ₽`, '']}
                    contentStyle={{
                      backgroundColor: '#111111',
                      border: '1px solid #1f1f1f',
                      borderRadius: 0,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-2 mt-4">
              {chartData.map((item, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3" style={{ backgroundColor: item.color }} />
                    <span className="text-gray-400">{item.name}</span>
                  </div>
                  <span className="text-white font-medium">
                    {item.value.toLocaleString()} ₽
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Notes */}
          {(config as any).ai_notes && (
            <div className="card p-5">
              <h3 className="text-lg font-heading font-semibold text-white mb-4">
                Рекомендации AI
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                {(config as any).ai_notes}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfigurationDetail;
