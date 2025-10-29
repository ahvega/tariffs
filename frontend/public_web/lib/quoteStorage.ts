// Quote session storage utilities
import { QuoteCalculation, QuoteRequest } from './api';

const QUOTE_KEY = 'sicargabox_quote';
const QUOTE_REQUEST_KEY = 'sicargabox_quote_request';

export interface StoredQuote {
  quote: QuoteCalculation;
  request: QuoteRequest;
  timestamp: number;
  expiresAt: number;
}

const QUOTE_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

export const quoteStorage = {
  /**
   * Save a quote and its request to session storage
   */
  save(quote: QuoteCalculation, request: QuoteRequest): void {
    if (typeof window === 'undefined') return;

    const now = Date.now();
    const storedQuote: StoredQuote = {
      quote,
      request,
      timestamp: now,
      expiresAt: now + QUOTE_EXPIRY_MS,
    };

    try {
      sessionStorage.setItem(QUOTE_KEY, JSON.stringify(storedQuote));
    } catch (error) {
      console.error('Error saving quote to session storage:', error);
    }
  },

  /**
   * Retrieve the stored quote if it exists and hasn't expired
   */
  get(): StoredQuote | null {
    if (typeof window === 'undefined') return null;

    try {
      const stored = sessionStorage.getItem(QUOTE_KEY);
      if (!stored) return null;

      const storedQuote: StoredQuote = JSON.parse(stored);

      // Check if expired
      if (Date.now() > storedQuote.expiresAt) {
        this.clear();
        return null;
      }

      return storedQuote;
    } catch (error) {
      console.error('Error retrieving quote from session storage:', error);
      return null;
    }
  },

  /**
   * Clear the stored quote
   */
  clear(): void {
    if (typeof window === 'undefined') return;

    try {
      sessionStorage.removeItem(QUOTE_KEY);
      sessionStorage.removeItem(QUOTE_REQUEST_KEY);
    } catch (error) {
      console.error('Error clearing quote from session storage:', error);
    }
  },

  /**
   * Check if a quote is stored
   */
  has(): boolean {
    return this.get() !== null;
  },

  /**
   * Get the quote calculation only
   */
  getQuote(): QuoteCalculation | null {
    const stored = this.get();
    return stored?.quote || null;
  },

  /**
   * Get the quote request only
   */
  getRequest(): QuoteRequest | null {
    const stored = this.get();
    return stored?.request || null;
  },
};
