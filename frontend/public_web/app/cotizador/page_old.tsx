'use client';

import { useState, useEffect } from 'react';
import { apiClient, type PartidaArancelaria, type QuoteCalculation } from '@/lib/api';
import ThemeToggle from '@/components/ThemeToggle';
import QuoteResults from '@/components/QuoteResults';

export default function CotizadorPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PartidaArancelaria[]>([]);
  const [selectedPartida, setSelectedPartida] = useState<PartidaArancelaria | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [quoteResult, setQuoteResult] = useState<QuoteCalculation | null>(null);

  const [formData, setFormData] = useState({
    descripcion_original: '',
    valor: '',
    peso: '',
    unidad_peso: 'lb' as 'lb' | 'kg',
    largo: '',
    ancho: '',
    alto: '',
  });

  const [showResults, setShowResults] = useState(false);

  // Debounced search
  useEffect(() => {
    if (searchQuery.length < 3) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      const results = await apiClient.searchPartidas(searchQuery);
      setSearchResults(results);
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

  // Handle weight unit conversion
  const handleWeightUnitChange = (newUnit: 'lb' | 'kg') => {
    const currentPeso = parseFloat(formData.peso);
    if (!isNaN(currentPeso) && currentPeso > 0) {
      let convertedPeso = currentPeso;
      if (newUnit === 'kg' && formData.unidad_peso === 'lb') {
        // Convert lb to kg
        convertedPeso = currentPeso * 0.453592;
      } else if (newUnit === 'lb' && formData.unidad_peso === 'kg') {
        // Convert kg to lb
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

    try {
      const quote = await apiClient.calculateQuote({
        valor: parseFloat(formData.valor),
        peso: parseFloat(formData.peso),
        unidad_peso: formData.unidad_peso,
        largo: formData.largo ? parseFloat(formData.largo) : undefined,
        ancho: formData.ancho ? parseFloat(formData.ancho) : undefined,
        alto: formData.alto ? parseFloat(formData.alto) : undefined,
        descripcion_original: formData.descripcion_original,
        partida_arancelaria: selectedPartida.id,
      });

      if (quote) {
        setQuoteResult(quote);
        // Scroll to results
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
    <div className="min-h-screen bg-base-200">
      {/* Header */}
      <div className="navbar bg-base-100 shadow-lg">
        <div className="flex-1">
          <a className="btn btn-ghost text-xl font-bold">
            SicargaBox
          </a>
        </div>
        <div className="flex-none">
          <ThemeToggle />
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="card bg-base-100 shadow-xl max-w-4xl mx-auto">
          <div className="card-body">
            {/* Title */}
            <div className="text-center mb-6">
              <h1 className="text-3xl font-bold mb-2">Cotizador de Envíos</h1>
              <p className="text-base-content/70">
                Calcula el costo de tu envío desde USA a Honduras en segundos
              </p>
            </div>

            {/* Stats */}
            <div className="stats stats-vertical lg:stats-horizontal shadow mb-6">
              <div className="stat">
                <div className="stat-title">Disponibles</div>
                <div className="stat-value text-success">4,682</div>
                <div className="stat-desc">Partidas permitidas</div>
              </div>
              <div className="stat">
                <div className="stat-title">Restringidas</div>
                <div className="stat-value text-warning">1,771</div>
                <div className="stat-desc">Requieren permiso</div>
              </div>
              <div className="stat">
                <div className="stat-title">Prohibidas</div>
                <div className="stat-value text-error">1,073</div>
                <div className="stat-desc">No permitidas</div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Item Description */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">
                    Descripción del Producto
                  </span>
                </label>
                <input
                  type="text"
                  placeholder="Ej: Laptop Dell, Zapatillas Nike, etc."
                  className="input input-bordered"
                  value={formData.descripcion_original}
                  onChange={(e) =>
                    setFormData({ ...formData, descripcion_original: e.target.value })
                  }
                  required
                />
                <label className="label">
                  <span className="label-text-alt">
                    Ingrese la descripción exacta del producto
                  </span>
                </label>
              </div>

              {/* Tariff Classification Search */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">
                    Partida Arancelaria
                  </span>
                </label>
                <input
                  type="text"
                  placeholder="Buscar partida arancelaria..."
                  className="input input-bordered"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  required
                />
                <label className="label">
                  <span className="label-text-alt">
                    Busque por código o descripción (mínimo 3 caracteres)
                  </span>
                </label>

                {/* Search Results Dropdown */}
                {(isSearching || searchResults.length > 0) && (
                  <div className="mt-2 card bg-base-200 shadow-lg max-h-60 overflow-y-auto">
                    <div className="card-body p-2">
                      {isSearching ? (
                        <div className="flex justify-center p-4">
                          <span className="loading loading-spinner loading-md"></span>
                        </div>
                      ) : (
                        <ul className="menu">
                          {searchResults.map((partida) => (
                            <li key={partida.id}>
                              <button
                                type="button"
                                onClick={() => {
                                  setSelectedPartida(partida);
                                  setSearchQuery(`${partida.item_no} - ${partida.descripcion}`);
                                  setSearchResults([]);
                                }}
                                className="text-left"
                              >
                                <div>
                                  <div className="font-semibold">{partida.item_no}</div>
                                  <div className="text-sm opacity-70">
                                    {partida.descripcion}
                                  </div>
                                </div>
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )}

                {/* Selected Partida */}
                {selectedPartida && (
                  <div className="alert alert-success mt-2">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="stroke-current shrink-0 h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span>
                      Partida seleccionada: <strong>{selectedPartida.item_no}</strong>
                    </span>
                  </div>
                )}
              </div>

              {/* Value and Weight Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Valor (USD)</span>
                  </label>
                  <label className="input-group">
                    <span>$</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="0.00"
                      className="input input-bordered w-full"
                      value={formData.valor}
                      onChange={(e) =>
                        setFormData({ ...formData, valor: e.target.value })
                      }
                      required
                    />
                  </label>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Peso</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    className="input input-bordered"
                    value={formData.peso}
                    onChange={(e) =>
                      setFormData({ ...formData, peso: e.target.value })
                    }
                    required
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Unidad</span>
                  </label>
                  <select
                    className="select select-bordered"
                    value={formData.unidad_peso}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        unidad_peso: e.target.value as 'lb' | 'kg',
                      })
                    }
                  >
                    <option value="lb">Libras (lb)</option>
                    <option value="kg">Kilogramos (kg)</option>
                  </select>
                </div>
              </div>

              {/* Dimensions Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Largo (pulgadas)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    placeholder="0.0"
                    className="input input-bordered"
                    value={formData.largo}
                    onChange={(e) =>
                      setFormData({ ...formData, largo: e.target.value })
                    }
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Ancho (pulgadas)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    placeholder="0.0"
                    className="input input-bordered"
                    value={formData.ancho}
                    onChange={(e) =>
                      setFormData({ ...formData, ancho: e.target.value })
                    }
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Alto (pulgadas)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    placeholder="0.0"
                    className="input input-bordered"
                    value={formData.alto}
                    onChange={(e) =>
                      setFormData({ ...formData, alto: e.target.value })
                    }
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="form-control mt-6">
                <button
                  type="submit"
                  className="btn btn-primary btn-lg"
                  disabled={isCalculating}
                >
                  {isCalculating ? (
                    <>
                      <span className="loading loading-spinner"></span>
                      Calculando...
                    </>
                  ) : (
                    'Calcular Cotización'
                  )}
                </button>
              </div>
            </form>
          </div>
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
