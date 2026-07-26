import React, { createContext, useState, useContext } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [usuario, setUsuario] = useState(authService.getUsuarioActual());

  const login = async (correo, password) => {
    const data = await authService.login(correo, password);
    // Solo actualizamos el estado si el login fue completo (no 2FA pendiente)
    if (!data?.requiere_2fa) {
      setUsuario(authService.getUsuarioActual());
    }
    return data;
  };

  const verificarCodigo2FA = async (correo, codigo) => {
    const data = await authService.verificarCodigo2FA(correo, codigo);
    setUsuario(authService.getUsuarioActual());
    return data;
  };

  const logout = () => {
    authService.logout();
    setUsuario(null);
  };

  const value = {
    usuario,
    login,
    verificarCodigo2FA,
    logout,
    isAuthenticated: !!usuario,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
