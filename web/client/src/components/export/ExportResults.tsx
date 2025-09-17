import React, { useState } from 'react';
import { GlassCard, GlassButton, GlassBadge } from '../../components/ui';

interface ExportResultsProps {
  taskId: string;
  onExport: (format: 'csv' | 'xlsx') => Promise<void>;
  isExporting?: boolean;
}

export const ExportResults: React.FC<ExportResultsProps> = ({
  taskId,
  onExport,
  isExporting = false,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<'csv' | 'xlsx'>('xlsx');
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleExport = async () => {
    try {
      setExportStatus('idle');
      await onExport(selectedFormat);
      setExportStatus('success');
      setTimeout(() => setExportStatus('idle'), 3000);
    } catch (error) {
      setExportStatus('error');
      setTimeout(() => setExportStatus('idle'), 5000);
    }
  };

  return (
    <GlassCard variant="gradient" className="w-full">
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-2">
            Exportar Resultados
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Descarga los resultados del análisis en el formato que prefieras
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormatOption
            format="xlsx"
            title="Excel (.xlsx)"
            description="Formato recomendado con múltiples hojas"
            features={[
              'Hoja de resumen',
              'Datos detallados por fila',
              'Gráficos incluidos',
              'Formato enriquecido',
            ]}
            isSelected={selectedFormat === 'xlsx'}
            onSelect={() => setSelectedFormat('xlsx')}
          />

          <FormatOption
            format="csv"
            title="CSV (.csv)"
            description="Formato simple compatible con cualquier software"
            features={[
              'Compatible universal',
              'Tamaño reducido',
              'Fácil importación',
              'Texto plano',
            ]}
            isSelected={selectedFormat === 'csv'}
            onSelect={() => setSelectedFormat('csv')}
          />
        </div>

        <div className="bg-blue-50/50 dark:bg-blue-900/20 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
            Contenido del Archivo
          </h3>
          <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-400">
            <li className="flex items-start">
              <span className="mr-2">[OK]</span>
              <span>Análisis completo de emociones para cada comentario</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">[OK]</span>
              <span>Puntuación NPS y clasificación por cliente</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">[OK]</span>
              <span>Índice de riesgo de abandono individual</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">[OK]</span>
              <span>Puntos de dolor identificados y frecuencias</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">[OK]</span>
              <span>Estadísticas agregadas y métricas generales</span>
            </li>
          </ul>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <GlassButton
            onClick={handleExport}
            variant="primary"
            size="lg"
            fullWidth
            loading={isExporting}
            disabled={isExporting}
            icon={
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            }
          >
            {isExporting ? 'Exportando...' : `Descargar como ${selectedFormat.toUpperCase()}`}
          </GlassButton>

          {exportStatus === 'success' && (
            <GlassBadge variant="success" size="md">
              [OK] Descarga exitosa
            </GlassBadge>
          )}

          {exportStatus === 'error' && (
            <GlassBadge variant="danger" size="md">
              [ERROR] Error en la descarga
            </GlassBadge>
          )}
        </div>

        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          <p>ID de Tarea: <span className="font-mono">{taskId}</span></p>
          <p className="mt-1">Los resultados están disponibles por 24 horas</p>
        </div>
      </div>
    </GlassCard>
  );
};

interface FormatOptionProps {
  format: 'csv' | 'xlsx';
  title: string;
  description: string;
  features: string[];
  isSelected: boolean;
  onSelect: () => void;
}

const FormatOption: React.FC<FormatOptionProps> = ({
  format,
  title,
  description,
  features,
  isSelected,
  onSelect,
}) => {
  return (
    <div
      onClick={onSelect}
      className={`
        p-4
        rounded-lg
        border-2
        cursor-pointer
        transition-all
        duration-300
        ${
          isSelected
            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20'
            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
        }
      `}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div
            className={`
              w-12 h-12 rounded-lg flex items-center justify-center
              ${
                format === 'xlsx'
                  ? 'bg-green-100 dark:bg-green-900/50 text-green-600'
                  : 'bg-orange-100 dark:bg-orange-900/50 text-orange-600'
              }
            `}
          >
            {format === 'xlsx' ? (
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M15.8,20H14L12,13.2L10,20H8.2L11.1,12L8.2,4H10L12,10.8L14,4H15.8L12.9,12L15.8,20M13,9V3.5L18.5,9H13Z" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13,9V3.5L18.5,9H13M10,11A2,2 0 0,0 8,13A2,2 0 0,0 10,15A2,2 0 0,0 12,13A2,2 0 0,0 10,11M10,17A2,2 0 0,0 8,19A2,2 0 0,0 10,21A2,2 0 0,0 12,19A2,2 0 0,0 10,17Z" />
              </svg>
            )}
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 dark:text-gray-100">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
          </div>
        </div>
        <div
          className={`
            w-5 h-5 rounded-full border-2 flex items-center justify-center
            ${
              isSelected
                ? 'border-blue-500 bg-blue-500'
                : 'border-gray-300 dark:border-gray-600'
            }
          `}
        >
          {isSelected && (
            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </div>
      <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center">
            <span className="mr-2 text-green-500">-</span>
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
};