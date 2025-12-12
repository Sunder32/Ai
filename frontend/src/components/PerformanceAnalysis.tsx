import React, { useState, useEffect, useCallback } from 'react';
import {
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
  FiCpu,
  FiMonitor,
  FiActivity,
  FiTarget,
  FiAlertTriangle,
  FiCheckCircle,
  FiChevronDown,
  FiChevronUp,
  FiSearch,
  FiZap,
  FiSettings,
} from 'react-icons/fi';
import api from '../services/api';

// Хелпер для иконок
const Icon = ({ icon, className }: { icon: any; className?: string }) =>
  React.createElement(icon as any, { className });

// Цветовая шкала FPS
const getFPSColor = (fps: number): string => {
  if (fps >= 144) return '#10B981'; // Green
  if (fps >= 60) return '#3B82F6';  // Blue
  if (fps >= 30) return '#F59E0B';  // Amber
  return '#EF4444'; // Red
};

const getFPSLabel = (fps: number): string => {
  if (fps >= 144) return 'Отлично';
  if (fps >= 60) return 'Хорошо';
  if (fps >= 30) return 'Играбельно';
  return 'Низкий';
};

interface BenchmarkResult {
  benchmark_type: string;
  score: number;
  component_name: string;
  source: string;
  percentile?: number;
}

interface FPSPrediction {
  game_name: string;
  resolution: string;
  quality_preset: string;
  predicted_fps: number;
  fps_1_low: number;
  confidence: number;
  ray_tracing: boolean;
  dlss_fsr?: string;
}

interface BottleneckAnalysis {
  status: 'balanced' | 'cpu_bottleneck' | 'gpu_bottleneck' | 'unknown';
  cpu_percentile?: number;
  gpu_percentile?: number;
  severity?: string;
  message: string;
}

interface PerformanceAnalysisData {
  cpu_benchmarks: Record<string, BenchmarkResult>;
  gpu_benchmarks: Record<string, BenchmarkResult>;
  gaming_performance: Record<string, FPSPrediction[]>;
  bottleneck_analysis: BottleneckAnalysis;
  recommendations: string[];
}

interface BenchmarksPanelProps {
  configurationId: number;
}

export const BenchmarksPanel: React.FC<BenchmarksPanelProps> = ({ configurationId }) => {
  const [benchmarks, setBenchmarks] = useState<{
    cpu_benchmarks: Record<string, BenchmarkResult>;
    gpu_benchmarks: Record<string, BenchmarkResult>;
    cpu_name?: string;
    gpu_name?: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBenchmarks = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get(`/recommendations/configurations/${configurationId}/benchmarks/`);
      setBenchmarks(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [configurationId]);

  useEffect(() => {
    fetchBenchmarks();
  }, [fetchBenchmarks]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-400 text-center py-4">{error}</div>;
  }

  if (!benchmarks) return null;

  const cpuData = benchmarks.cpu_benchmarks;
  const gpuData = benchmarks.gpu_benchmarks;

  const percentileItems: Array<{ key: string; label: string; value: number | null; barClass: string }> = [
    {
      key: 'cpu_single',
      label: 'CPU Single (Cinebench R23)',
      value: cpuData?.cinebench_single?.percentile ?? null,
      barClass: 'bg-amber-500',
    },
    {
      key: 'cpu_multi',
      label: 'CPU Multi (Cinebench R23)',
      value: cpuData?.cinebench_multi?.percentile ?? null,
      barClass: 'bg-amber-500',
    },
    {
      key: 'gpu_raster',
      label: 'GPU Raster (3DMark Time Spy)',
      value: gpuData?.timespy?.percentile ?? null,
      barClass: 'bg-green-500',
    },
    {
      key: 'gpu_rt',
      label: 'GPU RT (3DMark Port Royal)',
      value: gpuData?.port_royal?.percentile ?? null,
      barClass: 'bg-purple-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        {Icon({ icon: FiActivity, className: 'w-5 h-5 text-purple-400' })}
        <h3 className="text-lg font-semibold text-white">Синтетические бенчмарки</h3>
      </div>

      <div className="bg-gray-800 rounded-xl p-6">
        <p className="text-gray-400 text-sm mb-4">
          Процентили (выше = лучше). 80% означает быстрее, чем ~80% базы.
        </p>
        <div className="space-y-3">
          {percentileItems.map((item) => {
            const raw = item.value ?? 0;
            const clamped = Math.max(0, Math.min(raw, 100));
            return (
              <div key={item.key} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">{item.label}</span>
                  <span className="text-gray-200 font-medium">
                    {item.value !== null ? `${item.value.toFixed(0)}%` : '—'}
                  </span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div className={`h-full ${item.barClass}`} style={{ width: `${clamped}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* CPU Benchmarks */}
      {benchmarks.cpu_name && (
        <div className="bg-gray-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            {Icon({ icon: FiCpu, className: 'w-5 h-5 text-amber-400' })}
            <span className="text-white font-medium">{benchmarks.cpu_name}</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cpuData?.cinebench_single && (
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Cinebench R23 (Single)</p>
                <p className="text-white text-2xl font-bold">
                  {cpuData.cinebench_single.score.toLocaleString()}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full"
                      style={{ width: `${cpuData.cinebench_single.percentile || 0}%` }}
                    />
                  </div>
                  <span className="text-amber-400 text-sm">
                    Процентиль: {cpuData.cinebench_single.percentile?.toFixed(0) ?? '—'}%
                  </span>
                </div>
              </div>
            )}
            
            {cpuData?.cinebench_multi && (
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Cinebench R23 (Multi)</p>
                <p className="text-white text-2xl font-bold">
                  {cpuData.cinebench_multi.score.toLocaleString()}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full"
                      style={{ width: `${cpuData.cinebench_multi.percentile || 0}%` }}
                    />
                  </div>
                  <span className="text-amber-400 text-sm">
                    Процентиль: {cpuData.cinebench_multi.percentile?.toFixed(0) ?? '—'}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* GPU Benchmarks */}
      {benchmarks.gpu_name && (
        <div className="bg-gray-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            {Icon({ icon: FiMonitor, className: 'w-5 h-5 text-green-400' })}
            <span className="text-white font-medium">{benchmarks.gpu_name}</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {gpuData?.timespy && (
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">3DMark Time Spy</p>
                <p className="text-white text-2xl font-bold">
                  {gpuData.timespy.score.toLocaleString()}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${gpuData.timespy.percentile || 0}%` }}
                    />
                  </div>
                  <span className="text-green-400 text-xs">
                    Процентиль: {gpuData.timespy.percentile?.toFixed(0) ?? '—'}%
                  </span>
                </div>
              </div>
            )}
            
            {gpuData?.firestrike && (
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Fire Strike</p>
                <p className="text-white text-2xl font-bold">
                  {gpuData.firestrike.score.toLocaleString()}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${gpuData.firestrike.percentile || 0}%` }}
                    />
                  </div>
                  <span className="text-green-400 text-xs">
                    Процентиль: {gpuData.firestrike.percentile?.toFixed(0) ?? '—'}%
                  </span>
                </div>
              </div>
            )}
            
            {gpuData?.port_royal && (
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Port Royal (RT)</p>
                <p className="text-white text-2xl font-bold">
                  {gpuData.port_royal.score.toLocaleString()}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500 rounded-full"
                      style={{ width: `${gpuData.port_royal.percentile || 0}%` }}
                    />
                  </div>
                  <span className="text-purple-400 text-xs">
                    Процентиль: {gpuData.port_royal.percentile?.toFixed(0) ?? '—'}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

interface FPSPredictionPanelProps {
  configurationId: number;
}

export const FPSPredictionPanel: React.FC<FPSPredictionPanelProps> = ({ configurationId }) => {
  const [predictions, setPredictions] = useState<FPSPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resolution, setResolution] = useState('1080p');
  const [showAll, setShowAll] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'fps' | 'name' | 'confidence'>('fps');

  const fetchPredictions = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get(`/recommendations/configurations/${configurationId}/fps-prediction/`, {
        params: { resolution },
      });
      setPredictions(response.data.predictions || []);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [configurationId, resolution]);

  useEffect(() => {
    fetchPredictions();
  }, [fetchPredictions]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-400 text-center py-4">{error}</div>;
  }

  if (!predictions || predictions.length === 0) {
    return <div className="text-gray-400 text-center py-4">Нет данных о FPS для этой конфигурации</div>;
  }

  const limit = 12;
  const normalizedQuery = searchQuery.trim().toLowerCase();

  const filteredGames = predictions
    .filter((p) => p && !p.ray_tracing)
    .filter((p) => {
      if (!normalizedQuery) return true;
      return (p.game_name || '').toLowerCase().includes(normalizedQuery);
    });

  const sortedGames = [...filteredGames].sort((a, b) => {
    if (sortBy === 'name') return (a.game_name || '').localeCompare(b.game_name || '');
    if (sortBy === 'confidence') return (b.confidence || 0) - (a.confidence || 0);
    return (b.predicted_fps || 0) - (a.predicted_fps || 0);
  });

  const displayedGames = showAll ? sortedGames : sortedGames.slice(0, limit);
  const chartGames = [...filteredGames].sort((a, b) => (b.predicted_fps || 0) - (a.predicted_fps || 0)).slice(0, 10);

  const chartData = chartGames.map((pred) => ({
    name:
      (pred.game_name || 'Unknown').length > 18
        ? (pred.game_name || 'Unknown').substring(0, 18) + '...'
        : (pred.game_name || 'Unknown'),
    fullName: pred.game_name || 'Unknown',
    fps: pred.predicted_fps || 0,
    color: getFPSColor(pred.predicted_fps || 0),
  }));

  const qualityPreset = (displayedGames[0]?.quality_preset || chartGames[0]?.quality_preset || 'Ultra').trim();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-2">
          {Icon({ icon: FiTarget, className: 'w-5 h-5 text-blue-400' })}
          <div>
            <h3 className="text-lg font-semibold text-white">Предсказание FPS в играх</h3>
            <p className="text-xs text-gray-400">
              Пресет: {qualityPreset} • Оценка по базе бенчмарков, реальный FPS зависит от настроек/драйверов
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          {['1080p', '1440p', '4k'].map((res) => (
            <button
              key={res}
              onClick={() => setResolution(res)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                resolution === res ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {res}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <div className="relative flex-1 min-w-0">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {Icon({ icon: FiSearch, className: 'w-4 h-4 text-gray-500' })}
          </div>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск игры..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-3 py-2 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'fps' | 'name' | 'confidence')}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
        >
          <option value="fps">Сортировка: FPS</option>
          <option value="confidence">Сортировка: Уверенность</option>
          <option value="name">Сортировка: Название</option>
        </select>
      </div>

      <div className="flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-gray-400">144+ FPS (Отлично)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span className="text-gray-400">60-143 FPS (Хорошо)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          <span className="text-gray-400">30-59 FPS (Играбельно)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-gray-400">&lt;30 FPS (Низкий)</span>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-gray-400 text-sm">Топ игр по среднему FPS</p>
          <p className="text-gray-500 text-xs">{chartGames.length} игр</p>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" tick={{ fill: '#9CA3AF' }} domain={[0, 'dataMax + 20']} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#9CA3AF', fontSize: 11 }} width={140} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label}
                formatter={(value: number) => [`${value.toFixed(0)} FPS`, 'Средний']}
              />
              <Bar dataKey="fps" name="FPS" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
          <p className="text-gray-400 text-sm">
            Показано: <span className="text-white font-medium">{displayedGames.length}</span> из{' '}
            <span className="text-white font-medium">{sortedGames.length}</span>
          </p>
          <p className="text-gray-500 text-xs">AVG / 1% low / уверенность</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">Игра</th>
                <th className="text-right px-4 py-3 text-gray-400 font-medium">AVG</th>
                <th className="text-right px-4 py-3 text-gray-400 font-medium">1% low</th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">Оценка</th>
                <th className="text-right px-4 py-3 text-gray-400 font-medium">Увер.</th>
              </tr>
            </thead>
            <tbody>
              {displayedGames.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-gray-400">
                    Ничего не найдено. Попробуйте другой запрос.
                  </td>
                </tr>
              ) : (
                displayedGames.map((pred) => {
                  const color = getFPSColor(pred.predicted_fps || 0);
                  const label = getFPSLabel(pred.predicted_fps || 0);
                  return (
                    <tr key={`${pred.game_name}-${pred.resolution}`} className="border-t border-gray-700/50">
                      <td className="px-4 py-3">
                        <div className="text-white font-medium max-w-[320px] truncate">{pred.game_name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {pred.quality_preset}
                          {pred.dlss_fsr ? ` • ${pred.dlss_fsr}` : ''}
                          {pred.ray_tracing ? ' • RT' : ''}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right font-semibold" style={{ color }}>
                        {pred.predicted_fps.toFixed(0)}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-300">{pred.fps_1_low.toFixed(0)}</td>
                      <td className="px-4 py-3">
                        <span
                          className="inline-flex px-2 py-0.5 rounded text-xs font-medium"
                          style={{ backgroundColor: color + '20', color }}
                        >
                          {label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-gray-300">{pred.confidence.toFixed(0)}%</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {sortedGames.length > limit && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full py-3 text-gray-400 hover:text-white transition-colors flex items-center justify-center gap-2"
        >
          {showAll ? (
            <>
              {Icon({ icon: FiChevronUp, className: 'w-4 h-4' })}
              Свернуть
            </>
          ) : (
            <>
              {Icon({ icon: FiChevronDown, className: 'w-4 h-4' })}
              Показать все игры ({sortedGames.length})
            </>
          )}
        </button>
      )}
    </div>
  );
};

interface PerformanceAnalysisPanelProps {
  configurationId: number;
}

export const PerformanceAnalysisPanel: React.FC<PerformanceAnalysisPanelProps> = ({
  configurationId,
}) => {
  const [analysis, setAnalysis] = useState<PerformanceAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'benchmarks' | 'fps' | 'bottleneck'>('fps');

  const fetchAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get(`/recommendations/configurations/${configurationId}/performance-analysis/`);
      setAnalysis(response.data.analysis);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [configurationId]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center py-8">
        {error}
      </div>
    );
  }

  const bottleneck = analysis?.bottleneck_analysis;
  const highlightCpu = bottleneck?.status === 'cpu_bottleneck';
  const highlightGpu = bottleneck?.status === 'gpu_bottleneck';

  const clampPercentile = (value?: number): number => {
    if (typeof value !== 'number' || !Number.isFinite(value)) return 0;
    return Math.max(0, Math.min(value, 100));
  };

  const formatPercentile = (value?: number): string => {
    if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
    return `${value.toFixed(0)}%`;
  };

  const percentileDiff =
    typeof bottleneck?.cpu_percentile === 'number' &&
    typeof bottleneck?.gpu_percentile === 'number'
      ? Math.abs(bottleneck.cpu_percentile - bottleneck.gpu_percentile)
      : null;

  const severityBadge =
    bottleneck?.severity === 'high'
      ? { label: 'Высокая', className: 'bg-red-500/15 text-red-300 border-red-500/30' }
      : bottleneck?.severity === 'medium'
        ? { label: 'Средняя', className: 'bg-amber-500/15 text-amber-300 border-amber-500/30' }
        : bottleneck?.severity
          ? { label: bottleneck.severity, className: 'bg-gray-500/15 text-gray-300 border-gray-500/30' }
          : null;

  const bottleneckCard = (() => {
    if (!bottleneck) return null;

    switch (bottleneck.status) {
      case 'balanced':
        return {
          icon: FiCheckCircle,
          title: 'Сбалансированная система',
          titleClass: 'text-green-400',
          containerClass: 'bg-green-500/10 border-green-500/30',
          hint: 'CPU и GPU близки по уровню — хороший баланс под большинство задач.',
        };
      case 'cpu_bottleneck':
        return {
          icon: FiAlertTriangle,
          title: 'Упор в процессор (CPU)',
          titleClass: 'text-amber-400',
          containerClass: 'bg-amber-500/10 border-amber-500/30',
          hint: 'Чаще заметно в 1080p и CPU‑зависимых играх.',
        };
      case 'gpu_bottleneck':
        return {
          icon: FiAlertTriangle,
          title: 'Упор в видеокарту (GPU)',
          titleClass: 'text-emerald-400',
          containerClass: 'bg-emerald-500/10 border-emerald-500/30',
          hint: 'Обычно главный ограничитель FPS в играх.',
        };
      default:
        return {
          icon: FiZap,
          title: 'Недостаточно данных',
          titleClass: 'text-gray-300',
          containerClass: 'bg-gray-500/10 border-gray-500/30',
          hint: 'Не удалось получить данные бенчмарков для сравнения CPU и GPU.',
        };
    }
  })();

  return (
    <div className="bg-gray-900 rounded-xl p-6 space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700 pb-4">
        <button
          onClick={() => setActiveTab('fps')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'fps'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {Icon({ icon: FiTarget, className: 'inline w-4 h-4 mr-2' })}
          FPS в играх
        </button>
        <button
          onClick={() => setActiveTab('benchmarks')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'benchmarks'
              ? 'bg-purple-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {Icon({ icon: FiActivity, className: 'inline w-4 h-4 mr-2' })}
          Бенчмарки
        </button>
        <button
          onClick={() => setActiveTab('bottleneck')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'bottleneck'
              ? 'bg-amber-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {Icon({ icon: FiSettings, className: 'inline w-4 h-4 mr-2' })}
          Баланс системы
        </button>
      </div>

      {/* Content */}
      {activeTab === 'fps' && <FPSPredictionPanel configurationId={configurationId} />}
      
      {activeTab === 'benchmarks' && <BenchmarksPanel configurationId={configurationId} />}
      
      {activeTab === 'bottleneck' && bottleneck && bottleneckCard && (
        <div className="space-y-6">
          {/* Status */}
          <div className={`p-6 rounded-xl border ${bottleneckCard.containerClass}`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                {Icon({ icon: bottleneckCard.icon, className: `w-8 h-8 ${bottleneckCard.titleClass}` })}
                <div>
                  <h3 className={`text-xl font-bold ${bottleneckCard.titleClass}`}>{bottleneckCard.title}</h3>
                  <p className="text-gray-200 mt-2">{bottleneck.message}</p>
                  <p className="text-gray-400 text-sm mt-1">{bottleneckCard.hint}</p>
                </div>
              </div>

              {severityBadge && (
                <span className={`text-xs px-2 py-1 rounded-md border ${severityBadge.className}`}>
                  Серьезность: {severityBadge.label}
                </span>
              )}
            </div>
          </div>

          {/* Comparison */}
          {(bottleneck.cpu_percentile !== undefined || bottleneck.gpu_percentile !== undefined) && (
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between gap-3 mb-4">
                <div className="text-white font-medium">Сравнение уровней (процентили)</div>
                {percentileDiff !== null && (
                  <div className="text-xs text-gray-300 bg-gray-900/60 border border-gray-700 px-2 py-1 rounded-md">
                    Разница: {percentileDiff.toFixed(0)} п.п.
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  className={`rounded-lg p-4 border ${
                    highlightCpu ? 'border-amber-500/40 bg-amber-500/5' : 'border-gray-700 bg-gray-900/40'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {Icon({ icon: FiCpu, className: 'w-5 h-5 text-amber-400' })}
                      <span className="text-white font-medium">CPU</span>
                    </div>
                    <div className="text-xl font-bold text-amber-400">{formatPercentile(bottleneck.cpu_percentile)}</div>
                  </div>
                  <div className="h-2 bg-gray-700/60 rounded-full overflow-hidden mt-3">
                    <div className="h-full bg-amber-500" style={{ width: `${clampPercentile(bottleneck.cpu_percentile)}%` }} />
                  </div>
                  <p className="text-xs text-gray-400 mt-2">Cinebench R23 (single)</p>
                </div>

                <div
                  className={`rounded-lg p-4 border ${
                    highlightGpu ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-gray-700 bg-gray-900/40'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {Icon({ icon: FiMonitor, className: 'w-5 h-5 text-emerald-400' })}
                      <span className="text-white font-medium">GPU</span>
                    </div>
                    <div className="text-xl font-bold text-emerald-400">{formatPercentile(bottleneck.gpu_percentile)}</div>
                  </div>
                  <div className="h-2 bg-gray-700/60 rounded-full overflow-hidden mt-3">
                    <div className="h-full bg-emerald-500" style={{ width: `${clampPercentile(bottleneck.gpu_percentile)}%` }} />
                  </div>
                  <p className="text-xs text-gray-400 mt-2">3DMark Time Spy (graphics)</p>
                </div>
              </div>

              <p className="text-gray-400 text-sm mt-4">
                Процентиль — относительный уровень компонента в базе (выше = лучше).
              </p>
            </div>
          )}

          {/* Recommendations */}
          {analysis?.recommendations && analysis.recommendations.length > 0 && (
            <div className="bg-gray-800 rounded-xl p-6">
              <h4 className="text-white font-semibold mb-4">Что можно улучшить</h4>
              <ul className="space-y-2">
                {analysis.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-gray-300">
                    <span className="text-primary mt-1">•</span>
                    <span className="flex-1">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PerformanceAnalysisPanel;
