import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { configurationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { StoreIntegrationPanel } from '../components/StoreIntegration';
import PerformanceAnalysisPanel from '../components/PerformanceAnalysis';
import AIChat from '../components/AIChat';
import type { PCConfiguration } from '../types';
import { FiCpu, FiMonitor, FiDatabase, FiHardDrive, FiZap, FiBox, FiThermometer, FiCheck, FiAlertTriangle, FiArrowLeft, FiHeadphones, FiMic, FiGrid, FiShoppingCart, FiActivity, FiEye, FiMessageSquare } from 'react-icons/fi';
import { BsKeyboard, BsMouse2, BsDisplay } from 'react-icons/bs';
import { MdChair, MdDesk, MdSpeaker } from 'react-icons/md';



const ConfigurationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [config, setConfig] = useState<PCConfiguration | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'pc' | 'peripherals' | 'workspace' | 'performance' | 'store' | 'chat'>('pc');


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

  // Getters для периферии
  const getWorkspace = () => config.workspace;
  const getMonitor = () => getWorkspace()?.monitor_primary_detail;
  const getMonitorSecondary = () => getWorkspace()?.monitor_secondary_detail;
  const getKeyboard = () => getWorkspace()?.keyboard_detail;
  const getMouse = () => getWorkspace()?.mouse_detail;
  const getHeadset = () => getWorkspace()?.headset_detail;
  const getWebcam = () => getWorkspace()?.webcam_detail;
  const getMicrophone = () => getWorkspace()?.microphone_detail;

  // Getters для рабочего места
  const getDesk = () => getWorkspace()?.desk_detail;
  const getChair = () => getWorkspace()?.chair_detail;

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
      <div className={`p-4 mb-6 flex items-center gap-3 ${config.compatibility_issues
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

      {/* Tabs Navigation */}
      <div className="flex gap-2 mb-6 border-b border-border-dark pb-4">
        <button
          onClick={() => setActiveTab('pc')}
          className={`px-6 py-3 font-medium transition-all flex items-center gap-2 ${activeTab === 'pc'
            ? 'bg-primary text-black'
            : 'bg-bg-card text-gray-400 hover:text-white hover:bg-bg-card-hover'
            }`}
        >
          {React.createElement(FiCpu as any, { className: "text-lg" })}
          ПК Компоненты
        </button>
        <button
          onClick={() => setActiveTab('peripherals')}
          className={`px-6 py-3 font-medium transition-all flex items-center gap-2 ${activeTab === 'peripherals'
            ? 'bg-primary text-black'
            : 'bg-bg-card text-gray-400 hover:text-white hover:bg-bg-card-hover'
            }`}
        >
          {React.createElement(BsKeyboard as any, { className: "text-lg" })}
          Периферия
        </button>
        <button
          onClick={() => setActiveTab('workspace')}
          className={`px-6 py-3 font-medium transition-all flex items-center gap-2 ${activeTab === 'workspace'
            ? 'bg-primary text-black'
            : 'bg-bg-card text-gray-400 hover:text-white hover:bg-bg-card-hover'
            }`}
        >
          {React.createElement(MdDesk as any, { className: "text-lg" })}
          Рабочее место
        </button>
        <button
          onClick={() => setActiveTab('performance')}
          className={`px-6 py-3 font-medium transition-all flex items-center gap-2 ${activeTab === 'performance'
            ? 'bg-primary text-black'
            : 'bg-bg-card text-gray-400 hover:text-white hover:bg-bg-card-hover'
            }`}
        >
          {React.createElement(FiActivity as any, { className: "text-lg" })}
          Производительность
        </button>
        <button
          onClick={() => setActiveTab('store')}
          className={`px-6 py-3 font-medium transition-all flex items-center gap-2 ${activeTab === 'store'
            ? 'bg-primary text-black'
            : 'bg-bg-card text-gray-400 hover:text-white hover:bg-bg-card-hover'
            }`}
        >
          {React.createElement(FiShoppingCart as any, { className: "text-lg" })}
          Магазины
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`px-6 py-3 font-medium transition-all flex items-center gap-2 ${activeTab === 'chat'
            ? 'bg-primary text-black'
            : 'bg-bg-card text-gray-400 hover:text-white hover:bg-bg-card-hover'
            }`}
        >
          {React.createElement(FiMessageSquare as any, { className: "text-lg" })}
          AI Консультант
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'pc' && (
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
      )}

      {/* Peripherals Tab */}
      {activeTab === 'peripherals' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <ComponentSection
              title="Монитор (основной)"
              component={getMonitor()}
              specs={{
                'Диагональ': getMonitor() ? `${getMonitor()?.screen_size}"` : '-',
                'Разрешение': getMonitor()?.resolution,
                'Частота обновления': getMonitor() ? `${getMonitor()?.refresh_rate} Гц` : '-',
                'Тип матрицы': getMonitor()?.panel_type,
                'Время отклика': getMonitor() ? `${getMonitor()?.response_time} мс` : '-',
                'HDR': getMonitor()?.hdr ? 'Да' : 'Нет',
                'Изогнутый': getMonitor()?.curved ? 'Да' : 'Нет',
              }}
              icon={BsDisplay}
            />

            {getMonitorSecondary() && (
              <ComponentSection
                title="Монитор (дополнительный)"
                component={getMonitorSecondary()}
                specs={{
                  'Диагональ': `${getMonitorSecondary()?.screen_size}"`,
                  'Разрешение': getMonitorSecondary()?.resolution,
                  'Частота обновления': `${getMonitorSecondary()?.refresh_rate} Гц`,
                  'Тип матрицы': getMonitorSecondary()?.panel_type,
                }}
                icon={BsDisplay}
              />
            )}

            <ComponentSection
              title="Клавиатура"
              component={getKeyboard()}
              specs={{
                'Тип переключателей': getKeyboard()?.switch_type === 'mechanical' ? 'Механические' :
                  getKeyboard()?.switch_type === 'membrane' ? 'Мембранные' :
                    getKeyboard()?.switch_type === 'optical' ? 'Оптические' : '-',
                'Модель свитчей': getKeyboard()?.switch_model || '-',
                'Подсветка RGB': getKeyboard()?.rgb ? 'Да' : 'Нет',
                'Беспроводная': getKeyboard()?.wireless ? 'Да' : 'Нет',
                'Форм-фактор': getKeyboard()?.form_factor || '-',
              }}
              icon={BsKeyboard}
            />

            <ComponentSection
              title="Мышь"
              component={getMouse()}
              specs={{
                'Тип сенсора': getMouse()?.sensor_type === 'optical' ? 'Оптический' : 'Лазерный',
                'DPI': getMouse()?.dpi,
                'Кнопок': getMouse()?.buttons,
                'Беспроводная': getMouse()?.wireless ? 'Да' : 'Нет',
                'RGB': getMouse()?.rgb ? 'Да' : 'Нет',
                'Вес': getMouse()?.weight ? `${getMouse()?.weight} г` : '-',
              }}
              icon={BsMouse2}
            />

            <ComponentSection
              title="Наушники / Гарнитура"
              component={getHeadset()}
              specs={{
                'Подключение': getHeadset()?.connection_type,
                'Беспроводные': getHeadset()?.wireless ? 'Да' : 'Нет',
                'Микрофон': getHeadset()?.microphone ? 'Да' : 'Нет',
                'Объемный звук': getHeadset()?.surround ? 'Да' : 'Нет',
                'Шумоподавление': getHeadset()?.noise_cancelling ? 'Да' : 'Нет',
              }}
              icon={FiHeadphones}
            />

            {getWebcam() && (
              <ComponentSection
                title="Веб-камера"
                component={getWebcam()}
                specs={{
                  'Разрешение': getWebcam()?.resolution,
                  'FPS': getWebcam()?.fps,
                  'Автофокус': getWebcam()?.autofocus ? 'Да' : 'Нет',
                  'Микрофон': getWebcam()?.microphone ? 'Да' : 'Нет',
                }}
                icon={FiMonitor}
              />
            )}

            {getMicrophone() && (
              <ComponentSection
                title="Микрофон"
                component={getMicrophone()}
                specs={{
                  'Тип': getMicrophone()?.mic_type === 'condenser' ? 'Конденсаторный' :
                    getMicrophone()?.mic_type === 'dynamic' ? 'Динамический' : 'USB',
                  'Диаграмма направленности': getMicrophone()?.polar_pattern || '-',
                  'Подключение': getMicrophone()?.connection_type,
                }}
                icon={FiMic}
              />
            )}
          </div>

          {/* Sidebar - Peripherals Summary */}
          <div className="space-y-6">
            <div className="card p-5">
              <h3 className="text-lg font-heading font-semibold text-white mb-4">
                Итого по периферии
              </h3>
              <div className="space-y-3">
                {getMonitor() && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Монитор</span>
                    <span className="text-white font-medium">{Number(getMonitor()?.price || 0).toLocaleString()} ₽</span>
                  </div>
                )}
                {getKeyboard() && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Клавиатура</span>
                    <span className="text-white font-medium">{Number(getKeyboard()?.price || 0).toLocaleString()} ₽</span>
                  </div>
                )}
                {getMouse() && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Мышь</span>
                    <span className="text-white font-medium">{Number(getMouse()?.price || 0).toLocaleString()} ₽</span>
                  </div>
                )}
                {getHeadset() && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Гарнитура</span>
                    <span className="text-white font-medium">{Number(getHeadset()?.price || 0).toLocaleString()} ₽</span>
                  </div>
                )}
                <div className="border-t border-border-dark pt-3 mt-3">
                  <div className="flex justify-between">
                    <span className="text-white font-medium">Всего</span>
                    <span className="text-primary text-xl font-bold">
                      {(
                        Number(getMonitor()?.price || 0) +
                        Number(getMonitorSecondary()?.price || 0) +
                        Number(getKeyboard()?.price || 0) +
                        Number(getMouse()?.price || 0) +
                        Number(getHeadset()?.price || 0) +
                        Number(getWebcam()?.price || 0) +
                        Number(getMicrophone()?.price || 0)
                      ).toLocaleString()} ₽
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {!getWorkspace() && (
              <div className="card p-5 text-center">
                <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center bg-gray-800 rounded-full">
                  {React.createElement(BsKeyboard as any, { className: "text-3xl text-gray-500" })}
                </div>
                <p className="text-gray-400">
                  Периферия не добавлена в эту конфигурацию
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Workspace Tab */}
      {activeTab === 'workspace' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <ComponentSection
              title="Стол"
              component={getDesk()}
              specs={{
                'Ширина': getDesk() ? `${getDesk()?.width} см` : '-',
                'Глубина': getDesk() ? `${getDesk()?.depth} см` : '-',
                'Регулировка высоты': getDesk()?.adjustable_height ? 'Да' : 'Нет',
                'Материал': getDesk()?.material || '-',
              }}
              icon={MdDesk}
            />

            <ComponentSection
              title="Кресло"
              component={getChair()}
              specs={{
                'Эргономичное': getChair()?.ergonomic ? 'Да' : 'Нет',
                'Поясничная поддержка': getChair()?.lumbar_support ? 'Да' : 'Нет',
                'Регулируемые подлокотники': getChair()?.armrests_adjustable ? 'Да' : 'Нет',
                'Макс. нагрузка': getChair()?.max_weight ? `${getChair()?.max_weight} кг` : '-',
                'Материал': getChair()?.material || '-',
              }}
              icon={MdChair}
            />

            {getWorkspace()?.lighting_recommendation && (
              <div className="card p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 flex items-center justify-center bg-yellow-500/10">
                    {React.createElement(FiZap as any, { className: "text-xl text-yellow-500" })}
                  </div>
                  <h3 className="text-lg font-heading font-semibold text-white">Рекомендации по освещению</h3>
                </div>
                <p className="text-gray-400">
                  {getWorkspace()?.lighting_recommendation}
                </p>
              </div>
            )}
          </div>

          {/* Sidebar - Workspace Summary */}
          <div className="space-y-6">
            <div className="card p-5">
              <h3 className="text-lg font-heading font-semibold text-white mb-4">
                Итого по рабочему месту
              </h3>
              <div className="space-y-3">
                {getDesk() && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Стол</span>
                    <span className="text-white font-medium">{Number(getDesk()?.price || 0).toLocaleString()} ₽</span>
                  </div>
                )}
                {getChair() && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Кресло</span>
                    <span className="text-white font-medium">{Number(getChair()?.price || 0).toLocaleString()} ₽</span>
                  </div>
                )}
                <div className="border-t border-border-dark pt-3 mt-3">
                  <div className="flex justify-between">
                    <span className="text-white font-medium">Всего</span>
                    <span className="text-primary text-xl font-bold">
                      {(
                        Number(getDesk()?.price || 0) +
                        Number(getChair()?.price || 0)
                      ).toLocaleString()} ₽
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {!getWorkspace() && (
              <div className="card p-5 text-center">
                <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center bg-gray-800 rounded-full">
                  {React.createElement(MdDesk as any, { className: "text-3xl text-gray-500" })}
                </div>
                <p className="text-gray-400">
                  Рабочее место не добавлено в эту конфигурацию
                </p>
              </div>
            )}

            {/* Total Configuration Price */}
            <div className="card p-5 bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/30">
              <h3 className="text-lg font-heading font-semibold text-white mb-4">
                Полная стоимость
              </h3>
              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                  <span className="text-gray-400">ПК комплектующие</span>
                  <span className="text-white">{Number(config.total_price || 0).toLocaleString()} ₽</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Периферия</span>
                  <span className="text-white">
                    {(
                      Number(getMonitor()?.price || 0) +
                      Number(getKeyboard()?.price || 0) +
                      Number(getMouse()?.price || 0) +
                      Number(getHeadset()?.price || 0)
                    ).toLocaleString()} ₽
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Рабочее место</span>
                  <span className="text-white">
                    {(
                      Number(getDesk()?.price || 0) +
                      Number(getChair()?.price || 0)
                    ).toLocaleString()} ₽
                  </span>
                </div>
              </div>
              <div className="border-t border-primary/30 pt-3">
                <div className="flex justify-between items-end">
                  <span className="text-white font-medium">ИТОГО</span>
                  <span className="text-primary text-2xl font-bold">
                    {(
                      Number(config.total_price || 0) +
                      Number(getMonitor()?.price || 0) +
                      Number(getMonitorSecondary()?.price || 0) +
                      Number(getKeyboard()?.price || 0) +
                      Number(getMouse()?.price || 0) +
                      Number(getHeadset()?.price || 0) +
                      Number(getWebcam()?.price || 0) +
                      Number(getMicrophone()?.price || 0) +
                      Number(getDesk()?.price || 0) +
                      Number(getChair()?.price || 0)
                    ).toLocaleString()} ₽
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Analysis Tab */}
      {activeTab === 'performance' && (
        <div className="space-y-6">
          <PerformanceAnalysisPanel configurationId={config.id} />
        </div>
      )}

      {/* Store Integration Tab */}
      {activeTab === 'store' && (
        <div className="space-y-6">
          <StoreIntegrationPanel configurationId={config.id} />
        </div>
      )}

      {/* AI Chat Tab */}
      {activeTab === 'chat' && (
        <div className="max-w-3xl">
          <AIChat configurationId={config.id} configName={config.name} />
        </div>
      )}

    </div>
  );
};

export default ConfigurationDetail;
