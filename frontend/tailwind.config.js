/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {

        'primary': '#10b981',
        'primary-light': '#34d399',
        'primary-dark': '#059669',
        'primary-neon': '#22ff88',
        'primary-deep': '#065f46',

        'bg-primary': '#0a0a0a',
        'bg-card': '#111111',
        'bg-surface': '#1a1a1a',
        'border-dark': '#1f1f1f',

        'neon-green': '#10b981',
        'neon-cyan': '#3b82f6',
        'neon-pink': '#ef4444',
        'matrix-dark': '#0a0a0a',

        'text-primary': '#ffffff',
        'text-secondary': '#9ca3af',
        'text-muted': '#6b7280',
      },
      fontFamily: {
        'heading': ['Space Grotesk', 'Outfit', 'sans-serif'],
        'body': ['Inter', 'SF Pro Display', '-apple-system', 'sans-serif'],
        'mono': ['JetBrains Mono', 'IBM Plex Mono', 'monospace'],

        'cyber': ['Space Grotesk', 'Outfit', 'sans-serif'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-lg': '0 0 20px rgba(16, 185, 129, 0.4), 0 0 40px rgba(16, 185, 129, 0.2)',
        'glow-hover': '0 0 30px rgba(52, 211, 153, 0.6)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.4)',
        'card-hover': '0 4px 32px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(16, 185, 129, 0.2)',

        'neon-green': '0 0 20px rgba(16, 185, 129, 0.4)',
        'neon-cyan': '0 0 20px rgba(59, 130, 246, 0.4)',
      },
      animation: {
        'spin-slow': 'spin 0.8s linear infinite',
        'fade-in': 'fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'corner-fade': 'cornerFade 0.2s ease',
      },
      keyframes: {
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        slideUp: {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        cornerFade: {
          'from': { opacity: '0', transform: 'scale(0.8)' },
          'to': { opacity: '1', transform: 'scale(1)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
