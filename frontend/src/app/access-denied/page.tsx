'use client';

import { useAuth } from '@/lib/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AccessDeniedPage() {
  const { user, userType, loading, signOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
        return;
      }
      
      // If user is approved, redirect to dashboard
      if (user.status === 'approved') {
        router.push('/dashboard');
        return;
      }

      // If user is pending, redirect to pending approval
      if (user.status === 'pending') {
        router.push('/pending-approval');
        return;
      }
    }
  }, [user, loading, router]);

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user || user.status !== 'rejected') {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-gray-900">
                  Agro Extension Digital
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-700">
                {user.displayName || user.email}
              </div>
              <button
                onClick={handleSignOut}
                className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6 text-center">
              {/* Icon */}
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Acceso Denegado
              </h2>
              
              <p className="text-lg text-gray-600 mb-6">
                Lo sentimos, tu solicitud de acceso ha sido rechazada.
              </p>

              {/* Rejection details */}
              <div className="bg-red-50 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Detalles del rechazo
                </h3>
                
                {user.rejectionReason ? (
                  <div className="bg-white rounded p-4 mb-4">
                    <p className="text-sm text-gray-700">
                      <strong>Razón:</strong> {user.rejectionReason}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-600 mb-4">
                    No se proporcionó una razón específica para el rechazo.
                  </p>
                )}

                <div className="text-left space-y-3">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-red-400 mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-gray-700">
                        Puedes contactar a nuestro equipo de soporte para obtener más información.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-red-400 mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-gray-700">
                        Si consideras que esto es un error, puedes solicitar una revisión.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-red-400 mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-gray-700">
                        Asegúrate de que tu información esté completa y sea precisa antes de volver a solicitar acceso.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* User info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="text-sm font-medium text-gray-900 mb-2">
                  Información de tu solicitud
                </h3>
                <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2 text-sm">
                  <div>
                    <dt className="text-gray-500">Email:</dt>
                    <dd className="text-gray-900">{user.email}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Tipo de usuario solicitado:</dt>
                    <dd className="text-gray-900">{userType?.displayName || 'Cargando...'}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Fecha de solicitud:</dt>
                    <dd className="text-gray-900">
                      {user.requestedAt ? new Date(user.requestedAt).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      }) : 'No disponible'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Fecha de rechazo:</dt>
                    <dd className="text-gray-900">
                      {user.rejectedAt ? new Date(user.rejectedAt).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      }) : 'No disponible'}
                    </dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-gray-500">Revisado por:</dt>
                    <dd className="text-gray-900">{user.rejectedBy || 'Administrador del sistema'}</dd>
                  </div>
                </dl>
              </div>

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={() => window.open('mailto:support@agroextension.com?subject=Solicitud de revisión de acceso')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-medium"
                >
                  Contactar Soporte
                </button>
                <button
                  onClick={handleSignOut}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-md text-sm font-medium"
                >
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
