import React from 'react';
import { Link } from 'react-router-dom';
import { FaEnvelope, FaPhone, FaGithub, FaTelegram, FaDiscord } from 'react-icons/fa';

const Footer: React.FC = () => {
  return (
    <footer className="relative mt-16 backdrop-blur-xl bg-white/5 border-t border-white/10">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI PC Configurator
            </h3>
            <p className="text-white/70 leading-relaxed">
              Интеллектуальный подбор конфигураций ПК на основе ваших требований и бюджета.
            </p>
            <div className="flex space-x-4 mt-6">
              <a href="#" className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white/70 hover:text-white transition-all duration-300">
                {React.createElement(FaGithub as any, { className: "text-xl" })}
              </a>
              <a href="#" className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white/70 hover:text-white transition-all duration-300">
                {React.createElement(FaTelegram as any, { className: "text-xl" })}
              </a>
              <a href="#" className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white/70 hover:text-white transition-all duration-300">
                {React.createElement(FaDiscord as any, { className: "text-xl" })}
              </a>
            </div>
          </div>
          <div>
            <h3 className="text-xl font-bold mb-4 text-white">Навигация</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/" className="text-white/70 hover:text-white transition-colors duration-300 flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  <span>Главная</span>
                </Link>
              </li>
              <li>
                <Link to="/configurator" className="text-white/70 hover:text-white transition-colors duration-300 flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                  <span>Конфигуратор</span>
                </Link>
              </li>
              <li>
                <Link to="/components" className="text-white/70 hover:text-white transition-colors duration-300 flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-pink-400"></span>
                  <span>Каталог компонентов</span>
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-xl font-bold mb-4 text-white">Контакты</h3>
            <div className="space-y-3">
              <p className="flex items-center space-x-3 text-white/70">
                {React.createElement(FaEnvelope as any, { className: "text-blue-400" })}
                <span>support@aipc.ru</span>
              </p>
              <p className="flex items-center space-x-3 text-white/70">
                {React.createElement(FaPhone as any, { className: "text-purple-400" })}
                <span>+7 (999) 123-45-67</span>
              </p>
            </div>
          </div>
        </div>
        <div className="border-t border-white/10 mt-8 pt-8 text-center text-white/50">
          <p>&copy; 2025 AI PC Configurator. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
