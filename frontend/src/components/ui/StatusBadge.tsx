// Componente StatusBadge - Sistema de etiquetas de estado semánticas
// Usa variables CSS semánticas para consistencia visual y accesibilidad

import { cn } from '@/lib/utils';
import { getRequestStatusColors } from '@/lib/utils/userTypeColors';

export interface StatusBadgeProps {
  status: 'pending' | 'approved' | 'rejected' | 'suspended' | 'active' | 'inactive';
  variant?: 'default' | 'outline' | 'solid';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children?: React.ReactNode;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  variant = 'default',
  size = 'md',
  className,
  children
}) => {
  // Mapeo de estados a colores semánticos
  const statusColors = getRequestStatusColors(status);
  
  // Configuración de variantes
  const variantStyles = {
    default: `${statusColors.badge} border border-transparent`,
    outline: `bg-transparent ${statusColors.text} border ${statusColors.border}`,
    solid: `${statusColors.background} ${statusColors.text} border border-transparent`
  };

  // Configuración de tamaños
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs font-medium',
    md: 'px-2.5 py-0.5 text-xs font-medium',
    lg: 'px-3 py-1 text-sm font-medium'
  };

  // Mapeo de texto por defecto para cada estado
  const statusText = {
    pending: 'Pendiente',
    approved: 'Aprobado',
    rejected: 'Rechazado',
    suspended: 'Suspendido',
    active: 'Activo',
    inactive: 'Inactivo'
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full transition-colors',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children || statusText[status]}
    </span>
  );
};

export default StatusBadge;
