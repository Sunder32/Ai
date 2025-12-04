// @ts-ignore
import html2pdf from 'html2pdf.js';

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

// Генерация HTML для PDF
const generatePDFHTML = (data: PDFBuildData): string => {
  const currentDate = new Date().toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  const renderComponentRows = (components: Component[], startIndex: number = 1) => {
    return components.map((comp, i) => `
      <tr>
        <td style="width: 35px; text-align: center; color: #666; font-size: 12px; padding: 12px 8px; border-bottom: 1px solid #eee;">
          ${startIndex + i}
        </td>
        <td style="width: 160px; font-weight: 600; color: #10b981; padding: 12px 8px; border-bottom: 1px solid #eee; font-size: 13px;">
          ${comp.label}
        </td>
        <td style="padding: 12px 8px; border-bottom: 1px solid #eee;">
          <div style="font-weight: 500; color: #1a1a1a; font-size: 13px;">${comp.name}</div>
          ${comp.specs ? `<div style="font-size: 11px; color: #888; margin-top: 2px;">${comp.specs}</div>` : ''}
        </td>
        <td style="width: 100px; color: #666; font-size: 12px; padding: 12px 8px; border-bottom: 1px solid #eee;">
          ${comp.manufacturer || '—'}
        </td>
        <td style="width: 110px; text-align: right; font-weight: 600; color: #1a1a1a; padding: 12px 8px; border-bottom: 1px solid #eee; font-size: 13px; white-space: nowrap;">
          ${comp.price.toLocaleString('ru-RU')} ₽
        </td>
      </tr>
    `).join('');
  };

  return `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Спецификация: ${data.name}</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
          font-size: 14px;
          line-height: 1.5;
          color: #1a1a1a;
          background: #fff;
          padding: 0;
        }
        
        .document {
          width: 100%;
          max-width: 800px;
          margin: 0 auto;
          padding: 30px;
          background: #fff;
        }
        
        .header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 25px;
          padding-bottom: 20px;
          border-bottom: 3px solid #10b981;
        }
        
        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .logo-icon {
          width: 45px;
          height: 45px;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 18px;
          font-weight: bold;
        }
        
        .logo-text {
          font-size: 20px;
          font-weight: 700;
          color: #10b981;
        }
        
        .logo-subtitle {
          font-size: 11px;
          color: #888;
          margin-top: 2px;
        }
        
        .doc-info {
          text-align: right;
          font-size: 12px;
          color: #666;
        }
        
        .doc-info .date {
          font-weight: 600;
          color: #333;
          font-size: 13px;
        }
        
        .title-section {
          text-align: center;
          margin-bottom: 30px;
          padding: 20px;
          background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
          border-radius: 12px;
        }
        
        .doc-title {
          font-size: 24px;
          font-weight: 700;
          color: #fff;
          margin-bottom: 8px;
          text-transform: uppercase;
          letter-spacing: 3px;
        }
        
        .build-name {
          font-size: 18px;
          color: #10b981;
          font-weight: 600;
        }
        
        .section {
          margin-bottom: 20px;
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .section-header {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          padding: 12px 16px;
          font-size: 14px;
          font-weight: 600;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .section-total {
          font-size: 14px;
          font-weight: 600;
          background: rgba(255,255,255,0.2);
          padding: 4px 12px;
          border-radius: 20px;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
          background: #fff;
        }
        
        .total-section {
          background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
          color: white;
          padding: 20px 25px;
          border-radius: 12px;
          margin: 25px 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .total-label {
          font-size: 16px;
          font-weight: 500;
        }
        
        .total-amount {
          font-size: 28px;
          font-weight: 700;
          color: #10b981;
        }
        
        .signatures-section {
          margin-top: 40px;
          page-break-inside: avoid;
        }
        
        .signatures-title {
          font-size: 12px;
          font-weight: 600;
          color: #888;
          margin-bottom: 15px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
        
        .signatures-grid {
          display: flex;
          gap: 30px;
        }
        
        .signature-box {
          flex: 1;
          border: 2px solid #e5e5e5;
          border-radius: 10px;
          padding: 18px;
          background: #fafafa;
        }
        
        .signature-role {
          font-size: 11px;
          color: #10b981;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 12px;
        }
        
        .signature-field {
          margin-bottom: 12px;
        }
        
        .signature-field label {
          display: block;
          font-size: 10px;
          color: #999;
          margin-bottom: 4px;
        }
        
        .signature-line {
          border-bottom: 1px solid #ccc;
          height: 25px;
        }
        
        .signature-field.signature .signature-line {
          height: 40px;
        }
        
        .signature-hint {
          font-size: 9px;
          color: #bbb;
          text-align: center;
          margin-top: 4px;
        }
        
        .footer {
          margin-top: 30px;
          padding-top: 15px;
          border-top: 1px solid #eee;
          text-align: center;
          color: #aaa;
          font-size: 10px;
        }
        
        .footer div {
          margin-bottom: 3px;
        }
      </style>
    </head>
    <body>
      <div class="document">
        <!-- Шапка -->
        <div class="header">
          <div class="logo">
            <div class="logo-icon">PC</div>
            <div>
              <div class="logo-text">PC Configurator</div>
              <div class="logo-subtitle">Конфигуратор компьютеров</div>
            </div>
          </div>
          <div class="doc-info">
            <div class="date">${currentDate}</div>
            <div>Документ №${data.id || Date.now().toString().slice(-6)}</div>
            ${data.createdAt ? `<div>Создан: ${new Date(data.createdAt).toLocaleDateString('ru-RU')}</div>` : ''}
          </div>
        </div>
        
        <!-- Заголовок -->
        <div class="title-section">
          <div class="doc-title">Спецификация сборки</div>
          <div class="build-name">${data.name}</div>
        </div>
        
        <!-- Компоненты ПК -->
        ${data.pcComponents.length > 0 ? `
        <div class="section">
          <div class="section-header">
            <span>💻 Компоненты ПК</span>
            <span class="section-total">${data.pcTotal.toLocaleString('ru-RU')} ₽</span>
          </div>
          <table>
            <tbody>
              ${renderComponentRows(data.pcComponents)}
            </tbody>
          </table>
        </div>
        ` : ''}
        
        <!-- Периферия -->
        ${data.peripherals.length > 0 ? `
        <div class="section">
          <div class="section-header">
            <span>🖥️ Периферия</span>
            <span class="section-total">${data.peripheralsTotal.toLocaleString('ru-RU')} ₽</span>
          </div>
          <table>
            <tbody>
              ${renderComponentRows(data.peripherals)}
            </tbody>
          </table>
        </div>
        ` : ''}
        
        <!-- Рабочее место -->
        ${data.workspace.length > 0 ? `
        <div class="section">
          <div class="section-header">
            <span>🪑 Рабочее место</span>
            <span class="section-total">${data.workspaceTotal.toLocaleString('ru-RU')} ₽</span>
          </div>
          <table>
            <tbody>
              ${renderComponentRows(data.workspace)}
            </tbody>
          </table>
        </div>
        ` : ''}
        
        <!-- Итого -->
        <div class="total-section">
          <div class="total-label">Общая стоимость:</div>
          <div class="total-amount">${data.grandTotal.toLocaleString('ru-RU')} ₽</div>
        </div>
        
        <!-- Подписи -->
        <div class="signatures-section">
          <div class="signatures-title">Подписи сторон</div>
          <div class="signatures-grid">
            <div class="signature-box">
              <div class="signature-role">Продавец</div>
              <div class="signature-field">
                <label>ФИО</label>
                <div class="signature-line"></div>
              </div>
              <div class="signature-field">
                <label>Должность</label>
                <div class="signature-line"></div>
              </div>
              <div class="signature-field signature">
                <label>Подпись / Печать</label>
                <div class="signature-line"></div>
                <div class="signature-hint">М.П.</div>
              </div>
            </div>
            
            <div class="signature-box">
              <div class="signature-role">Покупатель</div>
              <div class="signature-field">
                <label>ФИО</label>
                <div class="signature-line"></div>
              </div>
              <div class="signature-field">
                <label>Телефон</label>
                <div class="signature-line"></div>
              </div>
              <div class="signature-field signature">
                <label>Подпись</label>
                <div class="signature-line"></div>
                <div class="signature-hint">Дата: _______________</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Футер -->
        <div class="footer">
          <div>Документ сформирован в системе PC Configurator</div>
          <div>© ${new Date().getFullYear()} PC Configurator</div>
        </div>
      </div>
    </body>
    </html>
  `;
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

// Хелперы для получения лейблов компонентов
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

export type { PDFBuildData, Component };
