import React from 'react';
import { Link } from 'react-router-dom';
import { FiGithub, FiMail, FiMessageSquare } from 'react-icons/fi';
import brandMark from '../assets/brand/mark.svg';

const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-border-dark bg-bg-card">
      <div className="container-main py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand Section */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <img
                src={brandMark}
                alt="AI PC Configurator"
                className="w-8 h-8"
                draggable={false}
              />
              <span className="text-lg font-heading font-semibold text-white">
                AI PC Configurator
              </span>
            </div>
            <p className="text-gray-500 text-sm leading-relaxed">
              Интеллектуальный подбор компьютерных конфигураций с использованием ИИ
            </p>
          </div>
          
          {/* Navigation Section */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
              Навигация
            </h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/" 
                  className="text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  Главная
                </Link>
              </li>
              <li>
                <Link 
                  to="/configurator" 
                  className="text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  Конфигуратор
                </Link>
              </li>
              <li>
                <Link 
                  to="/components" 
                  className="text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  Компоненты
                </Link>
              </li>
              <li>
                <Link 
                  to="/my-configurations" 
                  className="text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  Мои сборки
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Contact Section */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
              Контакты
            </h3>
            <ul className="space-y-3">
              <li>
                <a 
                  href="mailto:support@aipc.ru" 
                  className="flex items-center gap-2 text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  {React.createElement(FiMail as any, { className: "text-lg" })}
                  <span>support@aipc.ru</span>
                </a>
              </li>
              <li>
                <a 
                  href="https://t.me/" 
                  target="_blank"
                  rel="noreferrer noopener"
                  className="flex items-center gap-2 text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  {React.createElement(FiMessageSquare as any, { className: "text-lg" })}
                  <span>Telegram</span>
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/" 
                  target="_blank"
                  rel="noreferrer noopener"
                  className="flex items-center gap-2 text-gray-500 hover:text-primary transition-colors duration-200 text-sm"
                >
                  {React.createElement(FiGithub as any, { className: "text-lg" })}
                  <span>GitHub</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Bottom Bar */}
        <div className="mt-12 pt-6 border-t border-border-dark">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-gray-600 text-sm">
              © 2025 AI PC Configurator. Все права защищены.
            </p>
            <div className="flex items-center gap-6 text-sm">
              <Link to="#" className="text-gray-500 hover:text-primary transition-colors duration-200">
                Политика конфиденциальности
              </Link>
              <Link to="#" className="text-gray-500 hover:text-primary transition-colors duration-200">
                Условия использования
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
