
interface PDFData {
    name: string;
    id?: number;
    date: string;
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
    }[];
    workspace: {
        label: string;
        name: string;
        price: number;
    }[];
    totals: {
        pc: number;
        peripherals: number;
        workspace: number;
        grand: number;
    };
}

export const getPDFTemplate = (data: PDFData): string => {
    return `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Сборка ${data.name}</title>
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
          font-family: 'Inter', sans-serif;
          font-size: 12px;
          line-height: 1.5;
          color: #1f2937;
          background: #fff;
        }

        .document {
          max-width: 800px;
          margin: 0 auto;
          padding: 40px;
        }

        /* Header */
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 40px;
          padding-bottom: 20px;
          border-bottom: 2px solid #10b981;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .brand-logo {
          width: 40px;
          height: 40px;
          background: #10b981;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #0a0a0a;
          font-weight: bold;
          font-size: 20px;
        }

        .brand-text h1 {
          font-size: 20px;
          font-weight: 700;
          color: #111827;
          line-height: 1.2;
        }

        .brand-text p {
          font-size: 12px;
          color: #6b7280;
        }

        .meta {
          text-align: right;
        }

        .meta-date {
          font-weight: 600;
          color: #374151;
        }

        .meta-id {
          font-size: 12px;
          color: #9ca3af;
          margin-top: 4px;
        }

        /* Summary Grid */
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 15px;
          margin-bottom: 30px;
          background: #f0fdf4;
          padding: 20px;
          border-radius: 12px;
          border: 1px solid #dcfce7;
        }

        .summary-item h3 {
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #15803d;
          margin-bottom: 6px;
        }

        .summary-item p {
          font-weight: 600;
          color: #111827;
          font-size: 13px;
        }

        .summary-item.price p {
          color: #10b981;
          font-size: 16px;
        }

        /* Section */
        .section {
          margin-bottom: 30px;
        }

        .section-title {
          font-size: 14px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 15px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-left: 4px solid #10b981;
          padding-left: 10px;
        }

        .section-total {
          font-size: 12px;
          font-weight: 600;
          color: #15803d;
          background: #dcfce7;
          padding: 4px 8px;
          border-radius: 6px;
        }

        /* Table */
        table {
          width: 100%;
          border-collapse: collapse;
        }

        th {
          text-align: left;
          font-size: 10px;
          text-transform: uppercase;
          color: #6b7280;
          padding: 10px 0;
          border-bottom: 1px solid #e5e7eb;
          font-weight: 600;
        }

        td {
          padding: 12px 0;
          border-bottom: 1px solid #f3f4f6;
          vertical-align: top;
        }

        .col-index { width: 30px; color: #9ca3af; font-size: 11px; padding-top: 14px; }
        .col-name { padding-right: 20px; }
        .col-type { width: 120px; color: #6b7280; font-size: 11px; padding-top: 14px; }
        .col-price { width: 100px; text-align: right; font-weight: 600; color: #1f2937; padding-top: 14px; }

        .item-name {
          font-weight: 500;
          color: #111827;
          margin-bottom: 2px;
          font-size: 13px;
        }

        .item-specs {
          font-size: 11px;
          color: #6b7280;
        }

        /* Grand Total */
        .grand-total {
          background: #0a0a0a;
          color: white;
          padding: 24px;
          border-radius: 12px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 40px;
          page-break-inside: avoid;
        }

        .total-label {
          font-size: 16px;
          font-weight: 500;
        }

        .total-value {
          font-size: 24px;
          font-weight: 700;
          color: #10b981;
        }

        /* Footer */
        .footer {
          margin-top: 60px;
          border-top: 1px solid #e5e7eb;
          padding-top: 20px;
          text-align: center;
          font-size: 11px;
          color: #9ca3af;
        }
      </style>
    </head>
    <body>
      <div class="document">
        <!-- Header -->
        <div class="header">
          <div class="brand">
            <div class="brand-logo">AI</div>
            <div class="brand-text">
              <h1>PC Configurator</h1>
              <p>AI Powered Builds</p>
            </div>
          </div>
          <div class="meta">
            <div class="meta-date">${data.date}</div>
            <div class="meta-id">Build #${data.id || 'Custom'}</div>
          </div>
        </div>

        <!-- Summary Grid -->
        <div class="summary-grid">
          <div class="summary-item">
            <h3>Процессор</h3>
            <p>${data.pcComponents.find(c => c.label === 'Процессор')?.name?.split(' ').slice(0, 2).join(' ') || '-'}</p>
          </div>
          <div class="summary-item">
            <h3>Видеокарта</h3>
            <p>${data.pcComponents.find(c => c.label === 'Видеокарта')?.name?.split(' ').slice(0, 2).join(' ') || '-'}</p>
          </div>
          <div class="summary-item">
            <h3>ОЗУ</h3>
            <p>${data.pcComponents.find(c => c.label.includes('память'))?.specs || '-'}</p>
          </div>
          <div class="summary-item price">
            <h3>Итого</h3>
            <p>${data.totals.grand.toLocaleString('ru-RU')} ₽</p>
          </div>
        </div>

        <!-- PC Components -->
        <div class="section">
          <div class="section-title">
            <span>Комплектующие</span>
            <span class="section-total">${data.totals.pc.toLocaleString('ru-RU')} ₽</span>
          </div>
          <table>
            <thead>
              <tr>
                <th class="col-index">#</th>
                <th class="col-name">Компонент</th>
                <th class="col-type">Тип</th>
                <th class="col-price">Цена</th>
              </tr>
            </thead>
            <tbody>
              ${data.pcComponents.map((comp, i) => `
                <tr>
                  <td class="col-index">${i + 1}</td>
                  <td class="col-name">
                    <div class="item-name">${comp.name}</div>
                    ${comp.specs ? `<div class="item-specs">${comp.specs}</div>` : ''}
                  </td>
                  <td class="col-type">${comp.label}</td>
                  <td class="col-price">${comp.price.toLocaleString('ru-RU')} ₽</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Peripherals -->
        ${data.peripherals.length > 0 ? `
          <div class="section">
            <div class="section-title">
              <span>Периферия</span>
              <span class="section-total">${data.totals.peripherals.toLocaleString('ru-RU')} ₽</span>
            </div>
            <table>
              <tbody>
                ${data.peripherals.map((comp, i) => `
                  <tr>
                    <td class="col-index">${i + 1}</td>
                    <td class="col-name">
                      <div class="item-name">${comp.name}</div>
                    </td>
                    <td class="col-type">${comp.label}</td>
                    <td class="col-price">${comp.price.toLocaleString('ru-RU')} ₽</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : ''}

        <!-- Workspace -->
        ${data.workspace.length > 0 ? `
          <div class="section">
            <div class="section-title">
              <span>Рабочее место</span>
              <span class="section-total">${data.totals.workspace.toLocaleString('ru-RU')} ₽</span>
            </div>
            <table>
              <tbody>
                ${data.workspace.map((comp, i) => `
                  <tr>
                    <td class="col-index">${i + 1}</td>
                    <td class="col-name">
                      <div class="item-name">${comp.name}</div>
                    </td>
                    <td class="col-type">${comp.label}</td>
                    <td class="col-price">${comp.price.toLocaleString('ru-RU')} ₽</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : ''}

        <!-- Grand Total -->
        <div class="grand-total">
          <div class="total-label">Итоговая стоимость</div>
          <div class="total-value">${data.totals.grand.toLocaleString('ru-RU')} ₽</div>
        </div>

        <!-- Footer -->
        <div class="footer">
          <p>© ${new Date().getFullYear()} PC Configurator. Цены являются ориентировочными и могут изменяться.</p>
        </div>
      </div>
    </body>
    </html>
  `;
};
