import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Configurator from './pages/Configurator';
import Components from './pages/Components';
import ConfigurationDetail from './pages/ConfigurationDetail';
import MyConfigurations from './pages/MyConfigurations';
import Login from './pages/Login';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/configurator" element={<Configurator />} />
          <Route path="/components" element={<Components />} />
          <Route path="/configuration/:id" element={<ConfigurationDetail />} />
          <Route path="/my-configurations" element={<MyConfigurations />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
