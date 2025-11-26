/**
 * API Configuration
 */
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
} as const;

/**
 * Application Configuration
 */
export const APP_CONFIG = {
  name: 'ChatBotAI',
  version: '1.0.0',
  environment: import.meta.env.VITE_ENV || 'development',
} as const;

/**
 * Route Paths
 */
export const ROUTES = {
  LOGIN: '/login',
  SIGNUP: '/signup',
  DASHBOARD: '/dashboard',
  ADMIN: '/admin',
  PROFILE: '/profile',
} as const;
