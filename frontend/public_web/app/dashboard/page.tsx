'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { apiClient, ShippingResponse } from '@/lib/api';
import Header from '@/components/Header';

type TabType = 'envios' | 'cotizaciones' | 'cuenta';

export default function DashboardPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [activeTab, setActiveTab] = useState<TabType>('envios');
  const [envios, setEnvios] = useState<ShippingResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (status === 'unauthenticated') {
        router.push('/login');
        return;
      }

      if (status === 'authenticated' && session) {
        try {
          const accessToken = (session as any).accessToken;
          if (!accessToken) {
            router.push('/login');
            return;
          }

          // Fetch envíos
          const enviosData = await apiClient.getUserEnvios(accessToken);
          setEnvios(enviosData);
        } catch (error) {
          console.error('Error fetching dashboard data:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchData();
  }, [status, session, router]);

  // Loading state
  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  const getStatusBadgeColor = (estado: string) => {
    switch (estado) {
      case 'Documentación Pendiente':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'Solicitado':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'Recibido en Miami':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
      case 'En tránsito a Honduras':
        return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400';
      case 'Entregado':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-HN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="container mx-auto px-4 max-w-6xl py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Mi Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona tus envíos, cotizaciones y configuración de cuenta
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          {/* Tab Headers */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('envios')}
                className={`
                  px-6 py-4 text-sm font-medium border-b-2 transition-colors
                  ${
                    activeTab === 'envios'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
                  }
                `}
              >
                📦 Mis Envíos
                {envios.length > 0 && (
                  <span className="ml-2 bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-full text-xs">
                    {envios.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('cotizaciones')}
                className={`
                  px-6 py-4 text-sm font-medium border-b-2 transition-colors
                  ${
                    activeTab === 'cotizaciones'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
                  }
                `}
              >
                💰 Mis Cotizaciones
              </button>
              <button
                onClick={() => setActiveTab('cuenta')}
                className={`
                  px-6 py-4 text-sm font-medium border-b-2 transition-colors
                  ${
                    activeTab === 'cuenta'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
                  }
                `}
              >
                👤 Mi Cuenta
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Mis Envíos Tab */}
            {activeTab === 'envios' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Mis Envíos
                  </h2>
                  <button
                    onClick={() => router.push('/cotizador')}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium text-sm"
                  >
                    + Nueva Cotización
                  </button>
                </div>

                {envios.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">📦</div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      No tienes envíos todavía
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      Comienza creando una cotización para tu primer envío
                    </p>
                    <button
                      onClick={() => router.push('/cotizador')}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                    >
                      Crear Primera Cotización
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {envios.map((envio) => (
                      <div
                        key={envio.id}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white font-mono">
                              {envio.tracking_number_sicarga}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              Solicitado: {formatDate(envio.fecha_solicitud)}
                            </p>
                          </div>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeColor(
                              envio.estado_envio
                            )}`}
                          >
                            {envio.estado_envio_display}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Tracking USA:</span>
                            <p className="font-medium text-gray-900 dark:text-white font-mono">
                              {envio.tracking_number_original || 'Pendiente'}
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Peso estimado:</span>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {envio.peso_estimado} lb
                            </p>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          {envio.estado_envio === 'Documentación Pendiente' && (
                            <button
                              onClick={() => router.push(`/envio/${envio.id}/actualizar`)}
                              className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors font-medium text-sm"
                            >
                              📋 Agregar Documentos
                            </button>
                          )}
                          <button
                            onClick={() => router.push(`/envio/${envio.id}`)}
                            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium text-sm"
                          >
                            Ver Detalles
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Mis Cotizaciones Tab */}
            {activeTab === 'cotizaciones' && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">💰</div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Próximamente
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Esta funcionalidad estará disponible pronto
                </p>
              </div>
            )}

            {/* Mi Cuenta Tab */}
            {activeTab === 'cuenta' && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">👤</div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Próximamente
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Configuración de cuenta estará disponible pronto
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
