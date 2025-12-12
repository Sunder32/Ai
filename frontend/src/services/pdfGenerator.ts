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

const readBlobAsDataUrl = (blob: Blob): Promise<string | null> =>
  new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(typeof reader.result === 'string' ? reader.result : null);
    reader.onerror = () => resolve(null);
    reader.readAsDataURL(blob);
  });

const getCurrentFaviconDataUrl = async (): Promise<string | null> => {
  if (typeof document === 'undefined') return null;

  const link =
    (document.querySelector('link[rel="icon"]') as HTMLLinkElement | null) ||
    (document.querySelector('link[rel="shortcut icon"]') as HTMLLinkElement | null) ||
    (document.querySelector('link[rel="apple-touch-icon"]') as HTMLLinkElement | null);

  const href = link?.href;
  if (!href) return null;

  try {
    const response = await fetch(href, { cache: 'force-cache' });
    if (!response.ok) return null;
    const blob = await response.blob();
    return await readBlobAsDataUrl(blob);
  } catch {
    return null;
  }
};

// Генерация HTML для PDF
const generatePDFHTML = (data: PDFBuildData, brandMarkDataUrl?: string): string => {
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
    brandMarkDataUrl,
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
      specs: c.specs,
      price: c.price,
      manufacturer: c.manufacturer
    })),
    workspace: data.workspace.map(c => ({
      label: c.label,
      name: c.name,
      specs: c.specs,
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
  const brandMarkDataUrl = await getCurrentFaviconDataUrl();
  const container = document.createElement('div');
  container.style.position = 'absolute';
  container.style.left = '-9999px';
  container.style.top = '0';
  container.innerHTML = generatePDFHTML(data, brandMarkDataUrl || undefined);
  document.body.appendChild(container);

  const element = container.querySelector('.document') as HTMLElement;

  const opt = {
    margin: [0, 0, 0, 0] as [number, number, number, number],
    filename: `Сборка_${data.name.replace(/[^a-zA-Zа-яА-Я0-9]/g, '_')}_${new Date().toLocaleDateString('ru-RU').replace(/\./g, '-')}.pdf`,
    image: { type: 'jpeg' as const, quality: 0.97 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      letterRendering: true,
      logging: false,
    },
    jsPDF: {
      unit: 'mm' as const,
      format: 'a4' as const,
      orientation: 'portrait' as const
    },
    pagebreak: { mode: ['css', 'legacy'] }
  };

  try {
    const worker: any = html2pdf().set(opt).from(element).toPdf();
    const pdf: any = await worker.get('pdf');

    if (pdf?.internal?.getNumberOfPages) {
      const totalPages: number = pdf.internal.getNumberOfPages();
      if (totalPages > 1) {
        const detailsPages = totalPages - 1;

        pdf.setFontSize(9);
        pdf.setTextColor(130);

        for (let page = 2; page <= totalPages; page += 1) {
          pdf.setPage(page);
          const pageSize = pdf.internal.pageSize;
          const pageWidth = typeof pageSize.getWidth === 'function' ? pageSize.getWidth() : pageSize.width;
          const pageHeight = typeof pageSize.getHeight === 'function' ? pageSize.getHeight() : pageSize.height;

          const label = `AI PC Configurator  Page ${page - 1}/${detailsPages}`;
          pdf.text(label, pageWidth - 10, pageHeight - 6, { align: 'right' });
        }
      }
    }

    await worker.save();
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
