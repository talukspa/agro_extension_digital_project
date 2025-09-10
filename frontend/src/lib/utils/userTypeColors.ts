import { USER_TYPES } from '@/lib/types/permissions';

/**
 * Mapeo de colores por tipo de usuario usando variables semánticas
 * Proporciona consistencia visual para diferentes tipos de usuario
 */
export const getUserTypeColors = (userType: string) => {
  switch (userType) {
    case USER_TYPES.ADMIN:
      return {
        text: 'text-admin-color',
        background: 'bg-admin-color/10',
        backgroundSolid: 'bg-admin-color',
        foreground: 'text-primary-foreground',
        border: 'border-admin-color',
        avatar: 'bg-admin-color/20 text-admin-color'
      };
    case USER_TYPES.AUDITOR:
      return {
        text: 'text-auditor-color',
        background: 'bg-auditor-color/10',
        backgroundSolid: 'bg-auditor-color',
        foreground: 'text-primary-foreground',
        border: 'border-auditor-color',
        avatar: 'bg-auditor-color/20 text-auditor-color'
      };
    case USER_TYPES.BUSINESS_USER:
    case USER_TYPES.BUSINESS_OWNER:
      return {
        text: 'text-business-color',
        background: 'bg-business-color/10',
        backgroundSolid: 'bg-business-color',
        foreground: 'text-accent-foreground',
        border: 'border-business-color',
        avatar: 'bg-business-color/20 text-business-color'
      };
    default:
      return {
        text: 'text-muted-foreground',
        background: 'bg-muted',
        backgroundSolid: 'bg-muted',
        foreground: 'text-muted-foreground',
        border: 'border-muted',
        avatar: 'bg-muted text-muted-foreground'
      };
  }
};

/**
 * Obtiene el color del avatar para un tipo de usuario específico
 */
export const getUserTypeAvatarColor = (userType: string): string => {
  return getUserTypeColors(userType).avatar;
};

/**
 * Obtiene el color del badge/etiqueta para un tipo de usuario específico
 */
export const getUserTypeBadgeColor = (userType: string): string => {
  const colors = getUserTypeColors(userType);
  return `${colors.background} ${colors.text}`;
};

/**
 * Colores para estados de solicitud (pendiente, aprobado, rechazado, etc.)
 */
export const getRequestStatusColors = (status: 'pending' | 'approved' | 'rejected' | 'suspended' | 'active' | 'inactive') => {
  switch (status) {
    case 'pending':
      return {
        text: 'text-warning',
        background: 'bg-warning-background',
        border: 'border-warning',
        badge: 'bg-warning-background text-warning'
      };
    case 'approved':
    case 'active':
      return {
        text: 'text-success',
        background: 'bg-success-background',
        border: 'border-success',
        badge: 'bg-success-background text-success'
      };
    case 'rejected':
    case 'suspended':
    case 'inactive':
      return {
        text: 'text-error',
        background: 'bg-error-background',
        border: 'border-error',
        badge: 'bg-error-background text-error'
      };
    default:
      return {
        text: 'text-muted-foreground',
        background: 'bg-muted',
        border: 'border',
        badge: 'bg-muted text-muted-foreground'
      };
  }
};
