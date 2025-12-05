import React, { useRef, useCallback, useEffect } from 'react';
import gsap from 'gsap';

interface MagicCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: string;
  enableParticles?: boolean;
  enableTilt?: boolean;
  onClick?: () => void;
}

const DEFAULT_GLOW_COLOR = '59, 130, 246'; // Blue
const PARTICLE_COUNT = 6;

const MagicCard: React.FC<MagicCardProps> = ({
  children,
  className = '',
  glowColor = DEFAULT_GLOW_COLOR,
  enableParticles = true,
  enableTilt = true,
  onClick
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const particlesRef = useRef<HTMLDivElement[]>([]);
  const timeoutsRef = useRef<NodeJS.Timeout[]>([]);
  const isHoveredRef = useRef(false);

  const createParticle = useCallback((x: number, y: number): HTMLDivElement => {
    const el = document.createElement('div');
    el.className = 'magic-particle';
    el.style.cssText = `
      position: absolute;
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: rgba(${glowColor}, 1);
      box-shadow: 0 0 6px rgba(${glowColor}, 0.6);
      pointer-events: none;
      z-index: 100;
      left: ${x}px;
      top: ${y}px;
    `;
    return el;
  }, [glowColor]);

  const clearParticles = useCallback(() => {
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
    if (!cardRef.current || !isHoveredRef.current || !enableParticles) return;

    clearParticles();

    const rect = cardRef.current.getBoundingClientRect();
    
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const timeoutId = setTimeout(() => {
        if (!cardRef.current || !isHoveredRef.current) return;

        const x = Math.random() * rect.width;
        const y = Math.random() * rect.height;
        
        const particle = createParticle(x, y);
        cardRef.current.appendChild(particle);
        particlesRef.current.push(particle);

        const angle = Math.random() * Math.PI * 2;
        const distance = 30 + Math.random() * 30;
        const tx = Math.cos(angle) * distance;
        const ty = Math.sin(angle) * distance;

        gsap.fromTo(particle,
          { scale: 0, opacity: 0 },
          {
            scale: 1,
            opacity: 1,
            duration: 0.3,
            ease: 'back.out(2)'
          }
        );

        gsap.to(particle, {
          x: tx,
          y: ty,
          opacity: 0,
          duration: 1 + Math.random() * 0.5,
          delay: 0.3,
          ease: 'power2.out',
          onComplete: () => {
            particle.parentNode?.removeChild(particle);
            const index = particlesRef.current.indexOf(particle);
            if (index > -1) particlesRef.current.splice(index, 1);
          }
        });

        gsap.to(particle, {
          scale: 0.3,
          duration: 1,
          delay: 0.5,
          ease: 'power2.inOut',
          repeat: -1,
          yoyo: true
        });
      }, i * 100);

      timeoutsRef.current.push(timeoutId);
    }
  }, [glowColor, createParticle, clearParticles, enableParticles]);

  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach(id => clearTimeout(id));
      clearParticles();
    };
  }, [clearParticles]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const xPercent = (x / rect.width) * 100;
    const yPercent = (y / rect.height) * 100;

    cardRef.current.style.setProperty('--glow-x', `${xPercent}%`);
    cardRef.current.style.setProperty('--glow-y', `${yPercent}%`);
    cardRef.current.style.setProperty('--glow-intensity', '1');

    if (enableTilt) {
      const xRotation = ((y / rect.height) - 0.5) * -8;
      const yRotation = ((x / rect.width) - 0.5) * 8;

      gsap.to(cardRef.current, {
        rotateX: xRotation,
        rotateY: yRotation,
        duration: 0.3,
        ease: 'power2.out'
      });
    }
  }, [enableTilt]);

  const handleMouseEnter = useCallback(() => {
    isHoveredRef.current = true;
    if (enableParticles) {
      animateParticles();
    }
  }, [animateParticles, enableParticles]);

  const handleMouseLeave = useCallback(() => {
    isHoveredRef.current = false;
    clearParticles();
    timeoutsRef.current.forEach(id => clearTimeout(id));
    timeoutsRef.current = [];

    if (cardRef.current) {
      cardRef.current.style.setProperty('--glow-intensity', '0');
      if (enableTilt) {
        gsap.to(cardRef.current, {
          rotateX: 0,
          rotateY: 0,
          duration: 0.5,
          ease: 'power2.out'
        });
      }
    }
  }, [clearParticles, enableTilt]);

  return (
    <div
      ref={cardRef}
      className={`magic-card relative overflow-hidden ${className}`}
      style={{
        '--glow-x': '50%',
        '--glow-y': '50%',
        '--glow-intensity': '0',
        '--glow-color': glowColor,
        transformStyle: enableTilt ? 'preserve-3d' : undefined,
        perspective: enableTilt ? '1000px' : undefined
      } as React.CSSProperties}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Glow Effect */}
      <div
        className="absolute inset-0 pointer-events-none opacity-0 transition-opacity duration-300"
        style={{
          background: `radial-gradient(300px circle at var(--glow-x) var(--glow-y),
            rgba(${glowColor}, calc(var(--glow-intensity) * 0.12)) 0%,
            rgba(${glowColor}, calc(var(--glow-intensity) * 0.06)) 30%,
            transparent 70%)`,
          opacity: 'var(--glow-intensity)'
        }}
      />

      {/* Border Glow */}
      <div
        className="absolute inset-0 rounded-[inherit] pointer-events-none"
        style={{
          padding: '1px',
          background: `radial-gradient(250px circle at var(--glow-x) var(--glow-y),
            rgba(${glowColor}, calc(var(--glow-intensity) * 0.6)) 0%,
            rgba(${glowColor}, calc(var(--glow-intensity) * 0.3)) 30%,
            transparent 60%)`,
          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          WebkitMaskComposite: 'xor',
          mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          maskComposite: 'exclude',
          opacity: 'var(--glow-intensity)'
        }}
      />

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

export default MagicCard;
