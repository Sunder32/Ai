import React, { useState } from 'react';

export type DockItemData = {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  active?: boolean;
};

export type DockProps = {
  items: DockItemData[];
  className?: string;
};

const Dock: React.FC<DockProps> = ({ items, className = '' }) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
      <div 
        className={`flex items-center gap-3 rounded-2xl border-2 border-white/10 bg-black/40 backdrop-blur-xl px-4 py-3 shadow-2xl ${className}`}
        onMouseLeave={() => setHoveredIndex(null)}
      >
        {items.map((item, index) => (
          <div
            key={index}
            className="relative"
            onMouseEnter={() => setHoveredIndex(index)}
          >
            <button
              onClick={item.onClick}
              className={`
                relative flex items-center justify-center rounded-full 
                transition-all duration-300 ease-out
                ${item.active 
                  ? 'bg-gradient-to-br from-blue-500 to-purple-600 border-2 border-white/30' 
                  : 'bg-[#0a0118] border-2 border-white/20 hover:border-white/40'
                }
                ${hoveredIndex === index ? 'w-16 h-16 shadow-lg shadow-purple-500/30' : 'w-14 h-14'}
              `}
              aria-label={item.label}
            >
              <div className={`
                transition-transform duration-300
                ${hoveredIndex === index ? 'scale-110' : 'scale-100'}
              `}>
                {item.icon}
              </div>
            </button>
            
            {/* Label on hover */}
            {hoveredIndex === index && (
              <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 whitespace-nowrap animate-fade-in">
                <div className="bg-[#0a0118] border border-white/20 rounded-lg px-3 py-1.5 text-xs text-white font-medium shadow-lg">
                  {item.label}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dock;
