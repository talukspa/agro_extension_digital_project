'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Button } from '@/components/ui/Button';

export default function UnauthorizedPage() {
  const { user, signOut } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="mx-auto h-12 w-12 flex items-center justify-center bg-red-600 rounded-full">
          <svg
            className="h-8 w-8 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-foreground">
          Acceso no autorizado
        </h2>
        <p className="mt-2 text-center text-sm text-muted-foreground">
          No tienes permisos para acceder a esta página
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            <svg
              className="mx-auto h-24 w-24 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L5.636 5.636"
              />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-foreground">
              Sin permisos suficientes
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Tu cuenta actual no tiene los permisos necesarios para acceder a este recurso.
            </p>

            {user && (
              <div className="mt-4 p-4 bg-background rounded-md">
                <p className="text-sm text-foreground">
                  <strong>Usuario actual:</strong> {user.email}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Si crees que esto es un error, contacta al administrador del sistema.
                </p>
              </div>
            )}

            <div className="mt-6 space-y-3">
              <Link
                href="/dashboard"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-plum-600 hover:bg-plum-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-plum-500"
              >
                Ir al Panel Principal
              </Link>
              
              <Link
                href="/"
                className="w-full flex justify-center py-2 px-4 border border rounded-md shadow-sm text-sm font-medium text-foreground bg-card hover:bg-background focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-plum-500"
              >
                Volver al Inicio
              </Link>

              {user && (
                <Button
                  onClick={handleSignOut}
                  variant="outline"
                  fullWidth
                  className="text-red-700 border-red-300 hover:bg-red-50 dark:text-red-300 dark:border-red-700 dark:hover:bg-red-900/20"
                >
                  Cerrar Sesión
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
