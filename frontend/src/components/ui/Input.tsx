// Componente Input - Campo de entrada consistente con la paleta Plum
// Incluye validación visual y accesibilidad completa

import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, helperText, variant = 'default', id, ...props }, ref) => {
    // Generar ID único si no se proporciona
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    
    // Determinar variante basada en error
    const currentVariant = error ? 'error' : variant;
    
    // Estilos base con accesibilidad WCAG AA
    const baseStyles = `
      flex w-full px-3 py-2 text-sm
      border rounded-md
      bg-background text-foreground
      placeholder:text-muted-foreground
      focus:outline-none focus:ring-2 focus:ring-offset-2
      disabled:cursor-not-allowed disabled:opacity-50
      transition-colors duration-200
    `;
    
    // Variantes de color
    const variantStyles = {
      default: `
        border-border
        focus:ring-ring focus:border-ring
        hover:border-ring/50
      `,
      success: `
        border-success-300 dark:border-success-700
        focus:ring-success-500 focus:border-success-500
        hover:border-success-400
      `,
      warning: `
        border-warning-300 dark:border-warning-700
        focus:ring-warning-500 focus:border-warning-500
        hover:border-warning-400
      `,
      error: `
        border-error-300 dark:border-error-700
        focus:ring-error-500 focus:border-error-500
        hover:border-error-400
      `
    };

    return (
      <div className="space-y-2">
        {label && (
          <label 
            htmlFor={inputId}
            className="text-sm font-medium text-foreground"
          >
            {label}
          </label>
        )}
        
        <input
          type={type}
          id={inputId}
          className={cn(
            baseStyles,
            variantStyles[currentVariant],
            className
          )}
          ref={ref}
          aria-invalid={!!error}
          aria-describedby={
            error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />
        
        {/* Mensaje de error */}
        {error && (
          <p 
            id={`${inputId}-error`}
            className="text-sm text-error-600 dark:text-error-400 flex items-center gap-1"
            role="alert"
          >
            <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        
        {/* Texto de ayuda */}
        {helperText && !error && (
          <p 
            id={`${inputId}-helper`}
            className="text-sm text-muted-foreground"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
