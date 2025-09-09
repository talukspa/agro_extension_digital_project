'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { getAllBusinesses, requestBusinessAccess, updateUserProfile } from '@/lib/firebase/firestore';
import { USER_TYPES } from '@/lib/types/permissions';
import { Business } from '@/lib/types/auth';

export default function JoinBusinessPage() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingBusinesses, setLoadingBusinesses] = useState(true);
  const [error, setError] = useState('');
  
  const { user, refreshUserData } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadBusinesses();
  }, []);

  const loadBusinesses = async () => {
    try {
      setLoadingBusinesses(true);
      const businessList = await getAllBusinesses();
      // Only show approved businesses
      const approvedBusinesses = businessList.filter(b => b.status === 'approved');
      setBusinesses(approvedBusinesses);
    } catch (err: any) {
      setError('Error al cargar las empresas: ' + err.message);
    } finally {
      setLoadingBusinesses(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !selectedBusinessId) return;

    setIsLoading(true);
    setError('');

    try {
      // Create request to join business
      await requestBusinessAccess(
        user.uid, 
        selectedBusinessId, 
        'employee',
        message || undefined
      );

      // Update user profile to business_user type with pending status
      await updateUserProfile(user.uid, {
        userTypeId: USER_TYPES.BUSINESS_USER,
        requestedBusinessId: selectedBusinessId,
        status: 'pending' // Request needs business owner approval
      });

      // Refresh user data
      await refreshUserData();

      // Redirect to pending approval page
      router.push('/pending-approval');
      
    } catch (err: any) {
      setError('Error al enviar la solicitud: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-plum-50 dark:bg-plum-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-plum-600 mx-auto"></div>
          <p className="mt-4 text-plum-700 dark:text-plum-300">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-plum-50 dark:bg-plum-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-plum-900 dark:text-plum-100 mb-4">
            Solicitar Acceso a Empresa
          </h1>
          <p className="text-lg text-plum-700 dark:text-plum-300">
            Como empleado, solicita acceso a una empresa existente. 
            El propietario de la empresa deberá aprobar tu solicitud.
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
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

        <div className="bg-white dark:bg-plum-900 shadow rounded-lg p-8">
          {loadingBusinesses ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-plum-600 mx-auto"></div>
              <p className="mt-4 text-plum-700 dark:text-plum-300">Cargando empresas...</p>
            </div>
          ) : businesses.length === 0 ? (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h3M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <p className="mt-4 text-plum-700 dark:text-plum-300">No hay empresas disponibles en este momento.</p>
              <p className="text-sm text-plum-600 dark:text-plum-400 mt-2">
                Las empresas deben ser aprobadas por un administrador antes de aparecer aquí.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-4">
                  Empresas Disponibles
                </label>
                <div className="space-y-3">
                  {businesses.map((business) => (
                    <div
                      key={business.id}
                      className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                        selectedBusinessId === business.id
                          ? 'border-plum-500 bg-green-50 ring-2 ring-green-200'
                          : 'border-plum-200 dark:border-plum-800 hover:border-plum-300 dark:border-plum-700 hover:bg-plum-50 dark:bg-plum-950'
                      }`}
                      onClick={() => setSelectedBusinessId(business.id)}
                    >
                      <div className="flex items-start">
                        <input
                          type="radio"
                          name="business"
                          value={business.id}
                          checked={selectedBusinessId === business.id}
                          onChange={() => setSelectedBusinessId(business.id)}
                          className="mt-1 focus:ring-plum-500 h-4 w-4 text-fresh-600 dark:text-fresh-400 border-plum-300 dark:border-plum-700"
                        />
                        <div className="ml-3 flex-1">
                          <h3 className="text-lg font-medium text-plum-900 dark:text-plum-100">
                            {business.businessName}
                          </h3>
                          {business.description && (
                            <p className="text-plum-700 dark:text-plum-300 mt-1">{business.description}</p>
                          )}
                          <div className="mt-2 flex flex-wrap gap-4 text-sm text-plum-600 dark:text-plum-400">
                            {business.businessType && (
                              <span>📍 {business.businessType}</span>
                            )}
                            {business.location && (
                              <span>🏢 {business.location}</span>
                            )}
                            {business.website && (
                              <a 
                                href={business.website} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-fresh-600 dark:text-fresh-400 hover:text-fresh-700 dark:hover:text-fresh-300"
                                onClick={(e) => e.stopPropagation()}
                              >
                                🌐 Sitio web
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {selectedBusinessId && (
                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
                    Mensaje (Opcional)
                  </label>
                  <textarea
                    name="message"
                    id="message"
                    rows={3}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
                    placeholder="Cuéntale al propietario de la empresa por qué quieres unirte..."
                  />
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-blue-800 text-sm">
                      <strong>Nota:</strong> Tu solicitud será enviada al propietario de la empresa seleccionada. 
                      Te notificaremos por email cuando tu solicitud sea aprobada.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => router.push('/onboarding/user-type')}
                  className="flex-1 py-3 px-4 border border-plum-300 dark:border-plum-700 rounded-md text-plum-800 dark:text-plum-200 hover:bg-plum-50 dark:bg-plum-950 font-medium transition-colors duration-200"
                >
                  Volver
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !selectedBusinessId}
                  className={`flex-1 py-3 px-4 rounded-md font-medium transition-colors duration-200 ${
                    isLoading || !selectedBusinessId
                      ? 'bg-gray-300 cursor-not-allowed'
                      : 'bg-plum-600 hover:bg-plum-700 text-white'
                  }`}
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Enviando Solicitud...
                    </div>
                  ) : (
                    'Enviar Solicitud'
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
