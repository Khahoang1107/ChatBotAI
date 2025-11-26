// User Types
export type UserRole = 'admin' | 'user';

export interface User {
  email: string;
  name: string;
  role: UserRole;
}

export interface Account extends User {
  password: string;
}

// Page Types
export type PageType = 'login' | 'signup';

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData extends LoginCredentials {
  name: string;
  confirmPassword: string;
}

// Dashboard Types
export interface DashboardProps {
  user: User;
  onLogout: () => void;
}

export interface UserDashboardProps extends DashboardProps {
  onUpdateUser: (name: string, email: string) => void;
}
