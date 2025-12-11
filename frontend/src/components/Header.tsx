import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiSettings, FiCpu, FiList, FiUser, FiMenu, FiX, FiTool } from 'react-icons/fi';

const Header: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const user = localStorage.getItem('user');
      setIsAuthenticated(!!token);
      if (user) {
        try {
          const userData = JSON.parse(user);
          setUsername(userData.username || '');
        } catch {
          setUsername('');
        }
      }
    };

    checkAuth();
    // Проверяем при изменении маршрута
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, [location]);

  const navItems = [
    { label: 'Главная', href: '/', icon: FiHome },
    { label: 'AI Конфигуратор', href: '/configurator', icon: FiSettings },
    { label: 'Собери сам', href: '/build-yourself', icon: FiTool },
    { label: 'Мои сборки', href: '/my-configurations', icon: FiList },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="header">
      <div className="container-main h-full">
        <div className="flex items-center justify-between h-full">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 flex items-center justify-center bg-primary transition-all duration-200 group-hover:shadow-glow">
              <span className="text-lg font-heading font-bold text-white">AI</span>
            </div>
            <div className="hidden sm:flex flex-col">
              <span className="text-lg font-heading font-semibold text-white">
                PC Configurator
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all duration-200 ${active ? 'text-primary' : 'text-gray-400 hover:text-primary'
                    }`}
                >
                  {React.createElement(item.icon as any, { className: "text-lg" })}
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Actions */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                to="/profile"
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all duration-200 ${isActive('/profile') ? 'text-primary' : 'text-gray-400 hover:text-primary'
                  }`}
              >
                <div className="w-8 h-8 flex items-center justify-center bg-primary/20 text-primary">
                  {React.createElement(FiUser as any, { className: "text-sm" })}
                </div>
                <span className="max-w-[100px] truncate">{username || 'Профиль'}</span>
              </Link>
            ) : (
              <Link
                to="/login"
                className="btn-secondary flex items-center gap-2 px-5 py-2 text-sm"
              >
                {React.createElement(FiUser as any, { className: "text-lg" })}
                <span>Войти</span>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden w-10 h-10 flex items-center justify-center text-gray-400 hover:text-primary transition-colors duration-200"
          >
            {isMobileMenuOpen
              ? React.createElement(FiX as any, { className: "text-xl" })
              : React.createElement(FiMenu as any, { className: "text-xl" })
            }
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-bg-card border-b border-border-dark animate-fade-in">
            <nav className="container-main py-4">
              <ul className="space-y-1">
                {navItems.map((item) => {
                  const active = isActive(item.href);
                  return (
                    <li key={item.href}>
                      <Link
                        to={item.href}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all duration-200 ${active
                          ? 'text-primary bg-primary/5'
                          : 'text-gray-400 hover:text-primary hover:bg-primary/5'
                          }`}
                      >
                        {React.createElement(item.icon as any, { className: "text-lg" })}
                        <span>{item.label}</span>
                      </Link>
                    </li>
                  );
                })}

                {/* Mobile Login/Profile Button */}
                <li className="pt-3 mt-3 border-t border-border-dark">
                  {isAuthenticated ? (
                    <Link
                      to="/profile"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="btn-primary w-full flex items-center justify-center gap-2 py-3"
                    >
                      {React.createElement(FiUser as any, {})}
                      <span>{username || 'Профиль'}</span>
                    </Link>
                  ) : (
                    <Link
                      to="/login"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="btn-primary w-full flex items-center justify-center gap-2 py-3"
                    >
                      {React.createElement(FiUser as any, {})}
                      <span>Войти</span>
                    </Link>
                  )}
                </li>
              </ul>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
