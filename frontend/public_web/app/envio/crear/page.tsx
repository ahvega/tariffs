'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { quoteStorage } from '@/lib/quoteStorage';
import { QuoteCalculation, apiClient, ParametrosSistema, User } from '@/lib/api';
import { getGoogleMapsUrl, getWazeUrl, getWhatsAppUrl } from '@/lib/addressUtils';
import Header from '@/components/Header';
import ShippingAddressDisplay from '@/components/ShippingAddressDisplay';

export default function ShippingRequestPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [quote, setQuote] = useState<QuoteCalculation | null>(null);
  const [formData, setFormData] = useState({
    us_tracking_number: '',
    direccion: '',
    ciudad: '',
    departamento: '',
    instrucciones_especiales: '',
  });
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parametros, setParametros] = useState<ParametrosSistema | null>(null);
  const [clienteInfo, setClienteInfo] = useState<{
    nombre_completo: string;
    codigo_cliente: string;
  } | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // Check authentication
      if (status === 'unauthenticated') {
        router.push('/login');
        return;
      }

      // Load quote from sessionStorage
      const storedQuote = quoteStorage.getQuote();
      if (!storedQuote) {
        // No quote found, redirect to calculator
        router.push('/cotizador');
        return;
      }

      setQuote(storedQuote);

      // Fetch system parameters and cliente info if authenticated
      if (status === 'authenticated' && session) {
        try {
          const accessToken = (session as any).accessToken;
          if (accessToken) {
            // Fetch system parameters
            const params = await apiClient.getParametrosSistema(accessToken);
            setParametros(params);

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
            }
          }
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      }
    };

    fetchData();
  }, [status, session, router]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate session and access token
      if (!session || !(session as any).accessToken) {
        setError('No se pudo obtener el token de autenticación. Por favor, inicia sesión nuevamente.');
        router.push('/login');
        return;
      }

      // Validate quote data
      if (!quote || !quote.partida_arancelaria_id) {
        setError('Información de cotización incompleta. Por favor, genera una nueva cotización.');
        router.push('/cotizador');
        return;
      }

      const accessToken = (session as any).accessToken;

      // Debug: log token info (remove in production)
      console.log('Session:', session);
      console.log('Access token:', accessToken ? 'exists' : 'missing');

      // Build shipping request
      // If pickup mode (no home delivery), use default address
      const isPickupMode = !parametros?.entrega_a_domicilio;

      const shippingRequest = {
        tracking_number_original: formData.us_tracking_number,
        direccion_entrega: isPickupMode ? 'PICKUP - Recoger en Oficina' : formData.direccion,
        ciudad: isPickupMode ? '' : formData.ciudad,
        departamento: isPickupMode ? '' : formData.departamento,
        instrucciones_especiales: isPickupMode ? '' : formData.instrucciones_especiales,
        factura_compra: invoiceFile,
        // Quote data
        valor_articulo: quote.valor_declarado,
        peso: quote.peso_original,
        largo: quote.largo,
        ancho: quote.ancho,
        alto: quote.alto,
        partida_arancelaria_id: quote.partida_arancelaria_id,
        descripcion_original: quote.descripcion_original,
      };

      // Call API
      const response = await apiClient.createShippingRequest(shippingRequest, accessToken);

      if (response) {
        // Success! Clear quote from storage
        quoteStorage.clear();

        // Build success message based on documentation status
        let successMessage = `¡Solicitud de envío creada exitosamente!\n\nNúmero de Rastreo SicargaBox: ${response.tracking_number_sicarga}\n\n`;

        if (response.estado_envio === 'Documentación Pendiente') {
          successMessage += `📋 Estado: Documentación Pendiente\n\nTu solicitud ha sido registrada. Podrás agregar el número de rastreo de USA y la factura de compra más tarde desde tu dashboard cuando los recibas de tu proveedor.\n\nRecuerda: Una vez que hagas tu compra y recibas el tracking number, regresa para completar tu solicitud.`;
        } else {
          successMessage += `✅ Tu solicitud está completa y en proceso.\n\nPuedes rastrear tu paquete en cualquier momento desde tu dashboard.`;
        }

        alert(successMessage);

        // Redirect to quote calculator
        router.push('/cotizador');
      } else {
        setError('Error al crear la solicitud de envío. Por favor, verifica los datos e intenta nuevamente.');
      }
    } catch (error: any) {
      console.error('Error creating shipping request:', error);

      // Try to parse error message if it's JSON
      let errorMessage = 'Error desconocido al crear la solicitud de envío.';
      try {
        const errorData = JSON.parse(error.message);
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else {
          errorMessage = JSON.stringify(errorData);
        }
      } catch {
        errorMessage = error.message || errorMessage;
      }

      setError(`Error: ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Loading state
  if (status === 'loading' || !quote) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="container mx-auto px-4 max-w-4xl py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Solicitud de Envío
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Complete la información para crear su solicitud de envío
          </p>
        </div>

        {/* Quote Summary */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Resumen de Cotización
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Descripción:</span>
              <span className="font-medium text-gray-900 dark:text-white">{quote.descripcion_original}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Partida Arancelaria:</span>
              <span className="font-mono text-gray-900 dark:text-white">{quote.partida_item_no}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Peso:</span>
              <span className="font-mono text-gray-900 dark:text-white">{quote.peso_a_usar.toFixed(2)} lb</span>
            </div>
            <div className="flex justify-between border-t border-gray-200 dark:border-gray-700 pt-3">
              <span className="text-lg font-semibold text-gray-900 dark:text-white">Total a Pagar:</span>
              <span className="text-lg font-bold font-mono text-blue-600 dark:text-blue-400">
                {formatCurrency(quote.cargos_totales)}
              </span>
            </div>
          </div>
        </div>

        {/* Miami Shipping Address */}
        {clienteInfo && parametros?.direccion_consolidador && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              📦 Tu Dirección de Envío en Miami
            </h2>
            <ShippingAddressDisplay
              clientName={clienteInfo.nombre_completo}
              clientCode={clienteInfo.codigo_cliente}
              consolidatorAddress={parametros.direccion_consolidador}
              showInstructions={true}
            />
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-start gap-2">
                <span className="text-xl">ℹ️</span>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Recordatorio Importante
                  </p>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Recuerda usar esta dirección exactamente como aparece arriba al realizar tu compra en USA.
                    Incluye tu nombre completo y código de cliente para que podamos identificar tu paquete cuando llegue a Miami.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">{error}</p>
          </div>
        )}

        {/* Shipping Request Form */}
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Información del Envío
          </h2>

          {/* US Tracking Number */}
          <div className="mb-6">
            <label htmlFor="us_tracking_number" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
              Número de Rastreo (USA) <span className="text-gray-500 dark:text-gray-400 font-normal">(Opcional - puedes agregarlo después)</span>
            </label>
            <input
              type="text"
              id="us_tracking_number"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
              placeholder="Ej: 1Z999AA10123456784"
              value={formData.us_tracking_number}
              onChange={(e) => setFormData({ ...formData, us_tracking_number: e.target.value })}
            />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Número de rastreo proporcionado por el courier en USA (USPS, UPS, FedEx, etc.). Si aún no lo tienes, podrás agregarlo más tarde desde tu dashboard.
            </p>
          </div>

          {/* Purchase Invoice Upload */}
          <div className="mb-6">
            <label htmlFor="invoice" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
              Factura de Compra <span className="text-gray-500 dark:text-gray-400 font-normal">(Opcional - puedes agregarla después)</span>
            </label>
            <input
              type="file"
              id="invoice"
              accept=".pdf,.jpg,.jpeg,.png"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              onChange={(e) => setInvoiceFile(e.target.files?.[0] || null)}
            />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Suba su factura de compra (PDF, JPG, PNG - Máx. 5MB). Si aún no la tienes, podrás agregarla más tarde desde tu dashboard.
            </p>
          </div>

          {/* Delivery Address or Pickup Information */}
          {parametros?.entrega_a_domicilio ? (
            // Show delivery address fields when home delivery is enabled
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Dirección de Entrega en Honduras
              </h3>

              <div className="space-y-4">
                <div>
                  <label htmlFor="direccion" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                    Dirección *
                  </label>
                  <input
                    type="text"
                    id="direccion"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Calle, número, colonia"
                    value={formData.direccion}
                    onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="ciudad" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                      Ciudad *
                    </label>
                    <input
                      type="text"
                      id="ciudad"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Ej: Tegucigalpa"
                      value={formData.ciudad}
                      onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="departamento" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                      Departamento *
                    </label>
                    <input
                      type="text"
                      id="departamento"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Ej: Francisco Morazán"
                      value={formData.departamento}
                      onChange={(e) => setFormData({ ...formData, departamento: e.target.value })}
                      required
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Show pickup information when home delivery is disabled
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📍 Recoger en Oficina
              </h3>

              <div className="bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-6">
                {/* Office Address */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Dirección de Nuestra Oficina:
                  </p>
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <pre className="text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                      {parametros?.direccion_oficina || 'Cargando dirección...'}
                    </pre>
                  </div>
                  {parametros?.telefono_oficina && (
                    <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                      ☎️ Teléfono: <span className="font-medium">{parametros.telefono_oficina}</span>
                    </p>
                  )}
                </div>

                {/* WhatsApp Contact */}
                {parametros?.whatsapp_oficina && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      📱 Contáctanos:
                    </p>
                    <a
                      href={getWhatsAppUrl(parametros.whatsapp_oficina)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                      WhatsApp: {parametros.whatsapp_oficina}
                    </a>
                  </div>
                )}

                {/* Navigation Buttons */}
                {parametros?.direccion_oficina && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      🗺️ Cómo llegar:
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <a
                        href={getGoogleMapsUrl(parametros.direccion_oficina)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 min-w-[150px] inline-flex items-center justify-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg transition-colors font-medium"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                        </svg>
                        Google Maps
                      </a>
                      <a
                        href={getWazeUrl(parametros.direccion_oficina)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 min-w-[150px] inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors font-medium"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>
                        </svg>
                        Waze
                      </a>
                    </div>
                  </div>
                )}

                {/* Info Note */}
                <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <p className="text-xs text-gray-700 dark:text-gray-300">
                    💡 <strong>Nota:</strong> Tu paquete estará disponible para recoger en nuestra oficina una vez que llegue a Honduras y sea liberado de aduana. Te notificaremos cuando esté listo.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Special Instructions - Only show for home delivery */}
          {parametros?.entrega_a_domicilio && (
            <div className="mb-6">
              <label htmlFor="instrucciones" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                Instrucciones Especiales (Opcional)
              </label>
              <textarea
                id="instrucciones"
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Horario preferido de entrega, punto de referencia, etc."
                value={formData.instrucciones_especiales}
                onChange={(e) => setFormData({ ...formData, instrucciones_especiales: e.target.value })}
              />
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={() => router.push('/cotizador')}
              className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Enviando...' : 'Crear Solicitud de Envío'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
