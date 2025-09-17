import React from 'react';
import { GlassCard, GlassButton } from '@/components/ui';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center py-20">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Analizador de Comentarios
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              con IA
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            Transforma los comentarios de clientes en insights accionables con análisis avanzado de IA
          </p>

          <div className="flex gap-4 justify-center">
            <GlassButton
              variant="primary"
              size="lg"
              onClick={() => window.location.href = '/analyzer'}
            >
              Comenzar Análisis
            </GlassButton>
            <GlassButton
              variant="secondary"
              size="lg"
              onClick={() => window.location.href = '/about'}
            >
              Saber Más
            </GlassButton>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Características Potentes
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <GlassCard variant="gradient" padding="lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-100">
                  Análisis con IA
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Usa GPT-4 para extraer emociones, puntos de dolor y riesgo de abandono de los comentarios
                </p>
              </div>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-100">
                  Visualizaciones Avanzadas
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Gráficos interactivos y dashboards para visualizar patrones de sentimiento y puntajes NPS
                </p>
              </div>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-100">
                  Exportar Resultados
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Descarga los resultados del análisis en formato CSV o Excel para procesamiento adicional
                </p>
              </div>
            </GlassCard>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-20">
          <GlassCard variant="gradient" padding="xl">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  16
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-2">Emociones Analizadas</p>
              </div>
              <div>
                <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  3000+
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-2">Comentarios/Lote</p>
              </div>
              <div>
                <div className="text-4xl font-bold bg-gradient-to-r from-pink-600 to-red-600 bg-clip-text text-transparent">
                  30s
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-2">Tiempo de Procesamiento</p>
              </div>
              <div>
                <div className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                  2
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-2">Idiomas</p>
              </div>
            </div>
          </GlassCard>
        </section>

        {/* CTA Section */}
        <section className="py-20 text-center">
          <GlassCard variant="gradient" padding="xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ¿Listo para Comenzar?
              </span>
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
              Carga tus datos de comentarios de clientes y obtén insights instantáneos con IA
            </p>
            <GlassButton
              variant="primary"
              size="xl"
              onClick={() => window.location.href = '/analyzer'}
              className="text-lg px-8 py-4"
            >
              Iniciar Análisis Gratuito
            </GlassButton>
          </GlassCard>
        </section>
      </div>
    </div>
  );
};