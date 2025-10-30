'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { QuoteCalculation, apiClient, User } from '@/lib/api';
import { quoteStorage } from '@/lib/quoteStorage';
import ShippingAddressDisplay from './ShippingAddressDisplay';

interface QuoteResultsProps {
  quote: QuoteCalculation;
}

export default function QuoteResults({ quote }: QuoteResultsProps) {
  const router = useRouter();
  const { data: session, status } = useSession();

  // State for address display
  const [showAddress, setShowAddress] = useState(false);
  const [clienteInfo, setClienteInfo] = useState<{
    nombre_completo: string;
    codigo_cliente: string;
  } | null>(null);
  const [consolidatorAddress, setConsolidatorAddress] = useState<string>('');
  const [addressLoading, setAddressLoading] = useState(false);

  // Fetch address data for authenticated users
  useEffect(() => {
    const fetchAddressData = async () => {
      if (status === 'authenticated' && session) {
        try {
          setAddressLoading(true);
          const accessToken = (session as any).accessToken;

          if (!accessToken) return;

          // Fetch current user with cliente info
          const userData = await apiClient.getCurrentUser(accessToken) as User & {
            cliente?: {
              id: number;
              codigo_cliente: string;
              nombre_completo: string;
            };
          };

          if (userData && userData.cliente) {
            setClienteInfo({
              nombre_completo: userData.cliente.nombre_completo,
              codigo_cliente: userData.cliente.codigo_cliente,
            });

            // Fetch system parameters
            const parametros = await apiClient.getParametrosSistema(accessToken);
            if (parametros) {
              setConsolidatorAddress(parametros.direccion_consolidador);

              // Check localStorage to auto-expand on first view
              const hasSeenAddress = localStorage.getItem('hasSeenMiamiAddress');
              if (!hasSeenAddress) {
                setShowAddress(true);
                localStorage.setItem('hasSeenMiamiAddress', 'true');
              }
            }
          }
        } catch (err) {
          console.error('Error fetching address data:', err);
        } finally {
          setAddressLoading(false);
        }
      }
    };

    fetchAddressData();
  }, [status, session]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatWeight = (value: number) => {
    return new Intl.NumberFormat('es-HN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

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

  const formatPartidaBreadcrumb = () => {
    const hierarchy = parsePartidaHierarchy(quote.partida_descripcion);

    if (!hierarchy) return null;

    const parts = [];
    if (hierarchy.grandparent) parts.push(hierarchy.grandparent);
    if (hierarchy.parent) parts.push(hierarchy.parent);
    parts.push(hierarchy.partida);

    return parts.map((part, index) => {
      const isLast = index === parts.length - 1;
      return (
        <span key={index}>
          {isLast ? <strong><small>{part}</small></strong> : <small>{part}</small>}
          {!isLast && <span className="mx-1">›</span>}
        </span>
      );
    });
  };

  // Handle "Aceptar y Continuar" button click
  const handleAcceptQuote = () => {
    if (session?.user) {
      // Authenticated: go to shipping request (to be implemented in Phase 4.4)
      router.push('/envio/crear');
    } else {
      // Not authenticated: go to login
      router.push('/login');
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
        Resultado de la Cotización
      </h2>

      {/* Main Summary */}
      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg">
        <div className="flex items-center gap-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            className="w-6 h-6 stroke-blue-600 dark:stroke-blue-400"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <div>
            <h3 className="font-bold text-gray-700 dark:text-gray-300">Total a Pagar</h3>
            <div className="font-mono text-3xl font-bold text-blue-600 dark:text-blue-400">
              {formatCurrency(quote.cargos_totales)}
            </div>
          </div>
        </div>
      </div>

      {/* Product Info */}
      <div className="mb-6">
        <h3 className="font-semibold text-lg mb-3 text-gray-900 dark:text-white">
          Información del Producto
        </h3>
        <div className="space-y-0">
          <div className="flex justify-between py-3 border-b border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Descripción:</span>
            <div className="font-medium text-right text-gray-900 dark:text-white">
              {quote.descripcion_original}
            </div>
          </div>
          <div className="py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Partida Arancelaria:</span>
              <div className="font-medium font-mono text-gray-900 dark:text-white">{quote.partida_item_no}</div>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {formatPartidaBreadcrumb()}
            </div>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Valor Declarado:</span>
            <div className="font-medium font-mono text-gray-900 dark:text-white">
              {formatCurrency(quote.valor_declarado)}
            </div>
          </div>
          <div className="py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Peso a Usar:</span>
              <div className="font-medium font-mono text-gray-900 dark:text-white">
                {formatWeight(quote.peso_a_usar)} lb
              </div>
            </div>
            <div className="text-sm font-mono text-gray-500 dark:text-gray-400 mt-1">
              {quote.peso_a_usar === quote.peso ? (
                'Peso Declarado'
              ) : (
                `Peso Volumétrico = ${formatWeight(quote.largo)} × ${formatWeight(quote.ancho)} × ${formatWeight(quote.alto)} ÷ ${quote.factor_volumetrico}`
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="mb-6">
        <h3 className="font-semibold text-lg mb-3 text-gray-900 dark:text-white border-t border-gray-200 dark:border-gray-700 pt-4">
          Desglose de Costos
        </h3>

        <div className="space-y-0">
          {/* Transport Cost */}
          <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
            <div>
              <div className="font-medium font-mono text-gray-900 dark:text-white">Costo de Transporte</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {formatWeight(quote.peso_a_usar)} lb × ${quote.costo_por_libra}
              </div>
            </div>
            <div className="font-bold font-mono text-gray-900 dark:text-white">
              {formatCurrency(quote.costo_transporte)}
            </div>
          </div>

          {/* CIF Value */}
          <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
            <div>
              <div className="font-medium font-mono text-gray-900 dark:text-white">Valor CIF</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Valor para cálculo de impuestos
              </div>
            </div>
            <div className="font-bold font-mono text-gray-900 dark:text-white">
              {formatCurrency(quote.valor_cif)}
            </div>
          </div>

          {/* Import Taxes */}
          <div className="py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-gray-900 dark:text-white">Impuestos de Importación</span>
              <span className="font-bold text-gray-900 dark:text-white">
                {formatCurrency(quote.impuestos_importacion)}
              </span>
            </div>
            <div className="pl-4 space-y-2">
              {quote.impuesto_dai > 0 && (
                <div className="flex justify-between text-sm py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="font-mono text-gray-600 dark:text-gray-400">DAI ({quote.porcentaje_dai}%)</span>
                  <span className="font-mono text-gray-900 dark:text-white">{formatCurrency(quote.impuesto_dai)}</span>
                </div>
              )}
              {quote.impuesto_isc > 0 && (
                <div className="flex justify-between text-sm py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="font-mono text-gray-600 dark:text-gray-400">ISC ({quote.porcentaje_isc}%)</span>
                  <span className="font-mono text-gray-900 dark:text-white">{formatCurrency(quote.impuesto_isc)}</span>
                </div>
              )}
              {quote.impuesto_ispc > 0 && (
                <div className="flex justify-between text-sm py-2 border-b border-gray-100 dark:border-gray-700">
                  <span className="font-mono text-gray-600 dark:text-gray-400">ISPC ({quote.porcentaje_ispc}%)</span>
                  <span className="font-mono text-gray-900 dark:text-white">{formatCurrency(quote.impuesto_ispc)}</span>
                </div>
              )}
            </div>
          </div>

          {/* ISV */}
          {quote.impuesto_isv > 0 && (
            <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
              <div>
                <div className="font-medium text-gray-900 dark:text-white">ISV (Impuesto Sobre Ventas)</div>
                <div className="text-sm font-mono text-gray-600 dark:text-gray-400">{quote.porcentaje_isv}%</div>
              </div>
              <div className="font-bold font-mono text-gray-900 dark:text-white">
                {formatCurrency(quote.impuesto_isv)}
              </div>
            </div>
          )}

          {/* Total Charges - HIGHLIGHTED */}
          <div className="flex justify-between items-center p-4 bg-blue-600 dark:bg-blue-700 text-white rounded-lg mt-3">
            <div>
              <div className="font-mono font-bold text-xl">Cargos Totales</div>
              <div className="text-sm opacity-90">
                (Transporte + Impuestos)
              </div>
            </div>
            <div className="font-mono font-bold text-2xl">
              {formatCurrency(quote.cargos_totales)}
            </div>
          </div>

          {/* Grand Total */}
          <div className="flex justify-between items-center p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg mt-3">
            <div>
              <div className="font-mono font-bold text-lg text-gray-900 dark:text-white">Total Incluido Valor</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Valor del producto + cargos
              </div>
            </div>
            <div className="font-mono font-bold text-lg text-gray-900 dark:text-white">
              {formatCurrency(quote.total_incluido_valor)}
            </div>
          </div>
        </div>
      </div>

      {/* Miami Address Section - For Authenticated Users */}
      {status === 'authenticated' && clienteInfo && consolidatorAddress && (
        <div className="mb-6 border-t border-gray-200 dark:border-gray-700 pt-6">
          <button
            onClick={() => setShowAddress(!showAddress)}
            className="w-full flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">📦</span>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  Dirección de tu Casillero en Miami
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Usa esta dirección al realizar tu compra
                </p>
              </div>
            </div>
            <svg
              className={`w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform ${
                showAddress ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAddress && (
            <div className="mt-4 animate-fadeIn">
              <ShippingAddressDisplay
                clientName={clienteInfo.nombre_completo}
                clientCode={clienteInfo.codigo_cliente}
                consolidatorAddress={consolidatorAddress}
                showInstructions={false}
              />
              <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <div className="flex items-start gap-2">
                  <span className="text-xl">⚠️</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      Importante
                    </p>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      Asegúrate de usar esta dirección exactamente como aparece arriba al realizar tu compra.
                      Incluye tu nombre y código de cliente para que podamos identificar tu paquete cuando llegue a Miami.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 mt-6">
        <button
          onClick={() => {
            quoteStorage.clear();
            window.location.reload();
          }}
          className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium"
        >
          Nueva Cotización
        </button>
        <button
          onClick={handleAcceptQuote}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
        >
          Aceptar y Continuar
        </button>
      </div>
    </div>
  );
}
