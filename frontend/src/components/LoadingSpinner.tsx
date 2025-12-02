import React from 'react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex flex-col justify-center items-center py-16">
      <div className="relative">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-white/10"></div>
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-t-blue-500 border-r-purple-500 absolute top-0 left-0"></div>
      </div>
      <p className="mt-4 text-white/70 font-medium">Загрузка...</p>
    </div>
  );
};

export default LoadingSpinner;
