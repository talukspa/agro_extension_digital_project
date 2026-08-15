'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { USER_TYPES, USER_TYPE_DISPLAY_NAMES, USER_TYPE_DESCRIPTIONS } from '@/lib/types/permissions';
import { Button } from '@/components/ui/Button';

function UserTypeSelectionContent() {
  const [selectedType, setSelectedType] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { user, signOut } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await signOut();
      router.push('/auth/signin');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
      setError('Error al cerrar sesión');
    }
  };

  const userTypeOptions = [
    {
      id: USER_TYPES.BUSINESS_OWNER,
      title: USER_TYPE_DISPLAY_NAMES[USER_TYPES.BUSINESS_OWNER],
      description: 'Crear una nueva empresa para certificación',
      icon: '👔',
      action: 'create-business'
    },
    {
      id: USER_TYPES.BUSINESS_USER,
      title: USER_TYPE_DISPLAY_NAMES[USER_TYPES.BUSINESS_USER],
      description: 'Unirse a una empresa existente',
      icon: '🏢',
      action: 'join-business'
    },
    {
      id: USER_TYPES.AUDITOR,
      title: USER_TYPE_DISPLAY_NAMES[USER_TYPES.AUDITOR],
      description: 'Solicitar ser auditor certificado',
      icon: '📋',
      action: 'auditor-application'
    }
  ];

  const handleSelection = async (userType: string, action: string) => {
    if (!user) return;
    
    setIsLoading(true);
    setError('');

    try {
      // Route based on the action
      switch (action) {
        case 'create-business':
          router.push('/onboarding/create-business');
          break;
        case 'join-business':
          router.push('/onboarding/join-business');
          break;
        case 'auditor-application':
          router.push('/onboarding/auditor-application');
          break;
        default:
          setError('Acción no válida');
      }
    } catch (err: any) {
      setError('Error al procesar la selección: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header with logout button */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center">
            <h2 className="text-lg font-semibold text-foreground">
              AgroExtensión Digital
            </h2>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
              {user?.email}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="text-muted-foreground hover:text-foreground"
            >
              Cerrar Sesión
            </Button>
          </div>
        </div>

        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-foreground mb-4">
            ¡Bienvenido a AgroExtensión Digital!
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Para comenzar, selecciona el tipo de usuario que mejor describe tu rol en el proceso de certificación agrícola.
          </p>
        </div>

        {error && (
          <div className="mb-8 bg-error-background border border-error rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-error" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-error">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {userTypeOptions.map((option) => (
            <div
              key={option.id}
              className={`relative bg-card rounded-lg shadow-sm border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
                selectedType === option.id
                  ? 'border-primary ring-2 ring-primary/20'
                  : 'border-border hover:border-primary/50'
              }`}
              onClick={() => setSelectedType(option.id)}
            >
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">{option.icon}</div>
                <h3 className="text-xl font-semibold text-card-foreground mb-3">
                  {option.title}
                </h3>
                <p className="text-muted-foreground mb-6">
                  {option.description}
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSelection(option.id, option.action);
                  }}
                  disabled={isLoading}
                  className={`w-full py-3 px-4 rounded-md font-medium transition-colors duration-200 ${
                    isLoading
                      ? 'bg-muted cursor-not-allowed text-muted-foreground'
                      : 'bg-primary hover:bg-primary/90 text-primary-foreground'
                  }`}
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                      Procesando...
                    </div>
                  ) : (
                    'Seleccionar'
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-muted-foreground">
            ¿Necesitas ayuda para decidir? 
            <a href="/help/user-types" className="text-primary hover:text-primary/80 ml-1">
              Conoce más sobre cada tipo de usuario
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function UserTypeSelectionPage() {
  return (
    <ProtectedRoute requireApproval={false}>
      <UserTypeSelectionContent />
    </ProtectedRoute>
  );
}
