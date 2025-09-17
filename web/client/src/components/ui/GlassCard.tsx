import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'light' | 'dark' | 'gradient';
  padding?: 'sm' | 'md' | 'lg' | 'xl';
  blur?: 'sm' | 'md' | 'lg';
  border?: boolean;
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  variant = 'light',
  padding = 'lg',
  blur = 'md',
  border = true,
  shadow = 'lg',
}) => {
  const paddingClasses = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
  };

  const blurClasses = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
  };

  const shadowClasses = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
    '2xl': 'shadow-2xl',
  };

  const variantClasses = {
    light: 'bg-white/80 dark:bg-gray-900/80',
    dark: 'bg-gray-800/80 dark:bg-gray-950/80',
    gradient: 'bg-gradient-to-br from-white/90 via-white/80 to-gray-100/70',
  };

  const borderClass = border ? 'border border-white/20' : '';

  return (
    <div
      className={`
        ${paddingClasses[padding]}
        ${blurClasses[blur]}
        ${shadowClasses[shadow]}
        ${variantClasses[variant]}
        ${borderClass}
        rounded-2xl
        transition-all
        duration-300
        ${className}
      `}
    >
      {children}
    </div>
  );
};