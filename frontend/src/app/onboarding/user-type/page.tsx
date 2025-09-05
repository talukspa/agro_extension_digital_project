'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { USER_TYPES, USER_TYPE_DISPLAY_NAMES, USER_TYPE_DESCRIPTIONS } from '@/lib/types/permissions';

export default function UserTypeSelectionPage() {
  const [selectedType, setSelectedType] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { user } = useAuth();
  const router = useRouter();

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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            ¡Bienvenido a AgroExtensión Digital!
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Para comenzar, selecciona el tipo de usuario que mejor describe tu rol en el proceso de certificación agrícola.
          </p>
        </div>

        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {userTypeOptions.map((option) => (
            <div
              key={option.id}
              className={`relative bg-white rounded-lg shadow-sm border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
                selectedType === option.id
                  ? 'border-green-500 ring-2 ring-green-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedType(option.id)}
            >
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">{option.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {option.title}
                </h3>
                <p className="text-gray-600 mb-6">
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
                      ? 'bg-gray-300 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
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
          <p className="text-sm text-gray-500">
            ¿Necesitas ayuda para decidir? 
            <a href="/help/user-types" className="text-green-600 hover:text-green-500 ml-1">
              Conoce más sobre cada tipo de usuario
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
