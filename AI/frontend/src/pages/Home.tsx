import React from 'react';
import { Link } from 'react-router-dom';
import { 
  FaRobot, 
  FaMicrochip, 
  FaChartLine, 
  FaShieldAlt,
  FaGamepad,
  FaCode,
  FaPaintBrush,
  FaBriefcase,
  FaGraduationCap,
  FaVideo,
  FaRocket,
  FaCheckCircle
} from 'react-icons/fa';
import { IconType } from 'react-icons';
import BentoMenu from '../components/BentoMenu';

const Home: React.FC = () => {
  const features = [
    {
      Icon: FaRobot,
      title: 'ИИ Подбор',
      description: 'Интеллектуальный алгоритм подберет оптимальную конфигурацию под ваши задачи и бюджет',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      Icon: FaMicrochip,
      title: 'Совместимость',
      description: 'Автоматическая проверка совместимости всех компонентов системы',
      gradient: 'from-teal-500 to-cyan-500'
    },
    {
      Icon: FaChartLine,
      title: 'Аналитика',
      description: 'Детальная аналитика производительности и распределения бюджета',
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      Icon: FaShieldAlt,
      title: 'Надежность',
      description: 'Подбор проверенных и надежных компонентов от ведущих производителей',
      gradient: 'from-orange-500 to-red-500'
    }
  ];

  const userTypes = [
    { Icon: FaGamepad, title: 'Геймер', type: 'gamer', color: 'from-red-500 to-pink-500' },
    { Icon: FaCode, title: 'Программист', type: 'programmer', color: 'from-blue-500 to-cyan-500' },
    { Icon: FaPaintBrush, title: 'Дизайнер', type: 'designer', color: 'from-cyan-500 to-blue-500' },
    { Icon: FaBriefcase, title: 'Офис', type: 'office', color: 'from-gray-500 to-slate-500' },
    { Icon: FaGraduationCap, title: 'Студент', type: 'student', color: 'from-green-500 to-emerald-500' },
    { Icon: FaVideo, title: 'Контент-мейкер', type: 'content_creator', color: 'from-orange-500 to-yellow-500' }
  ];

  const stats = [
    { value: '10,000+', label: 'Конфигураций создано' },
    { value: '500+', label: 'Компонентов в базе' },
    { value: '99.9%', label: 'Точность подбора' },
    { value: '24/7', label: 'Поддержка' }
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center py-16">
        <div className="inline-block mb-6">
          <div className="p-4 rounded-3xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-sm border border-white/10">
            {React.createElement(FaRocket as any, { className: "text-6xl text-white" })}
          </div>
        </div>
        <h1 className="text-6xl font-bold mb-6">
          <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
            AI PC Configurator
          </span>
        </h1>
        <p className="text-xl text-white/70 mb-8 max-w-2xl mx-auto leading-relaxed">
          Создайте идеальную конфигурацию ПК с помощью искусственного интеллекта.
          Автоматический подбор компонентов под ваши задачи и бюджет.
        </p>
        <Link
          to="/configurator"
          className="inline-flex items-center space-x-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-bold text-lg transition-all duration-300 shadow-2xl shadow-blue-500/50 hover:scale-105"
        >
          {React.createElement(FaRobot as any, { className: "text-2xl" })}
          <span>Начать подбор конфигурации</span>
        </Link>
      </div>

      {/* Bento Menu Navigation */}
      <BentoMenu glowColor="132, 0, 255" className="py-16" />

      {/* Features Grid */}
      <div>
        <h2 className="text-4xl font-bold text-center mb-12 text-white">
          Почему выбирают нас
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.Icon;
            return (
              <div
                key={index}
                className="group backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10 hover:border-white/30 transition-all duration-300 hover:scale-105"
              >
                <div className={`inline-block p-4 rounded-xl bg-gradient-to-br ${feature.gradient} bg-opacity-20 mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  {React.createElement(Icon as any, { className: "text-4xl" })}
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-white/70 leading-relaxed">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* User Types */}
      <div>
        <h2 className="text-4xl font-bold text-center mb-4 text-white">
          Конфигурация для каждого
        </h2>
        <p className="text-center text-white/70 mb-12 text-lg">
          Выберите профиль, который соответствует вашим задачам
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {userTypes.map((type, index) => {
            const Icon = type.Icon;
            return (
              <Link
                key={index}
                to={`/configurator?type=${type.type}`}
                className="group backdrop-blur-xl bg-white/5 rounded-2xl p-6 border border-white/10 hover:border-white/30 transition-all duration-300 hover:scale-105 text-center"
              >
                <div className={`inline-block p-4 rounded-xl bg-gradient-to-br ${type.color} bg-opacity-20 mb-4 text-4xl text-white group-hover:scale-110 transition-transform duration-300`}>
                  {React.createElement(Icon as any)}
                </div>
                <h3 className="text-white font-semibold">{type.title}</h3>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Stats */}
      <div className="backdrop-blur-xl bg-white/5 rounded-3xl p-12 border border-white/10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-2">
                {stat.value}
              </div>
              <div className="text-white/70">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="backdrop-blur-xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl p-12 border border-white/20 text-center">
        <h2 className="text-4xl font-bold text-white mb-4">
          Готовы создать идеальный ПК?
        </h2>
        <p className="text-xl text-white/80 mb-8">
          Начните прямо сейчас — это быстро, бесплатно и просто
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/configurator"
            className="inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-bold transition-all duration-300 shadow-lg hover:scale-105"
          >
            {React.createElement(FaRocket as any)}
            <span>Создать конфигурацию</span>
          </Link>
          <Link
            to="/components"
            className="inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-xl backdrop-blur-sm bg-white/10 hover:bg-white/20 border border-white/20 text-white font-bold transition-all duration-300"
          >
            {React.createElement(FaMicrochip as any)}
            <span>Каталог компонентов</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
