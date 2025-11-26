import { apiService } from './apiService';
import { User, LoginCredentials } from '../types';

export class AuthService {
  /**
   * Authenticate user with email and password
   * @param credentials - Login credentials
   * @returns User object if authentication successful, null otherwise
   */
  static async login(credentials: LoginCredentials): Promise<User | null> {
    try {
      const { user } = await apiService.login(credentials);
      return user;
    } catch (error) {
      console.error('Login failed:', error);
      return null;
    }
  }

  /**
   * Register a new user
   * @param email - User email
   * @param password - User password
   * @param name - User name
   * @returns User if registration successful, null otherwise
   */
  static async register(email: string, password: string, name: string): Promise<User | null> {
    try {
      const user = await apiService.register(email, password, name);
      return user;
    } catch (error) {
      console.error('Registration failed:', error);
      return null;
    }
  }

  /**
   * Logout user
   */
  static logout(): void {
    apiService.logout();
  }

  /**
   * Validate email format
   * @param email - Email to validate
   * @returns true if email is valid
   */
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate password strength
   * @param password - Password to validate
   * @returns true if password meets requirements
   */
  static isValidPassword(password: string): boolean {
    return password.length >= 6;
  }
}
