interface PDFData {
  name: string;
  id?: number;
  date: string;
  createdAt?: string;
  brandMarkDataUrl?: string;
  pcComponents: {
    label: string;
    name: string;
    specs?: string;
    price: number;
    manufacturer?: string;
  }[];
  peripherals: {
    label: string;
    name: string;
    price: number;
    manufacturer?: string;
    specs?: string;
  }[];
  workspace: {
    label: string;
    name: string;
    price: number;
    manufacturer?: string;
    specs?: string;
  }[];
  totals: {
    pc: number;
    peripherals: number;
    workspace: number;
    grand: number;
  };
}

const BRAND_MARK_SVG = `
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AI PC Configurator">
  <defs>
    <linearGradient id="brandGradient" x1="10" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
      <stop stop-color="#10b981" />
      <stop offset="1" stop-color="#34d399" />
    </linearGradient>
  </defs>
  <path d="M12 8H42L56 22V56H12V8Z" fill="url(#brandGradient)" />
  <path d="M42 8V22H56" fill="#000000" opacity="0.1" />
  <path d="M12 8H42L56 22V56H12V8Z" stroke="#064e3b" stroke-width="2" />
  <path d="M22 44L32 20L42 44" stroke="#0a0a0a" stroke-width="6" stroke-linecap="square" stroke-linejoin="miter" />
  <path d="M26 34H38" stroke="#0a0a0a" stroke-width="6" stroke-linecap="square" />
  <path d="M48 20V44" stroke="#0a0a0a" stroke-width="6" stroke-linecap="square" />
  <circle cx="48" cy="44" r="3" fill="#0a0a0a" />
</svg>
`.trim();

const escapeHtml = (value: string): string =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

const escapeHtmlAttr = (value: string): string => escapeHtml(value);

const safeNumber = (value: unknown): number => {
  const num = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(num) ? num : 0;
};

const money = (value: number): string => `${safeNumber(value).toLocaleString('ru-RU')} ₽`;

const shortText = (value: string | undefined, max = 46): string => {
  const text = (value ?? '').trim();
  if (!text) return '—';
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
};

const formatMaybeDateTime = (value?: string): string | null => {
  if (!value) return null;
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) return escapeHtml(String(value));
  return escapeHtml(dt.toLocaleString('ru-RU'));
};

const findByLabel = (items: PDFData['pcComponents'], label: string) =>
  items.find((c) => (c.label || '').toLowerCase() === label.toLowerCase());

const renderTable = (
  title: string,
  subtitle: string,
  totalLabel: string,
  items: Array<{ label: string; name: string; manufacturer?: string; specs?: string; price: number }>
): string => {
  const rows = items
    .map((item, index) => {
      const name = escapeHtml(item.name || '—');
      const type = escapeHtml(item.label || '—');
      const manufacturer = escapeHtml(item.manufacturer || '—');
      const specs = escapeHtml(item.specs || '—');
      const price = money(item.price);

      return `
        <tr>
          <td class="col-index">${index + 1}</td>
          <td class="col-name">
            <div class="item-name">${name}</div>
            <div class="item-sub">${manufacturer}</div>
          </td>
          <td class="col-type">${type}</td>
          <td class="col-specs">${specs}</td>
          <td class="col-price">${price}</td>
        </tr>
      `;
    })
    .join('');

  return `
    <div class="section">
      <div class="section-head">
        <div>
          <div class="section-title">${escapeHtml(title)}</div>
          <div class="section-sub">${escapeHtml(subtitle)}</div>
        </div>
        <div class="section-total">${escapeHtml(totalLabel)}</div>
      </div>

      <table class="table">
        <thead>
          <tr>
            <th class="col-index">#</th>
            <th class="col-name">Наименование</th>
            <th class="col-type">Тип</th>
            <th class="col-specs">Характеристики</th>
            <th class="col-price">Цена</th>
          </tr>
        </thead>
        <tbody>
          ${rows || `<tr><td class="empty" colspan="5">Нет данных</td></tr>`}
        </tbody>
      </table>
    </div>
  `;
};

const renderPageHeader = (buildName: string, metaRight: string, markHtml: string): string => `
  <div class="page-header">
    <div class="header-left">
      <div class="mark">${markHtml}</div>
      <div>
        <div class="brand">AI PC Configurator</div>
        <div class="header-title">${escapeHtml(buildName)}</div>
      </div>
    </div>
    <div class="header-meta">${metaRight}</div>
  </div>
`;

export const getPDFTemplate = (data: PDFData): string => {
  const buildName = data.name || 'Сборка';
  const buildId = data.id ?? null;
  const markHtml = data.brandMarkDataUrl
    ? `<img class="mark-img" src="${escapeHtmlAttr(data.brandMarkDataUrl)}" alt="AI PC Configurator" />`
    : BRAND_MARK_SVG;

  const cpu = findByLabel(data.pcComponents, 'Процессор');
  const gpu = findByLabel(data.pcComponents, 'Видеокарта');
  const ram = data.pcComponents.find((c) => (c.label || '').toLowerCase().includes('память'));
  const storagePrimary =
    findByLabel(data.pcComponents, 'Накопитель (основной)') ||
    data.pcComponents.find((c) => /накоп/i.test(c.label || '') && /осн/i.test(c.label || '')) ||
    data.pcComponents.find((c) => /storage/i.test(c.label || '') && /primary/i.test(c.label || ''));
  const storageSecondary =
    findByLabel(data.pcComponents, 'Накопитель (доп.)') ||
    findByLabel(data.pcComponents, 'Накопитель (дополнительный)');

  const metaRight = `
    <div class="meta">
      <div class="meta-row"><span>Дата</span><strong>${escapeHtml(data.date)}</strong></div>
      <div class="meta-row"><span>Сборка</span><strong>${buildId ? `#${buildId}` : 'Custom'}</strong></div>
    </div>
  `;

  const coverTotals = `
    <div class="card">
      <div class="card-title">Итоговая стоимость</div>
      <div class="grand">${money(data.totals.grand)}</div>
      <div class="divider"></div>
      <div class="kv">
        <div class="kv-row"><span>Комплектующие</span><strong>${money(data.totals.pc)}</strong></div>
        <div class="kv-row"><span>Периферия</span><strong>${money(data.totals.peripherals)}</strong></div>
        <div class="kv-row"><span>Рабочее место</span><strong>${money(data.totals.workspace)}</strong></div>
      </div>
    </div>
  `;

  const coverHighlights = `
    <div class="card">
      <div class="card-title">Ключевые компоненты</div>
      <div class="kv">
        <div class="kv-row"><span>CPU</span><strong>${escapeHtml(shortText(cpu?.name, 44))}</strong></div>
        <div class="kv-row"><span>GPU</span><strong>${escapeHtml(shortText(gpu?.name, 44))}</strong></div>
        <div class="kv-row"><span>RAM</span><strong>${escapeHtml(shortText(ram?.specs || ram?.name, 44))}</strong></div>
        <div class="kv-row"><span>SSD/HDD</span><strong>${escapeHtml(shortText(storagePrimary?.name, 44))}</strong></div>
        ${storageSecondary ? `<div class="kv-row"><span>Доп. диск</span><strong>${escapeHtml(shortText(storageSecondary?.name, 44))}</strong></div>` : ''}
      </div>
      <div class="note">
        Полные спецификации находятся на следующих страницах.
      </div>
    </div>
  `;

  const cover = `
    <section class="page cover">
      <div class="cover-top">
        ${renderPageHeader(buildName, metaRight, markHtml)}
      </div>

      <div class="cover-center">
        <div class="doc-kind">Официальный отчет</div>
        <h1 class="doc-title">Сборка ПК</h1>
        <div class="doc-name">${escapeHtml(buildName)}</div>
        ${formatMaybeDateTime(data.createdAt) ? `<div class="doc-created">Создано: ${formatMaybeDateTime(data.createdAt)}</div>` : ''}
      </div>

      <div class="cover-grid">
        ${coverTotals}
        ${coverHighlights}
      </div>

      <div class="cover-bottom">
        <div class="fineprint">
          Цены являются ориентировочными и могут изменяться. Отчет сформирован автоматически сервисом AI PC Configurator.
        </div>
      </div>
    </section>
  `;

  const pcPage = `
    <section class="page">
      ${renderPageHeader(buildName, metaRight, markHtml)}
      ${renderTable(
        'Комплектующие ПК',
        'Подробная спецификация выбранных компонентов.',
        money(data.totals.pc),
        data.pcComponents
      )}
    </section>
  `;

  const peripheralsPage = data.peripherals.length
    ? `
      <section class="page">
        ${renderPageHeader(buildName, metaRight, markHtml)}
        ${renderTable(
          'Периферия',
          'Устройства ввода/вывода и аксессуары.',
          money(data.totals.peripherals),
          data.peripherals
        )}
      </section>
    `
    : '';

  const workspacePage = data.workspace.length
    ? `
      <section class="page">
        ${renderPageHeader(buildName, metaRight, markHtml)}
        ${renderTable(
          'Рабочее место',
          'Стол, кресло и дополнительные элементы.',
          money(data.totals.workspace),
          data.workspace
        )}
      </section>
    `
    : '';

  return `
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <title>Сборка ${escapeHtml(buildName)}</title>
    <style>
      :root {
        --ink: #111827;
        --muted: #6b7280;
        --border: #e5e7eb;
        --surface: #ffffff;
        --surface-2: #f9fafb;
        --accent: #10b981;
        --accent-2: #34d399;
        --shadow: 0 10px 30px rgba(17, 24, 39, 0.08);
      }

      * { box-sizing: border-box; }
      html, body { height: 100%; }

      body {
        margin: 0;
        background: var(--surface);
        color: var(--ink);
        font-family: Inter, "Segoe UI", Arial, sans-serif;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }

      .document { width: 100%; }

      .page {
        padding: 16mm 14mm 14mm;
        page-break-after: always;
      }
      .page:last-child { page-break-after: auto; }

      /* Header (each page) */
      .page-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        padding-bottom: 6mm;
        border-bottom: 2px solid var(--accent);
        margin-bottom: 8mm;
      }

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
      }

      .mark { width: 44px; height: 44px; flex: 0 0 auto; }
      .mark svg { width: 44px; height: 44px; display: block; }
      .mark-img { width: 44px; height: 44px; display: block; }

      .brand {
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
        font-size: 16px;
      }

      .header-title {
        font-size: 12px;
        color: var(--muted);
        margin-top: 2px;
        max-width: 420px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .header-meta { text-align: right; }
      .meta { display: grid; gap: 4px; }
      .meta-row { display: flex; gap: 8px; justify-content: flex-end; }
      .meta-row span { color: var(--muted); font-size: 11px; }
      .meta-row strong { font-size: 11px; }

      /* Cover page */
      .cover { padding-top: 22mm; }
      .cover {
        padding-top: 18mm;
        display: flex;
        flex-direction: column;
      }
      .cover-top { margin-bottom: 0; }

      .cover-center {
        text-align: center;
        margin: 10mm 0 8mm;
      }

      .doc-kind {
        display: inline-block;
        padding: 6px 10px;
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        background: var(--surface-2);
        color: var(--muted);
        font-size: 11px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }

      .doc-title {
        margin: 14px 0 6px;
        font-size: 34px;
        letter-spacing: -0.03em;
        line-height: 1.1;
      }

      .doc-name {
        margin: 0 auto;
        max-width: 640px;
        font-size: 16px;
        color: var(--muted);
      }

      .doc-created {
        margin-top: 8px;
        font-size: 11px;
        color: var(--muted);
      }

      .cover-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-top: 0;
      }

      .card {
        border: 1px solid var(--border);
        background: var(--surface);
        box-shadow: var(--shadow);
        padding: 14px;
      }

      .card-title {
        font-size: 11px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 10px;
      }

      .grand {
        font-size: 26px;
        font-weight: 900;
        letter-spacing: -0.02em;
        color: var(--accent);
      }

      .divider {
        height: 1px;
        background: var(--border);
        margin: 12px 0;
      }

      .kv { display: grid; gap: 8px; }
      .kv-row { display: flex; justify-content: space-between; gap: 10px; }
      .kv-row span { color: var(--muted); font-size: 12px; }
      .kv-row strong { text-align: right; font-size: 12px; max-width: 340px; }

      .note {
        margin-top: 12px;
        font-size: 11px;
        color: var(--muted);
        border-top: 1px dashed var(--border);
        padding-top: 10px;
      }

      .cover-bottom {
        margin-top: auto;
        padding-top: 6mm;
        border-top: 1px solid var(--border);
      }

      .fineprint {
        font-size: 10px;
        color: var(--muted);
        text-align: center;
      }

      /* Sections */
      .section { margin-top: 0; }

      .section-head {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 14px;
        margin-bottom: 10px;
      }

      .section-title {
        font-size: 16px;
        font-weight: 800;
        letter-spacing: -0.02em;
      }

      .section-sub {
        font-size: 11px;
        color: var(--muted);
        margin-top: 3px;
      }

      .section-total {
        font-size: 12px;
        font-weight: 800;
        color: var(--ink);
        background: #ecfdf5;
        border: 1px solid #bbf7d0;
        padding: 6px 10px;
      }

      /* Table */
      .table {
        width: 100%;
        border-collapse: collapse;
        border: 1px solid var(--border);
      }

      .table thead th {
        background: var(--surface-2);
        color: var(--muted);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 10px 10px;
        border-bottom: 1px solid var(--border);
        text-align: left;
      }

      .table tbody td {
        padding: 10px 10px;
        border-bottom: 1px solid var(--border);
        vertical-align: top;
        font-size: 11px;
      }

      .table tbody tr:nth-child(even) td { background: #fcfcfd; }

      .col-index { width: 34px; color: var(--muted); text-align: right; }
      .col-type { width: 120px; color: var(--muted); }
      .col-specs { width: 210px; color: var(--muted); }
      .col-price { width: 110px; text-align: right; font-weight: 800; }

      .item-name { font-weight: 700; color: var(--ink); }
      .item-sub { color: var(--muted); font-size: 10px; margin-top: 3px; }

      .empty {
        text-align: center;
        color: var(--muted);
        padding: 18px 10px;
      }

      /* Page-break safety */
      tr { page-break-inside: avoid; break-inside: avoid; }
      .card { page-break-inside: avoid; break-inside: avoid; }
      .section-head { page-break-after: avoid; break-after: avoid; }
    </style>
  </head>
  <body>
    <div class="document">
      ${cover}
      ${pcPage}
      ${peripheralsPage}
      ${workspacePage}
    </div>
  </body>
</html>
  `.trim();
};
