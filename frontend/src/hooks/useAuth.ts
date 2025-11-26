import { useState } from 'react';
import { User, LoginCredentials } from '../types';
import { AuthService } from '../services/authService';
import { apiService } from '../services/apiService';

export function useAuth() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      const user = await AuthService.login(credentials);
      if (user) {
        setCurrentUser(user);
        return true;
      }
      setError('Invalid credentials');
      return false;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    AuthService.logout();
    setCurrentUser(null);
  };

  const updateUser = async (name: string, email: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      const updatedUser = await apiService.updateProfile(name, email);
      setCurrentUser(updatedUser);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      const user = await AuthService.register(email, password, name);
      if (user) {
        setCurrentUser(user);
        return true;
      }
      setError('Registration failed');
      return false;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    currentUser,
    login,
    logout,
    updateUser,
    register,
    isAuthenticated: !!currentUser,
    isLoading,
    error,
  };
}
