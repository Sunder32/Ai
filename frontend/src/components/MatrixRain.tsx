import React, { useEffect, useRef } from 'react';

interface MatrixRainProps {
  opacity?: number;
  speed?: number;
  density?: number;
}

const MatrixRain: React.FC<MatrixRainProps> = ({
  opacity = 0.05,
  speed = 1,
  density = 0.6
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Matrix characters - mix of katakana, numbers, and symbols
    const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*()+-=[]{}|;:,.<>?';
    const charArray = chars.split('');

    let animationId: number;
    let columns: number;
    let drops: number[];

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      
      const fontSize = 14;
      columns = Math.floor(canvas.width / fontSize * density);
      drops = [];
      
      for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100;
      }
    };

    const draw = () => {
      // Semi-transparent black to create trail effect
      ctx.fillStyle = `rgba(0, 0, 0, 0.05)`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const fontSize = 14;
      ctx.font = `${fontSize}px 'Share Tech Mono', monospace`;

      for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = charArray[Math.floor(Math.random() * charArray.length)];
        
        // X position
        const x = i * (fontSize / density);
        
        // Y position
        const y = drops[i] * fontSize;

        // Gradient effect - brighter at the head
        const gradient = ctx.createLinearGradient(x, y - fontSize * 5, x, y);
        gradient.addColorStop(0, 'rgba(0, 255, 65, 0)');
        gradient.addColorStop(0.8, 'rgba(0, 255, 65, 0.5)');
        gradient.addColorStop(1, 'rgba(0, 255, 65, 1)');
        
        ctx.fillStyle = gradient;
        ctx.fillText(char, x, y);

        // Add extra bright character at the head
        if (Math.random() > 0.9) {
          ctx.fillStyle = '#ffffff';
          ctx.fillText(char, x, y);
        }

        // Reset drop to top when it reaches bottom
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }

        // Move drop down
        drops[i] += speed;
      }

      animationId = requestAnimationFrame(draw);
    };

    resizeCanvas();
    draw();

    window.addEventListener('resize', resizeCanvas);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, [opacity, speed, density]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      style={{ opacity }}
    />
  );
};

export default MatrixRain;
