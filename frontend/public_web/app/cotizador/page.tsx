'use client';

import { useState, useEffect, useRef } from 'react';
import { apiClient, type PartidaArancelaria, type QuoteCalculation, type QuoteRequest } from '@/lib/api';
import { quoteStorage } from '@/lib/quoteStorage';
import Header from '@/components/Header';
import QuoteResults from '@/components/QuoteResults';

export default function CotizadorPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PartidaArancelaria[]>([]);
  const [selectedPartida, setSelectedPartida] = useState<PartidaArancelaria | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [quoteResult, setQuoteResult] = useState<QuoteCalculation | null>(null);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const [formData, setFormData] = useState({
    descripcion_original: '',
    valor: '',
    peso: '',
    unidad_peso: 'lb' as 'lb' | 'kg',
    largo: '',
    ancho: '',
    alto: '',
  });

  // Load stored quote on mount
  useEffect(() => {
    const storedQuote = quoteStorage.getQuote();
    if (storedQuote) {
      setQuoteResult(storedQuote);

      // Optionally restore form data from stored request
      const storedRequest = quoteStorage.getRequest();
      if (storedRequest) {
        setFormData({
          descripcion_original: storedRequest.descripcion_original,
          valor: storedRequest.valor.toString(),
          peso: storedRequest.peso.toString(),
          unidad_peso: storedRequest.unidad_peso,
          largo: storedRequest.largo?.toString() || '',
          ancho: storedRequest.ancho?.toString() || '',
          alto: storedRequest.alto?.toString() || '',
        });
      }
    }
  }, []);

  // Debounced search
  useEffect(() => {
    if (searchQuery.length < 3) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      const results = await apiClient.searchPartidas(searchQuery);
      setSearchResults(results);
      setShowSearchResults(true);
      setIsSearching(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Auto-fill search query when description changes
  useEffect(() => {
    if (formData.descripcion_original && !selectedPartida) {
      setSearchQuery(formData.descripcion_original);
    }
  }, [formData.descripcion_original, selectedPartida]);

  // Click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Parse hierarchical partida description
  // Format: "Partida name | Parent partida name | Grandparent Partida name"
  // Display: Grandparent (if exists), then Parent indented, then Partida indented more
  const parsePartidaHierarchy = (descripcion: string) => {
    const parts = descripcion.split("|").map(p => p.trim()).filter(p => p);

    if (parts.length === 0) return null;

    // parts[0] = Partida, parts[1] = Parent, parts[2] = Grandparent
    return {
      partida: parts[0] || "",
      parent: parts[1] || null,
      grandparent: parts[2] || null,
    };
  };


  // Handle weight unit conversion
  const handleWeightUnitChange = (newUnit: 'lb' | 'kg') => {
    const currentPeso = parseFloat(formData.peso);
    if (!isNaN(currentPeso) && currentPeso > 0) {
      let convertedPeso = currentPeso;
      if (newUnit === 'kg' && formData.unidad_peso === 'lb') {
        convertedPeso = currentPeso * 0.453592;
      } else if (newUnit === 'lb' && formData.unidad_peso === 'kg') {
        convertedPeso = currentPeso * 2.20462;
      }
      setFormData({
        ...formData,
        peso: convertedPeso.toFixed(2),
        unidad_peso: newUnit,
      });
    } else {
      setFormData({ ...formData, unidad_peso: newUnit });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedPartida) {
      alert('Por favor selecciona una partida arancelaria');
      return;
    }

    setIsCalculating(true);
    setQuoteResult(null);

    const quoteRequest: QuoteRequest = {
      valor: parseFloat(formData.valor),
      peso: parseFloat(formData.peso),
      unidad_peso: formData.unidad_peso,
      largo: parseFloat(formData.largo),
      ancho: parseFloat(formData.ancho),
      alto: parseFloat(formData.alto),
      descripcion_original: formData.descripcion_original,
      partida_arancelaria: selectedPartida.id,
    };

    try {
      const quote = await apiClient.calculateQuote(quoteRequest);

      if (quote) {
        // Add partida_arancelaria_id to quote for shipping request
        quote.partida_arancelaria_id = selectedPartida.id;
        setQuoteResult(quote);

        // Save quote to session storage
        quoteStorage.save(quote, quoteRequest);

        setTimeout(() => {
          document.getElementById('quote-results')?.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }, 100);
      } else {
        alert('Error al calcular la cotización. Por favor intenta de nuevo.');
      }
    } catch (error) {
      console.error('Error calculating quote:', error);
      alert('Error al calcular la cotización. Por favor intenta de nuevo.');
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Header />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6">
          {/* Title */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2 text-gray-900 dark:text-white">Cotizador de Envíos</h2>
            <p className="text-gray-600 dark:text-gray-400">
              Calcula el costo de tu envío desde USA a Honduras en segundos
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6" suppressHydrationWarning>
            {/* Item Description */}
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                Descripción del Producto
              </label>
              <input
                type="text"
                placeholder="Ej: Laptop Dell, Zapatillas Nike, etc."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                value={formData.descripcion_original}
                onChange={(e) =>
                  setFormData({ ...formData, descripcion_original: e.target.value })
                }
                required
                suppressHydrationWarning
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Ingrese la descripción exacta del producto
              </p>
            </div>

            {/* Tariff Classification Search */}
            <div className="relative" ref={searchRef}>
              <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                Partida Arancelaria
              </label>
              <input
                type="text"
                placeholder="Buscar partida arancelaria..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => searchResults.length > 0 && setShowSearchResults(true)}
                required
                suppressHydrationWarning
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Busque por código o descripción (mínimo 3 caracteres)
              </p>

              {/* Search Results Dropdown */}
              {showSearchResults && (isSearching || searchResults.length > 0) && (
                <div className="absolute z-10 w-full mt-2 bg-white dark:bg-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600">
                  {isSearching ? (
                    <div className="flex justify-center p-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                  ) : (
                    <ul className="py-2">
                      {searchResults.map((partida) => (
                        <li key={partida.id}>
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedPartida(partida);
                              setSearchQuery(`${partida.item_no} - ${partida.descripcion}`);
                              setShowSearchResults(false);
                            }}
                            className="w-full text-left px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                          >
                            <div className="font-mono font-semibold text-sm text-gray-900 dark:text-white mb-1">{partida.item_no}</div>
                            <div className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                              {(() => {
                                const hierarchy = parsePartidaHierarchy(partida.descripcion);
                                if (!hierarchy) return partida.descripcion;

                                return (
                                  <div className="space-y-0.5">
                                    {hierarchy.grandparent && (
                                      <div className="font-normal">{hierarchy.grandparent}</div>
                                    )}
                                    {hierarchy.parent && (
                                      <div className="pl-2 font-normal">{hierarchy.parent}</div>
                                    )}
                                    <div className={`font-semibold ${hierarchy.parent ? "pl-4" : hierarchy.grandparent ? "pl-2" : ""}`}>
                                      {hierarchy.partida}
                                    </div>
                                  </div>
                                );
                              })()}
                            </div>
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {/* Selected Partida */}
              {selectedPartida && !showSearchResults && (
                <div className="mt-2 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-lg flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-green-600 dark:text-green-400"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span className="text-green-800 dark:text-green-200">
                    Partida seleccionada: <strong className="font-mono">{selectedPartida.item_no}</strong>
                  </span>
                </div>
              )}
            </div>

            {/* Valor, Peso and Unidad in same row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Value */}
              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                  Valor (USD)
                </label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 text-sm text-gray-900 bg-gray-200 border border-r-0 border-gray-300 rounded-l-lg dark:bg-gray-600 dark:text-gray-400 dark:border-gray-600">
                    $
                  </span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    className="rounded-none rounded-r-lg flex-1 min-w-0 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                    value={formData.valor}
                    onChange={(e) =>
                      setFormData({ ...formData, valor: e.target.value })
                    }
                    required
                    suppressHydrationWarning
                  />
                </div>
              </div>

              {/* Peso */}
              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                  Peso
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                  value={formData.peso}
                  onChange={(e) =>
                    setFormData({ ...formData, peso: e.target.value })
                  }
                  required
                  suppressHydrationWarning
                />
              </div>

              {/* Unidad - Label above, value below */}
              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                  Unidad
                </label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  value={formData.unidad_peso}
                  onChange={(e) =>
                    handleWeightUnitChange(e.target.value as 'lb' | 'kg')
                  }
                  suppressHydrationWarning
                >
                  <option value="lb">Libras (lb)</option>
                  <option value="kg">Kilogramos (kg)</option>
                </select>
              </div>
            </div>

            {/* Dimensions Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                  Largo (pulgadas)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  placeholder="0.0"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                  value={formData.largo}
                  onChange={(e) =>
                    setFormData({ ...formData, largo: e.target.value })
                  }
                  required
                  suppressHydrationWarning
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                  Ancho (pulgadas)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  placeholder="0.0"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                  value={formData.ancho}
                  onChange={(e) =>
                    setFormData({ ...formData, ancho: e.target.value })
                  }
                  required
                  suppressHydrationWarning
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                  Alto (pulgadas)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  placeholder="0.0"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                  value={formData.alto}
                  onChange={(e) =>
                    setFormData({ ...formData, alto: e.target.value })
                  }
                  required
                  suppressHydrationWarning
                />
              </div>
            </div>

            {/* Submit Button */}
            <div className="mt-8">
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isCalculating}
                suppressHydrationWarning
              >
                {isCalculating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Calculando...</span>
                  </>
                ) : (
                  <>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                      />
                    </svg>
                    <span>Calcular Cotización</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Quote Results */}
        {quoteResult && (
          <div id="quote-results">
            <QuoteResults quote={quoteResult} />
          </div>
        )}
      </div>
    </div>
  );
}
