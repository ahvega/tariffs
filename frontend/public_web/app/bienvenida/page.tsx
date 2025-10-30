'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import Header from '@/components/Header';
import ShippingAddressDisplay from '@/components/ShippingAddressDisplay';
import { apiClient, User } from '@/lib/api';

export default function WelcomePage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clienteInfo, setClienteInfo] = useState<{
    nombre_completo: string;
    codigo_cliente: string;
  } | null>(null);
  const [consolidatorAddress, setConsolidatorAddress] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      if (status === 'unauthenticated') {
        router.push('/login');
        return;
      }

      if (status === 'authenticated' && session) {
        try {
          setLoading(true);
          const accessToken = (session as any).accessToken;

          if (!accessToken) {
            setError('No se pudo obtener el token de autenticación.');
            return;
          }

          // Fetch current user with cliente info
          const userData = await apiClient.getCurrentUser(accessToken) as User & {
            cliente?: {
              id: number;
              codigo_cliente: string;
              nombre_completo: string;
            };
          };

          if (!userData) {
            setError('No se pudo obtener la información del usuario.');
            return;
          }

          if (!userData.cliente) {
            setError('No se encontró información de cliente asociada.');
            return;
          }

          setClienteInfo({
            nombre_completo: userData.cliente.nombre_completo,
            codigo_cliente: userData.cliente.codigo_cliente,
          });

          // Fetch system parameters
          const parametros = await apiClient.getParametrosSistema(accessToken);

          if (!parametros) {
            setError('No se pudo obtener los parámetros del sistema.');
            return;
          }

          setConsolidatorAddress(parametros.direccion_consolidador);
        } catch (err: any) {
          console.error('Error fetching data:', err);
          setError('Error al cargar la información. Por favor, intenta nuevamente.');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchData();
  }, [status, session, router]);

  const handleContinue = () => {
    router.push('/cotizador');
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando...</p>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Header />
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="text-center">
              <div className="text-red-500 text-5xl mb-4">⚠️</div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Error
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
              <button
                onClick={() => router.push('/cotizador')}
                className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Ir al Cotizador
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4">
        <div className="max-w-3xl mx-auto">
          {/* Welcome Message */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full mb-4">
              <span className="text-4xl">🎉</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
              ¡Bienvenido a SicargaBox!
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Tu cuenta ha sido creada exitosamente. Ahora tienes tu propio casillero en Miami.
            </p>
          </div>

          {/* Shipping Address Display */}
          {clienteInfo && consolidatorAddress && (
            <div className="mb-8">
              <ShippingAddressDisplay
                clientName={clienteInfo.nombre_corto}
                clientCode={clienteInfo.codigo_cliente}
                consolidatorAddress={consolidatorAddress}
                showInstructions={true}
              />
            </div>
          )}

          {/* Additional Information */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              ¿Qué sigue?
            </h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <span className="text-2xl">1️⃣</span>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Realiza tus compras online
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Usa tu dirección de Miami al finalizar la compra en tu tienda favorita de USA
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">2️⃣</span>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Cotiza el envío
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Usa nuestra calculadora para saber cuánto costará traer tu paquete a Honduras
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">3️⃣</span>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Solicita tu envío
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Completa los detalles y nosotros nos encargamos del resto
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">4️⃣</span>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    Recibe tu paquete
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Recoge tu paquete en nuestra oficina o recíbelo en tu domicilio
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <div className="text-center">
            <button
              onClick={handleContinue}
              className="inline-flex items-center gap-2 py-4 px-8 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-lg transition-colors shadow-lg hover:shadow-xl"
            >
              Comenzar a Cotizar
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>

          {/* Help Text */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500 dark:text-gray-500">
              ¿Necesitas ayuda? Contáctanos en cualquier momento
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
