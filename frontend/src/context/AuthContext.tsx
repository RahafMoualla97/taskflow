import { createContext, useState, useContext, useEffect } from 'react';
import apiClient from '../api/client';
import type { User, AuthContextType } from '../types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await apiClient.get('/auth/users/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    await fetchUser();
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const googleLogin = () => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    window.location.href = `${apiUrl}/auth/google`;
  };

  const updateUser = async (data: { name?: string; avatar_url?: string }) => {
    try {
      const response = await apiClient.put('/auth/users/me', {
        name: data.name,
        avatar_url: data.avatar_url
      });
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Update user error:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      login, 
      logout, 
      googleLogin,
      updateUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};