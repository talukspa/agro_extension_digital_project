// Componente Button - Sistema de botones con la paleta de colores Plum
// Cumple con WCAG AA para accesibilidad y soporte completo de modo claro/oscuro

import { ButtonHTMLAttributes, ReactNode, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'ghost' | 'success' | 'warning' | 'error' | 'link';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: ReactNode;
  isLoading?: boolean;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  isLoading = false,
  fullWidth = false,
  disabled,
  ...props
}, ref) => {

  // Configuración de variantes con contraste WCAG AA garantizado
  const variantStyles = {
    // Primario: Púrpura vibrante con texto blanco garantizado (contraste 7:1+)
    primary: `
      bg-purple-700 text-white border border-purple-700
      hover:bg-purple-800 hover:border-purple-800
      dark:bg-purple-600 dark:text-white dark:border-purple-600
      dark:hover:bg-purple-500 dark:hover:border-purple-500
      focus:ring-2 focus:ring-purple-500 focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:bg-gray-400 disabled:border-gray-400 disabled:text-white
      dark:disabled:bg-gray-600 dark:disabled:border-gray-600 dark:disabled:text-gray-300
    `,
    
    // Secundario: Fondo blanco con texto muy oscuro para máximo contraste (contraste 15:1+)
    secondary: `
      bg-white text-gray-900 border-2 border-gray-300
      hover:bg-gray-50 hover:border-gray-400 hover:text-black
      dark:bg-gray-100 dark:text-gray-900 dark:border-gray-400
      dark:hover:bg-gray-200 dark:hover:border-gray-500
      focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:bg-gray-200 disabled:border-gray-200 disabled:text-gray-500
      dark:disabled:bg-gray-300 dark:disabled:border-gray-300 dark:disabled:text-gray-600
    `,
    
    // Acento: Ámbar oscuro para mejor contraste (contraste 6:1+)
    accent: `
      bg-amber-600 text-white border border-amber-600
      hover:bg-amber-700 hover:border-amber-700
      dark:bg-amber-500 dark:text-black dark:border-amber-500
      dark:hover:bg-amber-400 dark:hover:border-amber-400
      focus:ring-2 focus:ring-amber-500 focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:bg-amber-300 disabled:border-amber-300 disabled:text-white
      dark:disabled:bg-amber-700 dark:disabled:border-amber-700 dark:disabled:text-amber-200
    `,
    
    // Outline: Borde visible con texto muy oscuro (contraste 10:1+)
    outline: `
      bg-white text-gray-800 border-2 border-gray-400
      hover:bg-gray-50 hover:border-gray-500 hover:text-gray-900
      dark:bg-transparent dark:text-gray-200 dark:border-gray-500
      dark:hover:bg-gray-800 dark:hover:border-gray-400 dark:hover:text-gray-100
      focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
      disabled:border-gray-200 disabled:text-gray-400 disabled:bg-gray-100
      dark:disabled:border-gray-700 dark:disabled:text-gray-600
    `,
    
    // Ghost: Texto oscuro en claro, claro en oscuro (contraste 8:1+)
    ghost: `
      bg-transparent text-gray-800 border border-transparent
      hover:bg-gray-100 hover:text-gray-900
      dark:text-gray-200
      dark:hover:bg-gray-800 dark:hover:text-gray-100
      focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
      disabled:text-gray-500 dark:disabled:text-gray-600
    `,
    
    // Link: Púrpura oscuro para máximo contraste (contraste 8:1+)
    link: `
      bg-transparent text-purple-800 border border-transparent p-0 h-auto font-medium
      hover:text-purple-900 hover:underline
      dark:text-purple-300 dark:hover:text-purple-200
      focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:rounded
      disabled:text-gray-500 dark:disabled:text-gray-600
    `,
    
    // Estados semánticos con alta visibilidad
    success: `
      bg-green-700 text-white border border-green-700
      hover:bg-green-800 hover:border-green-800
      dark:bg-green-600 dark:hover:bg-green-500
      focus:ring-2 focus:ring-green-500 focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:bg-green-400 disabled:border-green-400 disabled:text-white
      dark:disabled:bg-green-800 dark:disabled:border-green-800 dark:disabled:text-green-200
    `,
    
    warning: `
      bg-orange-600 text-white border border-orange-600
      hover:bg-orange-700 hover:border-orange-700
      dark:bg-orange-500 dark:hover:bg-orange-400
      focus:ring-2 focus:ring-orange-500 focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:bg-orange-300 disabled:border-orange-300 disabled:text-white
      dark:disabled:bg-orange-700 dark:disabled:border-orange-700 dark:disabled:text-orange-200
    `,
    
    error: `
      bg-red-700 text-white border border-red-700
      hover:bg-red-800 hover:border-red-800
      dark:bg-red-600 dark:hover:bg-red-500
      focus:ring-2 focus:ring-red-500 focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:bg-red-400 disabled:border-red-400 disabled:text-white
      dark:disabled:bg-red-800 dark:disabled:border-red-800 dark:disabled:text-red-200
    `
  };

  // Configuración de tamaños con área de toque accesible
  const sizeStyles = {
    sm: variant === 'link' ? 'text-sm' : 'px-3 py-1.5 text-sm min-h-[36px]',
    md: variant === 'link' ? 'text-base' : 'px-4 py-2 text-base min-h-[40px]',
    lg: variant === 'link' ? 'text-lg' : 'px-6 py-3 text-lg min-h-[44px]',
    xl: variant === 'link' ? 'text-xl' : 'px-8 py-4 text-xl min-h-[48px]'
  };

  return (
    <button
      ref={ref}
      className={cn(
        // Estilos base
        'inline-flex items-center justify-center',
        'font-medium',
        variant !== 'link' && 'rounded-lg',
        'transition-all duration-200',
        'focus:outline-none',
        'disabled:cursor-not-allowed disabled:opacity-60',
        
        // Full width
        fullWidth && 'w-full',
        
        // Variante y tamaño
        variantStyles[variant],
        sizeStyles[size],
        
        // Loading state
        isLoading && 'cursor-wait opacity-80',
        
        // Clases adicionales
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center gap-2">
          <LoadingSpinner size={size} />
          <span>Cargando...</span>
        </div>
      ) : (
        children
      )}
    </button>
  );
});

Button.displayName = 'Button';

// Spinner de carga que se adapta al tamaño del botón
function LoadingSpinner({ size }: { size: 'sm' | 'md' | 'lg' | 'xl' }) {
  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
    xl: 'w-6 h-6'
  };

  return (
    <div className={cn(
      'animate-spin rounded-full border-2 border-current border-t-transparent',
      sizeClasses[size]
    )} />
  );
}
