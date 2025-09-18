import React, { useId } from 'react';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  icon?: React.ReactNode;
  ariaLabel?: string;
}

export const GlassInput: React.FC<GlassInputProps> = ({
  label,
  error,
  helper,
  icon,
  className = '',
  ariaLabel,
  id: providedId,
  ...props
}) => {
  const generatedId = useId();
  const inputId = providedId || generatedId;
  const errorId = error ? `${inputId}-error` : undefined;
  const helperId = helper ? `${inputId}-helper` : undefined;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          {label}
          {props.required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none" aria-hidden="true">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          aria-label={!label ? (ariaLabel || props.placeholder) : undefined}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={[errorId, helperId].filter(Boolean).join(' ') || undefined}
          aria-required={props.required}
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
        <p id={errorId} className="mt-2 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      )}
      {helper && !error && (
        <p id={helperId} className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {helper}
        </p>
      )}
    </div>
  );
};