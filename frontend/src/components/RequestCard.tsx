import React from 'react';
import { User, Business, AuditorProfile, BusinessUserRequest } from '@/lib/types/auth';

interface RequestCardProps {
  type: 'user' | 'business' | 'auditor' | 'business-user';
  data: User | Business | AuditorProfile | (BusinessUserRequest & { user?: User | null; business?: Business | null });
  onApprove: () => void;
  onReject: () => void;
}

const RequestCard: React.FC<RequestCardProps> = ({ type, data, onApprove, onReject }) => {
  const getAvatar = () => {
    switch (type) {
      case 'user':
        const user = data as User;
        return user.displayName?.charAt(0) || user.email.charAt(0);
      case 'business':
        const business = data as Business;
        return business.businessName?.charAt(0) || 'E';
      case 'auditor':
        return 'A';
      case 'business-user':
        const request = data as BusinessUserRequest & { user?: User | null };
        return request.user?.displayName?.charAt(0) || request.user?.email?.charAt(0) || 'U';
      default:
        return '?';
    }
  };

  const getAvatarColor = () => {
    switch (type) {
      case 'user':
        return 'bg-gray-300 text-plum-800 dark:text-plum-200';
      case 'business':
        return 'bg-blue-100 text-blue-700';
      case 'auditor':
        return 'bg-purple-100 text-purple-700';
      case 'business-user':
        return 'bg-fresh-100 dark:bg-fresh-900 text-fresh-700 dark:text-fresh-300';
      default:
        return 'bg-gray-300 text-plum-800 dark:text-plum-200';
    }
  };

  const getBadgeColor = () => {
    switch (type) {
      case 'user':
        return 'bg-yellow-100 text-yellow-800';
      case 'business':
        return 'bg-blue-100 text-blue-800';
      case 'auditor':
        return 'bg-purple-100 text-purple-800';
      case 'business-user':
        return 'bg-fresh-100 dark:bg-fresh-900 text-fresh-800 dark:text-fresh-100';
      default:
        return 'bg-plum-100 dark:bg-plum-800 text-plum-800 dark:text-plum-200';
    }
  };

  const renderContent = () => {
    switch (type) {
      case 'user':
        const user = data as User;
        return (
          <div>
            <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
              {user.displayName || 'Sin nombre'}
            </h4>
            <p className="text-sm text-plum-600 dark:text-plum-400">{user.email}</p>
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-plum-400 dark:text-plum-500">
                Solicitado: {user.requestedAt ? new Date(user.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor()}`}>
                Pendiente
              </span>
            </div>
          </div>
        );

      case 'business':
        const business = data as Business;
        return (
          <div>
            <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
              {business.businessName || 'Sin nombre'}
            </h4>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Tipo: {business.businessType || 'No especificado'}
            </p>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Contacto: {business.contactEmail || 'No especificado'}
            </p>
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-plum-400 dark:text-plum-500">
                Solicitado: {business.requestedAt ? new Date(business.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor()}`}>
                Pendiente
              </span>
            </div>
          </div>
        );

      case 'auditor':
        const auditor = data as AuditorProfile;
        return (
          <div>
            <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
              Solicitud de Auditor
            </h4>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Usuario: {auditor.userId}
            </p>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Certificaciones: {auditor.certifications?.join(', ') || 'N/A'}
            </p>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Especializaciones: {auditor.specializations?.join(', ') || 'N/A'}
            </p>
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-plum-400 dark:text-plum-500">
                Solicitado: {auditor.requestedAt ? new Date(auditor.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor()}`}>
                Pendiente
              </span>
            </div>
          </div>
        );

      case 'business-user':
        const request = data as BusinessUserRequest & { user?: User | null; business?: Business | null };
        return (
          <div>
            <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
              {request.user?.displayName || request.user?.email || 'Usuario desconocido'}
            </h4>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Quiere unirse a: <span className="font-medium">{request.business?.businessName || 'Empresa desconocida'}</span>
            </p>
            <p className="text-sm text-plum-600 dark:text-plum-400">
              Rol solicitado: <span className="font-medium">{request.requestedRole}</span>
            </p>
            {request.message && (
              <p className="text-sm text-plum-600 dark:text-plum-400">
                Mensaje: "{request.message}"
              </p>
            )}
            <div className="flex items-center space-x-4 mt-1">
              <p className="text-xs text-plum-400 dark:text-plum-500">
                Solicitado: {request.requestedAt ? new Date(request.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
              </p>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeColor()}`}>
                Pendiente
              </span>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="border border-plum-200 dark:border-plum-800 rounded-lg p-4 hover:bg-plum-50 dark:bg-plum-950 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className={`h-10 w-10 rounded-full ${getAvatarColor()} flex items-center justify-center`}>
                <span className="text-sm font-medium">
                  {getAvatar()}
                </span>
              </div>
            </div>
            {renderContent()}
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={onApprove}
            className="bg-fresh-600 dark:bg-fresh-700 hover:bg-fresh-700 dark:hover:bg-fresh-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            Aprobar
          </button>
          <button
            onClick={onReject}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            Rechazar
          </button>
        </div>
      </div>
    </div>
  );
};

export default RequestCard;
