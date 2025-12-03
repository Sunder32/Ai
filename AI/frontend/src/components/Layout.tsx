import React from 'react';
import Header from './Header';
import Footer from './Footer';
import Galaxy from './Galaxy';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen relative">
      {/* Galaxy Background */}
      <div className="fixed inset-0 z-0">
        <Galaxy
          density={0.8}
          speed={0.5}
          hueShift={200}
          glowIntensity={0.4}
          saturation={0.3}
          twinkleIntensity={0.4}
          rotationSpeed={0.02}
          mouseRepulsion={true}
          repulsionStrength={2}
          transparent={false}
        />
      </div>
      
      {/* Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow container mx-auto px-6 py-8 mt-20">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default Layout;
