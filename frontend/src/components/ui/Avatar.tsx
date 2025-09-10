// Componente Avatar - Sistema de avatares con tipado de usuario semántico
// Usa variables CSS semánticas para diferenciación visual por tipo de usuario

import { cn } from '@/lib/utils';
import { getUserTypeAvatarColor } from '@/lib/utils/userTypeColors';

export interface AvatarProps {
  userType?: string;
  initials: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  customColors?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  userType,
  initials,
  size = 'md',
  className,
  customColors
}) => {
  // Obtener colores basados en el tipo de usuario o usar colores personalizados
  const avatarColors = customColors || (userType ? getUserTypeAvatarColor(userType) : 'bg-muted text-muted-foreground');

  // Configuración de tamaños
  const sizeStyles = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
    xl: 'h-16 w-16 text-lg'
  };

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center rounded-full font-medium uppercase',
        sizeStyles[size],
        avatarColors,
        className
      )}
    >
      {initials.slice(0, 2)}
    </div>
  );
};

export default Avatar;
