import React from 'react';
import { User, Business, AuditorProfile, BusinessUserRequest } from '@/lib/types/auth';
import { USER_TYPES } from '@/lib/types/permissions';
import { Avatar } from '@/components/ui/Avatar';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';

interface RequestCardProps {
  type: 'user' | 'business' | 'auditor' | 'business-user';
  data: User | Business | AuditorProfile | (BusinessUserRequest & { user?: User | null; business?: Business | null });
  onApprove: () => void;
  onReject: () => void;
}

const RequestCard: React.FC<RequestCardProps> = ({ type, data, onApprove, onReject }) => {
  const getAvatarData = () => {
    switch (type) {
      case 'user':
        const user = data as User;
        return {
          initials: user.displayName?.charAt(0) || user.email.charAt(0),
          userType: USER_TYPES.ADMIN // Asumiendo que son usuarios generales
        };
      case 'business':
        const business = data as Business;
        return {
          initials: business.businessName?.charAt(0) || 'E',
          userType: USER_TYPES.BUSINESS_OWNER
        };
      case 'auditor':
        return {
          initials: 'A',
          userType: USER_TYPES.AUDITOR
        };
      case 'business-user':
        const request = data as BusinessUserRequest & { user?: User | null };
        return {
          initials: request.user?.displayName?.charAt(0) || request.user?.email?.charAt(0) || 'U',
          userType: USER_TYPES.BUSINESS_USER
        };
      default:
        return {
          initials: '?',
          userType: undefined
        };
    }
  };

  const renderContent = () => {
    switch (type) {
      case 'user':
        const user = data as User;
        return (
          <div>
            <h4 className="text-sm font-medium text-foreground">
              {user.displayName || 'Sin nombre'}
            </h4>
            <p className="text-sm text-muted-foreground">{user.email}</p>
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-muted-foreground">
                Solicitado: {user.requestedAt ? new Date(user.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <StatusBadge status="pending" />
            </div>
          </div>
        );

      case 'business':
        const business = data as Business;
        return (
          <div>
            <h4 className="text-sm font-medium text-foreground">
              {business.businessName || 'Sin nombre'}
            </h4>
            <p className="text-sm text-muted-foreground">
              Tipo: {business.businessType || 'No especificado'}
            </p>
            <p className="text-sm text-muted-foreground">
              Contacto: {business.contactEmail || 'No especificado'}
            </p>
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-muted-foreground">
                Solicitado: {business.requestedAt ? new Date(business.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <StatusBadge status="pending" />
            </div>
          </div>
        );

      case 'auditor':
        const auditor = data as AuditorProfile;
        return (
          <div>
            <h4 className="text-sm font-medium text-foreground">
              Solicitud de Auditor
            </h4>
            <p className="text-sm text-muted-foreground">
              Usuario: {auditor.userId}
            </p>
            <p className="text-sm text-muted-foreground">
              Certificaciones: {auditor.certifications?.join(', ') || 'N/A'}
            </p>
            <p className="text-sm text-muted-foreground">
              Especializaciones: {auditor.specializations?.join(', ') || 'N/A'}
            </p>
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-muted-foreground">
                Solicitado: {auditor.requestedAt ? new Date(auditor.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <StatusBadge status="pending" />
            </div>
          </div>
        );

      case 'business-user':
        const request = data as BusinessUserRequest & { user?: User | null; business?: Business | null };
        return (
          <div>
            <h4 className="text-sm font-medium text-foreground">
              {request.user?.displayName || request.user?.email || 'Usuario desconocido'}
            </h4>
            <p className="text-sm text-muted-foreground">
              Quiere unirse a: <span className="font-medium">{request.business?.businessName || 'Empresa desconocida'}</span>
            </p>
            <p className="text-sm text-muted-foreground">
              Rol solicitado: <span className="font-medium">{request.requestedRole}</span>
            </p>
            {request.message && (
              <p className="text-sm text-muted-foreground">
                Mensaje: "{request.message}"
              </p>
            )}
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-muted-foreground">
                Solicitado: {request.requestedAt ? new Date(request.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <StatusBadge status="pending" />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const avatarData = getAvatarData();

  return (
    <div className="border border-border rounded-lg p-4 bg-card hover:bg-accent/5 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <Avatar 
                initials={avatarData.initials}
                userType={avatarData.userType}
                size="md"
              />
            </div>
            {renderContent()}
          </div>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="success"
            size="sm"
            onClick={onApprove}
          >
            Aprobar
          </Button>
          <Button
            variant="error"
            size="sm"
            onClick={onReject}
          >
            Rechazar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default RequestCard;
