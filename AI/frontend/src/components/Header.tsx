import React, { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaCog, FaMicrochip, FaList, FaSignInAlt, FaRobot } from 'react-icons/fa';
import { gsap } from 'gsap';
import LanyardTooltip from './LanyardTooltip';

interface NavItem {
  label: string;
  href: string;
  icon: any;
}

const Header: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const circleRefs = useRef<Array<HTMLSpanElement | null>>([]);
  const tlRefs = useRef<Array<gsap.core.Timeline | null>>([]);
  const activeTweenRefs = useRef<Array<gsap.core.Tween | null>>([]);
  const logoImgRef = useRef<HTMLDivElement | null>(null);
  const logoTweenRef = useRef<gsap.core.Tween | null>(null);
  const hamburgerRef = useRef<HTMLButtonElement | null>(null);
  const mobileMenuRef = useRef<HTMLDivElement | null>(null);
  const navItemsRef = useRef<HTMLDivElement | null>(null);
  const logoRef = useRef<HTMLAnchorElement | null>(null);

  const navItems: NavItem[] = [
    { label: 'Главная', href: '/', icon: FaHome },
    { label: 'Конфигуратор', href: '/configurator', icon: FaCog },
    { label: 'Компоненты', href: '/components', icon: FaMicrochip },
    { label: 'Мои сборки', href: '/my-configurations', icon: FaList },
  ];

  const isActive = (path: string) => location.pathname === path;
  const ease = 'power3.easeOut';

  useEffect(() => {
    const layout = () => {
      circleRefs.current.forEach(circle => {
        if (!circle?.parentElement) return;

        const pill = circle.parentElement as HTMLElement;
        const rect = pill.getBoundingClientRect();
        const { width: w, height: h } = rect;
        const R = ((w * w) / 4 + h * h) / (2 * h);
        const D = Math.ceil(2 * R) + 2;
        const delta = Math.ceil(R - Math.sqrt(Math.max(0, R * R - (w * w) / 4))) + 1;
        const originY = D - delta;

        circle.style.width = `${D}px`;
        circle.style.height = `${D}px`;
        circle.style.bottom = `-${delta}px`;

        gsap.set(circle, {
          xPercent: -50,
          scale: 0,
          transformOrigin: `50% ${originY}px`
        });

        const label = pill.querySelector<HTMLElement>('.pill-label');
        const white = pill.querySelector<HTMLElement>('.pill-label-hover');

        if (label) gsap.set(label, { y: 0 });
        if (white) gsap.set(white, { y: h + 12, opacity: 0 });

        const index = circleRefs.current.indexOf(circle);
        if (index === -1) return;

        tlRefs.current[index]?.kill();
        const tl = gsap.timeline({ paused: true });

        tl.to(circle, { scale: 1.2, xPercent: -50, duration: 2, ease, overwrite: 'auto' }, 0);

        if (label) {
          tl.to(label, { y: -(h + 8), duration: 2, ease, overwrite: 'auto' }, 0);
        }

        if (white) {
          gsap.set(white, { y: Math.ceil(h + 100), opacity: 0 });
          tl.to(white, { y: 0, opacity: 1, duration: 2, ease, overwrite: 'auto' }, 0);
        }

        tlRefs.current[index] = tl;
      });
    };

    layout();

    const onResize = () => layout();
    window.addEventListener('resize', onResize);

    if (document.fonts) {
      document.fonts.ready.then(layout).catch(() => {});
    }

    const menu = mobileMenuRef.current;
    if (menu) {
      gsap.set(menu, { visibility: 'hidden', opacity: 0, y: -20 });
    }

    // Initial load animation
    const logo = logoRef.current;
    const navItemsEl = navItemsRef.current;

    if (logo) {
      gsap.set(logo, { scale: 0, opacity: 0 });
      gsap.to(logo, { scale: 1, opacity: 1, duration: 0.6, ease });
    }

    if (navItemsEl) {
      gsap.set(navItemsEl, { width: 0, overflow: 'hidden' });
      gsap.to(navItemsEl, { width: 'auto', duration: 0.8, ease, delay: 0.2 });
    }

    return () => window.removeEventListener('resize', onResize);
  }, []);

  const handleEnter = (i: number) => {
    const tl = tlRefs.current[i];
    if (!tl) return;
    activeTweenRefs.current[i]?.kill();
    activeTweenRefs.current[i] = tl.tweenTo(tl.duration(), {
      duration: 0.3,
      ease,
      overwrite: 'auto'
    });
  };

  const handleLeave = (i: number) => {
    const tl = tlRefs.current[i];
    if (!tl) return;
    activeTweenRefs.current[i]?.kill();
    activeTweenRefs.current[i] = tl.tweenTo(0, {
      duration: 0.2,
      ease,
      overwrite: 'auto'
    });
  };

  const handleLogoEnter = () => {
    const img = logoImgRef.current;
    if (!img) return;
    logoTweenRef.current?.kill();
    gsap.set(img, { rotate: 0 });
    logoTweenRef.current = gsap.to(img, {
      rotate: 360,
      duration: 0.6,
      ease,
      overwrite: 'auto'
    });
  };

  const toggleMobileMenu = () => {
    const newState = !isMobileMenuOpen;
    setIsMobileMenuOpen(newState);

    const hamburger = hamburgerRef.current;
    const menu = mobileMenuRef.current;

    if (hamburger) {
      const lines = hamburger.querySelectorAll('.hamburger-line');
      if (newState) {
        gsap.to(lines[0], { rotation: 45, y: 6, duration: 0.3, ease });
        gsap.to(lines[1], { rotation: -45, y: -6, duration: 0.3, ease });
      } else {
        gsap.to(lines[0], { rotation: 0, y: 0, duration: 0.3, ease });
        gsap.to(lines[1], { rotation: 0, y: 0, duration: 0.3, ease });
      }
    }

    if (menu) {
      if (newState) {
        gsap.set(menu, { visibility: 'visible' });
        gsap.fromTo(
          menu,
          { opacity: 0, y: -20 },
          { opacity: 1, y: 0, duration: 0.3, ease }
        );
      } else {
        gsap.to(menu, {
          opacity: 0,
          y: -20,
          duration: 0.2,
          ease,
          onComplete: () => {
            gsap.set(menu, { visibility: 'hidden' });
          }
        });
      }
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link
            ref={logoRef}
            to="/"
            onMouseEnter={handleLogoEnter}
            className="flex items-center space-x-3 text-2xl font-bold text-white transition-all duration-300"
          >
            <div
              ref={logoImgRef}
              className="p-2 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 backdrop-blur-sm border border-white/20 shadow-lg shadow-blue-500/30"
              style={{ width: '52px', height: '52px' }}
            >
              {React.createElement(FaRobot as any, { className: "text-3xl text-white" })}
            </div>
            <span className="hidden lg:inline-block bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI PC Configurator
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div
            ref={navItemsRef}
            className="hidden md:flex items-center rounded-full backdrop-blur-xl bg-white/5 border border-white/10 shadow-lg"
            style={{ height: '52px' }}
          >
            <ul className="flex items-stretch m-0 p-1 h-full gap-1">
              {navItems.map((item, i) => {
                const Icon = item.icon;
                const active = isActive(item.href);

                return (
                  <li key={item.href} className="flex h-full">
                    <Link
                      to={item.href}
                      className="pill-nav-item relative overflow-hidden inline-flex items-center justify-center gap-2 h-full px-5 rounded-full text-white/90 font-semibold text-sm uppercase tracking-wide whitespace-nowrap cursor-pointer transition-colors duration-200"
                      onMouseEnter={() => handleEnter(i)}
                      onMouseLeave={() => handleLeave(i)}
                    >
                      {/* Hover Circle */}
                      <span
                        className="hover-circle absolute left-1/2 bottom-0 rounded-full z-[1] block pointer-events-none bg-gradient-to-br from-blue-500 to-purple-500"
                        style={{ willChange: 'transform' }}
                        ref={el => { circleRefs.current[i] = el; }}
                      />

                      {/* Icon */}
                      <span className="relative z-[2]">
                        {React.createElement(Icon as any, { className: "text-lg" })}
                      </span>

                      {/* Label Stack */}
                      <span className="label-stack relative inline-block leading-none z-[2]">
                        <span
                          className="pill-label relative z-[2] inline-block leading-none"
                          style={{ willChange: 'transform' }}
                        >
                          {item.label}
                        </span>
                        <span
                          className="pill-label-hover absolute left-0 top-0 z-[3] inline-block text-white"
                          style={{ willChange: 'transform, opacity' }}
                        >
                          {item.label}
                        </span>
                      </span>

                      {/* Active Indicator */}
                      {active && (
                        <span
                          className="absolute left-1/2 -bottom-1 -translate-x-1/2 w-2 h-2 rounded-full z-[4] bg-gradient-to-r from-blue-400 to-purple-400 shadow-lg shadow-blue-500/50"
                        />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Right Actions */}
          <div className="hidden md:flex items-center space-x-3">
            <LanyardTooltip 
              buttonText="Визитка" 
              buttonClassName="px-5 py-2.5"
            />
            <Link
              to="/login"
              className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 border border-white/20 text-white font-semibold transition-all duration-300 shadow-lg hover:shadow-blue-500/50 hover:scale-105"
            >
              {React.createElement(FaSignInAlt as any)}
              <span>Войти</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            ref={hamburgerRef}
            onClick={toggleMobileMenu}
            className="md:hidden rounded-full border-0 flex flex-col items-center justify-center gap-2 cursor-pointer p-0 backdrop-blur-xl bg-white/5 border border-white/10"
            style={{ width: '52px', height: '52px' }}
          >
            <span className="hamburger-line w-6 h-0.5 rounded origin-center bg-white" />
            <span className="hamburger-line w-6 h-0.5 rounded origin-center bg-white" />
          </button>
        </div>

        {/* Mobile Menu */}
        <div
          ref={mobileMenuRef}
          className="md:hidden absolute top-[70px] left-4 right-4 rounded-3xl backdrop-blur-xl bg-white/5 border border-white/10 shadow-2xl origin-top"
        >
          <ul className="list-none m-0 p-2 flex flex-col gap-1">
            {navItems.map(item => {
              const Icon = item.icon;
              return (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    className="flex items-center gap-3 py-3 px-4 text-base font-medium rounded-2xl transition-all duration-200 text-white/90 hover:text-white hover:bg-white/10"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {React.createElement(Icon as any, { className: "text-xl" })}
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
            <li className="pt-2 border-t border-white/10">
              <Link
                to="/login"
                className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow-lg"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {React.createElement(FaSignInAlt as any)}
                <span>Войти</span>
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </header>
  );
};

export default Header;
