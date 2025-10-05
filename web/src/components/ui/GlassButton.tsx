import React from 'react';
import { cn } from '@/utils/utils';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  ariaLabel?: string;
  pressed?: boolean;
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  icon,
  className = '',
  disabled,
  ariaLabel,
  pressed,
  ...props
}) => {
  // Using design tokens via Tailwind classes (mapped in tailwind.config.ts)
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm font-medium',
    md: 'px-5 py-2.5 text-base font-medium',
    lg: 'px-7 py-3.5 text-lg font-semibold',
    xl: 'px-9 py-4 text-xl font-semibold',
  };

  // Using CSS variables and Tailwind classes for variants (tokens applied via CSS vars)
  const variantClasses = {
    primary: 'bg-gradient-to-r from-brand-primary/90 to-brand-secondary/90 hover:from-brand-primary-dark/95 hover:to-brand-secondary-dark/95 text-white shadow-primary focus-visible:ring-brand-primary',
    secondary: 'bg-white/80 dark:bg-gray-800/80 hover:bg-white/90 dark:hover:bg-gray-700/90 text-gray-800 dark:text-gray-100 border border-gray-200/50 focus-visible:ring-gray-500',
    success: 'bg-gradient-to-r from-success/90 to-emerald-600/90 hover:from-success-dark/95 hover:to-emerald-700/95 text-white shadow-success focus-visible:ring-success',
    danger: 'bg-gradient-to-r from-error/90 to-pink-600/90 hover:from-error-dark/95 hover:to-pink-700/95 text-white shadow-error focus-visible:ring-error',
    ghost: 'bg-transparent hover:bg-white/10 text-gray-700 dark:text-gray-300 border border-gray-300/30 focus-visible:ring-gray-400',
  };

  const widthClass = fullWidth ? 'w-full' : '';
  const isDisabled = disabled || loading;

  return (
    <button
      className={cn(
        // Base styles
        'btn-base backdrop-blur-md',
        // Size classes
        sizeClasses[size],
        // Variant classes
        variantClasses[variant],
        // Width
        widthClass,
        // Custom className
        className
      )}
      disabled={isDisabled}
      aria-label={ariaLabel || (typeof children === 'string' ? children : undefined)}
      aria-busy={loading}
      aria-pressed={pressed}
      role="button"
      {...props}
    >
      {loading ? (
        <>
          <div className="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full" aria-hidden="true" />
          <span className="sr-only">Cargando...</span>
        </>
      ) : icon ? (
        <>
          <span aria-hidden="true">{icon}</span>
          {children}
        </>
      ) : (
        children
      )}
    </button>
  );
};