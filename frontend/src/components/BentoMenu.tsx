import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiSettings, FiCpu, FiList } from 'react-icons/fi';

interface MenuItem {
  path: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}

const menuItems: MenuItem[] = [
  {
    path: '/',
    icon: React.createElement(FiHome as any, { className: "text-xl" }),
    title: 'Главная',
    description: 'Начните здесь'
  },
  {
    path: '/configurator',
    icon: React.createElement(FiSettings as any, { className: "text-xl" }),
    title: 'Конфигуратор',
    description: 'Создайте сборку'
  },
  {
    path: '/components',
    icon: React.createElement(FiCpu as any, { className: "text-xl" }),
    title: 'Компоненты',
    description: 'Каталог деталей'
  },
  {
    path: '/my-configurations',
    icon: React.createElement(FiList as any, { className: "text-xl" }),
    title: 'Мои сборки',
    description: 'Сохраненные конфиги'
  }
];

const BentoMenu: React.FC = () => {
  const location = useLocation();

  return (
    <div className="grid grid-cols-2 gap-4 p-4">
      {menuItems.map((item) => {
        const isActive = location.pathname === item.path;
        
        return (
          <Link
            key={item.path}
            to={item.path}
            className={`card-accent p-5 group ${isActive ? 'border-primary bg-primary/5' : ''}`}
          >
            <div className={`w-10 h-10 flex items-center justify-center bg-bg-surface mb-3 
              group-hover:bg-primary/10 transition-colors duration-200 ${isActive ? 'text-primary' : 'text-gray-400 group-hover:text-primary'}`}>
              {item.icon}
            </div>
            <h3 className="text-base font-heading font-semibold text-white mb-1">
              {item.title}
            </h3>
            <p className="text-sm text-gray-500">
              {item.description}
            </p>
          </Link>
        );
      })}
    </div>
  );
};

export default BentoMenu;
