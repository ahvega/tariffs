// API client for Django backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PartidaArancelaria {
  id: number;
  item_no: string;
  descripcion: string;
  impuesto_dai?: number;
  impuesto_isc?: number;
  impuesto_ispc?: number;
  impuesto_isv?: number;
  courier_category?: 'ALLOWED' | 'RESTRICTED' | 'PROHIBITED';
  search_keywords?: string[];
}

// Response from search endpoint
interface SearchResult {
  id: string;
  text: string;
  codigo: string;
  descripcion: string;
  keywords: string[];
  score: number;
}

export interface QuoteCalculation {
  valor_declarado: number;
  valor_cif: number;
  peso: number;  // Peso in lbs (converted if needed)
  peso_original: number;  // Original peso submitted
  unidad_peso: 'lb' | 'kg';  // Original unit submitted
  peso_volumetrico: number;
  peso_a_usar: number;
  largo: number;
  ancho: number;
  alto: number;
  factor_volumetrico: number;
  costo_por_libra: string;
  impuesto_dai: number;
  impuesto_isc: number;
  impuesto_ispc: number;
  impuestos_importacion: number;
  impuesto_isv: number;
  costo_transporte: number;
  cargos_totales: number;
  total_incluido_valor: number;
  porcentaje_dai: string;
  porcentaje_isc: string;
  porcentaje_ispc: string;
  porcentaje_isv: string;
  partida_item_no: string;
  partida_descripcion: string;
  partida_arancelaria_numero: string;
  descripcion_original: string;
}

export interface QuoteRequest {
  valor: number;
  peso: number;
  unidad_peso: 'lb' | 'kg';
  largo?: number;
  ancho?: number;
  alto?: number;
  descripcion_original: string;
  partida_arancelaria: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async searchPartidas(query: string): Promise<PartidaArancelaria[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/MiCasillero/buscar-partidas/?q=${encodeURIComponent(query)}`
      );

      if (!response.ok) {
        throw new Error('Error searching partidas');
      }

      const data: { results: SearchResult[] } = await response.json();

      // Convert search results to PartidaArancelaria format and sort by relevance score (descending)
      return data.results
        .sort((a, b) => b.score - a.score)
        .map(result => ({
          id: parseInt(result.id),
          item_no: result.codigo,
          descripcion: result.descripcion,
          search_keywords: result.keywords,
        }));
    } catch (error) {
      console.error('Error searching partidas:', error);
      return [];
    }
  }

  async calculateQuote(quoteRequest: QuoteRequest): Promise<QuoteCalculation | null> {
    try {
      const response = await fetch(`${this.baseUrl}/MiCasillero/cotizar-json/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(quoteRequest),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error calculating quote:', errorData);
        throw new Error(errorData.error || 'Error calculating quote');
      }

      const data: { success: boolean; data: QuoteCalculation } = await response.json();

      if (data.success) {
        return data.data;
      } else {
        throw new Error('Quote calculation failed');
      }
    } catch (error) {
      console.error('Error calculating quote:', error);
      return null;
    }
  }

  async getAllowedPartidas(): Promise<PartidaArancelaria[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/PartidaArancelaria/?courier_category=ALLOWED&page_size=100`
      );

      if (!response.ok) {
        throw new Error('Error fetching partidas');
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Error fetching partidas:', error);
      return [];
    }
  }

  // Authentication methods
  async register(registerData: RegisterRequest): Promise<AuthResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error registering user:', errorData);
        throw new Error(JSON.stringify(errorData));
      }

      return await response.json();
    } catch (error) {
      console.error('Error registering user:', error);
      return null;
    }
  }

  async login(loginData: LoginRequest): Promise<AuthResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error logging in:', errorData);
        throw new Error(JSON.stringify(errorData));
      }

      return await response.json();
    } catch (error) {
      console.error('Error logging in:', error);
      return null;
    }
  }

  async getCurrentUser(accessToken: string): Promise<User | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/me/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Error fetching current user');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching current user:', error);
      return null;
    }
  }

  async refreshToken(refreshToken: string): Promise<{ access: string } | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Error refreshing token');
      }

      return await response.json();
    } catch (error) {
      console.error('Error refreshing token:', error);
      return null;
    }
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
