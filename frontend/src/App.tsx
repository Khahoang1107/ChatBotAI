import { useState } from 'react';
import { Toaster } from 'sonner';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { UserDashboard } from './pages/UserDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { useAuth } from './hooks/useAuth';
import { PageType } from './types';

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('login');
  const { currentUser, login, logout, updateUser } = useAuth();

  const handleLogin = async (email: string, password: string): Promise<boolean> => {
    return await login({ email, password });
  };

  const handleLogout = () => {
    logout();
    setCurrentPage('login');
  };

  // If user is logged in, show appropriate dashboard
  if (currentUser) {
    if (currentUser.role === 'admin') {
      return (
        <>
          <Toaster position="top-right" richColors expand={true} />
          <AdminDashboard user={currentUser} onLogout={handleLogout} />
        </>
      );
    } else {
      return (
        <>
          <Toaster position="top-right" richColors expand={true} />
          <UserDashboard 
            user={currentUser} 
            onLogout={handleLogout} 
            onUpdateUser={updateUser} 
          />
        </>
      );
    }
  }

  // Show login or signup page
  return (
    <>
      <Toaster position="top-right" richColors expand={true} />
      {currentPage === 'login' ? (
        <LoginPage 
          onNavigateToSignup={() => setCurrentPage('signup')}
          onLogin={handleLogin}
        />
      ) : (
        <SignupPage onNavigateToLogin={() => setCurrentPage('login')} />
      )}
    </>
  );
}
