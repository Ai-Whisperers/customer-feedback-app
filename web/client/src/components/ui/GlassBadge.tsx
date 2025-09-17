import React from 'react';

interface GlassBadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  rounded?: boolean;
}

export const GlassBadge: React.FC<GlassBadgeProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  rounded = false,
}) => {
  const sizeClasses = {
    xs: 'px-2 py-0.5 text-xs',
    sm: 'px-2.5 py-1 text-sm',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  const variantClasses = {
    primary: 'bg-blue-100/80 text-blue-800 dark:bg-blue-900/80 dark:text-blue-200',
    secondary: 'bg-gray-100/80 text-gray-800 dark:bg-gray-800/80 dark:text-gray-200',
    success: 'bg-green-100/80 text-green-800 dark:bg-green-900/80 dark:text-green-200',
    warning: 'bg-yellow-100/80 text-yellow-800 dark:bg-yellow-900/80 dark:text-yellow-200',
    danger: 'bg-red-100/80 text-red-800 dark:bg-red-900/80 dark:text-red-200',
    info: 'bg-cyan-100/80 text-cyan-800 dark:bg-cyan-900/80 dark:text-cyan-200',
  };

  return (
    <span
      className={`
        inline-flex
        items-center
        font-medium
        backdrop-blur-sm
        border
        border-white/20
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${rounded ? 'rounded-full' : 'rounded-lg'}
      `}
    >
      {children}
    </span>
  );
};