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

  // Configuración de variantes con variables semánticas WCAG AA
  const variantStyles = {
    // Primario: Usa la variable --primary con contraste garantizado
    primary: `
      bg-primary text-primary-foreground border border-primary
      hover:bg-primary/90 hover:border-primary/90
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    // Secundario: Usa variables --secondary para consistencia
    secondary: `
      bg-secondary text-secondary-foreground border border-secondary
      hover:bg-secondary/80 hover:border-secondary/80
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    // Acento: Usa la variable --accent
    accent: `
      bg-accent text-accent-foreground border border-accent
      hover:bg-accent/90 hover:border-accent/90
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    // Outline: Transparente con borde semántico
    outline: `
      bg-transparent text-foreground border border-border
      hover:bg-accent/10 hover:border-accent
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    // Ghost: Completamente transparente
    ghost: `
      bg-transparent text-foreground border border-transparent
      hover:bg-accent/10 hover:text-accent
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    // Link: Sin fondo, solo texto
    link: `
      bg-transparent text-primary border border-transparent p-0 h-auto font-medium
      hover:text-primary/80 hover:underline
      focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:rounded
      disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline
    `,
    
    // Estados semánticos usando nuevas variables
    success: `
      bg-success text-success-foreground border border-success
      hover:bg-success/90 hover:border-success/90
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    warning: `
      bg-warning text-warning-foreground border border-warning
      hover:bg-warning/90 hover:border-warning/90
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    
    error: `
      bg-error text-error-foreground border border-error
      hover:bg-error/90 hover:border-error/90
      focus:ring-2 focus:ring-ring focus:ring-offset-2
      shadow-sm hover:shadow-md
      disabled:opacity-50 disabled:cursor-not-allowed
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
