import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { FiCpu, FiZap, FiShield, FiBarChart2, FiArrowRight, FiMonitor, FiCode, FiEdit3, FiBriefcase, FiVideo, FiBookOpen, FiCheckCircle, FiSearch, FiSettings } from 'react-icons/fi';
const gridPattern = '/grid.svg';

// -- Helper Components --

const TypewriterText = ({ texts, typingSpeed = 150, deletingSpeed = 75, pauseTime = 2000 }: { texts: string[], typingSpeed?: number, deletingSpeed?: number, pauseTime?: number }) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [loopNum, setLoopNum] = useState(0);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    const currentFullText = texts[loopNum % texts.length];

    if (isDeleting) {
      timer = setTimeout(() => {
        setDisplayText(currentFullText.substring(0, currentIndex - 1));
        setCurrentIndex(currentIndex - 1);
      }, deletingSpeed);
    } else {
      timer = setTimeout(() => {
        setDisplayText(currentFullText.substring(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }, typingSpeed);
    }

    if (!isDeleting && currentIndex === currentFullText.length) {
      timer = setTimeout(() => setIsDeleting(true), pauseTime);
    } else if (isDeleting && currentIndex === 0) {
      setIsDeleting(false);
      setLoopNum(loopNum + 1);
    }

    return () => clearTimeout(timer);
  }, [currentIndex, isDeleting, loopNum, texts, typingSpeed, deletingSpeed, pauseTime]);

  return (
    <span className="inline-block min-w-[2ch]">
      {displayText}
      <span className="animate-pulse ml-1 text-primary">|</span>
    </span>
  );
};

const AnimatedCounter = ({ end, duration = 2000, suffix = '' }: { end: number, duration?: number, suffix?: string }) => {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    let startTime: number;
    let animationFrame: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);

      // Easing function: easeOutQuart
      const ease = 1 - Math.pow(1 - percentage, 4);

      setCount(Math.floor(end * ease));

      if (progress < duration) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration, isVisible]);

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>;
};


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
    { value: 10000, suffix: '+', label: 'Конфигураций' },
    { value: 500, suffix: '+', label: 'Компонентов' },
    { value: 99, suffix: '.9%', label: 'Точность' },
    { value: 24, suffix: '/7', label: 'Онлайн' }
  ];

  const steps = [
    {
      icon: FiSearch,
      title: 'Укажите бюджет',
      desc: 'И предпочтения по играм или задачам'
    },
    {
      icon: FiCpu,
      title: 'AI подберет',
      desc: 'Оптимальные компоненты за секунды'
    },
    {
      icon: FiSettings,
      title: 'Настройте',
      desc: 'Измените детали под свой вкус'
    },
    {
      icon: FiCheckCircle,
      title: 'Готово!',
      desc: 'Получите идеальную сборку'
    }
  ];

  const heroTexts = [
    "Идеальный PC",
    "Мощный Игровой PC",
    "Надежную Рабочую Станцию",
    "Тихий Медиацентр"
  ];

  return (
    <div className="space-y-24 pb-16">
      {/* Hero Section */}
      <section className="relative min-h-[85vh] flex items-center justify-center pt-20 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-bg-page to-bg-page z-0" />
        <div className="absolute top-0 left-0 w-full h-full opacity-[0.03] z-0" style={{ backgroundImage: `url(${gridPattern})` }} />

        <div className="container-main relative z-10 flex flex-col items-center text-center max-w-5xl mx-auto px-4">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full animate-fade-in hover:bg-primary/20 transition-colors cursor-default mb-8">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              <span className="text-sm text-primary font-medium tracking-wide">AI POWERED CONFIGURATOR</span>
            </div>

            <h1 className="text-display text-5xl md:text-7xl lg:text-8xl text-white leading-tight font-bold mb-8 tracking-tight">
              Создайте <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">
                <TypewriterText texts={heroTexts} />
              </span> <br />
              с помощью ИИ
            </h1>

            <p className="text-body text-gray-400 text-lg md:text-xl max-w-2xl leading-relaxed mb-10 mx-auto">
              Забудьте о проблемах совместимости. Наша нейросеть подберет лучшие компоненты под ваш бюджет и задачи за считанные секунды.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center w-full sm:w-auto">
              <Link
                to="/configurator"
                className="group btn-primary inline-flex items-center justify-center gap-3 px-8 py-4 text-lg shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all duration-300 transform hover:-translate-y-1 relative overflow-hidden rounded-xl min-w-[200px]"
              >
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                <span className="relative z-10 font-bold">Собрать PC</span>
                {React.createElement(FiArrowRight as any, { className: "text-xl relative z-10 group-hover:translate-x-1 transition-transform" })}
              </Link>
              <Link
                to="/build-yourself"
                className="btn-secondary inline-flex items-center justify-center gap-3 px-8 py-4 text-lg hover:bg-white/5 transition-all duration-300 backdrop-blur-sm rounded-xl border border-white/10 hover:border-white/20 min-w-[200px]"
              >
                <span className="font-medium">Ручной режим</span>
              </Link>
            </div>

            {/* Trust Badges */}
            <div className="flex flex-wrap justify-center items-center gap-8 pt-12 text-gray-500 text-sm font-medium">
              <div className="flex items-center gap-2">
                {React.createElement(FiCheckCircle as any, { className: "text-primary" })}
                <span>100% Совместимость</span>
              </div>
              <div className="flex items-center gap-2">
                {React.createElement(FiCheckCircle as any, { className: "text-primary" })}
                <span>Актуальные цены</span>
              </div>
            </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-y border-white/5 bg-white/[0.02]">
        <div className="container-main py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center group hover:transform hover:scale-105 transition-transform duration-300">
                <div className="text-4xl md:text-5xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-gray-500 mb-2 group-hover:from-primary group-hover:to-emerald-400 transition-all duration-300">
                  <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                </div>
                <div className="text-sm font-medium text-gray-500 uppercase tracking-widest group-hover:text-gray-300 transition-colors">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="container-main py-16">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-4">
            Как это работает?
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Всего 4 простых шага отделяют вас от компьютера мечты
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
          {/* Connecting Line (Desktop) */}
          <div className="hidden md:block absolute top-12 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

          {steps.map((step, index) => (
            <div key={index} className="relative flex flex-col items-center text-center group">
              <div className="w-24 h-24 rounded-2xl bg-bg-card border border-white/10 flex items-center justify-center mb-6 relative z-10 group-hover:border-primary/50 group-hover:shadow-[0_0_30px_rgba(16,185,129,0.2)] transition-all duration-300 bg-gray-900">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
                {React.createElement(step.icon as any, { className: "text-3xl text-gray-400 group-hover:text-primary transition-colors transform group-hover:scale-110 duration-300" })}
                <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-bg-page border border-white/10 flex items-center justify-center text-sm font-bold text-primary shadow-lg z-20">
                  {index + 1}
                </div>
              </div>
              <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary transition-colors">
                {step.title}
              </h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section className="container-main">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-6">
              Мощные инструменты <br />
              <span className="text-primary">для профессионалов</span>
            </h2>
            <p className="text-gray-400 text-lg mb-8 leading-relaxed">
              Мы не просто подбираем совместимые детали. Наша система анализирует тысячи бенчмарков, чтобы гарантировать максимальную производительность на каждый вложенный рубль.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {features.map((feature, index) => (
                <div key={index} className="flex gap-4 group">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                    {React.createElement(feature.Icon as any, { className: "text-xl text-primary group-hover:scale-110 transition-transform" })}
                  </div>
                  <div>
                    <h4 className="text-white font-bold mb-1 group-hover:text-primary transition-colors">{feature.title}</h4>
                    <p className="text-sm text-gray-500">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-3xl blur-3xl opacity-50 group-hover:opacity-75 transition-opacity duration-1000" />
            <div className="relative bg-bg-card border border-white/10 rounded-3xl p-8 shadow-2xl backdrop-blur-sm">
              <div className="flex items-center justify-between mb-8">
                <div className="text-white font-bold text-lg">Сравнение производительности</div>
                <div className="text-xs text-gray-500 bg-white/5 px-3 py-1 rounded-full border border-white/5">Cyberpunk 2077</div>
              </div>

              <div className="space-y-6">
                <div className="group/bar">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-white">Наша сборка (AI)</span>
                    <span className="text-primary font-bold">145 FPS</span>
                  </div>
                  <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-primary to-emerald-400 w-[0%] animate-[widthGrow_1.5s_ease-out_forwards] rounded-full" style={{ width: '90%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Типичная сборка</span>
                    <span className="text-gray-400 font-bold">112 FPS</span>
                  </div>
                  <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gray-600 w-[0%] animate-[widthGrow_1.5s_ease-out_0.2s_forwards] rounded-full" style={{ width: '70%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Готовый ПК из магазина</span>
                    <span className="text-gray-400 font-bold">85 FPS</span>
                  </div>
                  <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gray-700 w-[0%] animate-[widthGrow_1.5s_ease-out_0.4s_forwards] rounded-full" style={{ width: '50%' }} />
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-white/5 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  Экономия бюджета: <span className="text-white font-bold">~15,000 ₽</span>
                </div>
                <button className="text-primary text-sm font-medium hover:underline">
                  Подробнее об аналитике
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* User Types */}
      <section className="container-main pt-16">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-heading font-bold text-white mb-4">
            Выберите свой профиль
          </h2>
          <p className="text-gray-500">
            Мы подготовили специализированные пресеты для разных задач
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {userTypes.map((userType, index) => (
            <Link
              key={index}
              to={`/configurator?type=${userType.type}`}
              className="card p-6 text-center group hover:border-primary/50 transition-all duration-300 hover:-translate-y-1 bg-gradient-to-b from-transparent to-transparent hover:from-white/5"
            >
              <div className="w-14 h-14 mx-auto flex items-center justify-center bg-bg-surface rounded-xl mb-4 
                group-hover:bg-primary/20 group-hover:scale-110 transition-all duration-300">
                {React.createElement(userType.Icon as any, { className: "text-2xl text-gray-400 group-hover:text-primary transition-colors" })}
              </div>
              <span className="text-sm font-medium text-gray-400 group-hover:text-white transition-colors">
                {userType.title}
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container-main pt-16">
        <div className="relative rounded-3xl overflow-hidden p-12 text-center border border-white/10 group">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-purple-500/10 to-primary/10 group-hover:opacity-70 transition-opacity" />
          <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: `url(${gridPattern})` }} />

          <div className="relative z-10">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-6">
              Готовы собрать компьютер мечты?
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto text-lg">
              Присоединяйтесь к тысячам пользователей, которые уже создали свои идеальные сборки с помощью нашего AI
            </p>
            <Link
              to="/configurator"
              className="btn-primary inline-flex items-center gap-3 px-10 py-5 text-lg shadow-xl shadow-primary/20 hover:shadow-primary/40 hover:scale-105 transition-all duration-300"
            >
              <span>Начать бесплатно</span>
              {React.createElement(FiZap as any, { className: "text-xl" })}
            </Link>
          </div>
        </div>
      </section>

      {/* Global Style for Keyframes if not in CSS */}
      <style>{`
        @keyframes widthGrow {
          from { width: 0; }
        }
      `}</style>
    </div>
  );
};

export default Home;
