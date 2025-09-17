import React from 'react';
import { GlassCard, GlassButton } from '../components/ui';

export const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-900 dark:to-purple-900">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              About Customer Feedback Analyzer
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Advanced AI-powered analysis for customer insights
          </p>
        </header>

        {/* Overview Section */}
        <section className="py-12">
          <GlassCard variant="gradient" padding="xl">
            <h2 className="text-2xl md:text-3xl font-bold mb-6 text-gray-800 dark:text-gray-100">
              Project Overview
            </h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-300">
              <p className="text-lg">
                Customer AI Driven Feedback Analyzer is a cutting-edge application designed to transform
                raw customer feedback into actionable business insights using advanced artificial intelligence.
              </p>
              <p className="text-lg">
                Our system processes customer comments in both Spanish and English, extracting emotions,
                identifying pain points, calculating churn risk, and determining NPS scores to help businesses
                understand their customers better.
              </p>
            </div>
          </GlassCard>
        </section>

        {/* Technical Architecture */}
        <section className="py-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Technical Architecture
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <GlassCard variant="gradient" padding="lg">
              <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                Frontend Stack
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  React + TypeScript for type-safe development
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  Tailwind CSS with glassmorphism design
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                  Plotly.js for interactive data visualization
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  Node.js BFF proxy for API communication
                </li>
              </ul>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                Backend Stack
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  FastAPI for high-performance REST APIs
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  Celery for distributed task processing
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                  Redis for caching and message brokering
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  OpenAI GPT-4 for intelligent analysis
                </li>
              </ul>
            </GlassCard>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              How It Works
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
                    Upload Your Data
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Upload CSV or Excel files containing customer feedback with comments and ratings.
                    Files must include 'Nota' (0-10) and 'Comentario Final' columns.
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
                    AI Processing
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Our system processes comments in batches using OpenAI's GPT-4, extracting 16 different emotions,
                    identifying pain points, and calculating churn risk scores.
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
                    Visualize Insights
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    View interactive charts showing emotion distributions, NPS breakdowns, churn risk analysis,
                    and pain point frequencies.
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
                    Export Results
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Download comprehensive analysis results in CSV or Excel format for further processing
                    or integration with your business intelligence tools.
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
              Performance Metrics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  850-1200 rows
                </div>
                <p className="text-gray-600 dark:text-gray-300">5-10 seconds processing</p>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                  1800 rows
                </div>
                <p className="text-gray-600 dark:text-gray-300">~18 seconds processing</p>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-red-600 bg-clip-text text-transparent mb-2">
                  3000 rows
                </div>
                <p className="text-gray-600 dark:text-gray-300">~30 seconds processing</p>
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
              onClick={() => window.location.href = '/analyzer'}
              className="text-lg px-8 py-4"
            >
              Try the Analyzer
            </GlassButton>
            <div>
              <GlassButton
                variant="secondary"
                size="lg"
                onClick={() => window.location.href = '/'}
              >
                Back to Home
              </GlassButton>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};