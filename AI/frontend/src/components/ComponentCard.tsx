import React from 'react';
import MagicCard from './MagicCard';

interface ComponentCardProps {
  title: string;
  manufacturer: string;
  price: string;
  image?: string;
  specs: Record<string, string | number | boolean>;
  onSelect?: () => void;
  isSelected?: boolean;
  glowColor?: string;
}

const ComponentCard: React.FC<ComponentCardProps> = ({
  title,
  manufacturer,
  price,
  image,
  specs,
  onSelect,
  isSelected,
  glowColor = '59, 130, 246',
}) => {
  return (
    <MagicCard
      className={`backdrop-blur-xl rounded-2xl shadow-2xl transition-all duration-300 p-6 cursor-pointer border ${
        isSelected ? 'border-blue-500/50 bg-white/20' : 'border-white/10 bg-white/10 hover:bg-white/15'
      }`}
      glowColor={glowColor}
      enableParticles={true}
      enableTilt={true}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="text-sm text-white/60">{manufacturer}</p>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            {Number(price).toLocaleString('ru-RU')} ₽
          </p>
        </div>
      </div>

      {image && (
        <div className="mb-4">
          <img src={image} alt={title} className="w-full h-48 object-cover rounded-xl" />
        </div>
      )}

      <div className="space-y-2">
        {Object.entries(specs).map(([key, value]) => (
          <div key={key} className="flex justify-between text-sm border-b border-white/5 pb-2">
            <span className="text-white/60">{key}:</span>
            <span className="font-medium text-white">
              {typeof value === 'boolean' ? (value ? 'Да' : 'Нет') : value}
            </span>
          </div>
        ))}
      </div>

      {onSelect && (
        <button
          className={`mt-4 w-full py-3 rounded-xl transition-all duration-300 font-semibold ${
            isSelected
              ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/50'
              : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
          }`}
        >
          {isSelected ? '✓ Выбрано' : 'Выбрать'}
        </button>
      )}
    </MagicCard>
  );
};

export default ComponentCard;
