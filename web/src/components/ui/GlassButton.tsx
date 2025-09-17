import React from 'react';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
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
  ...props
}) => {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-7 py-3.5 text-lg',
  };

  const variantClasses = {
    primary: `
      bg-gradient-to-r from-blue-500/90 to-purple-600/90
      hover:from-blue-600/95 hover:to-purple-700/95
      text-white
      shadow-lg shadow-blue-500/25
    `,
    secondary: `
      bg-white/80 dark:bg-gray-800/80
      hover:bg-white/90 dark:hover:bg-gray-700/90
      text-gray-800 dark:text-gray-100
      border border-gray-200/50
    `,
    success: `
      bg-gradient-to-r from-green-500/90 to-emerald-600/90
      hover:from-green-600/95 hover:to-emerald-700/95
      text-white
      shadow-lg shadow-green-500/25
    `,
    danger: `
      bg-gradient-to-r from-red-500/90 to-pink-600/90
      hover:from-red-600/95 hover:to-pink-700/95
      text-white
      shadow-lg shadow-red-500/25
    `,
    ghost: `
      bg-transparent
      hover:bg-white/10
      text-gray-700 dark:text-gray-300
      border border-gray-300/30
    `,
  };

  const widthClass = fullWidth ? 'w-full' : '';
  const isDisabled = disabled || loading;

  return (
    <button
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${widthClass}
        backdrop-blur-md
        rounded-xl
        font-medium
        transition-all
        duration-300
        transform
        hover:scale-105
        active:scale-95
        disabled:opacity-50
        disabled:cursor-not-allowed
        disabled:hover:scale-100
        flex
        items-center
        justify-center
        gap-2
        ${className}
      `}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <div className="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full" />
      ) : icon ? (
        <>
          {icon}
          {children}
        </>
      ) : (
        children
      )}
    </button>
  );
};