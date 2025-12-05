import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
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
            {/* Защищённые маршруты - требуют авторизации */}
            <Route path="/configurator" element={
              <ProtectedRoute>
                <Configurator />
              </ProtectedRoute>
            } />
            <Route path="/build-yourself" element={
              <ProtectedRoute>
                <BuildYourself />
              </ProtectedRoute>
            } />
            <Route path="/components" element={
              <ProtectedRoute>
                <Components />
              </ProtectedRoute>
            } />
            <Route path="/my-configurations" element={
              <ProtectedRoute>
                <MyConfigurations />
              </ProtectedRoute>
            } />
            <Route path="/configuration/:id" element={
              <ProtectedRoute>
                <ConfigurationDetail />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            {/* Публичные маршруты */}
            <Route path="/build/:shareCode" element={<SharedBuild />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
