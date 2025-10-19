import Link from 'next/link';
import ThemeToggle from '@/components/ThemeToggle';

export default function Home() {
  return (
    <div className="min-h-screen bg-base-200">
      {/* Hero Section */}
      <div className="hero min-h-screen">
        <div className="hero-content text-center">
          <div className="max-w-2xl">
            <div className="absolute top-4 right-4">
              <ThemeToggle />
            </div>

            <h1 className="text-5xl font-bold mb-6">
              Bienvenido a <span className="text-primary">SicargaBox</span>
            </h1>

            <p className="text-xl mb-8 text-base-content/80">
              Tu solución confiable para envíos desde USA a Honduras
            </p>

            <p className="mb-8 text-lg">
              Calcula el costo de tu envío en segundos, obtén cotizaciones instantáneas
              y rastrea tus paquetes en tiempo real.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/cotizador" className="btn btn-primary btn-lg">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 mr-2"
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
                Cotizar Ahora
              </Link>

              <Link href="/rastreo" className="btn btn-outline btn-lg">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                Rastrear Envío
              </Link>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
              <div className="card bg-base-100 shadow-xl">
                <div className="card-body items-center text-center">
                  <div className="text-4xl mb-2">⚡</div>
                  <h3 className="card-title">Cotización Instantánea</h3>
                  <p>Obtén tu cotización en segundos con nuestro sistema inteligente</p>
                </div>
              </div>

              <div className="card bg-base-100 shadow-xl">
                <div className="card-body items-center text-center">
                  <div className="text-4xl mb-2">🔍</div>
                  <h3 className="card-title">Búsqueda Inteligente</h3>
                  <p>AI-powered search para encontrar la clasificación arancelaria correcta</p>
                </div>
              </div>

              <div className="card bg-base-100 shadow-xl">
                <div className="card-body items-center text-center">
                  <div className="text-4xl mb-2">📦</div>
                  <h3 className="card-title">Rastreo en Tiempo Real</h3>
                  <p>Monitorea tu paquete desde Miami hasta Honduras</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
