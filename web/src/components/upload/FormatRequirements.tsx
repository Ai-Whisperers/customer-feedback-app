import React from 'react';

export const FormatRequirements: React.FC = () => {
  return (
    <div className="bg-blue-50/50 dark:bg-blue-900/20 p-4 rounded-lg">
      <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
        Formato Requerido
      </h3>
      <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-400">
        <li className="flex items-start">
          <span className="mr-2">-</span>
          <span>
            <strong>Columna "Nota":</strong> Calificación del 0 al 10
          </span>
        </li>
        <li className="flex items-start">
          <span className="mr-2">-</span>
          <span>
            <strong>Columna "Comentario Final":</strong> Texto del comentario (3-2000 caracteres)
          </span>
        </li>
        <li className="flex items-start">
          <span className="mr-2">-</span>
          <span>
            <strong>Columna "NPS" (opcional):</strong> Si existe, se usará directamente
          </span>
        </li>
      </ul>
    </div>
  );
};