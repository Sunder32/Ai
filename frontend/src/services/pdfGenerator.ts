// @ts-ignore
import html2pdf from 'html2pdf.js';
import { getPDFTemplate } from './pdfTemplate';

interface Component {
  label: string;
  name: string;
  price: number;
  manufacturer?: string;
  specs?: string;
}

interface PDFBuildData {
  name: string;
  id?: number;
  createdAt?: string;
  pcComponents: Component[];
  peripherals: Component[];
  workspace: Component[];
  pcTotal: number;
  peripheralsTotal: number;
  workspaceTotal: number;
  grandTotal: number;
}



// Хелпер для получения лейблов компонентов
export const componentLabels: Record<string, string> = {
  cpu: 'Процессор',
  gpu: 'Видеокарта',
  motherboard: 'Материнская плата',
  ram: 'Оперативная память',
  storage: 'Накопитель (основной)',
  storage2: 'Накопитель (доп.)',
  storage_primary: 'Накопитель (основной)',
  storage_secondary: 'Накопитель (доп.)',
  psu: 'Блок питания',
  case: 'Корпус',
  cooling: 'Охлаждение',
  monitor: 'Монитор (основной)',
  monitor2: 'Монитор (доп.)',
  monitor_primary: 'Монитор (основной)',
  monitor_secondary: 'Монитор (доп.)',
  keyboard: 'Клавиатура',
  mouse: 'Мышь',
  headset: 'Наушники',
  speakers: 'Колонки',
  mousepad: 'Коврик',
  webcam: 'Веб-камера',
  microphone: 'Микрофон',
  monitorArm: 'Кронштейн',
  monitor_arm: 'Кронштейн',
  usbHub: 'USB-хаб',
  usb_hub: 'USB-хаб',
  lighting: 'Освещение',
  streamDeck: 'Стрим-пульт',
  stream_deck: 'Стрим-пульт',
  captureCard: 'Карта захвата',
  capture_card: 'Карта захвата',
  gamepad: 'Геймпад',
  headphoneStand: 'Подставка наушников',
  headphone_stand: 'Подставка наушников',
  desk: 'Стол',
  chair: 'Кресло',
};

export const getComponentLabel = (key: string): string => {
  return componentLabels[key] || key;
};

// Генерация HTML для PDF
const generatePDFHTML = (data: PDFBuildData): string => {
  const currentDate = new Date().toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  // Подготовка данных для шаблона
  const templateData = {
    name: data.name,
    id: data.id,
    date: currentDate,
    createdAt: data.createdAt,
    pcComponents: data.pcComponents.map(c => ({
      label: c.label,
      name: c.name,
      specs: c.specs,
      price: c.price,
      manufacturer: c.manufacturer
    })),
    peripherals: data.peripherals.map(c => ({
      label: c.label,
      name: c.name,
      price: c.price,
      manufacturer: c.manufacturer
    })),
    workspace: data.workspace.map(c => ({
      label: c.label,
      name: c.name,
      price: c.price
    })),
    totals: {
      pc: data.pcTotal,
      peripherals: data.peripheralsTotal,
      workspace: data.workspaceTotal,
      grand: data.grandTotal
    }
  };

  return getPDFTemplate(templateData);
};

// Сохранение в PDF
export const saveToPDF = async (data: PDFBuildData): Promise<void> => {
  const container = document.createElement('div');
  container.style.position = 'absolute';
  container.style.left = '-9999px';
  container.style.top = '0';
  container.innerHTML = generatePDFHTML(data);
  document.body.appendChild(container);

  const element = container.querySelector('.document') as HTMLElement;

  const opt = {
    margin: [5, 5, 5, 5] as [number, number, number, number],
    filename: `Сборка_${data.name.replace(/[^a-zA-Zа-яА-Я0-9]/g, '_')}_${new Date().toLocaleDateString('ru-RU').replace(/\./g, '-')}.pdf`,
    image: { type: 'jpeg' as const, quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      letterRendering: true,
      logging: false,
    },
    jsPDF: {
      unit: 'mm' as const,
      format: 'a4' as const,
      orientation: 'portrait' as const
    },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
  };

  try {
    await html2pdf().set(opt).from(element).save();
  } finally {
    document.body.removeChild(container);
  }
};

// Печать документа
export const printDocument = (data: PDFBuildData): void => {
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(generatePDFHTML(data));
    printWindow.document.close();
    setTimeout(() => {
      printWindow.print();
    }, 300);
  }
};



export type { PDFBuildData, Component };
