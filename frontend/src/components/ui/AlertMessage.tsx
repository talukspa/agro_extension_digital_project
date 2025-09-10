// Componente AlertMessage - Sistema de alertas semánticas
// Usa variables CSS semánticas para estados de error, warning, success e info

import { cn } from '@/lib/utils';

// Iconos SVG simples para evitar dependencias adicionales
const CheckCircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
  </svg>
);

const AlertCircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
  </svg>
);

const XCircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
  </svg>
);

const InfoIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
  </svg>
);

const XIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
);

export interface AlertMessageProps {
  type: 'success' | 'warning' | 'error' | 'info';
  title?: string;
  message: string;
  icon?: boolean;
  className?: string;
  onClose?: () => void;
}

export const AlertMessage: React.FC<AlertMessageProps> = ({
  type,
  title,
  message,
  icon = true,
  className,
  onClose
}) => {
  // Configuración de estilos por tipo usando variables semánticas
  const typeStyles = {
    success: {
      container: 'bg-success-background border-success text-success',
      icon: CheckCircleIcon,
      iconColor: 'text-success'
    },
    warning: {
      container: 'bg-warning-background border-warning text-warning',
      icon: AlertCircleIcon,
      iconColor: 'text-warning'
    },
    error: {
      container: 'bg-error-background border-error text-error',
      icon: XCircleIcon,
      iconColor: 'text-error'
    },
    info: {
      container: 'bg-primary/10 border-primary text-primary',
      icon: InfoIcon,
      iconColor: 'text-primary'
    }
  };

  const config = typeStyles[type];
  const IconComponent = config.icon;

  return (
    <div
      className={cn(
        'border rounded-md p-4',
        config.container,
        className
      )}
      role="alert"
    >
      <div className="flex">
        {icon && (
          <div className="flex-shrink-0">
            <IconComponent 
              className={cn('h-5 w-5', config.iconColor)} 
              aria-hidden="true" 
            />
          </div>
        )}
        <div className={cn('flex-1', icon && 'ml-3')}>
          {title && (
            <h3 className="font-medium mb-1">
              {title}
            </h3>
          )}
          <p className={cn('text-sm', !title && 'font-medium')}>
            {message}
          </p>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <button
              type="button"
              className={cn(
                'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2',
                'hover:bg-black/5 dark:hover:bg-white/5',
                config.iconColor,
                'focus:ring-ring'
              )}
              onClick={onClose}
            >
              <span className="sr-only">Cerrar</span>
              <XIcon className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertMessage;
