import React from 'react';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-bg-primary">
      {/* Background Effects */}
      <div className="bg-orbs" />
      <div className="fixed inset-0 bg-grid pointer-events-none z-[1]" />
      <div className="bg-noise" />
      
      {/* Gradient accent at top */}
      <div className="fixed top-0 left-0 right-0 h-[400px] bg-gradient-to-b from-primary/5 via-transparent to-transparent pointer-events-none z-[2]" />
      
      {/* Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow container-main py-8 mt-20">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default Layout;
