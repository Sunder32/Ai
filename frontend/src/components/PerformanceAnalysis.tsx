import React, { useState, useEffect, useCallback } from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
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

  // Данные для radar chart
  const radarData = [
    {
      metric: 'CPU Single',
      score: cpuData?.cinebench_single?.percentile || 0,
    },
    {
      metric: 'CPU Multi',
      score: cpuData?.cinebench_multi?.percentile || 0,
    },
    {
      metric: 'GPU Raster',
      score: gpuData?.timespy?.percentile || 0,
    },
    {
      metric: 'GPU RT',
      score: gpuData?.port_royal?.percentile || 0,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        {Icon({ icon: FiActivity, className: 'w-5 h-5 text-purple-400' })}
        <h3 className="text-lg font-semibold text-white">Синтетические бенчмарки</h3>
      </div>

      {/* Radar Chart */}
      <div className="bg-gray-800 rounded-xl p-6">
        <p className="text-gray-400 text-sm mb-4">Относительная производительность (процентиль)</p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            {/* @ts-ignore */}
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              {/* @ts-ignore */}
              <PolarAngleAxis dataKey="metric" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
              {/* @ts-ignore */}
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#6B7280', fontSize: 10 }} />
              <Radar
                name="Производительность"
                dataKey="score"
                stroke="#8B5CF6"
                fill="#8B5CF6"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Процентиль']}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CPU Benchmarks */}
      {benchmarks.cpu_name && (
        <div className="bg-gray-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            {Icon({ icon: FiCpu, className: 'w-5 h-5 text-amber-400' })}
            <span className="text-white font-medium">{benchmarks.cpu_name}</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
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
                    Top {(100 - (cpuData.cinebench_single.percentile || 0)).toFixed(0)}%
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
                    Top {(100 - (cpuData.cinebench_multi.percentile || 0)).toFixed(0)}%
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
          
          <div className="grid grid-cols-3 gap-4">
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
                    {gpuData.timespy.percentile?.toFixed(0)}%
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
              </div>
            )}
            
            {gpuData?.port_royal && (
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs mb-1">Port Royal (RT)</p>
                <p className="text-white text-2xl font-bold">
                  {gpuData.port_royal.score.toLocaleString()}
                </p>
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

  // Фильтруем уникальные игры (без RT дубликатов для отображения)
  const uniqueGames = predictions.filter((p) => p && !p.ray_tracing);
  const displayedGames = showAll ? uniqueGames : uniqueGames.slice(0, 8);

  // Данные для bar chart
  const chartData = displayedGames.map((pred) => ({
    name: (pred.game_name || 'Unknown').length > 15 ? (pred.game_name || 'Unknown').substring(0, 15) + '...' : (pred.game_name || 'Unknown'),
    fullName: pred.game_name || 'Unknown',
    fps: pred.predicted_fps || 0,
    fps1Low: pred.fps_1_low || 0,
    color: getFPSColor(pred.predicted_fps || 0),
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {Icon({ icon: FiTarget, className: 'w-5 h-5 text-blue-400' })}
          <h3 className="text-lg font-semibold text-white">Предсказание FPS в играх</h3>
        </div>

        {/* Выбор разрешения */}
        <div className="flex gap-2">
          {['1080p', '1440p', '4k'].map((res) => (
            <button
              key={res}
              onClick={() => setResolution(res)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                resolution === res
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {res}
            </button>
          ))}
        </div>
      </div>

      {/* Легенда */}
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

      {/* График */}
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" tick={{ fill: '#9CA3AF' }} domain={[0, 'dataMax + 20']} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#9CA3AF', fontSize: 11 }}
                width={120}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label}
                formatter={(value: number, name: string) => [
                  `${value.toFixed(0)} FPS`,
                  name === 'fps' ? 'Средний' : '1% Low',
                ]}
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

      {/* Детали по играм */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {displayedGames.map((pred) => (
          <div key={pred.game_name} className="bg-gray-800 rounded-lg p-4">
            <p className="text-white font-medium truncate mb-2">{pred.game_name}</p>
            <div className="flex items-baseline gap-2">
              <span
                className="text-3xl font-bold"
                style={{ color: getFPSColor(pred.predicted_fps) }}
              >
                {pred.predicted_fps.toFixed(0)}
              </span>
              <span className="text-gray-400 text-sm">FPS</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-sm">
              <span className="text-gray-500">1% Low: {pred.fps_1_low.toFixed(0)}</span>
              <span
                className="px-2 py-0.5 rounded text-xs font-medium"
                style={{
                  backgroundColor: getFPSColor(pred.predicted_fps) + '20',
                  color: getFPSColor(pred.predicted_fps),
                }}
              >
                {getFPSLabel(pred.predicted_fps)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Показать все */}
      {uniqueGames.length > 8 && (
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
              Показать все игры ({uniqueGames.length})
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
      
      {activeTab === 'bottleneck' && bottleneck && (
        <div className="space-y-6">
          {/* Bottleneck Status */}
          <div
            className={`p-6 rounded-xl border ${
              bottleneck.status === 'balanced'
                ? 'bg-green-500/10 border-green-500/30'
                : bottleneck.status === 'cpu_bottleneck'
                ? 'bg-amber-500/10 border-amber-500/30'
                : bottleneck.status === 'gpu_bottleneck'
                ? 'bg-purple-500/10 border-purple-500/30'
                : 'bg-gray-500/10 border-gray-500/30'
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              {bottleneck.status === 'balanced' ? (
                <>
                  {Icon({ icon: FiCheckCircle, className: 'w-8 h-8 text-green-400' })}
                  <h3 className="text-xl font-bold text-green-400">Сбалансированная система</h3>
                </>
              ) : bottleneck.status === 'cpu_bottleneck' ? (
                <>
                  {Icon({ icon: FiAlertTriangle, className: 'w-8 h-8 text-amber-400' })}
                  <h3 className="text-xl font-bold text-amber-400">CPU Bottleneck</h3>
                </>
              ) : bottleneck.status === 'gpu_bottleneck' ? (
                <>
                  {Icon({ icon: FiAlertTriangle, className: 'w-8 h-8 text-purple-400' })}
                  <h3 className="text-xl font-bold text-purple-400">GPU Bottleneck</h3>
                </>
              ) : (
                <>
                  {Icon({ icon: FiZap, className: 'w-8 h-8 text-gray-400' })}
                  <h3 className="text-xl font-bold text-gray-400">Статус неизвестен</h3>
                </>
              )}
            </div>
            <p className="text-gray-300">{bottleneck.message}</p>
          </div>

          {/* Percentile Comparison */}
          {(bottleneck.cpu_percentile !== undefined || bottleneck.gpu_percentile !== undefined) && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  {Icon({ icon: FiCpu, className: 'w-5 h-5 text-amber-400' })}
                  <span className="text-white font-medium">CPU</span>
                </div>
                <div className="text-3xl font-bold text-amber-400 mb-2">
                  {bottleneck.cpu_percentile?.toFixed(0)}%
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full transition-all"
                    style={{ width: `${bottleneck.cpu_percentile || 0}%` }}
                  />
                </div>
                <p className="text-gray-400 text-sm mt-2">Процентиль производительности</p>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  {Icon({ icon: FiMonitor, className: 'w-5 h-5 text-green-400' })}
                  <span className="text-white font-medium">GPU</span>
                </div>
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {bottleneck.gpu_percentile?.toFixed(0)}%
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full transition-all"
                    style={{ width: `${bottleneck.gpu_percentile || 0}%` }}
                  />
                </div>
                <p className="text-gray-400 text-sm mt-2">Процентиль производительности</p>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {analysis?.recommendations && analysis.recommendations.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h4 className="text-white font-medium mb-3">Рекомендации</h4>
              <ul className="space-y-2">
                {analysis.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-gray-300">
                    <span className="text-blue-400 mt-1">•</span>
                    {rec}
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
