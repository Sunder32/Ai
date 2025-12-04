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
        className={`flex items-center gap-2 bg-bg-card border border-border-dark backdrop-blur-xl px-3 py-2 ${className}`}
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
                relative flex items-center justify-center w-12 h-12
                transition-all duration-200
                ${item.active 
                  ? 'bg-primary text-white' 
                  : 'bg-bg-surface text-gray-400 hover:text-primary hover:bg-primary/10'
                }
              `}
              aria-label={item.label}
            >
              <div className={`transition-transform duration-200 ${hoveredIndex === index ? 'scale-110' : 'scale-100'}`}>
                {item.icon}
              </div>
            </button>
            
            {/* Label on hover */}
            {hoveredIndex === index && (
              <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 whitespace-nowrap animate-fade-in">
                <div className="bg-bg-card border border-border-dark px-3 py-1.5 text-xs text-white">
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
