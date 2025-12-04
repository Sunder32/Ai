import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import Home from './pages/Home';
import Configurator from './pages/Configurator';
import Components from './pages/Components';
import ConfigurationDetail from './pages/ConfigurationDetail';
import MyConfigurations from './pages/MyConfigurations';
import Login from './pages/Login';
import Profile from './pages/Profile';
import BuildYourself from './pages/BuildYourself';
import SharedBuild from './pages/SharedBuild';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/configurator" element={<Configurator />} />
            <Route path="/build-yourself" element={<BuildYourself />} />
            <Route path="/build/:shareCode" element={<SharedBuild />} />
            <Route path="/components" element={<Components />} />
            <Route path="/configuration/:id" element={<ConfigurationDetail />} />
            <Route path="/my-configurations" element={<MyConfigurations />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
