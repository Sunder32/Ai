import React, { useState, useEffect, useCallback } from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import {
  FiShoppingCart,
  FiExternalLink,
  FiTrendingDown,
  FiTrendingUp,
  FiMinus,
  FiCheckCircle,
  FiClock,
} from 'react-icons/fi';
import api from '../services/api';

// Хелпер для иконок
const Icon = ({ icon, className }: { icon: any; className?: string }) =>
  React.createElement(icon as any, { className });

// Логотипы магазинов
const STORE_LOGOS: Record<string, { name: string; color: string }> = {
  dns: { name: 'DNS', color: '#FF6B00' },
  citilink: { name: 'Citilink', color: '#00A651' },
  regard: { name: 'Regard', color: '#E31E24' },
  mvideo: { name: 'М.Видео', color: '#C4002B' },
  eldorado: { name: 'Эльдорадо', color: '#FFD700' },
};

interface StoreLink {
  name: string;
  stores: Record<string, string>;
}

interface PricePoint {
  date: string;
  price: number;
  store: string;
  in_stock: boolean;
}

interface PriceHistoryData {
  data: PricePoint[];
  stats: {
    min_price: number;
    max_price: number;
    avg_price: number;
    current_price: number;
    price_change_30d: number;
    best_time_to_buy: boolean;
  };
}

interface ComponentPriceHistory {
  name: string;
  current_price: number;
  history: PriceHistoryData;
}

interface StoreLinksProps {
  configurationId: number;
}

export const StoreLinks: React.FC<StoreLinksProps> = ({ configurationId }) => {
  const [links, setLinks] = useState<Record<string, StoreLink>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStoreLinks = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get(`/recommendations/configurations/${configurationId}/store-links/`);
      setLinks(response.data.components || {});
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [configurationId]);

  useEffect(() => {
    fetchStoreLinks();
  }, [fetchStoreLinks]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center py-4">{error}</div>
    );
  }

  const componentLabels: Record<string, string> = {
    cpu: 'Процессор',
    gpu: 'Видеокарта',
    motherboard: 'Материнская плата',
    ram: 'Оперативная память',
    storage_primary: 'Накопитель',
    psu: 'Блок питания',
    case: 'Корпус',
    cooling: 'Охлаждение',
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        {Icon({ icon: FiShoppingCart, className: 'w-5 h-5 text-green-400' })}
        <h3 className="text-lg font-semibold text-white">Купить в магазинах</h3>
      </div>

      {Object.entries(links).map(([compType, data]) => (
        <div key={compType} className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-gray-400 text-sm">{componentLabels[compType] || compType}</span>
              <p className="text-white font-medium">{data.name}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {Object.entries(data.stores).map(([store, url]) => {
              const storeInfo = STORE_LOGOS[store] || { name: store, color: '#666' };
              return (
                <a
                  key={store}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all hover:scale-105"
                  style={{ backgroundColor: storeInfo.color + '20', borderColor: storeInfo.color }}
                >
                  <span className="text-white text-sm font-medium">{storeInfo.name}</span>
                  {Icon({ icon: FiExternalLink, className: 'w-4 h-4 text-gray-400' })}
                </a>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

interface PriceHistoryProps {
  configurationId: number;
  days?: number;
}

export const PriceHistory: React.FC<PriceHistoryProps> = ({
  configurationId,
  days = 30,
}) => {
  const [history, setHistory] = useState<Record<string, ComponentPriceHistory>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

  const fetchPriceHistory = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/configurations/${configurationId}/price-history/`, {
        params: { days },
      });
      setHistory(response.data.price_history || {});
      
      // Выбираем первый компонент по умолчанию
      const keys = Object.keys(response.data.price_history || {});
      if (keys.length > 0) {
        setSelectedComponent((prev) => prev || keys[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [configurationId, days]);

  useEffect(() => {
    fetchPriceHistory();
  }, [fetchPriceHistory]);

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

  const componentLabels: Record<string, string> = {
    cpu: 'CPU',
    gpu: 'GPU',
    motherboard: 'MB',
    ram: 'RAM',
    storage_primary: 'SSD',
    psu: 'PSU',
    case: 'Case',
    cooling: 'Cooling',
  };

  const selectedData = selectedComponent ? history[selectedComponent] : null;
  const stats = selectedData?.history?.stats;

  // Форматирование данных для графика
  const chartData = selectedData?.history?.data?.map((point) => ({
    date: new Date(point.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
    price: point.price,
    inStock: point.in_stock,
  })) || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        {Icon({ icon: FiClock, className: 'w-5 h-5 text-blue-400' })}
        <h3 className="text-lg font-semibold text-white">История цен</h3>
      </div>

      {/* Выбор компонента */}
      <div className="flex flex-wrap gap-2">
        {Object.keys(history).map((comp) => (
          <button
            key={comp}
            onClick={() => setSelectedComponent(comp)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              selectedComponent === comp
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {componentLabels[comp] || comp}
          </button>
        ))}
      </div>

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-gray-400 text-xs">Текущая цена</p>
            <p className="text-white font-bold text-lg">
              {stats.current_price?.toLocaleString('ru-RU')} ₽
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-gray-400 text-xs">Минимум</p>
            <p className="text-green-400 font-bold text-lg">
              {stats.min_price?.toLocaleString('ru-RU')} ₽
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-gray-400 text-xs">Максимум</p>
            <p className="text-red-400 font-bold text-lg">
              {stats.max_price?.toLocaleString('ru-RU')} ₽
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-gray-400 text-xs">Изменение 30д</p>
            <div className="flex items-center gap-1">
              {stats.price_change_30d < 0 ? (
                <>
                  {Icon({ icon: FiTrendingDown, className: 'w-4 h-4 text-green-400' })}
                  <span className="text-green-400 font-bold">
                    {stats.price_change_30d?.toFixed(1)}%
                  </span>
                </>
              ) : stats.price_change_30d > 0 ? (
                <>
                  {Icon({ icon: FiTrendingUp, className: 'w-4 h-4 text-red-400' })}
                  <span className="text-red-400 font-bold">
                    +{stats.price_change_30d?.toFixed(1)}%
                  </span>
                </>
              ) : (
                <>
                  {Icon({ icon: FiMinus, className: 'w-4 h-4 text-gray-400' })}
                  <span className="text-gray-400 font-bold">0%</span>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Подсказка о лучшем времени покупки */}
      {stats?.best_time_to_buy && (
        <div className="flex items-center gap-2 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
          {Icon({ icon: FiCheckCircle, className: 'w-5 h-5 text-green-400' })}
          <span className="text-green-400">Сейчас лучшее время для покупки — цена минимальная!</span>
        </div>
      )}

      {/* График */}
      {chartData.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-2">{selectedData?.name}</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9CA3AF', fontSize: 11 }} />
                <YAxis
                  tick={{ fill: '#9CA3AF' }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                  domain={['dataMin - 1000', 'dataMax + 1000']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => [
                    `${value.toLocaleString('ru-RU')} ₽`,
                    'Цена',
                  ]}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#3B82F6"
                  fill="url(#priceGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

// Комбинированный компонент
interface StoreIntegrationPanelProps {
  configurationId: number;
}

export const StoreIntegrationPanel: React.FC<StoreIntegrationPanelProps> = ({
  configurationId,
}) => {
  const [activeTab, setActiveTab] = useState<'links' | 'history'>('links');

  return (
    <div className="bg-gray-900 rounded-xl p-6">
      {/* Табы */}
      <div className="flex gap-2 mb-6 border-b border-gray-700 pb-4">
        <button
          onClick={() => setActiveTab('links')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'links'
              ? 'bg-green-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {Icon({ icon: FiShoppingCart, className: 'inline w-4 h-4 mr-2' })}
          Магазины
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'history'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {Icon({ icon: FiClock, className: 'inline w-4 h-4 mr-2' })}
          История цен
        </button>
      </div>

      {/* Контент */}
      {activeTab === 'links' && <StoreLinks configurationId={configurationId} />}
      {activeTab === 'history' && <PriceHistory configurationId={configurationId} />}
    </div>
  );
};

export default StoreIntegrationPanel;
