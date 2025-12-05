import React, { useState, useEffect, useCallback } from 'react';
import { computerAPI } from '../services/api';
import ComponentCard from '../components/ComponentCard';
import LoadingSpinner from '../components/LoadingSpinner';
import type { CPU, GPU, RAM, Storage } from '../types';
import { FaMicrochip, FaVideo, FaMemory, FaHdd } from 'react-icons/fa';

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
    { id: 'cpu', name: 'Процессоры', Icon: FaMicrochip },
    { id: 'gpu', name: 'Видеокарты', Icon: FaVideo },
    { id: 'ram', name: 'Память', Icon: FaMemory },
    { id: 'storage', name: 'Накопители', Icon: FaHdd },
  ];

  return (
    <div>
      <h1 className="text-5xl font-bold mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-center">
        Каталог компонентов
      </h1>

      {/* Tabs */}
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-3 mb-8">
        <div className="flex flex-wrap gap-3">
          {tabs.map((tab) => {
            const Icon = tab.Icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 min-w-[140px] py-4 px-5 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-105'
                    : 'bg-white/5 text-white/80 hover:bg-white/10 hover:text-white border border-white/10'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  {React.createElement(Icon as any, { className: "text-xl" })}
                  <span>{tab.name}</span>
                </div>
              </button>
            );
          })}
        </div>
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

      {!loading && (
        <div>
          {(activeTab === 'cpu' && cpus.length === 0) ||
          (activeTab === 'gpu' && gpus.length === 0) ||
          (activeTab === 'ram' && ram.length === 0) ||
          (activeTab === 'storage' && storage.length === 0) ? (
            <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-12 text-center">
              <p className="text-2xl font-semibold text-white mb-2">Компоненты не найдены</p>
              <p className="text-white/70">Попробуйте добавить компоненты через админ-панель</p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default Components;
