import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GlassCard, GlassButton } from '@/components/ui';
import { useTranslations } from '@/i18n';

export const AboutPage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslations();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-900 dark:to-purple-900">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {t('about.title')}
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            {t('about.subtitle')}
          </p>
        </header>

        {/* Overview Section */}
        <section className="py-12">
          <GlassCard variant="gradient" padding="xl">
            <h2 className="text-2xl md:text-3xl font-bold mb-6 text-gray-800 dark:text-gray-100">
              {t('about.overview.title')}
            </h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-300">
              <p className="text-lg">
                {t('about.overview.paragraph1')}
              </p>
              <p className="text-lg">
                {t('about.overview.paragraph2')}
              </p>
            </div>
          </GlassCard>
        </section>

        {/* Technical Architecture */}
        <section className="py-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {t('about.techStack.title')}
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <GlassCard variant="gradient" padding="lg">
              <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                {t('about.techStack.frontend')}
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  {t('about.techStack.frontendItems.react')}
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  {t('about.techStack.frontendItems.tailwind')}
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                  {t('about.techStack.frontendItems.plotly')}
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  {t('about.techStack.frontendItems.bff')}
                </li>
              </ul>
            </GlassCard>

            <GlassCard variant="gradient" padding="lg">
              <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                {t('about.techStack.backend')}
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  {t('about.techStack.backendItems.fastapi')}
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  {t('about.techStack.backendItems.celery')}
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-pink-500 rounded-full mr-3"></span>
                  {t('about.techStack.backendItems.redis')}
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  {t('about.techStack.backendItems.openai')}
                </li>
              </ul>
            </GlassCard>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              {t('about.howItWorks.title')}
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
                    {t('about.howItWorks.step1.title')}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {t('about.howItWorks.step1.description')}
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
                    {t('about.howItWorks.step2.title')}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {t('about.howItWorks.step2.description')}
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
                    {t('about.howItWorks.step3.title')}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {t('about.howItWorks.step3.description')}
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
                    {t('about.howItWorks.step4.title')}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {t('about.howItWorks.step4.description')}
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
              {t('about.performance.title')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  {t('about.performance.metric1')}
                </div>
                <p className="text-gray-600 dark:text-gray-300">{t('about.performance.metric1Desc')}</p>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                  {t('about.performance.metric2')}
                </div>
                <p className="text-gray-600 dark:text-gray-300">{t('about.performance.metric2Desc')}</p>
              </div>
              <div className="p-4">
                <div className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-red-600 bg-clip-text text-transparent mb-2">
                  {t('about.performance.metric3')}
                </div>
                <p className="text-gray-600 dark:text-gray-300">{t('about.performance.metric3Desc')}</p>
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
              onClick={() => navigate('/analyzer')}
              className="text-lg px-8 py-4"
            >
              {t('about.cta.tryAnalyzer')}
            </GlassButton>
            <div>
              <GlassButton
                variant="secondary"
                size="lg"
                onClick={() => navigate('/')}
              >
                {t('about.cta.backHome')}
              </GlassButton>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};