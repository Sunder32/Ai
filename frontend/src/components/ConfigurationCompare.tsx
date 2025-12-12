import React, { useState, useEffect } from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  FiX,
  FiCpu,
  FiHardDrive,
  FiMonitor,
  FiDollarSign,
  FiTrendingUp,
  FiPlus,
  FiSearch,
  FiChevronDown,
  FiChevronUp,
  FiAward,
} from 'react-icons/fi';
import api from '../services/api';

// Хелпер для иконок
const Icon = ({ icon, className }: { icon: any; className?: string }) =>
  React.createElement(icon as any, { className });

// Цветовая палитра для сборок
const COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // purple
];

interface Component {
  name: string | null;
  price: number | null;
  cores?: number | null;
  threads?: number | null;
  base_clock?: number | null;
  boost_clock?: number | null;
  performance_score?: number | null;
  memory?: number | null;
  memory_type?: string | null;
  capacity?: number | null;
  speed?: number | null;
  storage_type?: string | null;
}

interface Build {
  id: number;
  name: string;
  total_price: number;
  performance_score: number;
  components: {
    cpu: Component | null;
    gpu: Component | null;
    ram: Component | null;
    storage_primary: Component | null;
  };
}

interface ComparisonData {
  builds: Build[];
  summary: {
    cheapest: string | null;
    most_expensive: string | null;
    price_difference: number;
    best_cpu_performance: Build | null;
    best_gpu_performance: Build | null;
  };
  criteria: {
    cpu_cores: Record<string, number | null>;
    gpu_memory: Record<string, number | null>;
    ram_capacity: Record<string, number | null>;
    storage_capacity: Record<string, number | null>;
    total_price: Record<string, number>;
  };
}

interface Configuration {
  id: number;
  name: string;
  total_price: number;
}

interface ConfigurationCompareProps {
  initialIds?: number[];
  onClose?: () => void;
  availableConfigs?: Configuration[];
}

const ConfigurationCompare: React.FC<ConfigurationCompareProps> = ({
  initialIds = [],
  onClose,
  availableConfigs = [],
}) => {
  const [selectedIds, setSelectedIds] = useState<number[]>(initialIds);
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSelector, setShowSelector] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState({
    specs: true,
    performance: true,
    price: true,
    details: false,
  });

  const fetchComparison = React.useCallback(async () => {
    if (selectedIds.length < 2) {
      setComparison(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/recommendations/configurations/compare/', {
        params: { ids: selectedIds.join(',') },
      });
      setComparison(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Не удалось загрузить сравнение. Попробуйте обновить страницу.');
    } finally {
      setLoading(false);
    }
  }, [selectedIds]);

  // Загрузка сравнения
  useEffect(() => {
    fetchComparison();
  }, [fetchComparison]);

  const toggleConfig = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((i) => i !== id));
    } else if (selectedIds.length < 5) {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  // Данные для Radar Chart
  const getRadarData = () => {
    if (!comparison) return [];

    const metrics = [
      { key: 'cpu_cores', label: 'CPU Ядра', max: 24 },
      { key: 'gpu_memory', label: 'GPU Память', max: 24 },
      { key: 'ram_capacity', label: 'RAM', max: 128 },
      { key: 'storage_capacity', label: 'Хранилище', max: 4000 },
    ];

    return metrics.map((metric) => {
      const data: Record<string, any> = { metric: metric.label };
      comparison.builds.forEach((build) => {
        const value = comparison.criteria[metric.key as keyof typeof comparison.criteria][build.name];
        // Нормализуем к 0-100
        data[build.name] = value ? Math.min((value / metric.max) * 100, 100) : 0;
      });
      return data;
    });
  };

  // Данные для ценового сравнения
  const getPriceData = () => {
    if (!comparison) return [];
    return comparison.builds.map((build, index) => ({
      name: build.name.length > 15 ? build.name.substring(0, 15) + '...' : build.name,
      fullName: build.name,
      price: build.total_price,
      color: COLORS[index % COLORS.length],
    }));
  };

  // Данные для сравнения компонентов по цене
  const getComponentPriceData = () => {
    if (!comparison) return [];

    const components = ['cpu', 'gpu', 'ram', 'storage_primary'];
    const labels: Record<string, string> = {
      cpu: 'CPU',
      gpu: 'GPU',
      ram: 'RAM',
      storage_primary: 'Накопитель',
    };

    return components.map((comp) => {
      const data: Record<string, any> = { component: labels[comp] };
      comparison.builds.forEach((build) => {
        const component = build.components[comp as keyof typeof build.components];
        data[build.name] = component?.price || 0;
      });
      return data;
    });
  };

  // Данные для производительности
  const getPerformanceData = () => {
    if (!comparison) return [];

    return comparison.builds.map((build, index) => ({
      name: build.name.length > 12 ? build.name.substring(0, 12) + '...' : build.name,
      fullName: build.name,
      cpu: build.components.cpu?.performance_score || 0,
      gpu: build.components.gpu?.performance_score || 0,
      total: build.performance_score || 0,
      color: COLORS[index % COLORS.length],
    }));
  };

  // Фильтрованные конфигурации
  const filteredConfigs = availableConfigs.filter(
    (c) =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toString().includes(searchQuery)
  );

  return (
    <div className="bg-gray-900 rounded-xl p-6 space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            {Icon({ icon: FiTrendingUp, className: 'w-6 h-6 text-blue-400' })}
            Сравнение конфигураций
          </h2>
          <p className="text-gray-400 mt-1">
            Выберите от 2 до 5 сборок для сравнения
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            {Icon({ icon: FiX, className: 'w-6 h-6' })}
          </button>
        )}
      </div>

      {/* Селектор конфигураций */}
      <div className="space-y-3">
        <div className="flex items-center gap-3 flex-wrap">
          {selectedIds.map((id, index) => {
            const config = availableConfigs.find((c) => c.id === id);
            return (
              <div
                key={id}
                className="flex items-center gap-2 px-3 py-2 rounded-lg"
                style={{ backgroundColor: COLORS[index % COLORS.length] + '20' }}
              >
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-white font-medium">
                  {config?.name || `Сборка #${id}`}
                </span>
                <button
                  onClick={() => toggleConfig(id)}
                  className="ml-1 text-gray-400 hover:text-red-400 transition-colors"
                >
                  {Icon({ icon: FiX, className: 'w-4 h-4' })}
                </button>
              </div>
            );
          })}

          {selectedIds.length < 5 && (
            <button
              onClick={() => setShowSelector(!showSelector)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
            >
              {Icon({ icon: FiPlus, className: 'w-4 h-4' })}
              Добавить сборку
            </button>
          )}
        </div>

        {/* Выпадающий список */}
        {showSelector && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="relative mb-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Поиск конфигурации..."
                className="w-full px-4 py-2 pl-10 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              />
              {Icon({
                icon: FiSearch,
                className: 'absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400',
              })}
            </div>

            <div className="max-h-48 overflow-y-auto space-y-1">
              {filteredConfigs.length === 0 ? (
                <p className="text-gray-400 text-center py-2">Конфигурации не найдены</p>
              ) : (
                filteredConfigs.map((config) => (
                  <button
                    key={config.id}
                    onClick={() => {
                      toggleConfig(config.id);
                      setShowSelector(false);
                      setSearchQuery('');
                    }}
                    disabled={selectedIds.includes(config.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${selectedIds.includes(config.id)
                        ? 'bg-blue-600/20 text-blue-400 cursor-not-allowed'
                        : 'hover:bg-gray-700 text-white'
                      }`}
                  >
                    <span>{config.name}</span>
                    <span className="text-gray-400">
                      {config.total_price?.toLocaleString('ru-RU')} ₽
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Ошибка */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Загрузка */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent" />
        </div>
      )}

      {/* Контент сравнения */}
      {comparison && !loading && (
        <div className="space-y-6">
          {/* Сводка */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-green-600/20 to-green-800/20 border border-green-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 text-green-400 mb-2">
                {Icon({ icon: FiDollarSign, className: 'w-5 h-5' })}
                <span className="font-medium">Самая выгодная</span>
              </div>
              <p className="text-white text-lg font-bold">{comparison.summary.cheapest}</p>
            </div>

            <div className="bg-gradient-to-br from-amber-600/20 to-amber-800/20 border border-amber-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 text-amber-400 mb-2">
                {Icon({ icon: FiCpu, className: 'w-5 h-5' })}
                <span className="font-medium">Лучший CPU</span>
              </div>
              <p className="text-white text-lg font-bold">
                {comparison.summary.best_cpu_performance?.name || 'N/A'}
              </p>
            </div>

            <div className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 border border-purple-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 text-purple-400 mb-2">
                {Icon({ icon: FiMonitor, className: 'w-5 h-5' })}
                <span className="font-medium">Лучший GPU</span>
              </div>
              <p className="text-white text-lg font-bold">
                {comparison.summary.best_gpu_performance?.name || 'N/A'}
              </p>
            </div>
          </div>

          {/* Radar Chart - Характеристики */}
          <div className="bg-gray-800 rounded-xl p-6">
            <button
              onClick={() => toggleSection('specs')}
              className="w-full flex items-center justify-between text-left"
            >
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                {Icon({ icon: FiAward, className: 'w-5 h-5 text-blue-400' })}
                Сравнение характеристик
              </h3>
              {Icon({
                icon: expandedSections.specs ? FiChevronUp : FiChevronDown,
                className: 'w-5 h-5 text-gray-400',
              })}
            </button>

            {expandedSections.specs && (
              <div className="mt-4 h-80">
                <ResponsiveContainer width="100%" height="100%">
                  {/* @ts-ignore - recharts types issue */}
                  <RadarChart data={getRadarData()}>
                    <PolarGrid stroke="#374151" />
                    {/* @ts-ignore */}
                    <PolarAngleAxis dataKey="metric" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                    {/* @ts-ignore */}
                    <PolarRadiusAxis
                      angle={90}
                      domain={[0, 100]}
                      tick={{ fill: '#6B7280', fontSize: 10 }}
                    />
                    {comparison.builds.map((build, index) => (
                      <Radar
                        key={build.id}
                        name={build.name}
                        dataKey={build.name}
                        stroke={COLORS[index % COLORS.length]}
                        fill={COLORS[index % COLORS.length]}
                        fillOpacity={0.2}
                        strokeWidth={2}
                      />
                    ))}
                    <Legend
                      wrapperStyle={{ paddingTop: 20 }}
                      formatter={(value) => <span className="text-gray-300">{value}</span>}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                      }}
                      labelStyle={{ color: '#F3F4F6' }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Производительность */}
          <div className="bg-gray-800 rounded-xl p-6">
            <button
              onClick={() => toggleSection('performance')}
              className="w-full flex items-center justify-between text-left"
            >
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                {Icon({ icon: FiTrendingUp, className: 'w-5 h-5 text-green-400' })}
                Оценка производительности
              </h3>
              {Icon({
                icon: expandedSections.performance ? FiChevronUp : FiChevronDown,
                className: 'w-5 h-5 text-gray-400',
              })}
            </button>

            {expandedSections.performance && (
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={getPerformanceData()} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" tick={{ fill: '#9CA3AF' }} domain={[0, 100]} />
                    <YAxis
                      type="category"
                      dataKey="name"
                      tick={{ fill: '#9CA3AF' }}
                      width={100}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                      }}
                      labelFormatter={(label, payload) =>
                        payload?.[0]?.payload?.fullName || label
                      }
                      formatter={(value: number, name: string) => [
                        `${value.toFixed(1)}%`,
                        name === 'cpu' ? 'CPU Score' : name === 'gpu' ? 'GPU Score' : 'Общий',
                      ]}
                    />
                    <Bar dataKey="cpu" name="CPU" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="gpu" name="GPU" fill="#10B981" radius={[0, 4, 4, 0]} />
                    <Legend
                      formatter={(value) => <span className="text-gray-300">{value}</span>}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Сравнение цен */}
          <div className="bg-gray-800 rounded-xl p-6">
            <button
              onClick={() => toggleSection('price')}
              className="w-full flex items-center justify-between text-left"
            >
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                {Icon({ icon: FiDollarSign, className: 'w-5 h-5 text-amber-400' })}
                Сравнение цен
                <span className="text-sm font-normal text-gray-400 ml-2">
                  (разница: {comparison.summary.price_difference.toLocaleString('ru-RU')} ₽)
                </span>
              </h3>
              {Icon({
                icon: expandedSections.price ? FiChevronUp : FiChevronDown,
                className: 'w-5 h-5 text-gray-400',
              })}
            </button>

            {expandedSections.price && (
              <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Общая стоимость */}
                <div className="h-64">
                  <p className="text-gray-400 text-sm mb-2">Общая стоимость</p>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getPriceData()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="name" tick={{ fill: '#9CA3AF', fontSize: 11 }} />
                      <YAxis
                        tick={{ fill: '#9CA3AF' }}
                        tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1F2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                        }}
                        labelFormatter={(label, payload) =>
                          payload?.[0]?.payload?.fullName || label
                        }
                        formatter={(value: number) => [
                          `${value.toLocaleString('ru-RU')} ₽`,
                          'Цена',
                        ]}
                      />
                      <Bar dataKey="price" radius={[4, 4, 0, 0]}>
                        {getPriceData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Цены по компонентам */}
                <div className="h-64">
                  <p className="text-gray-400 text-sm mb-2">Стоимость по компонентам</p>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getComponentPriceData()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="component" tick={{ fill: '#9CA3AF' }} />
                      <YAxis
                        tick={{ fill: '#9CA3AF' }}
                        tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1F2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number, name: string) => [
                          `${value.toLocaleString('ru-RU')} ₽`,
                          name,
                        ]}
                      />
                      {comparison.builds.map((build, index) => (
                        <Bar
                          key={build.id}
                          dataKey={build.name}
                          fill={COLORS[index % COLORS.length]}
                          radius={[2, 2, 0, 0]}
                        />
                      ))}
                      <Legend
                        formatter={(value) => (
                          <span className="text-gray-300 text-xs">{value}</span>
                        )}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>

          {/* Детальное сравнение (таблица) */}
          <div className="bg-gray-800 rounded-xl p-6">
            <button
              onClick={() => toggleSection('details')}
              className="w-full flex items-center justify-between text-left"
            >
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                {Icon({ icon: FiHardDrive, className: 'w-5 h-5 text-cyan-400' })}
                Детальное сравнение компонентов
              </h3>
              {Icon({
                icon: expandedSections.details ? FiChevronUp : FiChevronDown,
                className: 'w-5 h-5 text-gray-400',
              })}
            </button>

            {expandedSections.details && (
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">
                        Компонент
                      </th>
                      {comparison.builds.map((build, index) => (
                        <th
                          key={build.id}
                          className="text-left py-3 px-4 font-medium"
                          style={{ color: COLORS[index % COLORS.length] }}
                        >
                          {build.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {/* CPU */}
                    <tr className="border-b border-gray-700/50">
                      <td className="py-3 px-4 text-gray-400">CPU</td>
                      {comparison.builds.map((build) => (
                        <td key={build.id} className="py-3 px-4 text-white">
                          {build.components.cpu ? (
                            <div>
                              <p className="font-medium">{build.components.cpu.name}</p>
                              <p className="text-sm text-gray-400">
                                {build.components.cpu.cores} ядер /{' '}
                                {build.components.cpu.threads} потоков
                              </p>
                              <p className="text-sm text-green-400">
                                {build.components.cpu.price?.toLocaleString('ru-RU')} ₽
                              </p>
                            </div>
                          ) : (
                            <span className="text-gray-500">—</span>
                          )}
                        </td>
                      ))}
                    </tr>

                    {/* GPU */}
                    <tr className="border-b border-gray-700/50">
                      <td className="py-3 px-4 text-gray-400">GPU</td>
                      {comparison.builds.map((build) => (
                        <td key={build.id} className="py-3 px-4 text-white">
                          {build.components.gpu ? (
                            <div>
                              <p className="font-medium">{build.components.gpu.name}</p>
                              <p className="text-sm text-gray-400">
                                {build.components.gpu.memory} GB {build.components.gpu.memory_type}
                              </p>
                              <p className="text-sm text-green-400">
                                {build.components.gpu.price?.toLocaleString('ru-RU')} ₽
                              </p>
                            </div>
                          ) : (
                            <span className="text-gray-500">—</span>
                          )}
                        </td>
                      ))}
                    </tr>

                    {/* RAM */}
                    <tr className="border-b border-gray-700/50">
                      <td className="py-3 px-4 text-gray-400">RAM</td>
                      {comparison.builds.map((build) => (
                        <td key={build.id} className="py-3 px-4 text-white">
                          {build.components.ram ? (
                            <div>
                              <p className="font-medium">{build.components.ram.name}</p>
                              <p className="text-sm text-gray-400">
                                {build.components.ram.capacity} GB @ {build.components.ram.speed} MHz
                              </p>
                              <p className="text-sm text-green-400">
                                {build.components.ram.price?.toLocaleString('ru-RU')} ₽
                              </p>
                            </div>
                          ) : (
                            <span className="text-gray-500">—</span>
                          )}
                        </td>
                      ))}
                    </tr>

                    {/* Storage */}
                    <tr className="border-b border-gray-700/50">
                      <td className="py-3 px-4 text-gray-400">Накопитель</td>
                      {comparison.builds.map((build) => (
                        <td key={build.id} className="py-3 px-4 text-white">
                          {build.components.storage_primary ? (
                            <div>
                              <p className="font-medium">{build.components.storage_primary.name}</p>
                              <p className="text-sm text-gray-400">
                                {build.components.storage_primary.capacity} GB{' '}
                                {build.components.storage_primary.storage_type}
                              </p>
                              <p className="text-sm text-green-400">
                                {build.components.storage_primary.price?.toLocaleString('ru-RU')} ₽
                              </p>
                            </div>
                          ) : (
                            <span className="text-gray-500">—</span>
                          )}
                        </td>
                      ))}
                    </tr>

                    {/* Итого */}
                    <tr className="bg-gray-700/30">
                      <td className="py-3 px-4 text-white font-semibold">ИТОГО</td>
                      {comparison.builds.map((build, index) => (
                        <td
                          key={build.id}
                          className="py-3 px-4 font-bold text-lg"
                          style={{ color: COLORS[index % COLORS.length] }}
                        >
                          {build.total_price.toLocaleString('ru-RU')} ₽
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Сообщение если мало сборок */}
      {selectedIds.length < 2 && !loading && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-700 flex items-center justify-center">
            {Icon({ icon: FiTrendingUp, className: 'w-8 h-8 text-gray-500' })}
          </div>
          <p className="text-gray-400 text-lg">
            Выберите минимум 2 конфигурации для сравнения
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Нажмите "Добавить сборку" чтобы начать
          </p>
        </div>
      )}
    </div>
  );
};

export default ConfigurationCompare;
