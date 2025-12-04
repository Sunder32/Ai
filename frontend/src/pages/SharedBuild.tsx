import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  FiCpu, FiMonitor, FiBox, FiArrowLeft, FiCopy, 
  FiCheck, FiX, FiHardDrive, FiZap, FiWind 
} from 'react-icons/fi';
import api from '../services/api';

interface ComponentDetail {
  id: number;
  name: string;
  manufacturer: string;
  price: string | number;
  [key: string]: any;
}

interface BuildData {
  id: number;
  name: string;
  total_price: string | number;
  created_at: string;
  compatibility_check: boolean;
  compatibility_notes: string;
  cpu_detail?: ComponentDetail;
  gpu_detail?: ComponentDetail;
  motherboard_detail?: ComponentDetail;
  ram_detail?: ComponentDetail;
  storage_primary_detail?: ComponentDetail;
  storage_secondary_detail?: ComponentDetail;
  psu_detail?: ComponentDetail;
  case_detail?: ComponentDetail;
  cooling_detail?: ComponentDetail;
  workspace?: {
    monitor_primary_detail?: ComponentDetail;
    monitor_secondary_detail?: ComponentDetail;
    keyboard_detail?: ComponentDetail;
    mouse_detail?: ComponentDetail;
    headset_detail?: ComponentDetail;
    speakers_detail?: ComponentDetail;
    webcam_detail?: ComponentDetail;
    microphone_detail?: ComponentDetail;
    desk_detail?: ComponentDetail;
    chair_detail?: ComponentDetail;
    mousepad_detail?: ComponentDetail;
    monitor_arm_detail?: ComponentDetail;
    usb_hub_detail?: ComponentDetail;
    lighting_detail?: ComponentDetail;
    stream_deck_detail?: ComponentDetail;
    capture_card_detail?: ComponentDetail;
    gamepad_detail?: ComponentDetail;
    headphone_stand_detail?: ComponentDetail;
    total_price: string | number;
  };
}

const SharedBuild: React.FC = () => {
  const { shareCode } = useParams<{ shareCode: string }>();
  const [build, setBuild] = useState<BuildData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const loadBuild = async () => {
      if (!shareCode) return;
      
      setLoading(true);
      try {
        const response = await api.get<BuildData>(`/recommendations/configurations/public/${shareCode}/`);
        setBuild(response.data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Сборка не найдена');
      } finally {
        setLoading(false);
      }
    };

    loadBuild();
  }, [shareCode]);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  const renderComponent = (label: string, component?: ComponentDetail, icon?: any) => {
    if (!component) return null;
    
    return (
      <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-3">
          {icon && React.createElement(icon as any, { className: "w-5 h-5 text-emerald-500" })}
          <div>
            <p className="text-xs text-gray-500">{label}</p>
            <p className="text-white font-medium">{component.name}</p>
            <p className="text-xs text-gray-400">{component.manufacturer}</p>
          </div>
        </div>
        <span className="text-emerald-400 font-semibold">
          {parseFloat(String(component.price)).toLocaleString('ru-RU')} ₽
        </span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Загрузка сборки...</p>
        </div>
      </div>
    );
  }

  if (error || !build) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            {React.createElement(FiX as any, { className: "w-8 h-8 text-red-500" })}
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Сборка не найдена</h2>
          <p className="text-gray-400 mb-4">{error || 'Возможно, ссылка недействительна или сборка удалена'}</p>
          <Link 
            to="/build-yourself"
            className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors"
          >
            {React.createElement(FiArrowLeft as any, { className: "w-4 h-4" })}
            Создать свою сборку
          </Link>
        </div>
      </div>
    );
  }

  // Считаем общую стоимость с периферией
  const totalWithWorkspace = parseFloat(String(build.total_price)) + 
    (build.workspace ? parseFloat(String(build.workspace.total_price)) - parseFloat(String(build.total_price)) : 0);

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link 
            to="/build-yourself"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            {React.createElement(FiArrowLeft as any, { className: "w-4 h-4" })}
            Вернуться к конструктору
          </Link>
          
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{build.name}</h1>
              <p className="text-gray-400">
                Создано: {new Date(build.created_at).toLocaleDateString('ru-RU', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric'
                })}
              </p>
            </div>
            
            <button
              onClick={copyLink}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              {copied 
                ? React.createElement(FiCheck as any, { className: "w-4 h-4 text-emerald-400" })
                : React.createElement(FiCopy as any, { className: "w-4 h-4" })
              }
              {copied ? 'Скопировано!' : 'Копировать ссылку'}
            </button>
          </div>
        </div>

        {/* Compatibility Badge */}
        <div className={`p-4 rounded-lg mb-6 flex items-center gap-3 ${
          build.compatibility_check 
            ? 'bg-emerald-500/10 border border-emerald-500/30'
            : 'bg-yellow-500/10 border border-yellow-500/30'
        }`}>
          {build.compatibility_check 
            ? React.createElement(FiCheck as any, { className: "w-5 h-5 text-emerald-400" })
            : React.createElement(FiX as any, { className: "w-5 h-5 text-yellow-400" })
          }
          <span className={build.compatibility_check ? 'text-emerald-400' : 'text-yellow-400'}>
            {build.compatibility_check 
              ? 'Все компоненты совместимы'
              : build.compatibility_notes || 'Есть замечания по совместимости'
            }
          </span>
        </div>

        {/* PC Components */}
        <div className="bg-gray-800/30 border border-gray-700 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            {React.createElement(FiCpu as any, { className: "w-5 h-5 text-emerald-500" })}
            Компоненты ПК
          </h2>
          
          <div className="space-y-3">
            {renderComponent('Процессор', build.cpu_detail, FiCpu)}
            {renderComponent('Видеокарта', build.gpu_detail, FiMonitor)}
            {renderComponent('Материнская плата', build.motherboard_detail, FiBox)}
            {renderComponent('Оперативная память', build.ram_detail, FiHardDrive)}
            {renderComponent('Основной накопитель', build.storage_primary_detail, FiHardDrive)}
            {renderComponent('Дополнительный накопитель', build.storage_secondary_detail, FiHardDrive)}
            {renderComponent('Блок питания', build.psu_detail, FiZap)}
            {renderComponent('Корпус', build.case_detail, FiBox)}
            {renderComponent('Охлаждение', build.cooling_detail, FiWind)}
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-700 flex justify-between items-center">
            <span className="text-gray-400">Стоимость ПК:</span>
            <span className="text-xl font-bold text-emerald-400">
              {parseFloat(String(build.total_price)).toLocaleString('ru-RU')} ₽
            </span>
          </div>
        </div>

        {/* Peripherals & Workspace */}
        {build.workspace && (
          <div className="bg-gray-800/30 border border-gray-700 rounded-xl p-6 mb-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              {React.createElement(FiMonitor as any, { className: "w-5 h-5 text-emerald-500" })}
              Периферия и рабочее место
            </h2>
            
            <div className="space-y-3">
              {renderComponent('Монитор (основной)', build.workspace.monitor_primary_detail, FiMonitor)}
              {renderComponent('Монитор (дополнительный)', build.workspace.monitor_secondary_detail, FiMonitor)}
              {renderComponent('Клавиатура', build.workspace.keyboard_detail, FiBox)}
              {renderComponent('Мышь', build.workspace.mouse_detail, FiBox)}
              {renderComponent('Наушники', build.workspace.headset_detail, FiBox)}
              {renderComponent('Колонки', build.workspace.speakers_detail, FiBox)}
              {renderComponent('Веб-камера', build.workspace.webcam_detail, FiBox)}
              {renderComponent('Микрофон', build.workspace.microphone_detail, FiBox)}
              {renderComponent('Коврик', build.workspace.mousepad_detail, FiBox)}
              {renderComponent('Кронштейн монитора', build.workspace.monitor_arm_detail, FiBox)}
              {renderComponent('USB-хаб', build.workspace.usb_hub_detail, FiBox)}
              {renderComponent('Освещение', build.workspace.lighting_detail, FiBox)}
              {renderComponent('Стрим-пульт', build.workspace.stream_deck_detail, FiBox)}
              {renderComponent('Карта захвата', build.workspace.capture_card_detail, FiBox)}
              {renderComponent('Геймпад', build.workspace.gamepad_detail, FiBox)}
              {renderComponent('Подставка для наушников', build.workspace.headphone_stand_detail, FiBox)}
              {renderComponent('Стол', build.workspace.desk_detail, FiBox)}
              {renderComponent('Кресло', build.workspace.chair_detail, FiBox)}
            </div>
          </div>
        )}

        {/* Total */}
        <div className="bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 border border-emerald-500/30 rounded-xl p-6">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-400 mb-1">Общая стоимость сборки</p>
              <p className="text-3xl font-bold text-emerald-400">
                {totalWithWorkspace.toLocaleString('ru-RU')} ₽
              </p>
            </div>
            <Link
              to="/build-yourself"
              className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-lg transition-colors"
            >
              Создать похожую сборку
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SharedBuild;
