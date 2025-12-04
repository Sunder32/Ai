import React from 'react';

interface LoadingSpinnerProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  text = 'Загрузка...', 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-14 h-14 border-4'
  };

  return (
    <div className="flex flex-col justify-center items-center py-16">
      {/* Circular Spinner */}
      <div 
        className={`${sizeClasses[size]} border-border-dark border-t-primary rounded-full animate-spin`}
        style={{ animationDuration: '0.8s' }}
      />
      
      {/* Loading text */}
      {text && (
        <p className="mt-4 text-sm text-gray-500">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
