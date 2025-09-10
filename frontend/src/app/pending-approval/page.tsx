'use client';

import { useAuth } from '@/lib/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';

export default function PendingApprovalPage() {
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

      // If user is rejected, redirect to access denied
      if (user.status === 'rejected') {
        router.push('/access-denied');
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
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user || user.status !== 'pending') {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-card shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-foreground">
                  Agro Extension Digital
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-foreground">
                {user.displayName || user.email}
              </div>
              <Button
                onClick={handleSignOut}
                variant="secondary"
                size="sm"
              >
                Cerrar sesión
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-card overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6 text-center">
              {/* Icon */}
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-warning-background mb-4">
                <svg className="h-8 w-8 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>

              <h2 className="text-2xl font-bold text-foreground mb-4">
                Aprobación Pendiente
              </h2>
              
              <p className="text-lg text-muted-foreground mb-6">
                Tu cuenta está siendo revisada por nuestro equipo de administradores.
              </p>

              <div className="bg-warning-background rounded-lg p-6 mb-6">
                <h3 className="text-lg font-medium text-foreground mb-3">
                  ¿Qué sigue?
                </h3>
                <div className="text-left space-y-3">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-warning mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-foreground">
                        Nuestro equipo revisará tu solicitud de acceso y verificará tu información.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-warning mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-foreground">
                        Recibirás una notificación por email una vez que tu cuenta sea aprobada.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="h-2 w-2 rounded-full bg-warning mt-2"></div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-foreground">
                        Una vez aprobada, podrás acceder a todas las funcionalidades según tu tipo de usuario.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* User info */}
              <div className="bg-background rounded-lg p-4 mb-6">
                <h3 className="text-sm font-medium text-foreground mb-2">
                  Información de tu solicitud
                </h3>
                <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2 text-sm">
                  <div>
                    <dt className="text-muted-foreground">Email:</dt>
                    <dd className="text-foreground">{user.email}</dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Tipo de usuario solicitado:</dt>
                    <dd className="text-foreground">{userType?.displayName || 'Cargando...'}</dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Fecha de solicitud:</dt>
                    <dd className="text-foreground">
                      {user.requestedAt ? new Date(user.requestedAt).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      }) : 'No disponible'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Estado:</dt>
                    <dd>
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-warning-background text-warning">
                        Pendiente de aprobación
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="text-sm text-muted-foreground">
                <p>
                  Si tienes preguntas sobre tu solicitud, puedes contactar a nuestro equipo de soporte.
                </p>
                <p className="mt-2">
                  <strong>Tiempo estimado de revisión:</strong> 1-3 días hábiles
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
