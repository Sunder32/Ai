import React from 'react';
import { Link } from 'react-router-dom';
import { FiCpu, FiZap, FiShield, FiBarChart2, FiArrowRight, FiMonitor, FiCode, FiEdit3, FiBriefcase, FiVideo, FiBookOpen } from 'react-icons/fi';

const Home: React.FC = () => {
  const features = [
    {
      Icon: FiCpu,
      title: 'AI подбор',
      description: 'Нейросеть анализирует ваши требования и подбирает оптимальную конфигурацию'
    },
    {
      Icon: FiZap,
      title: 'Совместимость',
      description: 'Автоматическая проверка совместимости всех компонентов системы'
    },
    {
      Icon: FiBarChart2,
      title: 'Аналитика',
      description: 'Детальный анализ производительности и распределения бюджета'
    },
    {
      Icon: FiShield,
      title: 'Надежность',
      description: 'Подбор проверенных компонентов от ведущих производителей'
    }
  ];

  const userTypes = [
    { Icon: FiMonitor, title: 'Геймер', type: 'gamer' },
    { Icon: FiCode, title: 'Разработчик', type: 'programmer' },
    { Icon: FiEdit3, title: 'Дизайнер', type: 'designer' },
    { Icon: FiBriefcase, title: 'Офис', type: 'office' },
    { Icon: FiBookOpen, title: 'Студент', type: 'student' },
    { Icon: FiVideo, title: 'Стример', type: 'content_creator' }
  ];

  const stats = [
    { value: '10,000+', label: 'Конфигураций' },
    { value: '500+', label: 'Компонентов' },
    { value: '99.9%', label: 'Точность' },
    { value: '24/7', label: 'Онлайн' }
  ];

  return (
    <div className="space-y-24 py-8">
      {/* Hero Section */}
      <section className="text-center py-16">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 mb-8">
          {React.createElement(FiCpu as any, { className: "text-primary" })}
          <span className="text-sm text-primary font-medium">Powered by AI</span>
        </div>
        
        <h1 className="text-display text-4xl md:text-6xl lg:text-7xl text-white mb-6 max-w-4xl mx-auto">
          Создайте идеальный
          <span className="text-primary"> PC</span> с помощью
          <span className="text-primary"> ИИ</span>
        </h1>
        
        <p className="text-body text-gray-400 text-lg md:text-xl mb-10 max-w-2xl mx-auto">
          Автоматический подбор компонентов, проверка совместимости 
          и оптимизация бюджета за считанные секунды
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/configurator"
            className="btn-primary inline-flex items-center justify-center gap-2 px-8 py-4 text-base"
          >
            <span>Запустить конфигуратор</span>
            {React.createElement(FiArrowRight as any, {})}
          </Link>
          <Link
            to="/components"
            className="btn-secondary inline-flex items-center justify-center gap-2 px-8 py-4 text-base"
          >
            <span>База компонентов</span>
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="text-center py-6">
            <div className="text-3xl md:text-4xl font-heading font-bold text-primary mb-2">
              {stat.value}
            </div>
            <div className="text-sm text-gray-500 uppercase tracking-wider">
              {stat.label}
            </div>
          </div>
        ))}
      </section>

      {/* Divider */}
      <div className="divider" />

      {/* Features Grid */}
      <section>
        <div className="text-center mb-12">
          <h2 className="text-heading text-2xl md:text-3xl text-white mb-4">
            Возможности системы
          </h2>
          <p className="text-gray-500">
            Все необходимое для создания идеальной сборки
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            return (
              <div
                key={index}
                className="card-accent p-6 group"
              >
                <div className="w-12 h-12 flex items-center justify-center bg-primary/10 mb-4 
                  group-hover:bg-primary/20 transition-colors duration-200">
                  {React.createElement(feature.Icon as any, { className: "text-2xl text-primary" })}
                </div>
                <h3 className="text-lg font-heading font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Divider */}
      <div className="divider-glow" />

      {/* User Types */}
      <section>
        <div className="text-center mb-12">
          <h2 className="text-heading text-2xl md:text-3xl text-white mb-4">
            Выберите профиль
          </h2>
          <p className="text-gray-500">
            Система адаптируется под ваши задачи
          </p>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {userTypes.map((userType, index) => {
            return (
              <Link
                key={index}
                to={`/configurator?type=${userType.type}`}
                className="card p-6 text-center group"
              >
                <div className="w-14 h-14 mx-auto flex items-center justify-center bg-bg-surface mb-4 
                  group-hover:bg-primary/10 transition-colors duration-200">
                  {React.createElement(userType.Icon as any, { className: "text-2xl text-gray-400 group-hover:text-primary transition-colors duration-200" })}
                </div>
                <span className="text-sm font-medium text-gray-400 group-hover:text-white transition-colors duration-200">
                  {userType.title}
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center py-16 bg-bg-card border border-border-dark">
        <h2 className="text-heading text-2xl md:text-3xl text-white mb-4">
          Готовы собрать свой идеальный PC?
        </h2>
        <p className="text-gray-500 mb-8 max-w-xl mx-auto">
          Наш AI-конфигуратор поможет подобрать оптимальные компоненты
          под ваш бюджет и задачи
        </p>
        <Link
          to="/configurator"
          className="btn-primary inline-flex items-center gap-2 px-8 py-4"
        >
          <span>Начать сейчас</span>
          {React.createElement(FiArrowRight as any, {})}
        </Link>
      </section>
    </div>
  );
};

export default Home;
