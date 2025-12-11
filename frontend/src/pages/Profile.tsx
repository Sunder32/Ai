import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser, FiMail, FiLogOut, FiCpu, FiDollarSign, FiCheck, FiGrid, FiSettings, FiClock, FiExternalLink, FiPrinter, FiDownload, FiSave, FiEdit2 } from 'react-icons/fi';
import { userAPI, authAPI, configurationAPI } from '../services/api';
import { printDocument, saveToPDF, PDFBuildData } from '../services/pdfGenerator';
import LoadingSpinner from '../components/LoadingSpinner';
import { PCConfiguration, User, UserProfile } from '../types';

// Helper to render icons safely
const Icon = ({ icon, ...props }: { icon: any, className?: string, size?: number }) => {
  return React.createElement(icon, props);
};

// Components matching the screenshot design - Darker Theme
const StatCard = ({ icon, label, value, subtext }: { icon: any, label: string, value: string, subtext?: string }) => (
  <div className="bg-bg-card rounded-xl p-6 relative overflow-hidden group border border-border-dark shadow-lg shadow-black/20">
    <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity pointer-events-none">
      <Icon icon={icon} className="w-24 h-24" />
    </div>
    <div className="relative z-10 flex flex-col h-full justify-between">
      <div>
        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 text-primary">
          <Icon icon={icon} className="w-6 h-6" />
        </div>
        <div className="text-3xl font-bold text-text-primary mb-1 tracking-tight font-heading">{value}</div>
        <div className="text-sm text-text-secondary font-medium">{label}</div>
      </div>
      {subtext && <div className="text-xs text-text-muted mt-4 pt-4 border-t border-border-dark">{subtext}</div>}
    </div>
  </div>
);

const BuildCard = ({ config, onOpen, onPrint, onPDF }: {
  config: PCConfiguration,
  onOpen: () => void,
  onPrint: () => void,
  onPDF: () => void
}) => {
  // Use _detail fields if available, otherwise fallback to direct object (if nested)
  const getCompName = (key: keyof PCConfiguration) => {
    const detailKey = `${key}_detail` as keyof PCConfiguration;
    const detail = config[detailKey] as any;
    if (detail && detail.name) return detail.name;

    // Fallback if key itself is object
    const val = config[key] as any;
    if (typeof val === 'object' && val?.name) return val.name;

    return '-';
  };

  const getCompCapacity = (key: keyof PCConfiguration) => {
    const detailKey = `${key}_detail` as keyof PCConfiguration;
    const detail = config[detailKey] as any;
    if (detail && detail.capacity) return `${detail.capacity}GB`;

    const val = config[key] as any;
    if (typeof val === 'object' && val?.capacity) return `${val.capacity}GB`;

    return '-';
  };

  return (
    <div className="bg-bg-card rounded-xl p-6 border border-border-dark hover:border-primary/30 transition-all duration-300 group hover:-translate-y-1 shadow-lg shadow-black/20">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-text-primary group-hover:text-primary transition-colors cursor-pointer tracking-tight font-heading" onClick={onOpen}>
            {config.name || `AI-сборка для ${config.user_type || 'пользователя'}`}
          </h3>
          <p className="text-xs text-text-muted mt-1 flex items-center gap-1.5">
            <Icon icon={FiClock} className="w-3 h-3" />
            {new Date(config.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="text-xl font-bold text-text-primary tracking-tight font-mono">
          {Number(config.total_price).toLocaleString()} ₽
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="bg-bg-surface rounded-lg px-3 py-2.5 text-xs border border-border-dark">
          <span className="text-text-muted block mb-1 font-medium">CPU:</span>
          <span className="text-text-secondary truncate block font-medium h-4">{getCompName('cpu')}</span>
        </div>
        <div className="bg-bg-surface rounded-lg px-3 py-2.5 text-xs border border-border-dark">
          <span className="text-text-muted block mb-1 font-medium">GPU:</span>
          <span className="text-text-secondary truncate block font-medium h-4">{getCompName('gpu')}</span>
        </div>
        <div className="bg-bg-surface rounded-lg px-3 py-2.5 text-xs border border-border-dark">
          <span className="text-text-muted block mb-1 font-medium">RAM:</span>
          <span className="text-text-secondary truncate block font-medium h-4">{getCompCapacity('ram')}</span>
        </div>
        <div className="bg-bg-surface rounded-lg px-3 py-2.5 text-xs border border-border-dark">
          <span className="text-text-muted block mb-1 font-medium">SSD:</span>
          <span className="text-text-secondary truncate block font-medium h-4">{getCompCapacity('storage_primary')}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button onClick={onOpen} className="flex-1 py-2.5 bg-primary hover:bg-primary-light text-black text-xs font-bold rounded-lg transition-all shadow-glow hover:shadow-glow-hover">
          Открыть
        </button>
        <button onClick={(e) => { e.stopPropagation(); onPrint(); }} className="p-2.5 text-text-muted hover:text-text-primary bg-bg-surface hover:bg-bg-card rounded-lg transition-colors border border-border-dark flex items-center justify-center">
          <Icon icon={FiPrinter} size={16} />
        </button>
        <button onClick={(e) => { e.stopPropagation(); onPDF(); }} className="p-2.5 text-text-muted hover:text-text-primary bg-bg-surface hover:bg-bg-card rounded-lg transition-colors border border-border-dark flex items-center justify-center">
          <Icon icon={FiDownload} size={16} />
        </button>
      </div>
    </div>
  );
};

// Main Component
const Profile: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [configurations, setConfigurations] = useState<PCConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<'builds' | 'preferences'>('builds');

  // Stats
  const [totalSpent, setTotalSpent] = useState(0);
  const [avgBuildPrice, setAvgBuildPrice] = useState(0);

  // Form
  const [formData, setFormData] = useState({
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
    loadUserData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  const loadUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) { navigate('/login'); return; }

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
          priority: profileRes.data.priority || 'performance',
          multitasking: profileRes.data.multitasking || false,
          work_with_4k: profileRes.data.work_with_4k || false,
          vr_support: profileRes.data.vr_support || false,
          video_editing: profileRes.data.video_editing || false,
          gaming: profileRes.data.gaming || false,
          streaming: profileRes.data.streaming || false,
        });
      }

      const configs = (configsRes.data.results || []) as PCConfiguration[];
      setConfigurations(configs);

      const total = configs.reduce((acc: number, curr: PCConfiguration) => acc + Number(curr.total_price || 0), 0);
      setTotalSpent(total);
      setAvgBuildPrice(configs.length > 0 ? Math.round(total / configs.length) : 0);

    } catch (err) {
      console.error('Error loading profile data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await userAPI.updateMyProfile(formData as any);
      setIsEditing(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  // Helper to safely get component object from config
  const getCompDetail = (config: PCConfiguration, key: keyof PCConfiguration) => {
    // Check detail field first
    const detailKey = `${key}_detail` as keyof PCConfiguration;
    const detail = config[detailKey];
    if (typeof detail === 'object' && detail !== null) return detail;

    // Check main field
    const val = config[key];
    if (typeof val === 'object' && val !== null) return val;

    return null;
  };

  const prepareConfigPDFData = (config: PCConfiguration): PDFBuildData => {
    const pcComponents = [
      { label: 'Процессор', val: getCompDetail(config, 'cpu') },
      { label: 'Видеокарта', val: getCompDetail(config, 'gpu') },
      { label: 'Материнская плата', val: getCompDetail(config, 'motherboard') },
      { label: 'ОЗУ', val: getCompDetail(config, 'ram') },
      { label: 'SSD', val: getCompDetail(config, 'storage_primary') },
      { label: 'БП', val: getCompDetail(config, 'psu') },
      { label: 'Корпус', val: getCompDetail(config, 'case') },
      { label: 'Охлаждение', val: getCompDetail(config, 'cooling') },
    ].filter(i => i.val).map(i => ({
      label: i.label,
      name: (i.val as any)?.name || '',
      price: Number((i.val as any)?.price || 0),
      manufacturer: (i.val as any)?.manufacturer,
      specs: (i.val as any)?.specs || (i.val as any)?.capacity ? `${(i.val as any).capacity}GB` : ''
    }));

    // Extract Workspace items if available
    const workspaceItems: any[] = [];
    if (config.workspace) {
      const ws = config.workspace;
      
      // Helper to add workspace item
      const addWsItem = (label: string, item: any) => {
        if (item) {
          workspaceItems.push({
            label,
            name: item.name || '',
            price: Number(item.price || 0),
            manufacturer: item.manufacturer
          });
        }
      };

      addWsItem('Монитор (осн.)', ws.monitor_primary_detail || (typeof ws.monitor_primary === 'object' ? ws.monitor_primary : null));
      addWsItem('Монитор (доп.)', ws.monitor_secondary_detail || (typeof ws.monitor_secondary === 'object' ? ws.monitor_secondary : null));
      addWsItem('Клавиатура', ws.keyboard_detail || (typeof ws.keyboard === 'object' ? ws.keyboard : null));
      addWsItem('Мышь', ws.mouse_detail || (typeof ws.mouse === 'object' ? ws.mouse : null));
      addWsItem('Гарнитура', ws.headset_detail || (typeof ws.headset === 'object' ? ws.headset : null));
      addWsItem('Веб-камера', ws.webcam_detail || (typeof ws.webcam === 'object' ? ws.webcam : null));
      addWsItem('Микрофон', ws.microphone_detail || (typeof ws.microphone === 'object' ? ws.microphone : null));
      addWsItem('Стол', ws.desk_detail || (typeof ws.desk === 'object' ? ws.desk : null));
      addWsItem('Кресло', ws.chair_detail || (typeof ws.chair === 'object' ? ws.chair : null));
    }

    // Separate peripherals vs furniture if needed, or group them. 
    // Based on PDF template structure:
    // peripherals: mouse, keyboard, headset, webcam, mic, etc.
    // workspace: desk, chair, monitor arms, etc.
    
    const peripherals = workspaceItems.filter(i => 
      ['Клавиатура', 'Мышь', 'Гарнитура', 'Веб-камера', 'Микрофон', 'Монитор (осн.)', 'Монитор (доп.)'].includes(i.label)
    );
    
    const workspace = workspaceItems.filter(i => 
      ['Стол', 'Кресло'].includes(i.label)
    );

    const pcTotal = pcComponents.reduce((a, b) => a + b.price, 0);
    const peripheralsTotal = peripherals.reduce((a, b) => a + b.price, 0);
    const workspaceTotal = workspace.reduce((a, b) => a + b.price, 0);

    return {
      name: config.name || `Сборка #${config.id}`,
      id: config.id,
      createdAt: config.created_at,
      pcComponents,
      peripherals,
      workspace,
      pcTotal,
      peripheralsTotal,
      workspaceTotal,
      grandTotal: Number(config.total_price)
    };
  };

  // PDF Wrappers with error handling
  const handlePrint = (config: PCConfiguration) => {
    try {
      const data = prepareConfigPDFData(config);
      printDocument(data);
    } catch (e) {
      console.error("Print error:", e);
      alert("Ошибка при печати. Проверьте консоль.");
    }
  };

  const handlePDF = async (config: PCConfiguration) => {
    try {
      const data = prepareConfigPDFData(config);
      await saveToPDF(data);
    } catch (e) {
      console.error("PDF generation error:", e);
      // Sometimes html2pdf throws standard errors
      alert("Не удалось создать PDF. Попробуйте обновить страницу.");
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-bg-primary text-text-primary"><LoadingSpinner /></div>;

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary font-body pb-20">
      {/* Navbar / Header Area */}
      <div className="bg-bg-primary border-b border-border-dark px-6 py-6 sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-5 w-full md:w-auto">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-primary to-primary-deep flex items-center justify-center text-2xl font-bold text-bg-primary shadow-glow ring-1 ring-border-dark">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-text-primary mb-1 tracking-tight font-heading">{user?.username}</h1>
              <div className="flex flex-wrap gap-2 text-sm">
                <span className="flex items-center gap-1.5 bg-bg-card px-3 py-0.5 rounded text-text-secondary border border-border-dark">
                  <Icon icon={FiUser} size={12} /> {user?.user_type || 'Пользователь'}
                </span>
                <span className="flex items-center gap-1.5 bg-bg-card px-3 py-0.5 rounded text-text-secondary border border-border-dark">
                  <Icon icon={FiMail} size={12} /> {user?.email}
                </span>
              </div>
            </div>
          </div>

          <button onClick={handleLogout} className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 border border-red-500/10">
            <Icon icon={FiLogOut} /> Выйти
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-10">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <StatCard
            icon={FiCpu}
            label="Создано сборок"
            value={configurations.length.toString()}
            subtext="Самая новая: сегодня"
          />
          <StatCard
            icon={FiDollarSign}
            label="Общая стоимость"
            value={`${(totalSpent / 1000).toFixed(1)}k ₽`}
            subtext={`В среднем ${Math.round(avgBuildPrice / 1000)}k ₽ за сборку`}
          />
          <StatCard
            icon={FiCheck}
            label="Статус профиля"
            value="Active"
            subtext="Все функции доступны"
          />
        </div>

        {/* Tabs */}
        <div className="flex gap-8 border-b border-border-dark mb-10">
          <button
            onClick={() => setActiveTab('builds')}
            className={`pb-4 px-1 font-medium text-sm transition-colors relative ${activeTab === 'builds' ? 'text-primary' : 'text-text-muted hover:text-text-primary'}`}
          >
            <span className="flex items-center gap-2"><Icon icon={FiGrid} /> Мои сборки</span>
            {activeTab === 'builds' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-primary shadow-glow" />}
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            className={`pb-4 px-1 font-medium text-sm transition-colors relative ${activeTab === 'preferences' ? 'text-primary' : 'text-text-muted hover:text-text-primary'}`}
          >
            <span className="flex items-center gap-2"><Icon icon={FiSettings} /> Настройки ИИ</span>
            {activeTab === 'preferences' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-primary shadow-glow" />}
          </button>
        </div>

        {/* Builds Section */}
        {activeTab === 'builds' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {configurations.map(config => (
              <BuildCard
                key={config.id}
                config={config}
                onOpen={() => navigate(`/configuration/${config.id}`)}
                onPrint={() => handlePrint(config)}
                onPDF={() => handlePDF(config)}
              />
            ))}
            {configurations.length === 0 && (
              <div className="col-span-full py-24 text-center border border-dashed border-border-dark rounded-2xl bg-bg-card">
                <div className="w-16 h-16 bg-bg-surface rounded-full flex items-center justify-center mx-auto mb-4 text-text-muted border border-border-dark">
                  <Icon icon={FiGrid} size={24} />
                </div>
                <h3 className="text-xl font-bold text-text-primary mb-2 font-heading">Нет сборок</h3>
                <p className="text-text-muted mb-6">Вы еще не создали ни одной конфигурации</p>
                <button
                  onClick={() => navigate('/')}
                  className="px-6 py-3 bg-primary hover:bg-primary-light text-bg-primary rounded-lg font-bold transition-colors shadow-glow"
                >
                  Создать первую сборку
                </button>
              </div>
            )}
          </div>
        )}

        {/* Preferences Section */}
        {activeTab === 'preferences' && (
          <div className="bg-bg-card border border-border-dark rounded-xl p-8 shadow-card">
            <div className="flex justify-between items-center mb-10">
              <div>
                <h2 className="text-2xl font-bold text-text-primary tracking-tight font-heading">Предпочтения ИИ</h2>
                <p className="text-text-secondary mt-1">Параметры для автоматического подбора комплектующих</p>
              </div>
              <button
                onClick={() => isEditing ? handleSave() : setIsEditing(true)}
                className={`px-5 py-2.5 rounded-lg flex items-center gap-2 font-medium transition-all ${isEditing
                    ? 'bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20'
                    : 'bg-bg-surface text-text-secondary hover:bg-bg-card border border-border-dark'
                  }`}
              >
                {isEditing ? <><Icon icon={FiSave} /> Сохранить</> : <><Icon icon={FiEdit2} /> Изменить</>}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-12">
              {/* Budget */}
              <div>
                <h3 className="text-sm font-bold text-text-muted uppercase tracking-wider mb-6 flex items-center gap-2">
                  <Icon icon={FiDollarSign} className="text-primary" /> Бюджет
                </h3>
                <div className="space-y-6">
                  <div>
                    <label className="block text-xs font-bold text-text-muted mb-2 uppercase tracking-wide">Минимальный бюджет</label>
                    {isEditing ? (
                      <input
                        type="number"
                        value={formData.min_budget}
                        onChange={e => setFormData({ ...formData, min_budget: Number(e.target.value) })}
                        className="w-full bg-bg-surface border border-border-dark rounded-lg px-4 py-3 text-text-primary focus:border-primary focus:outline-none transition-colors"
                      />
                    ) : (
                      <div className="text-xl font-medium text-text-primary tracking-tight font-mono">{formData.min_budget.toLocaleString()} ₽</div>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-text-muted mb-2 uppercase tracking-wide">Максимальный бюджет</label>
                    {isEditing ? (
                      <input
                        type="number"
                        value={formData.max_budget}
                        onChange={e => setFormData({ ...formData, max_budget: Number(e.target.value) })}
                        className="w-full bg-bg-surface border border-border-dark rounded-lg px-4 py-3 text-text-primary focus:border-primary focus:outline-none transition-colors"
                      />
                    ) : (
                      <div className="text-xl font-medium text-text-primary tracking-tight font-mono">{formData.max_budget.toLocaleString()} ₽</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Priority */}
              <div>
                <h3 className="text-sm font-bold text-text-muted uppercase tracking-wider mb-6 flex items-center gap-2">
                  <Icon icon={FiSettings} className="text-primary-light" /> Приоритеты
                </h3>
                <div className="mb-8">
                  <label className="block text-xs font-bold text-text-muted mb-2 uppercase tracking-wide">Главный приоритет</label>
                  {isEditing ? (
                    <select
                      value={formData.priority}
                      onChange={e => setFormData({ ...formData, priority: e.target.value })}
                      className="w-full bg-bg-surface border border-border-dark rounded-lg px-4 py-3 text-text-primary focus:border-primary focus:outline-none transition-colors"
                    >
                      <option value="performance">Максимальная производительность</option>
                      <option value="silence">Тишина и охлаждение</option>
                      <option value="aesthetics">Внешний вид (RGB)</option>
                      <option value="compactness">Компактность (SFF)</option>
                    </select>
                  ) : (
                    <div className="inline-flex items-center px-4 py-2 bg-primary/10 text-primary rounded-lg text-sm font-semibold border border-primary/20">
                      {formData.priority === 'performance' && 'Максимальная производительность'}
                      {formData.priority === 'silence' && 'Тишина и охлаждение'}
                      {formData.priority === 'aesthetics' && 'Внешний вид (RGB)'}
                      {formData.priority === 'compactness' && 'Компактность (SFF)'}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: 'gaming', label: 'Игры' },
                    { key: 'streaming', label: 'Стриминг' },
                    { key: 'video_editing', label: 'Монтаж' },
                    { key: 'work_with_4k', label: '4K контент' },
                    { key: 'vr_support', label: 'VR' },
                    { key: 'multitasking', label: 'Многозадачность' },
                  ].map(item => (
                    <label key={item.key} className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${(formData as any)[item.key]
                        ? 'bg-primary/10 border-primary/30'
                        : 'bg-bg-surface border-border-dark opacity-60'
                      } ${isEditing ? 'cursor-pointer hover:border-text-muted' : ''}`}>
                      <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${(formData as any)[item.key] ? 'bg-primary border-primary' : 'border-text-muted'
                        }`}>
                        {(formData as any)[item.key] && <Icon icon={FiCheck} size={14} className="text-bg-primary" />}
                      </div>
                      {isEditing && <input
                        type="checkbox"
                        hidden
                        checked={(formData as any)[item.key]}
                        onChange={e => setFormData({ ...formData, [item.key]: e.target.checked })}
                      />}
                      <span className={`text-sm ${(formData as any)[item.key] ? 'text-text-primary font-medium' : 'text-text-muted'}`}>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
