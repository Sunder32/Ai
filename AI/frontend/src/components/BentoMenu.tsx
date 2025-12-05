import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { gsap } from 'gsap';
import { FaHome, FaCog, FaMicrochip, FaList, FaRobot, FaChartLine } from 'react-icons/fa';

interface MenuItem {
  path: string;
  icon: any;
  title: string;
  description: string;
  label: string;
  color?: string;
}

const menuItems: MenuItem[] = [
  {
    path: '/',
    icon: FaHome,
    title: 'Главная',
    description: 'Начните здесь',
    label: 'Home',
    color: '#1e40af'
  },
  {
    path: '/configurator',
    icon: FaCog,
    title: 'Конфигуратор',
    description: 'Создайте сборку',
    label: 'Build',
    color: '#7c3aed'
  },
  {
    path: '/components',
    icon: FaMicrochip,
    title: 'Компоненты',
    description: 'Каталог деталей',
    label: 'Parts',
    color: '#db2777'
  },
  {
    path: '/my-configurations',
    icon: FaList,
    title: 'Мои сборки',
    description: 'Сохраненные конфиги',
    label: 'Saved',
    color: '#059669'
  }
];

const DEFAULT_GLOW_COLOR = '132, 0, 255';
const PARTICLE_COUNT = 8;

const createParticleElement = (x: number, y: number, color: string = DEFAULT_GLOW_COLOR): HTMLDivElement => {
  const el = document.createElement('div');
  el.className = 'bento-particle';
  el.style.cssText = `
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: rgba(${color}, 1);
    box-shadow: 0 0 6px rgba(${color}, 0.6);
    pointer-events: none;
    z-index: 100;
    left: ${x}px;
    top: ${y}px;
  `;
  return el;
};

const BentoMenuItem: React.FC<{
  item: MenuItem;
  isActive: boolean;
  glowColor?: string;
}> = ({ item, isActive, glowColor = DEFAULT_GLOW_COLOR }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const particlesRef = useRef<HTMLDivElement[]>([]);
  const timeoutsRef = useRef<NodeJS.Timeout[]>([]);
  const isHoveredRef = useRef(false);

  const clearAllParticles = useCallback(() => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];

    particlesRef.current.forEach(particle => {
      gsap.to(particle, {
        scale: 0,
        opacity: 0,
        duration: 0.3,
        ease: 'back.in(1.7)',
        onComplete: () => {
          particle.parentNode?.removeChild(particle);
        }
      });
    });
    particlesRef.current = [];
  }, []);

  const animateParticles = useCallback(() => {
    if (!cardRef.current || !isHoveredRef.current) return;

    const { width, height } = cardRef.current.getBoundingClientRect();

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const timeoutId = setTimeout(() => {
        if (!isHoveredRef.current || !cardRef.current) return;

        const particle = createParticleElement(
          Math.random() * width,
          Math.random() * height,
          glowColor
        );
        cardRef.current.appendChild(particle);
        particlesRef.current.push(particle);

        gsap.fromTo(
          particle,
          { scale: 0, opacity: 0 },
          { scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(1.7)' }
        );

        gsap.to(particle, {
          x: (Math.random() - 0.5) * 80,
          y: (Math.random() - 0.5) * 80,
          rotation: Math.random() * 360,
          duration: 2 + Math.random() * 2,
          ease: 'none',
          repeat: -1,
          yoyo: true
        });

        gsap.to(particle, {
          opacity: 0.3,
          duration: 1.5,
          ease: 'power2.inOut',
          repeat: -1,
          yoyo: true
        });
      }, i * 100);

      timeoutsRef.current.push(timeoutId);
    }
  }, [glowColor]);

  useEffect(() => {
    if (!cardRef.current) return;

    const element = cardRef.current;

    const handleMouseEnter = () => {
      isHoveredRef.current = true;
      animateParticles();

      gsap.to(element, {
        rotateX: 5,
        rotateY: 5,
        duration: 0.3,
        ease: 'power2.out',
        transformPerspective: 1000
      });
    };

    const handleMouseLeave = () => {
      isHoveredRef.current = false;
      clearAllParticles();

      gsap.to(element, {
        rotateX: 0,
        rotateY: 0,
        x: 0,
        y: 0,
        duration: 0.3,
        ease: 'power2.out'
      });
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -8;
      const rotateY = ((x - centerX) / centerX) * 8;

      gsap.to(element, {
        rotateX,
        rotateY,
        duration: 0.1,
        ease: 'power2.out',
        transformPerspective: 1000
      });

      const magnetX = (x - centerX) * 0.05;
      const magnetY = (y - centerY) * 0.05;

      gsap.to(element, {
        x: magnetX,
        y: magnetY,
        duration: 0.3,
        ease: 'power2.out'
      });

      const relativeX = (x / rect.width) * 100;
      const relativeY = (y / rect.height) * 100;

      element.style.setProperty('--glow-x', `${relativeX}%`);
      element.style.setProperty('--glow-y', `${relativeY}%`);
      element.style.setProperty('--glow-intensity', '1');
    };

    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);
    element.addEventListener('mousemove', handleMouseMove);

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
      element.removeEventListener('mousemove', handleMouseMove);
      clearAllParticles();
    };
  }, [animateParticles, clearAllParticles]);

  const Icon = item.icon;

  return (
    <Link to={item.path} className="block">
      <div
        ref={cardRef}
        className={`bento-menu-item relative overflow-hidden rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl ${
          isActive
            ? 'border-white/30 bg-white/10'
            : 'border-white/10 bg-white/5 hover:bg-white/10'
        }`}
        style={{
          '--glow-x': '50%',
          '--glow-y': '50%',
          '--glow-intensity': '0',
          '--glow-color': glowColor
        } as React.CSSProperties}
      >
        {/* Glow Effect */}
        <div
          className="absolute inset-0 pointer-events-none opacity-0 transition-opacity duration-300"
          style={{
            background: `radial-gradient(200px circle at var(--glow-x) var(--glow-y),
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.15)) 0%,
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.08)) 30%,
              transparent 70%)`
          }}
        />

        {/* Border Glow */}
        <div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            padding: '1px',
            background: `radial-gradient(200px circle at var(--glow-x) var(--glow-y),
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.8)) 0%,
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.4)) 30%,
              transparent 60%)`,
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude'
          }}
        />

        <div className="relative p-6 flex flex-col justify-between min-h-[180px]">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <span className="text-sm text-white/70 font-medium">{item.label}</span>
            <div
              className="p-3 rounded-xl transition-all duration-300"
              style={{ backgroundColor: `${item.color}30` }}
            >
              {React.createElement(Icon as any, {
                className: 'text-2xl',
                style: { color: item.color }
              })}
            </div>
          </div>

          {/* Content */}
          <div>
            <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
            <p className="text-sm text-white/70 leading-relaxed">{item.description}</p>
          </div>

          {/* Active Indicator */}
          {isActive && (
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />
          )}
        </div>
      </div>
    </Link>
  );
};

const BentoMenu: React.FC<{
  glowColor?: string;
  className?: string;
}> = ({ glowColor = DEFAULT_GLOW_COLOR, className = '' }) => {
  const location = useLocation();
  const gridRef = useRef<HTMLDivElement>(null);
  const spotlightRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!gridRef.current) return;

    const spotlight = document.createElement('div');
    spotlight.className = 'bento-spotlight';
    spotlight.style.cssText = `
      position: fixed;
      width: 600px;
      height: 600px;
      border-radius: 50%;
      pointer-events: none;
      background: radial-gradient(circle,
        rgba(${glowColor}, 0.12) 0%,
        rgba(${glowColor}, 0.06) 20%,
        rgba(${glowColor}, 0.03) 40%,
        transparent 70%
      );
      z-index: 200;
      opacity: 0;
      transform: translate(-50%, -50%);
      mix-blend-mode: screen;
    `;
    document.body.appendChild(spotlight);
    spotlightRef.current = spotlight;

    const handleMouseMove = (e: MouseEvent) => {
      if (!spotlightRef.current || !gridRef.current) return;

      const rect = gridRef.current.getBoundingClientRect();
      const mouseInside =
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        e.clientY >= rect.top &&
        e.clientY <= rect.bottom;

      if (!mouseInside) {
        gsap.to(spotlightRef.current, { opacity: 0, duration: 0.3 });
        return;
      }

      gsap.to(spotlightRef.current, {
        left: e.clientX,
        top: e.clientY,
        opacity: 0.6,
        duration: 0.2,
        ease: 'power2.out'
      });
    };

    document.addEventListener('mousemove', handleMouseMove);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      spotlightRef.current?.parentNode?.removeChild(spotlightRef.current);
    };
  }, [glowColor]);

  return (
    <div className={`bento-menu-container ${className}`}>
      <style>
        {`
          .bento-menu-item:hover .absolute.inset-0:first-of-type {
            opacity: 1;
          }
          
          .bento-particle::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: rgba(${glowColor}, 0.2);
            border-radius: 50%;
            z-index: -1;
          }
        `}
      </style>

      <div
        ref={gridRef}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-7xl mx-auto"
      >
        {menuItems.map((item) => (
          <BentoMenuItem
            key={item.path}
            item={item}
            isActive={location.pathname === item.path}
            glowColor={glowColor}
          />
        ))}
      </div>
    </div>
  );
};

export default BentoMenu;
