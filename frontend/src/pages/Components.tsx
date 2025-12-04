import React, { useState, useEffect, useCallback } from 'react';
import { computerAPI } from '../services/api';
import ComponentCard from '../components/ComponentCard';
import LoadingSpinner from '../components/LoadingSpinner';
import type { CPU, GPU, RAM, Storage } from '../types';
import { FiCpu, FiMonitor, FiDatabase, FiHardDrive } from 'react-icons/fi';

const Components: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'cpu' | 'gpu' | 'ram' | 'storage'>('cpu');
  const [cpus, setCPUs] = useState<CPU[]>([]);
  const [gpus, setGPUs] = useState<GPU[]>([]);
  const [ram, setRAM] = useState<RAM[]>([]);
  const [storage, setStorage] = useState<Storage[]>([]);
  const [loading, setLoading] = useState(false);

  const loadComponents = useCallback(async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'cpu':
          const cpuRes = await computerAPI.getCPUs({ ordering: '-performance_score' });
          setCPUs(cpuRes.data.results);
          break;
        case 'gpu':
          const gpuRes = await computerAPI.getGPUs({ ordering: '-performance_score' });
          setGPUs(gpuRes.data.results);
          break;
        case 'ram':
          const ramRes = await computerAPI.getRAM({ ordering: '-capacity' });
          setRAM(ramRes.data.results);
          break;
        case 'storage':
          const storageRes = await computerAPI.getStorage({ ordering: '-capacity' });
          setStorage(storageRes.data.results);
          break;
      }
    } catch (error) {
      console.error('Ошибка загрузки компонентов:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    loadComponents();
  }, [loadComponents]);

  const tabs = [
    { id: 'cpu', name: 'Процессоры', Icon: FiCpu },
    { id: 'gpu', name: 'Видеокарты', Icon: FiMonitor },
    { id: 'ram', name: 'Память', Icon: FiDatabase },
    { id: 'storage', name: 'Накопители', Icon: FiHardDrive },
  ];

  const getItemCount = () => {
    switch (activeTab) {
      case 'cpu': return cpus.length;
      case 'gpu': return gpus.length;
      case 'ram': return ram.length;
      case 'storage': return storage.length;
      default: return 0;
    }
  };

  return (
    <div className="py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-heading text-3xl md:text-4xl text-white mb-2">
          Каталог компонентов
        </h1>
        <p className="text-gray-500">
          Выберите категорию для просмотра доступных компонентов
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-8 p-1 bg-bg-card border border-border-dark">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 min-w-[120px] py-3 px-4 font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2 ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-400 hover:text-white hover:bg-bg-surface'
              }`}
            >
              {React.createElement(tab.Icon as any, { className: "text-lg" })}
              <span>{tab.name}</span>
            </button>
          );
        })}
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-border-dark">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-primary rounded-full" />
          <span className="text-sm text-gray-500">
            {loading ? 'Загрузка...' : `${getItemCount()} компонентов`}
          </span>
        </div>
        <span className="text-sm text-gray-500">
          {tabs.find(t => t.id === activeTab)?.name}
        </span>
      </div>

      {/* Components Grid */}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeTab === 'cpu' &&
            cpus.map((cpu) => (
              <ComponentCard
                key={cpu.id}
                title={cpu.name}
                manufacturer={cpu.manufacturer}
                price={cpu.price}
                specs={{
                  'Сокет': cpu.socket,
                  'Ядра': cpu.cores,
                  'Потоки': cpu.threads,
                  'Частота': `${cpu.base_clock} - ${cpu.boost_clock} ГГц`,
                  'TDP': `${cpu.tdp} Вт`,
                  'Рейтинг': cpu.performance_score,
                }}
              />
            ))}

          {activeTab === 'gpu' &&
            gpus.map((gpu) => (
              <ComponentCard
                key={gpu.id}
                title={gpu.name}
                manufacturer={gpu.manufacturer}
                price={gpu.price}
                specs={{
                  'Чипсет': gpu.chipset,
                  'Память': `${gpu.memory} GB ${gpu.memory_type}`,
                  'Частота': `${gpu.core_clock} MHz`,
                  'TDP': `${gpu.tdp} Вт`,
                  'Рекомендуемый БП': `${gpu.recommended_psu} Вт`,
                  'Рейтинг': gpu.performance_score,
                }}
              />
            ))}

          {activeTab === 'ram' &&
            ram.map((r) => (
              <ComponentCard
                key={r.id}
                title={r.name}
                manufacturer={r.manufacturer}
                price={r.price}
                specs={{
                  'Тип': r.memory_type,
                  'Объем': `${r.capacity} GB`,
                  'Частота': `${r.speed} MHz`,
                  'Модулей': r.modules,
                  ...(r.cas_latency && { 'CAS': r.cas_latency }),
                }}
              />
            ))}

          {activeTab === 'storage' &&
            storage.map((s) => (
              <ComponentCard
                key={s.id}
                title={s.name}
                manufacturer={s.manufacturer}
                price={s.price}
                specs={{
                  'Тип': s.storage_type.toUpperCase(),
                  'Объем': `${s.capacity} GB`,
                  ...(s.read_speed && { 'Чтение': `${s.read_speed} MB/s` }),
                  ...(s.write_speed && { 'Запись': `${s.write_speed} MB/s` }),
                }}
              />
            ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && getItemCount() === 0 && (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 mx-auto flex items-center justify-center bg-bg-surface mb-4">
            {React.createElement(FiDatabase as any, { className: "text-3xl text-gray-500" })}
          </div>
          <h3 className="text-xl font-heading font-semibold text-white mb-2">
            Нет данных
          </h3>
          <p className="text-gray-500">
            Компоненты в этой категории пока не добавлены
          </p>
        </div>
      )}
    </div>
  );
};

export default Components;
