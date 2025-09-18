import React from 'react';

interface GlassProgressProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

export const GlassProgress: React.FC<GlassProgressProps> = ({
  value,
  max = 100,
  label,
  showPercentage = true,
  variant = 'primary',
  size = 'md',
  animated = true,
}) => {
  const percentage = Math.round((value / max) * 100);

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-4',
    lg: 'h-6',
  };

  const variantClasses = {
    primary: 'from-blue-500 to-purple-600',
    success: 'from-green-500 to-emerald-600',
    warning: 'from-yellow-400 to-orange-500',
    danger: 'from-red-500 to-pink-600',
  };

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex justify-between mb-2">
          {label && (
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {label}
            </span>
          )}
          {showPercentage && (
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {percentage}%
            </span>
          )}
        </div>
      )}
      <div
        className={`
          w-full
          ${sizeClasses[size]}
          bg-gray-200/50
          dark:bg-gray-700/50
          backdrop-blur-sm
          rounded-full
          overflow-hidden
          border
          border-white/20
        `}
      >
        <div
          className={`
            h-full
            bg-gradient-to-r
            ${variantClasses[variant]}
            transition-all
            duration-500
            ease-out
            ${animated ? 'animate-pulse' : ''}
            shadow-lg
          `}
          style={{ width: `${percentage}%` }}
        >
          <div className="h-full bg-white/20 backdrop-blur-sm" />
        </div>
      </div>
    </div>
  );
};