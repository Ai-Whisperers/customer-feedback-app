import React from 'react';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  icon?: React.ReactNode;
}

export const GlassInput: React.FC<GlassInputProps> = ({
  label,
  error,
  helper,
  icon,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {icon}
          </div>
        )}
        <input
          className={`
            w-full
            ${icon ? 'pl-10' : 'pl-4'}
            pr-4
            py-3
            bg-white/80
            dark:bg-gray-800/80
            backdrop-blur-md
            border
            ${error ? 'border-red-300' : 'border-gray-200/50'}
            rounded-xl
            text-gray-900
            dark:text-gray-100
            placeholder-gray-500
            focus:outline-none
            focus:ring-2
            ${error ? 'focus:ring-red-500/50' : 'focus:ring-blue-500/50'}
            focus:border-transparent
            transition-all
            duration-300
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
      {helper && !error && (
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{helper}</p>
      )}
    </div>
  );
};