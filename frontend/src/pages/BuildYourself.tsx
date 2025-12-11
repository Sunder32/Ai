import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  FiCpu, FiMonitor, FiHardDrive, FiBox, FiWind, FiZap,
  FiShoppingCart, FiCheck, FiX, FiChevronDown, FiChevronUp,
  FiTrash2, FiSave, FiShare2, FiLink, FiPrinter, FiList,
  FiExternalLink, FiCopy, FiSearch, FiFilter, FiChevronRight,
  FiHome, FiDownload
} from 'react-icons/fi';
import { computerAPI, peripheralAPI, configurationAPI, BuildRequest } from '../services/api';
import { saveToPDF as savePDF, printDocument, getComponentLabel, type PDFBuildData, type Component } from '../services/pdfGenerator';
import type {
  CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling,
  Monitor, Keyboard, Mouse, Headset, Webcam, Microphone,
  Desk, Chair, Speakers, Mousepad, MonitorArm, USBHub,
  DeskLighting, StreamDeck, CaptureCard, Gamepad, HeadphoneStand
} from '../types';

// Типы для выбранных компонентов
interface SelectedComponents {
  cpu: CPU | null;
  gpu: GPU | null;
  motherboard: Motherboard | null;
  ram: RAM | null;
  storage: Storage | null;
  storage2: Storage | null;
  psu: PSU | null;
  case: Case | null;
  cooling: Cooling | null;
}

interface SelectedPeripherals {
  monitor: Monitor | null;
  monitor2: Monitor | null;
  keyboard: Keyboard | null;
  mouse: Mouse | null;
  headset: Headset | null;
  webcam: Webcam | null;
  microphone: Microphone | null;
  speakers: Speakers | null;
  mousepad: Mousepad | null;
  monitorArm: MonitorArm | null;
  usbHub: USBHub | null;
  lighting: DeskLighting | null;
  streamDeck: StreamDeck | null;
  captureCard: CaptureCard | null;
  gamepad: Gamepad | null;
  headphoneStand: HeadphoneStand | null;
}

interface SelectedWorkspace {
  desk: Desk | null;
  chair: Chair | null;
}

type ComponentCategory = 'pc' | 'peripherals' | 'workspace';

type SortOption = 'price-asc' | 'price-desc' | 'name-asc' | 'name-desc' | 'popular';

interface FilterState {
  search: string;
  minPrice: number | '';
  maxPrice: number | '';
  manufacturer: string;
  sortBy: SortOption;
}

interface ComponentSection {
  key: string;
  label: string;
  icon: any; // IconType from react-icons
  required?: boolean;
}

const pcSections: ComponentSection[] = [
  { key: 'cpu', label: 'Процессор', icon: FiCpu, required: true },
  { key: 'gpu', label: 'Видеокарта', icon: FiMonitor, required: true },
  { key: 'motherboard', label: 'Материнская плата', icon: FiBox, required: true },
  { key: 'ram', label: 'Оперативная память', icon: FiHardDrive, required: true },
  { key: 'storage', label: 'Накопитель (основной)', icon: FiHardDrive, required: true },
  { key: 'storage2', label: 'Накопитель (дополнительный)', icon: FiHardDrive },
  { key: 'psu', label: 'Блок питания', icon: FiZap, required: true },
  { key: 'case', label: 'Корпус', icon: FiBox, required: true },
  { key: 'cooling', label: 'Охлаждение', icon: FiWind, required: true },
];

const peripheralSections: ComponentSection[] = [
  { key: 'monitor', label: 'Монитор (основной)', icon: FiMonitor },
  { key: 'monitor2', label: 'Монитор (дополнительный)', icon: FiMonitor },
  { key: 'keyboard', label: 'Клавиатура', icon: FiBox },
  { key: 'mouse', label: 'Мышь', icon: FiBox },
  { key: 'headset', label: 'Наушники/Гарнитура', icon: FiBox },
  { key: 'speakers', label: 'Колонки', icon: FiBox },
  { key: 'mousepad', label: 'Коврик для мыши', icon: FiBox },
  { key: 'webcam', label: 'Веб-камера', icon: FiBox },
  { key: 'microphone', label: 'Микрофон', icon: FiBox },
  { key: 'monitorArm', label: 'Кронштейн для монитора', icon: FiBox },
  { key: 'usbHub', label: 'USB-хаб', icon: FiBox },
  { key: 'lighting', label: 'Освещение', icon: FiBox },
  { key: 'streamDeck', label: 'Стрим-пульт', icon: FiBox },
  { key: 'captureCard', label: 'Карта захвата', icon: FiBox },
  { key: 'gamepad', label: 'Геймпад', icon: FiBox },
  { key: 'headphoneStand', label: 'Подставка для наушников', icon: FiBox },
];

const workspaceSections: ComponentSection[] = [
  { key: 'desk', label: 'Стол', icon: FiBox },
  { key: 'chair', label: 'Кресло', icon: FiBox },
];

const BuildYourself: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<ComponentCategory>('pc');
  const [expandedSection, setExpandedSection] = useState<string | null>('cpu');

  // Состояния для компонентов ПК
  const [cpus, setCpus] = useState<CPU[]>([]);
  const [gpus, setGpus] = useState<GPU[]>([]);
  const [motherboards, setMotherboards] = useState<Motherboard[]>([]);
  const [rams, setRams] = useState<RAM[]>([]);
  const [storages, setStorages] = useState<Storage[]>([]);
  const [psus, setPsus] = useState<PSU[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [coolings, setCoolings] = useState<Cooling[]>([]);

  // Состояния для периферии
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [keyboards, setKeyboards] = useState<Keyboard[]>([]);
  const [mice, setMice] = useState<Mouse[]>([]);
  const [headsets, setHeadsets] = useState<Headset[]>([]);
  const [webcams, setWebcams] = useState<Webcam[]>([]);
  const [microphones, setMicrophones] = useState<Microphone[]>([]);
  const [speakers, setSpeakers] = useState<Speakers[]>([]);
  const [mousepads, setMousepads] = useState<Mousepad[]>([]);
  const [monitorArms, setMonitorArms] = useState<MonitorArm[]>([]);
  const [usbHubs, setUsbHubs] = useState<USBHub[]>([]);
  const [lighting, setLighting] = useState<DeskLighting[]>([]);
  const [streamDecks, setStreamDecks] = useState<StreamDeck[]>([]);
  const [captureCards, setCaptureCards] = useState<CaptureCard[]>([]);
  const [gamepads, setGamepads] = useState<Gamepad[]>([]);
  const [headphoneStands, setHeadphoneStands] = useState<HeadphoneStand[]>([]);

  // Состояния для рабочего места
  const [desks, setDesks] = useState<Desk[]>([]);
  const [chairs, setChairs] = useState<Chair[]>([]);

  // Выбранные компоненты
  const [selectedPC, setSelectedPC] = useState<SelectedComponents>({
    cpu: null, gpu: null, motherboard: null, ram: null,
    storage: null, storage2: null, psu: null, case: null, cooling: null
  });

  const [selectedPeripherals, setSelectedPeripherals] = useState<SelectedPeripherals>({
    monitor: null, monitor2: null, keyboard: null, mouse: null,
    headset: null, webcam: null, microphone: null, speakers: null,
    mousepad: null, monitorArm: null, usbHub: null, lighting: null,
    streamDeck: null, captureCard: null, gamepad: null, headphoneStand: null
  });

  const [selectedWorkspace, setSelectedWorkspace] = useState<SelectedWorkspace>({
    desk: null, chair: null
  });

  const [loading, setLoading] = useState(true);
  const [buildName, setBuildName] = useState('Моя сборка');
  const [saving, setSaving] = useState(false);
  const [isPublic, setIsPublic] = useState(false);
  const [savedBuilds, setSavedBuilds] = useState<any[]>([]);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [showBuildsModal, setShowBuildsModal] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Состояния для поиска, фильтров и сортировки
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    minPrice: '',
    maxPrice: '',
    manufacturer: '',
    sortBy: 'popular'
  });

  // Загрузка сборки из localStorage при монтировании
  useEffect(() => {
    const savedDraft = localStorage.getItem('buildyourself_draft');
    if (savedDraft) {
      try {
        const data = JSON.parse(savedDraft);
        if (data.pc) setSelectedPC(data.pc);
        if (data.peripherals) setSelectedPeripherals(data.peripherals);
        if (data.workspace) setSelectedWorkspace(data.workspace);
        if (data.buildName) setBuildName(data.buildName);
        if (data.isPublic !== undefined) setIsPublic(data.isPublic);
      } catch (e) {
        console.error('Ошибка загрузки черновика сборки:', e);
      }
    }
  }, []);

  // Сохранение сборки в localStorage при изменениях
  useEffect(() => {
    const draftData = {
      pc: selectedPC,
      peripherals: selectedPeripherals,
      workspace: selectedWorkspace,
      buildName,
      isPublic
    };
    localStorage.setItem('buildyourself_draft', JSON.stringify(draftData));
  }, [selectedPC, selectedPeripherals, selectedWorkspace, buildName, isPublic]);
  const [showFilters, setShowFilters] = useState(false);

  // Загрузка всех компонентов
  useEffect(() => {
    const loadComponents = async () => {
      setLoading(true);
      try {
        // Загружаем PC компоненты
        const [cpuRes, gpuRes, mbRes, ramRes, storageRes, psuRes, caseRes, coolingRes] = await Promise.all([
          computerAPI.getCPUs(),
          computerAPI.getGPUs(),
          computerAPI.getMotherboards(),
          computerAPI.getRAM(),
          computerAPI.getStorage(),
          computerAPI.getPSU(),
          computerAPI.getCases(),
          computerAPI.getCooling(),
        ]);

        // Хелпер для извлечения данных (поддержка с пагинацией и без)
        const extractData = (res: any) => Array.isArray(res.data) ? res.data : (res.data.results || []);

        setCpus(extractData(cpuRes));
        setGpus(extractData(gpuRes));
        setMotherboards(extractData(mbRes));
        setRams(extractData(ramRes));
        setStorages(extractData(storageRes));
        setPsus(extractData(psuRes));
        setCases(extractData(caseRes));
        setCoolings(extractData(coolingRes));

        // Загружаем периферию
        const peripheralPromises = [
          peripheralAPI.getMonitors(),
          peripheralAPI.getKeyboards(),
          peripheralAPI.getMice(),
          peripheralAPI.getHeadsets(),
          peripheralAPI.getWebcams(),
          peripheralAPI.getMicrophones(),
          peripheralAPI.getSpeakers(),
          peripheralAPI.getMousepads(),
          peripheralAPI.getMonitorArms(),
          peripheralAPI.getUSBHubs(),
          peripheralAPI.getLighting(),
          peripheralAPI.getStreamDecks(),
          peripheralAPI.getCaptureCards(),
          peripheralAPI.getGamepads(),
          peripheralAPI.getHeadphoneStands(),
          peripheralAPI.getDesks(),
          peripheralAPI.getChairs(),
        ];

        const results = await Promise.all(peripheralPromises);

        const [
          monitorRes, keyboardRes, mouseRes, headsetRes, webcamRes, micRes,
          speakersRes, mousepadRes, armRes, hubRes, lightRes, deckRes,
          captureRes, gamepadRes, standRes, deskRes, chairRes
        ] = results as any[];

        setMonitors(extractData(monitorRes));
        setKeyboards(extractData(keyboardRes));
        setMice(extractData(mouseRes));
        setHeadsets(extractData(headsetRes));
        setWebcams(extractData(webcamRes));
        setMicrophones(extractData(micRes));
        setSpeakers(extractData(speakersRes));
        setMousepads(extractData(mousepadRes));
        setMonitorArms(extractData(armRes));
        setUsbHubs(extractData(hubRes));
        setLighting(extractData(lightRes));
        setStreamDecks(extractData(deckRes));
        setCaptureCards(extractData(captureRes));
        setGamepads(extractData(gamepadRes));
        setHeadphoneStands(extractData(standRes));
        setDesks(extractData(deskRes));
        setChairs(extractData(chairRes));

      } catch (error) {
        console.error('Ошибка загрузки компонентов:', error);
      } finally {
        setLoading(false);
      }
    };

    loadComponents();
  }, []);

  // Умная фильтрация компонентов по совместимости
  const getCompatibleComponents = useMemo(() => {
    return (key: string): any[] => {
      // Базовые списки компонентов
      const baseComponents: Record<string, any[]> = {
        cpu: cpus, gpu: gpus, motherboard: motherboards, ram: rams,
        storage: storages, storage2: storages, psu: psus, case: cases, cooling: coolings,
        monitor: monitors, monitor2: monitors, keyboard: keyboards, mouse: mice,
        headset: headsets, webcam: webcams, microphone: microphones,
        speakers: speakers, mousepad: mousepads, monitorArm: monitorArms,
        usbHub: usbHubs, lighting: lighting, streamDeck: streamDecks,
        captureCard: captureCards, gamepad: gamepads, headphoneStand: headphoneStands,
        desk: desks, chair: chairs
      };

      let components = [...(baseComponents[key] || [])];

      // Фильтрация материнских плат по выбранному CPU (по сокету)
      if (key === 'motherboard' && selectedPC.cpu) {
        components = components.filter((mb: Motherboard) => mb.socket === selectedPC.cpu!.socket);
      }

      // Фильтрация CPU по выбранной материнской плате (по сокету)
      if (key === 'cpu' && selectedPC.motherboard) {
        components = components.filter((cpu: CPU) => cpu.socket === selectedPC.motherboard!.socket);
      }

      // Фильтрация RAM по типу памяти материнской платы
      if (key === 'ram' && selectedPC.motherboard) {
        components = components.filter((ram: RAM) => ram.memory_type === selectedPC.motherboard!.memory_type);
      }

      // Фильтрация материнских плат по типу выбранной RAM
      if (key === 'motherboard' && selectedPC.ram) {
        components = components.filter((mb: Motherboard) => mb.memory_type === selectedPC.ram!.memory_type);
      }

      // Фильтрация охлаждения по сокету CPU
      if (key === 'cooling' && selectedPC.cpu) {
        components = components.filter((cooling: Cooling) => {
          const socketCompat = cooling.socket_compatibility || '';
          return socketCompat.includes(selectedPC.cpu!.socket);
        });
      }

      // Фильтрация БП по требованиям GPU (рекомендуемая мощность)
      if (key === 'psu' && selectedPC.gpu) {
        const recommendedPsu = selectedPC.gpu.recommended_psu || 0;
        components = components.filter((psu: PSU) => psu.wattage >= recommendedPsu);
      }

      // Фильтрация GPU по мощности выбранного БП
      if (key === 'gpu' && selectedPC.psu) {
        components = components.filter((gpu: GPU) => {
          const recommendedPsu = gpu.recommended_psu || 0;
          return selectedPC.psu!.wattage >= recommendedPsu;
        });
      }

      // Фильтрация корпусов по форм-фактору материнской платы
      if (key === 'case' && selectedPC.motherboard) {
        const mbFormFactor = selectedPC.motherboard.form_factor;
        components = components.filter((c: Case) => {
          // ATX корпус подходит для ATX, Micro-ATX, Mini-ITX
          // Micro-ATX корпус подходит для Micro-ATX, Mini-ITX
          // Mini-ITX корпус только для Mini-ITX
          const caseFF = c.form_factor?.toLowerCase() || '';
          const mbFF = mbFormFactor?.toLowerCase() || '';

          if (caseFF.includes('full') || caseFF.includes('atx')) {
            return true; // Full/ATX корпус подходит всем
          }
          if (caseFF.includes('micro') || caseFF.includes('matx')) {
            return mbFF.includes('micro') || mbFF.includes('matx') || mbFF.includes('mini') || mbFF.includes('itx');
          }
          if (caseFF.includes('mini') || caseFF.includes('itx')) {
            return mbFF.includes('mini') || mbFF.includes('itx');
          }
          return true;
        });
      }

      return components;
    };
  }, [
    cpus, gpus, motherboards, rams, storages, psus, cases, coolings,
    monitors, keyboards, mice, headsets, webcams, microphones,
    speakers, mousepads, monitorArms, usbHubs, lighting, streamDecks,
    captureCards, gamepads, headphoneStands, desks, chairs,
    selectedPC.cpu, selectedPC.motherboard, selectedPC.ram, selectedPC.gpu, selectedPC.psu
  ]);

  // Получение уникальных производителей для текущей категории
  const getManufacturers = useCallback((key: string): string[] => {
    const components = getCompatibleComponents(key);
    const manufacturers = new Set<string>();
    components.forEach((c: any) => {
      if (c.manufacturer) manufacturers.add(c.manufacturer);
    });
    return Array.from(manufacturers).sort();
  }, [getCompatibleComponents]);

  // Применение фильтров и сортировки к компонентам
  const getFilteredComponents = useCallback((key: string): any[] => {
    let components = getCompatibleComponents(key);

    // Поиск по названию
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      components = components.filter((c: any) =>
        c.name?.toLowerCase().includes(searchLower) ||
        c.manufacturer?.toLowerCase().includes(searchLower)
      );
    }

    // Фильтр по производителю
    if (filters.manufacturer) {
      components = components.filter((c: any) => c.manufacturer === filters.manufacturer);
    }

    // Фильтр по минимальной цене
    if (filters.minPrice !== '') {
      components = components.filter((c: any) => parseFloat(String(c.price)) >= Number(filters.minPrice));
    }

    // Фильтр по максимальной цене
    if (filters.maxPrice !== '') {
      components = components.filter((c: any) => parseFloat(String(c.price)) <= Number(filters.maxPrice));
    }

    // Сортировка
    components.sort((a: any, b: any) => {
      switch (filters.sortBy) {
        case 'price-asc':
          return parseFloat(String(a.price)) - parseFloat(String(b.price));
        case 'price-desc':
          return parseFloat(String(b.price)) - parseFloat(String(a.price));
        case 'name-asc':
          return (a.name || '').localeCompare(b.name || '');
        case 'name-desc':
          return (b.name || '').localeCompare(a.name || '');
        case 'popular':
        default:
          // По умолчанию сортировка по рейтингу или ID
          return (b.rating || 0) - (a.rating || 0) || a.id - b.id;
      }
    });

    return components;
  }, [getCompatibleComponents, filters]);

  // Сброс фильтров
  const resetFilters = () => {
    setFilters({
      search: '',
      minPrice: '',
      maxPrice: '',
      manufacturer: '',
      sortBy: 'popular'
    });
  };

  // Получение выбранного компонента для секции
  const getSelectedComponent = (key: string): any => {
    if (key in selectedPC) return selectedPC[key as keyof SelectedComponents];
    if (key in selectedPeripherals) return selectedPeripherals[key as keyof SelectedPeripherals];
    if (key in selectedWorkspace) return selectedWorkspace[key as keyof SelectedWorkspace];
    return null;
  };

  // Выбор компонента
  const selectComponent = (key: string, component: any) => {
    if (key in selectedPC) {
      setSelectedPC(prev => ({ ...prev, [key]: component }));
    } else if (key in selectedPeripherals) {
      setSelectedPeripherals(prev => ({ ...prev, [key]: component }));
    } else if (key in selectedWorkspace) {
      setSelectedWorkspace(prev => ({ ...prev, [key]: component }));
    }
  };

  // Удаление компонента
  const removeComponent = (key: string) => {
    selectComponent(key, null);
  };

  // Расчет общей стоимости
  const totalPrice = useMemo(() => {
    let total = 0;

    // PC компоненты
    Object.values(selectedPC).forEach(component => {
      if (component?.price) {
        total += parseFloat(String(component.price));
      }
    });

    // Периферия
    Object.values(selectedPeripherals).forEach(component => {
      if (component?.price) {
        total += parseFloat(String(component.price));
      }
    });

    // Рабочее место
    Object.values(selectedWorkspace).forEach(component => {
      if (component?.price) {
        total += parseFloat(String(component.price));
      }
    });

    return total;
  }, [selectedPC, selectedPeripherals, selectedWorkspace]);

  // Информация о текущих фильтрах совместимости
  const compatibilityInfo = useMemo(() => {
    const info: string[] = [];

    if (selectedPC.cpu) {
      info.push(`Сокет: ${selectedPC.cpu.socket}`);
    }
    if (selectedPC.motherboard) {
      info.push(`Память: ${selectedPC.motherboard.memory_type}`);
    }
    if (selectedPC.gpu && selectedPC.gpu.recommended_psu) {
      info.push(`Мин. БП: ${selectedPC.gpu.recommended_psu}W`);
    }

    return info;
  }, [selectedPC]);

  // Подсчет выбранных компонентов
  const selectedCount = useMemo(() => {
    let count = 0;
    Object.values(selectedPC).forEach(c => c && count++);
    Object.values(selectedPeripherals).forEach(c => c && count++);
    Object.values(selectedWorkspace).forEach(c => c && count++);
    return count;
  }, [selectedPC, selectedPeripherals, selectedWorkspace]);

  // Показ уведомления
  const showNotification = useCallback((type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 4000);
  }, []);

  // Сохранение сборки
  const saveBuild = async () => {
    if (selectedCount === 0) return;

    setSaving(true);
    try {
      const buildData: BuildRequest = {
        name: buildName,
        is_public: isPublic,
        cpu: selectedPC.cpu?.id || null,
        gpu: selectedPC.gpu?.id || null,
        motherboard: selectedPC.motherboard?.id || null,
        ram: selectedPC.ram?.id || null,
        storage_primary: selectedPC.storage?.id || null,
        storage_secondary: selectedPC.storage2?.id || null,
        psu: selectedPC.psu?.id || null,
        case: selectedPC.case?.id || null,
        cooling: selectedPC.cooling?.id || null,
        monitor_primary: selectedPeripherals.monitor?.id || null,
        monitor_secondary: selectedPeripherals.monitor2?.id || null,
        keyboard: selectedPeripherals.keyboard?.id || null,
        mouse: selectedPeripherals.mouse?.id || null,
        headset: selectedPeripherals.headset?.id || null,
        webcam: selectedPeripherals.webcam?.id || null,
        microphone: selectedPeripherals.microphone?.id || null,
        desk: selectedWorkspace.desk?.id || null,
        chair: selectedWorkspace.chair?.id || null,
        speakers: selectedPeripherals.speakers?.id || null,
        mousepad: selectedPeripherals.mousepad?.id || null,
        monitor_arm: selectedPeripherals.monitorArm?.id || null,
        usb_hub: selectedPeripherals.usbHub?.id || null,
        lighting: selectedPeripherals.lighting?.id || null,
        stream_deck: selectedPeripherals.streamDeck?.id || null,
        capture_card: selectedPeripherals.captureCard?.id || null,
        gamepad: selectedPeripherals.gamepad?.id || null,
        headphone_stand: selectedPeripherals.headphoneStand?.id || null,
      };

      const response = await configurationAPI.saveBuild(buildData);
      showNotification('success', 'Сборка успешно сохранена!');

      // Очищаем черновик после успешного сохранения
      localStorage.removeItem('buildyourself_draft');

      if (response.data.share_url) {
        setShareUrl(window.location.origin + response.data.share_url);
      }

      // Обновляем список сохраненных сборок
      loadSavedBuilds();
    } catch (error: any) {
      console.error('Ошибка сохранения:', error);
      showNotification('error', error.response?.data?.error || 'Ошибка при сохранении сборки');
    } finally {
      setSaving(false);
    }
  };

  // Загрузка сохраненных сборок
  const loadSavedBuilds = async () => {
    try {
      const response = await configurationAPI.getMyBuilds();
      setSavedBuilds(response.data);
    } catch (error) {
      console.error('Ошибка загрузки сборок:', error);
    }
  };

  // Загрузка сборки из сохраненных
  const loadBuild = (build: any) => {
    setBuildName(build.name);

    // Загружаем PC компоненты
    setSelectedPC({
      cpu: build.cpu_detail || null,
      gpu: build.gpu_detail || null,
      motherboard: build.motherboard_detail || null,
      ram: build.ram_detail || null,
      storage: build.storage_primary_detail || null,
      storage2: build.storage_secondary_detail || null,
      psu: build.psu_detail || null,
      case: build.case_detail || null,
      cooling: build.cooling_detail || null,
    });

    // Загружаем периферию если есть workspace
    if (build.workspace) {
      const ws = build.workspace;
      setSelectedPeripherals({
        monitor: ws.monitor_primary_detail || null,
        monitor2: ws.monitor_secondary_detail || null,
        keyboard: ws.keyboard_detail || null,
        mouse: ws.mouse_detail || null,
        headset: ws.headset_detail || null,
        webcam: ws.webcam_detail || null,
        microphone: ws.microphone_detail || null,
        speakers: ws.speakers_detail || null,
        mousepad: ws.mousepad_detail || null,
        monitorArm: ws.monitor_arm_detail || null,
        usbHub: ws.usb_hub_detail || null,
        lighting: ws.lighting_detail || null,
        streamDeck: ws.stream_deck_detail || null,
        captureCard: ws.capture_card_detail || null,
        gamepad: ws.gamepad_detail || null,
        headphoneStand: ws.headphone_stand_detail || null,
      });
      setSelectedWorkspace({
        desk: ws.desk_detail || null,
        chair: ws.chair_detail || null,
      });
    }

    setShowBuildsModal(false);
    showNotification('success', 'Сборка загружена');
  };

  // Копирование ссылки
  const copyShareLink = async () => {
    if (shareUrl) {
      try {
        await navigator.clipboard.writeText(shareUrl);
        showNotification('success', 'Ссылка скопирована!');
      } catch {
        showNotification('error', 'Не удалось скопировать ссылку');
      }
    }
  };

  // Подготовка данных для PDF
  const preparePDFData = (): PDFBuildData => {
    const pcComponents: Component[] = [];
    const peripherals: Component[] = [];
    const workspace: Component[] = [];

    let pcTotal = 0;
    let peripheralsTotal = 0;
    let workspaceTotal = 0;

    // PC компоненты
    Object.entries(selectedPC).forEach(([key, comp]) => {
      if (comp) {
        const price = parseFloat(String(comp.price)) || 0;
        pcTotal += price;
        pcComponents.push({
          label: getComponentLabel(key),
          name: comp.name,
          price,
          manufacturer: comp.manufacturer,
        });
      }
    });

    // Периферия
    Object.entries(selectedPeripherals).forEach(([key, comp]) => {
      if (comp) {
        const price = parseFloat(String(comp.price)) || 0;
        peripheralsTotal += price;
        peripherals.push({
          label: getComponentLabel(key),
          name: comp.name,
          price,
          manufacturer: comp.manufacturer,
        });
      }
    });

    // Рабочее место
    Object.entries(selectedWorkspace).forEach(([key, comp]) => {
      if (comp) {
        const price = parseFloat(String(comp.price)) || 0;
        workspaceTotal += price;
        workspace.push({
          label: getComponentLabel(key),
          name: comp.name,
          price,
          manufacturer: comp.manufacturer,
        });
      }
    });

    return {
      name: buildName,
      pcComponents,
      peripherals,
      workspace,
      pcTotal,
      peripheralsTotal,
      workspaceTotal,
      grandTotal: pcTotal + peripheralsTotal + workspaceTotal,
    };
  };

  // Печать сборки
  const printBuild = () => {
    printDocument(preparePDFData());
  };

  // Сохранение в PDF
  const saveToPDF = async () => {
    try {
      await savePDF(preparePDFData());
      showNotification('success', 'PDF файл сохранён!');
    } catch {
      showNotification('error', 'Ошибка при сохранении PDF');
    }
  };

  // Загружаем сохраненные сборки при монтировании
  useEffect(() => {
    loadSavedBuilds();
  }, []);

  // Рендер карточки компонента
  const renderComponentCard = (component: any, isSelected: boolean, onSelect: () => void, sectionKey: string) => {
    const getComponentSpecs = () => {
      // Разные спеки для разных типов компонентов
      if ('cores' in component) {
        return `${component.cores} ядер, ${component.base_clock} ГГц`;
      }
      if ('memory' in component && 'chipset' in component) {
        return `${component.memory} ГБ, ${component.chipset}`;
      }
      if ('capacity' in component && 'speed' in component) {
        return `${component.capacity} ГБ, ${component.speed} МГц`;
      }
      if ('wattage' in component) {
        return `${component.wattage}W, ${component.efficiency_rating}`;
      }
      if ('refresh_rate' in component) {
        return `${component.screen_size}", ${component.resolution}, ${component.refresh_rate}Гц`;
      }
      if ('dpi' in component) {
        return `${component.dpi} DPI, ${component.wireless ? 'Беспроводная' : 'Проводная'}`;
      }
      if ('switch_type' in component) {
        return `${component.switch_type}, ${component.wireless ? 'Беспроводная' : 'Проводная'}`;
      }
      if ('storage_type' in component) {
        return `${component.capacity} ГБ, ${component.storage_type}`;
      }
      return component.manufacturer;
    };

    return (
      <div
        key={component.id}
        onClick={onSelect}
        className={`p-4 rounded-lg cursor-pointer transition-all duration-200 border-2 ${isSelected
          ? 'border-emerald-500 bg-emerald-500/10'
          : 'border-gray-700 bg-gray-800/50 hover:border-gray-600 hover:bg-gray-800'
          }`}
      >
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <h4 className="font-medium text-white text-sm truncate">{component.name}</h4>
            <p className="text-xs text-gray-400">{component.manufacturer}</p>
          </div>
          {isSelected && (
            <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 ml-2">
              {React.createElement(FiCheck as any, { className: "w-4 h-4 text-white" })}
            </div>
          )}
        </div>
        <p className="text-xs text-gray-500 mb-2">{getComponentSpecs()}</p>
        <p className="text-emerald-400 font-semibold">
          {parseFloat(String(component.price)).toLocaleString('ru-RU')} ₽
        </p>
      </div>
    );
  };

  // Рендер секции компонентов
  const renderSection = (section: ComponentSection, category: ComponentCategory) => {
    const compatibleCount = getCompatibleComponents(section.key).length;
    const filteredComponents = getFilteredComponents(section.key);
    const selected = getSelectedComponent(section.key);
    const isExpanded = expandedSection === section.key;
    const manufacturers = getManufacturers(section.key);

    return (
      <div key={section.key} className="border border-gray-700 rounded-lg overflow-hidden mb-3">
        <button
          onClick={() => setExpandedSection(isExpanded ? null : section.key)}
          className="w-full p-4 flex items-center justify-between bg-gray-800/50 hover:bg-gray-800 transition-colors"
        >
          <div className="flex items-center gap-3">
            {React.createElement(section.icon as any, { className: "w-5 h-5 text-emerald-500" })}
            <span className="font-medium text-white">{section.label}</span>
            {section.required && <span className="text-red-400 text-xs">*</span>}
            <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
              {compatibleCount} шт.
            </span>
          </div>
          <div className="flex items-center gap-3">
            {selected ? (
              <div className="flex items-center gap-2">
                <span className="text-sm text-emerald-400 truncate max-w-[200px]">{selected.name}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeComponent(section.key);
                  }}
                  className="p-1 hover:bg-red-500/20 rounded transition-colors"
                >
                  {React.createElement(FiX as any, { className: "w-4 h-4 text-red-400" })}
                </button>
              </div>
            ) : (
              <span className="text-sm text-gray-500">Не выбрано</span>
            )}
            {isExpanded
              ? React.createElement(FiChevronUp as any, { className: "w-5 h-5 text-gray-400" })
              : React.createElement(FiChevronDown as any, { className: "w-5 h-5 text-gray-400" })
            }
          </div>
        </button>

        {isExpanded && (
          <div className="p-4 bg-gray-900/50">
            {/* Панель поиска и фильтров */}
            <div className="mb-4 space-y-3">
              {/* Поиск */}
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  {React.createElement(FiSearch as any, { className: "w-4 h-4 text-gray-500" })}
                </div>
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  placeholder="Поиск по названию..."
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white text-sm focus:border-emerald-500 focus:outline-none"
                />
              </div>

              {/* Кнопка показа фильтров и сортировка */}
              <div className="flex flex-wrap gap-2 items-center">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${showFilters ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-800 text-gray-400 hover:text-white'
                    }`}
                >
                  {React.createElement(FiFilter as any, { className: "w-4 h-4" })}
                  Фильтры
                </button>

                {/* Сортировка */}
                <select
                  value={filters.sortBy}
                  onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value as SortOption }))}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="popular">По популярности</option>
                  <option value="price-asc">Сначала дешевые</option>
                  <option value="price-desc">Сначала дорогие</option>
                  <option value="name-asc">По названию (А-Я)</option>
                  <option value="name-desc">По названию (Я-А)</option>
                </select>

                {/* Счетчик результатов */}
                <span className="text-xs text-gray-500 ml-auto">
                  Показано: {filteredComponents.length} из {compatibleCount}
                </span>
              </div>

              {/* Расширенные фильтры */}
              {showFilters && (
                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {/* Производитель */}
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Производитель</label>
                      <select
                        value={filters.manufacturer}
                        onChange={(e) => setFilters(prev => ({ ...prev, manufacturer: e.target.value }))}
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
                      >
                        <option value="">Все производители</option>
                        {manufacturers.map(m => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>

                    {/* Мин. цена */}
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Мин. цена (₽)</label>
                      <input
                        type="number"
                        value={filters.minPrice}
                        onChange={(e) => setFilters(prev => ({ ...prev, minPrice: e.target.value ? Number(e.target.value) : '' }))}
                        placeholder="От"
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
                      />
                    </div>

                    {/* Макс. цена */}
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Макс. цена (₽)</label>
                      <input
                        type="number"
                        value={filters.maxPrice}
                        onChange={(e) => setFilters(prev => ({ ...prev, maxPrice: e.target.value ? Number(e.target.value) : '' }))}
                        placeholder="До"
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  <button
                    onClick={resetFilters}
                    className="text-xs text-gray-400 hover:text-white transition-colors"
                  >
                    Сбросить фильтры
                  </button>
                </div>
              )}
            </div>

            {filteredComponents.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                {compatibleCount === 0 ? 'Нет совместимых компонентов' : 'Ничего не найдено по вашим фильтрам'}
              </p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[400px] overflow-y-auto">
                {filteredComponents.map((component: any) =>
                  renderComponentCard(
                    component,
                    selected?.id === component.id,
                    () => selectComponent(section.key, component),
                    section.key
                  )
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen py-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Breadcrumbs Skeleton */}
          <div className="h-4 w-48 bg-gray-800 rounded animate-pulse mb-6"></div>

          {/* Header Skeleton */}
          <div className="mb-8">
            <div className="h-9 w-64 bg-gray-800 rounded animate-pulse mb-2"></div>
            <div className="h-5 w-96 bg-gray-800/50 rounded animate-pulse"></div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main Content Skeleton */}
            <div className="lg:col-span-3">
              {/* Input Skeleton */}
              <div className="h-12 bg-gray-800 rounded-lg animate-pulse mb-6"></div>

              {/* Tabs Skeleton */}
              <div className="flex gap-2 mb-6">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-10 w-32 bg-gray-800 rounded-lg animate-pulse"></div>
                ))}
              </div>

              {/* Sections Skeleton */}
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="border border-gray-700 rounded-lg overflow-hidden mb-3">
                  <div className="p-4 bg-gray-800/50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-5 h-5 bg-gray-700 rounded animate-pulse"></div>
                        <div className="h-5 w-32 bg-gray-700 rounded animate-pulse"></div>
                        <div className="h-4 w-12 bg-gray-700 rounded-full animate-pulse"></div>
                      </div>
                      <div className="h-5 w-24 bg-gray-700 rounded animate-pulse"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Sidebar Skeleton */}
            <div className="lg:col-span-1">
              <div className="sticky top-4 bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <div className="h-6 w-32 bg-gray-700 rounded animate-pulse mb-4"></div>
                <div className="space-y-2 mb-4">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-10 bg-gray-700/50 rounded animate-pulse"></div>
                  ))}
                </div>
                <div className="border-t border-gray-700 pt-4">
                  <div className="h-8 bg-gray-700 rounded animate-pulse mb-4"></div>
                  <div className="h-12 bg-emerald-500/30 rounded-lg animate-pulse mb-2"></div>
                  <div className="h-10 bg-gray-700 rounded-lg animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-2 text-sm mb-6">
          <Link to="/" className="text-gray-400 hover:text-white transition-colors flex items-center gap-1">
            {React.createElement(FiHome as any, { className: "w-4 h-4" })}
            Главная
          </Link>
          {React.createElement(FiChevronRight as any, { className: "w-4 h-4 text-gray-600" })}
          <span className="text-emerald-400">Собери сам</span>
        </nav>

        {/* Заголовок */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            {React.createElement(FiBox as any, { className: "inline w-8 h-8 text-emerald-500 mr-3" })}
            Собери сам
          </h1>
          <p className="text-gray-400">
            Создайте свою идеальную сборку ПК и рабочего места
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Основной контент */}
          <div className="lg:col-span-3">
            {/* Название сборки */}
            <div className="mb-6">
              <input
                type="text"
                value={buildName}
                onChange={(e) => setBuildName(e.target.value)}
                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-emerald-500 focus:outline-none transition-colors"
                placeholder="Название вашей сборки"
              />
            </div>

            {/* Табы категорий */}
            <div className="flex gap-2 mb-6 flex-wrap">
              {[
                { key: 'pc', label: 'Компоненты ПК', icon: FiCpu },
                { key: 'peripherals', label: 'Периферия', icon: FiMonitor },
                { key: 'workspace', label: 'Рабочее место', icon: FiBox },
              ].map(cat => (
                <button
                  key={cat.key}
                  onClick={() => {
                    setActiveCategory(cat.key as ComponentCategory);
                    setExpandedSection(null);
                  }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeCategory === cat.key
                    ? 'bg-emerald-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                >
                  {React.createElement(cat.icon as any, { className: "w-4 h-4" })}
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Секции компонентов */}
            <div>
              {activeCategory === 'pc' && pcSections.map(section => renderSection(section, 'pc'))}
              {activeCategory === 'peripherals' && peripheralSections.map(section => renderSection(section, 'peripherals'))}
              {activeCategory === 'workspace' && workspaceSections.map(section => renderSection(section, 'workspace'))}
            </div>
          </div>

          {/* Боковая панель - сводка */}
          <div className="lg:col-span-1">
            <div className="sticky top-4 bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                {React.createElement(FiShoppingCart as any, { className: "w-5 h-5 text-emerald-500" })}
                Ваша сборка
              </h3>

              {/* Информация о фильтрах совместимости */}
              {compatibilityInfo.length > 0 && (
                <div className="mb-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                  <div className="flex items-center gap-2 text-emerald-400 mb-2">
                    {React.createElement(FiCheck as any, { className: "w-4 h-4" })}
                    <span className="font-medium text-sm">Автофильтр совместимости</span>
                  </div>
                  <ul className="text-xs text-emerald-400/80 space-y-1">
                    {compatibilityInfo.map((info, i) => (
                      <li key={i}>• {info}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Список выбранных компонентов */}
              <div className="space-y-2 mb-4 max-h-[400px] overflow-y-auto">
                {/* PC */}
                {Object.entries(selectedPC).map(([key, component]) => component && (
                  <div key={key} className="flex justify-between items-center text-sm p-2 bg-gray-900/50 rounded">
                    <span className="text-gray-400 truncate flex-1">{component.name}</span>
                    <span className="text-emerald-400 ml-2">{parseFloat(String(component.price)).toLocaleString('ru-RU')} ₽</span>
                  </div>
                ))}

                {/* Периферия */}
                {Object.entries(selectedPeripherals).map(([key, component]) => component && (
                  <div key={key} className="flex justify-between items-center text-sm p-2 bg-gray-900/50 rounded">
                    <span className="text-gray-400 truncate flex-1">{component.name}</span>
                    <span className="text-emerald-400 ml-2">{parseFloat(String(component.price)).toLocaleString('ru-RU')} ₽</span>
                  </div>
                ))}

                {/* Рабочее место */}
                {Object.entries(selectedWorkspace).map(([key, component]) => component && (
                  <div key={key} className="flex justify-between items-center text-sm p-2 bg-gray-900/50 rounded">
                    <span className="text-gray-400 truncate flex-1">{component.name}</span>
                    <span className="text-emerald-400 ml-2">{parseFloat(String(component.price)).toLocaleString('ru-RU')} ₽</span>
                  </div>
                ))}

                {selectedCount === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">
                    Выберите компоненты для сборки
                  </p>
                )}
              </div>

              {/* Итого */}
              <div className="border-t border-gray-700 pt-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Компонентов:</span>
                  <span className="text-white font-medium">{selectedCount}</span>
                </div>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-gray-400">Итого:</span>
                  <span className="text-2xl font-bold text-emerald-400">
                    {totalPrice.toLocaleString('ru-RU')} ₽
                  </span>
                </div>

                {/* Кнопки действий */}
                <div className="space-y-2">
                  {/* Чекбокс публичности */}
                  <label className="flex items-center gap-2 text-sm text-gray-400 mb-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isPublic}
                      onChange={(e) => setIsPublic(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-emerald-500 focus:ring-emerald-500"
                    />
                    Публичная сборка (можно делиться)
                  </label>

                  <button
                    onClick={saveBuild}
                    disabled={selectedCount === 0 || saving}
                    className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {saving ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Сохранение...
                      </>
                    ) : (
                      <>
                        {React.createElement(FiSave as any, { className: "w-4 h-4" })}
                        Сохранить сборку
                      </>
                    )}
                  </button>

                  {/* Кнопки экспорта */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setShowShareModal(true)}
                      disabled={!shareUrl}
                      className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      {React.createElement(FiShare2 as any, { className: "w-4 h-4" })}
                      Поделиться
                    </button>
                    <button
                      onClick={printBuild}
                      disabled={selectedCount === 0}
                      className="flex-1 py-2 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      {React.createElement(FiPrinter as any, { className: "w-4 h-4" })}
                      Печать
                    </button>
                  </div>

                  {/* Кнопка сохранения в PDF */}
                  <button
                    onClick={saveToPDF}
                    disabled={selectedCount === 0}
                    className="w-full py-2 bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-700 hover:to-pink-700 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2"
                  >
                    {React.createElement(FiDownload as any, { className: "w-4 h-4" })}
                    Сохранить PDF
                  </button>

                  {/* Кнопка загрузки сохраненных */}
                  <button
                    onClick={() => setShowBuildsModal(true)}
                    className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {React.createElement(FiList as any, { className: "w-4 h-4" })}
                    Мои сборки ({savedBuilds.length})
                  </button>

                  <button
                    onClick={() => {
                      setSelectedPC({
                        cpu: null, gpu: null, motherboard: null, ram: null,
                        storage: null, storage2: null, psu: null, case: null, cooling: null
                      });
                      setSelectedPeripherals({
                        monitor: null, monitor2: null, keyboard: null, mouse: null,
                        headset: null, webcam: null, microphone: null, speakers: null,
                        mousepad: null, monitorArm: null, usbHub: null, lighting: null,
                        streamDeck: null, captureCard: null, gamepad: null, headphoneStand: null
                      });
                      setSelectedWorkspace({ desk: null, chair: null });
                      setShareUrl(null);
                      setBuildName('Моя сборка');
                      localStorage.removeItem('buildyourself_draft');
                    }}
                    className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {React.createElement(FiTrash2 as any, { className: "w-4 h-4" })}
                    Очистить
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Модальное окно шаринга */}
        {showShareModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-xl p-6 max-w-md w-full border border-gray-700">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  {React.createElement(FiShare2 as any, { className: "w-5 h-5 text-emerald-500" })}
                  Поделиться сборкой
                </h3>
                <button
                  onClick={() => setShowShareModal(false)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {React.createElement(FiX as any, { className: "w-5 h-5 text-gray-400" })}
                </button>
              </div>

              <p className="text-gray-400 text-sm mb-4">
                Скопируйте ссылку и отправьте друзьям или коллегам
              </p>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={shareUrl || ''}
                  readOnly
                  className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-gray-300 text-sm"
                />
                <button
                  onClick={copyShareLink}
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors flex items-center gap-2"
                >
                  {React.createElement(FiCopy as any, { className: "w-4 h-4" })}
                  Копировать
                </button>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    if (shareUrl) window.open(shareUrl, '_blank');
                  }}
                  className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {React.createElement(FiExternalLink as any, { className: "w-4 h-4" })}
                  Открыть
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Модальное окно со списком сборок */}
        {showBuildsModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-hidden border border-gray-700 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  {React.createElement(FiList as any, { className: "w-5 h-5 text-emerald-500" })}
                  Мои сборки
                </h3>
                <button
                  onClick={() => setShowBuildsModal(false)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {React.createElement(FiX as any, { className: "w-5 h-5 text-gray-400" })}
                </button>
              </div>

              <div className="flex-1 overflow-y-auto space-y-3">
                {savedBuilds.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    У вас пока нет сохраненных сборок
                  </p>
                ) : (
                  savedBuilds.map((build) => (
                    <div
                      key={build.id}
                      className="bg-gray-900/50 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium text-white">{build.name}</h4>
                          <p className="text-xs text-gray-500">
                            {new Date(build.created_at).toLocaleDateString('ru-RU')}
                          </p>
                        </div>
                        <span className="text-emerald-400 font-semibold">
                          {parseFloat(build.total_price).toLocaleString('ru-RU')} ₽
                        </span>
                      </div>
                      <div className="flex gap-2 mt-3">
                        <button
                          onClick={() => loadBuild(build)}
                          className="flex-1 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg transition-colors text-sm"
                        >
                          Загрузить
                        </button>
                        {build.share_code && (
                          <button
                            onClick={() => {
                              setShareUrl(window.location.origin + `/build/${build.share_code}`);
                              setShowShareModal(true);
                              setShowBuildsModal(false);
                            }}
                            className="px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors"
                          >
                            {React.createElement(FiLink as any, { className: "w-4 h-4" })}
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Уведомления */}
        {notification && (
          <div className={`fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2 ${notification.type === 'success'
            ? 'bg-emerald-500 text-white'
            : 'bg-red-500 text-white'
            }`}>
            {notification.type === 'success'
              ? React.createElement(FiCheck as any, { className: "w-5 h-5" })
              : React.createElement(FiX as any, { className: "w-5 h-5" })
            }
            {notification.message}
          </div>
        )}
      </div>
    </div>
  );
};

export default BuildYourself;
