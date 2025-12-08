import { API_CONFIG } from '../constants/config';
import type { User, LoginCredentials } from '../types';

/**
 * API Service for backend communication
 */
class APIService {
  private baseURL: string;
  private timeout: number;

  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.timeout = API_CONFIG.timeout;
  }

  /**
   * Make HTTP request with timeout
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  }

  /**
   * Register new user
   */
  async register(data: { email: string; password: string; name?: string }): Promise<{ user: User; token: string }> {
    const response = await this.request<{ access_token: string; token_type: string; user: User }>(
      '/api/auth/register',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
    
    // Store token
    localStorage.setItem('token', response.access_token);
    
    return {
      user: response.user,
      token: response.access_token,
    };
  }

  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    const response = await this.request<{ access_token: string; token_type: string; user: User }>(
      '/api/auth/login',
      {
        method: 'POST',
        body: JSON.stringify(credentials),
      }
    );

    // Store token in localStorage
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
    }

    return {
      user: response.user,
      token: response.access_token,
    };
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('token');
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    return await this.request<User>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  /**
   * Update user profile
   */
  async updateProfile(name: string, email: string): Promise<User> {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    return await this.request<User>('/api/auth/profile', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name, email }),
    });
  }

  /**
   * Upload invoice image for OCR processing
   */
  async uploadInvoice(file: File): Promise<any> {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseURL}/api/upload`, {
        method: 'POST',
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(error.detail || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Upload timeout');
        }
        throw error;
      }
      throw new Error('Upload failed');
    }
  }

  /**
   * Get invoices list
   */
  async getInvoices(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<{ invoices: any[]; total: number }> {
    const token = localStorage.getItem('token');
    const queryParams = new URLSearchParams();
    
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);

    const endpoint = `/api/invoices${queryParams.toString() ? `?${queryParams}` : ''}`;

    return await this.request(endpoint, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
  }

  /**
   * Get invoice statistics
   */
  async getInvoiceStats(): Promise<{
    total: number;
    processed: number;
    pending: number;
    failed: number;
  }> {
    const token = localStorage.getItem('token');
    
    return await this.request('/api/invoices/stats', {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
  }

  /**
   * Send chat message
   */
  async sendChatMessage(message: string): Promise<{ response: string }> {
    const token = localStorage.getItem('token');
    
    return await this.request('/api/chat', {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ message }),
    });
  }

  /**
   * Check backend health
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    return await this.request('/health');
  }
}

export const apiService = new APIService();
export default apiService;
