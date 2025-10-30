'use client';

import { useState } from 'react';
import { copyToClipboard } from '@/lib/addressUtils';

interface ShippingAddressDisplayProps {
  clientName: string;
  clientCode: string;
  consolidatorAddress: string;
  showInstructions?: boolean;
  className?: string;
}

export default function ShippingAddressDisplay({
  clientName,
  clientCode,
  consolidatorAddress,
  showInstructions = true,
  className = '',
}: ShippingAddressDisplayProps) {
  const [copied, setCopied] = useState(false);

  const fullAddress = `${clientName} - ${clientCode}\n${consolidatorAddress}`;

  const handleCopy = async () => {
    const success = await copyToClipboard(fullAddress);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={`bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-6 ${className}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-3xl">📦</span>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Tu Casillero en Miami
          </h3>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-700">
        <pre className="text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap font-mono leading-relaxed">
          {fullAddress}
        </pre>
      </div>

      <button
        onClick={handleCopy}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
          copied
            ? 'bg-green-500 hover:bg-green-600 text-white'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {copied ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            ¡Dirección Copiada!
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Copiar Dirección
          </span>
        )}
      </button>

      {showInstructions && (
        <div className="mt-4 text-sm text-gray-700 dark:text-gray-300">
          <p className="font-medium mb-2">💡 Importante:</p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Usa esta dirección como <strong>Dirección de Envío</strong> en tus compras online</li>
            <li>Asegúrate de incluir tu nombre y código exactamente como aparece arriba</li>
            <li>Una vez que tu paquete llegue a Miami, te notificaremos</li>
          </ul>
        </div>
      )}
    </div>
  );
}
