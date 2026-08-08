import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import Login from './pages/Login';
import Registro from './pages/Registro';
import Dashboard from './pages/Dashboard';
import ConfigurarDosFactor from './pages/ConfigurarDosFactor';
import PersonalizarPanel from './pages/PersonalizarPanel';

import Historial from './pages/Historial';

const App = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/" element={
        isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
      } />
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
      } />
      <Route path="/registro" element={
        isAuthenticated ? <Navigate to="/dashboard" replace /> : <Registro />
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/personalizar" element={
        <ProtectedRoute>
          <PersonalizarPanel />
        </ProtectedRoute>
      } />
      <Route path="/historial" element={
        <ProtectedRoute>
          <Historial />
        </ProtectedRoute>
      } />
      <Route path="/2fa/configurar" element={
        <ProtectedRoute>
          <ConfigurarDosFactor />
        </ProtectedRoute>
      } />
    </Routes>
  );
};

export default App;
