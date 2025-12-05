import React from 'react';
import { FiCheck } from 'react-icons/fi';

interface ComponentCardProps {
  title: string;
  manufacturer: string;
  price: string;
  image?: string;
  specs: Record<string, string | number | boolean>;
  onSelect?: () => void;
  isSelected?: boolean;
}

const ComponentCard: React.FC<ComponentCardProps> = ({
  title,
  manufacturer,
  price,
  image,
  specs,
  onSelect,
  isSelected,
}) => {
  return (
    <div
      className={`card-accent p-5 cursor-pointer transition-all duration-200 ${
        isSelected 
          ? 'border-primary bg-primary/5' 
          : ''
      }`}
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1 pr-4">
          <h3 className="text-base font-heading font-semibold text-white mb-1 line-clamp-2">
            {title}
          </h3>
          <p className="text-xs text-gray-500">{manufacturer}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="text-lg font-heading font-bold text-primary">
            {Number(price).toLocaleString('ru-RU')} ₽
          </p>
        </div>
      </div>

      {/* Image */}
      {image && (
        <div className="mb-4 bg-bg-surface">
          <img 
            src={image} 
            alt={title} 
            className="w-full h-40 object-cover opacity-90 hover:opacity-100 transition-opacity" 
          />
        </div>
      )}

      {/* Specs */}
      <div className="space-y-2 text-sm">
        {Object.entries(specs).map(([key, value]) => (
          <div key={key} className="flex justify-between py-1.5 border-b border-border-dark last:border-0">
            <span className="text-gray-500">{key}</span>
            <span className="font-medium text-white">
              {typeof value === 'boolean' ? (value ? 'Да' : 'Нет') : value}
            </span>
          </div>
        ))}
      </div>

      {/* Select Button */}
      {onSelect && (
        <button
          className={`mt-4 w-full py-2.5 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
            isSelected
              ? 'btn-primary'
              : 'btn-secondary'
          }`}
        >
          {isSelected ? (
            <>
              {React.createElement(FiCheck as any, {})}
              <span>Выбрано</span>
            </>
          ) : (
            <span>Выбрать</span>
          )}
        </button>
      )}
    </div>
  );
};

export default ComponentCard;
