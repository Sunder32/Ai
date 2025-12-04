import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FiUser, FiMail, FiPhone, FiSettings, FiSave, FiLogOut, 
  FiCpu, FiMonitor, FiDollarSign, FiCheck, FiX, FiEdit2,
  FiPrinter, FiDownload, FiExternalLink
} from 'react-icons/fi';
import { userAPI, authAPI, configurationAPI } from '../services/api';
import { saveToPDF, printDocument, type PDFBuildData, type Component } from '../services/pdfGenerator';
import LoadingSpinner from '../components/LoadingSpinner';
import type { User, UserProfile, PCConfiguration } from '../types';

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [configurations, setConfigurations] = useState<PCConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  
  const [formData, setFormData] = useState<{
    min_budget: number;
    max_budget: number;
    priority: 'performance' | 'silence' | 'compactness' | 'aesthetics';
    multitasking: boolean;
    work_with_4k: boolean;
    vr_support: boolean;
    video_editing: boolean;
    gaming: boolean;
    streaming: boolean;
  }>({
    min_budget: 50000,
    max_budget: 150000,
    priority: 'performance',
    multitasking: false,
    work_with_4k: false,
    vr_support: false,
    video_editing: false,
    gaming: true,
    streaming: false,
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    loadUserData();
  }, [navigate]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const [userRes, profileRes, configsRes] = await Promise.all([
        userAPI.getCurrentUser(),
        userAPI.getMyProfile().catch(() => null),
        configurationAPI.getConfigurations().catch(() => ({ data: { results: [] } })),
      ]);
      
      setUser(userRes.data);
      
      if (profileRes?.data) {
        setProfile(profileRes.data);
        setFormData({
          min_budget: profileRes.data.min_budget || 50000,
          max_budget: profileRes.data.max_budget || 150000,
          priority: profileRes.data.priority || 'performance' as const,
          multitasking: profileRes.data.multitasking || false,
          work_with_4k: profileRes.data.work_with_4k || false,
          vr_support: profileRes.data.vr_support || false,
          video_editing: profileRes.data.video_editing || false,
          gaming: profileRes.data.gaming || false,
          streaming: profileRes.data.streaming || false,
        });
      }
      
      setConfigurations(configsRes.data.results || []);
    } catch (err: any) {
      console.error('Error loading user data:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
      } else {
        setError('Ошибка загрузки данных профиля');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (name === 'priority') {
      setFormData(prev => ({
        ...prev,
        priority: value as 'performance' | 'silence' | 'compactness' | 'aesthetics'
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : 
                type === 'number' ? parseInt(value) : value
      }));
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      await userAPI.updateMyProfile(formData);
      setSuccess('Профиль успешно сохранён!');
      setIsEditing(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Ошибка сохранения профиля');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      // Игнорируем ошибки выхода
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/login');
    }
  };

  const renderIcon = (IconComponent: any, className: string = '') => {
    return React.createElement(IconComponent, { className });
  };

  const getUserTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      gamer: 'Геймер',
      designer: 'Дизайнер',
      programmer: 'Программист',
      content_creator: 'Контент-криэйтор',
      office: 'Офисный работник',
      student: 'Студент',
    };
    return types[type] || type;
  };

  const getPriorityLabel = (priority: string) => {
    const priorities: Record<string, string> = {
      performance: 'Производительность',
      silence: 'Тишина работы',
      compactness: 'Компактность',
      aesthetics: 'Эстетика',
    };
    return priorities[priority] || priority;
  };

  // Подготовка данных конфигурации для PDF
  const prepareConfigPDFData = (config: PCConfiguration): PDFBuildData => {
    // Компоненты с лейблами
    const componentLabels: Record<string, string> = {
      cpu: 'Процессор',
      gpu: 'Видеокарта',
      motherboard: 'Материнская плата',
      ram: 'Оперативная память',
      storage_primary: 'Накопитель (основной)',
      storage_secondary: 'Накопитель (дополнительный)',
      psu: 'Блок питания',
      case: 'Корпус',
      cooling: 'Охлаждение',
    };

    const peripheralLabels: Record<string, string> = {
      monitor_primary: 'Монитор (основной)',
      monitor_secondary: 'Монитор (дополнительный)',
      keyboard: 'Клавиатура',
      mouse: 'Мышь',
      headset: 'Наушники',
      webcam: 'Веб-камера',
      microphone: 'Микрофон',
      speakers: 'Колонки',
      mousepad: 'Коврик для мыши',
    };

    const workspaceLabels: Record<string, string> = {
      desk: 'Стол',
      chair: 'Кресло',
    };

    // Собираем компоненты ПК
    const pcComponents: Component[] = [];
    Object.entries(componentLabels).forEach(([key, label]) => {
      const detailKey = `${key}_detail`;
      const detail = (config as any)[detailKey];
      if (detail) {
        pcComponents.push({
          label,
          name: detail.name || 'Без названия',
          price: parseFloat(detail.price) || 0,
          manufacturer: detail.manufacturer,
        });
      }
    });

    // Собираем периферию из workspace
    const peripherals: Component[] = [];
    const workspace: Component[] = [];
    const workspaceData = (config as any).workspace;
    
    if (workspaceData) {
      Object.entries(peripheralLabels).forEach(([key, label]) => {
        const detailKey = `${key}_detail`;
        const detail = workspaceData[detailKey];
        if (detail) {
          peripherals.push({
            label,
            name: detail.name || 'Без названия',
            price: parseFloat(detail.price) || 0,
            manufacturer: detail.manufacturer,
          });
        }
      });

      Object.entries(workspaceLabels).forEach(([key, label]) => {
        const detailKey = `${key}_detail`;
        const detail = workspaceData[detailKey];
        if (detail) {
          workspace.push({
            label,
            name: detail.name || 'Без названия',
            price: parseFloat(detail.price) || 0,
            manufacturer: detail.manufacturer,
          });
        }
      });
    }

    const pcTotal = pcComponents.reduce((sum, c) => sum + c.price, 0);
    const peripheralsTotal = peripherals.reduce((sum, c) => sum + c.price, 0);
    const workspaceTotal = workspace.reduce((sum, c) => sum + c.price, 0);
    const grandTotal = parseFloat(String(config.total_price)) || (pcTotal + peripheralsTotal + workspaceTotal);

    return {
      name: config.name || `Сборка #${config.id}`,
      pcComponents,
      peripherals,
      workspace,
      pcTotal,
      peripheralsTotal,
      workspaceTotal,
      grandTotal,
    };
  };

  // Печать конфигурации
  const printConfig = (config: PCConfiguration) => {
    printDocument(prepareConfigPDFData(config));
  };

  // Сохранение в PDF
  const saveConfigToPDF = async (config: PCConfiguration) => {
    try {
      await saveToPDF(prepareConfigPDFData(config));
    } catch (error) {
      console.error('Ошибка при сохранении PDF:', error);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="py-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-heading text-3xl md:text-4xl text-white mb-2">
          Мой профиль
        </h1>
        <p className="text-gray-500">
          Управление аккаунтом и настройками
        </p>
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-2">
          {renderIcon(FiX, 'text-lg')}
          {error}
        </div>
      )}
      
      {success && (
        <div className="mb-6 p-4 bg-primary/10 border border-primary/30 text-primary text-sm flex items-center gap-2">
          {renderIcon(FiCheck, 'text-lg')}
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Info Card */}
        <div className="lg:col-span-1">
          <div className="card p-6">
            <div className="text-center mb-6">
              <div className="w-20 h-20 mx-auto bg-primary/20 flex items-center justify-center mb-4">
                {renderIcon(FiUser, 'text-3xl text-primary')}
              </div>
              <h2 className="text-xl font-heading font-semibold text-white">
                {user?.username}
              </h2>
              <p className="text-sm text-gray-500">
                {getUserTypeLabel(user?.user_type || '')}
              </p>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3 text-gray-400">
                {renderIcon(FiMail, 'text-primary')}
                <span className="truncate">{user?.email || 'Не указан'}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-400">
                {renderIcon(FiPhone, 'text-primary')}
                <span>{user?.phone || 'Не указан'}</span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-border-dark">
              <button
                onClick={handleLogout}
                className="btn-secondary w-full flex items-center justify-center gap-2 text-red-400 hover:text-red-300 hover:border-red-500/50"
              >
                {renderIcon(FiLogOut)}
                <span>Выйти из аккаунта</span>
              </button>
            </div>
          </div>

          {/* Stats Card */}
          <div className="card p-6 mt-6">
            <h3 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
              {renderIcon(FiCpu, 'text-primary')}
              Статистика
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Сборок создано</span>
                <span className="text-xl font-heading font-bold text-primary">
                  {configurations.length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Бюджет (мин)</span>
                <span className="text-white font-medium">
                  {formData.min_budget.toLocaleString()} ₽
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Бюджет (макс)</span>
                <span className="text-white font-medium">
                  {formData.max_budget.toLocaleString()} ₽
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Card */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-heading font-semibold text-white flex items-center gap-2">
                {renderIcon(FiSettings, 'text-primary')}
                Настройки конфигуратора
              </h3>
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn-secondary px-4 py-2 text-sm flex items-center gap-2"
                >
                  {renderIcon(FiEdit2)}
                  Редактировать
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="btn-secondary px-4 py-2 text-sm"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="btn-primary px-4 py-2 text-sm flex items-center gap-2"
                  >
                    {saving ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      renderIcon(FiSave)
                    )}
                    Сохранить
                  </button>
                </div>
              )}
            </div>

            {/* Budget */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                {renderIcon(FiDollarSign, 'text-primary')}
                Бюджет
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Минимум (₽)</label>
                  <input
                    type="number"
                    name="min_budget"
                    value={formData.min_budget}
                    onChange={handleChange}
                    disabled={!isEditing}
                    min="10000"
                    step="5000"
                    className="input disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="label">Максимум (₽)</label>
                  <input
                    type="number"
                    name="max_budget"
                    value={formData.max_budget}
                    onChange={handleChange}
                    disabled={!isEditing}
                    min="20000"
                    step="5000"
                    className="input disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>
            </div>

            {/* Priority */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                {renderIcon(FiMonitor, 'text-primary')}
                Приоритет
              </h4>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                disabled={!isEditing}
                className="input disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="performance">Производительность</option>
                <option value="silence">Тишина работы</option>
                <option value="compactness">Компактность</option>
                <option value="aesthetics">Эстетика</option>
              </select>
            </div>

            {/* Requirements */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                {renderIcon(FiCheck, 'text-primary')}
                Требования
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { name: 'multitasking', label: 'Многозадачность' },
                  { name: 'work_with_4k', label: 'Работа с 4K' },
                  { name: 'vr_support', label: 'Поддержка VR' },
                  { name: 'video_editing', label: 'Видеомонтаж' },
                  { name: 'gaming', label: 'Гейминг' },
                  { name: 'streaming', label: 'Стриминг' },
                ].map((item) => (
                  <label
                    key={item.name}
                    className={`flex items-center gap-2 p-3 bg-bg-surface border border-border-dark 
                      ${isEditing ? 'cursor-pointer hover:border-primary/30' : 'cursor-not-allowed opacity-70'}
                      transition-colors ${(formData as any)[item.name] ? 'border-primary/50 bg-primary/5' : ''}`}
                  >
                    <input
                      type="checkbox"
                      name={item.name}
                      checked={(formData as any)[item.name]}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-4 h-4 accent-primary"
                    />
                    <span className="text-sm text-gray-400">{item.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Configurations */}
          {configurations.length > 0 && (
            <div className="card p-6 mt-6">
              <h3 className="text-lg font-heading font-semibold text-white mb-4 flex items-center gap-2">
                {renderIcon(FiCpu, 'text-primary')}
                Последние сборки
              </h3>
              <div className="space-y-3">
                {configurations.slice(0, 5).map((config) => (
                  <div
                    key={config.id}
                    className="p-4 bg-bg-surface border border-border-dark hover:border-primary/30 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div 
                        onClick={() => navigate(`/configuration/${config.id}`)}
                        className="cursor-pointer flex-1"
                      >
                        <p className="text-white font-medium hover:text-primary transition-colors">
                          {config.name || `Сборка #${config.id}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(config.created_at).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                      <p className="text-primary font-heading font-bold text-lg">
                        {Number(config.total_price).toLocaleString()} ₽
                      </p>
                    </div>
                    
                    {/* Action buttons */}
                    <div className="flex gap-2 pt-3 border-t border-border-dark">
                      <button
                        onClick={() => navigate(`/configuration/${config.id}`)}
                        className="flex-1 py-2 px-3 bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium 
                          transition-colors flex items-center justify-center gap-2"
                      >
                        {renderIcon(FiExternalLink, 'w-4 h-4')}
                        Открыть
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          printConfig(config);
                        }}
                        className="py-2 px-3 bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm font-medium 
                          transition-colors flex items-center justify-center gap-2"
                        title="Печать"
                      >
                        {renderIcon(FiPrinter, 'w-4 h-4')}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          saveConfigToPDF(config);
                        }}
                        className="py-2 px-3 bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-700 hover:to-pink-700 
                          text-white text-sm font-medium transition-all flex items-center justify-center gap-2"
                        title="Сохранить PDF"
                      >
                        {renderIcon(FiDownload, 'w-4 h-4')}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {configurations.length > 5 && (
                <button
                  onClick={() => navigate('/my-configurations')}
                  className="mt-4 text-sm text-primary hover:text-bright transition-colors"
                >
                  Показать все ({configurations.length})
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
