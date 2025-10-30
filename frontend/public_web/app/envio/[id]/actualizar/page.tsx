'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { apiClient } from '@/lib/api';
import Header from '@/components/Header';

export default function UpdateEnvioPage() {
  const router = useRouter();
  const params = useParams();
  const { data: session, status } = useSession();
  const [envio, setEnvio] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    tracking_number: '',
  });
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const envioId = params.id as string;

  useEffect(() => {
    const fetchEnvio = async () => {
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

          // For now, we'll need to implement a getEnvio endpoint
          // For Sprint 2, we'll show a simple form
          // In Sprint 3, we'll fetch the actual envío details
          setLoading(false);
        } catch (error) {
          console.error('Error fetching envío:', error);
          setError('Error al cargar la información del envío');
          setLoading(false);
        }
      }
    };

    fetchEnvio();
  }, [status, session, envioId, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      if (!session || !(session as any).accessToken) {
        setError('No se pudo obtener el token de autenticación. Por favor, inicia sesión nuevamente.');
        router.push('/login');
        return;
      }

      const accessToken = (session as any).accessToken;

      // Prepare updates
      const updates: {
        tracking_number_original?: string;
        factura_compra?: File;
      } = {};

      if (formData.tracking_number.trim()) {
        updates.tracking_number_original = formData.tracking_number.trim();
      }

      if (invoiceFile) {
        updates.factura_compra = invoiceFile;
      }

      // Validate that at least one field is being updated
      if (!updates.tracking_number_original && !updates.factura_compra) {
        setError('Por favor, proporciona al menos un documento (número de rastreo o factura)');
        setIsSubmitting(false);
        return;
      }

      // Call update API
      const response = await apiClient.updateShippingRequest(
        parseInt(envioId),
        updates,
        accessToken
      );

      if (response) {
        setSuccess('¡Documentación actualizada exitosamente! Tu envío ha sido actualizado.');

        // Clear form
        setFormData({ tracking_number: '' });
        setInvoiceFile(null);

        // Redirect after 2 seconds
        setTimeout(() => {
          router.push('/cotizador'); // Will redirect to dashboard in Sprint 3
        }, 2000);
      } else {
        setError('Error al actualizar la documentación. Por favor, intenta nuevamente.');
      }
    } catch (error: any) {
      console.error('Error updating envío:', error);

      let errorMessage = 'Error desconocido al actualizar el envío.';
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="container mx-auto px-4 max-w-3xl py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Actualizar Documentación
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Envío #{envioId}
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-100 dark:bg-green-900/30 border border-green-400 dark:border-green-700 text-green-700 dark:text-green-400 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">{success}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">{error}</p>
          </div>
        )}

        {/* Information Banner */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">📋</span>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Completa tu Documentación
              </h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Para procesar tu envío necesitamos el número de rastreo de USA y la factura de compra.
                Puedes agregar uno o ambos documentos ahora.
              </p>
            </div>
          </div>
        </div>

        {/* Update Form */}
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Agregar Documentación
          </h2>

          {/* US Tracking Number */}
          <div className="mb-6">
            <label htmlFor="tracking_number" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
              Número de Rastreo (USA)
            </label>
            <input
              type="text"
              id="tracking_number"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
              placeholder="Ej: 1Z999AA10123456784"
              value={formData.tracking_number}
              onChange={(e) => setFormData({ ...formData, tracking_number: e.target.value })}
            />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Número de rastreo proporcionado por tu proveedor (USPS, UPS, FedEx, Amazon, etc.)
            </p>
          </div>

          {/* Purchase Invoice Upload */}
          <div className="mb-6">
            <label htmlFor="invoice" className="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
              Factura de Compra
            </label>
            <input
              type="file"
              id="invoice"
              accept=".pdf,.jpg,.jpeg,.png"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              onChange={(e) => setInvoiceFile(e.target.files?.[0] || null)}
            />
            {invoiceFile && (
              <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                ✓ Archivo seleccionado: {invoiceFile.name}
              </p>
            )}
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Formatos aceptados: PDF, JPG, PNG (Máx. 5MB)
            </p>
          </div>

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
              {isSubmitting ? 'Actualizando...' : 'Actualizar Documentación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
