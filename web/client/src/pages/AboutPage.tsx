import React from 'react';
import { GlassCard, GlassButton } from '@/components/ui';

export const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-900 dark:to-purple-900">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Acerca del Analizador de Comentarios
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Análisis avanzado con IA para insights de clientes
          </p>
        </header>

        {/* Overview Section */}
        <section className="py-12">
          <GlassCard variant="gradient" padding="xl">
            <h2 className="text-2xl md:text-3xl font-bold mb-6 text-gray-800 dark:text-gray-100">
              Descripción del Proyecto
            </h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-300">
              <p className="text-lg">
                Customer AI Driven Feedback Analyzer es una aplicación de vanguardia diseñada para transformar
                comentarios de clientes en insights de negocio accionables usando inteligencia artificial avanzada.
              </p>
              <p className="text-lg">
                Nuestro sistema procesa comentarios de clientes en español e inglés, extrayendo emociones,
                identificando puntos de dolor, calculando riesgo de abandono y determinando puntajes NPS para ayudar
                a las empresas a entender mejor a sus clientes.
              </p>
            </div>
          </GlassCard>
        </section>

        {/* Technical Architecture */}
        <section className="py-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Arquitectura Técnica
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <GlassCard variant="gradient" padding="lg">
              <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                Stack Frontend
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  React + TypeScript para desarrollo seguro
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  Tailwind CSS con diseño glassmorphism
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                  Plotly.js para visualización interactiva de datos
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  Node.js BFF proxy para comunicación con API
                </li>
              </ul>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                Stack Backend
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  FastAPI para APIs REST de alto rendimiento
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  Celery para procesamiento distribuido de tareas
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                  Redis para caché y message brokering
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  OpenAI GPT-4 para análisis inteligente
                </li>
              </ul>
            </GlassCard>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Cómo Funciona
            </span>
          </h2>

          <div className="space-y-6">
            <GlassCard variant="gradient" padding="lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    1
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-100">
                    Carga tus Datos
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Carga archivos CSV o Excel con comentarios de clientes y calificaciones.
                    Los archivos deben incluir columnas 'Nota' (0-10) y 'Comentario Final'.
                  </p>
                </div>
              </div>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-white font-bold">
                    2
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-100">
                    Procesamiento con IA
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Nuestro sistema procesa comentarios en lotes usando GPT-4 de OpenAI, extrayendo 16 emociones diferentes,
                    identificando puntos de dolor y calculando puntajes de riesgo de abandono.
                  </p>
                </div>
              </div>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-red-600 flex items-center justify-center text-white font-bold">
                    3
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-100">
                    Visualizar Insights
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Ve gráficos interactivos mostrando distribuciones de emociones, desgloses de NPS, análisis de
                    riesgo de abandono y frecuencias de puntos de dolor.
                  </p>
                </div>
              </div>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center text-white font-bold">
                    4
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-100">
                    Exportar Resultados
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Descarga resultados completos del análisis en formato CSV o Excel para procesamiento adicional
                    o integración con tus herramientas de inteligencia de negocio.
                  </p>
                </div>
              </div>
            </GlassCard>
          </div>
        </section>

        {/* Performance Metrics */}
        <section className="py-12">
          <GlassCard variant="gradient" padding="xl">
            <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center text-gray-800 dark:text-gray-100">
              Métricas de Rendimiento
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  850-1200 filas
                </div>
                <p className="text-gray-600 dark:text-gray-300">5-10 segundos de procesamiento</p>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                  1800 filas
                </div>
                <p className="text-gray-600 dark:text-gray-300">~18 segundos de procesamiento</p>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-red-600 bg-clip-text text-transparent mb-2">
                  3000 filas
                </div>
                <p className="text-gray-600 dark:text-gray-300">~30 segundos de procesamiento</p>
              </div>
            </div>
          </GlassCard>
        </section>

        {/* CTA Section */}
        <section className="py-12 text-center">
          <div className="space-y-4">
            <GlassButton
              variant="primary"
              size="xl"
              onClick={() => window.location.href = '/analyzer.html'}
              className="text-lg px-8 py-4"
            >
              Probar el Analizador
            </GlassButton>
            <div>
              <GlassButton
                variant="secondary"
                size="lg"
                onClick={() => window.location.href = '/'}
              >
                Volver al Inicio
              </GlassButton>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};