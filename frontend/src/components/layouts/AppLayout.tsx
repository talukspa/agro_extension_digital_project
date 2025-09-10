'use client';

import { ReactNode } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Button } from '@/components/ui/Button';
import { getUserTypeColors } from '@/lib/utils/userTypeColors';
import { Avatar } from '@/components/ui/Avatar';
import { USER_TYPE_DISPLAY_NAMES } from '@/lib/types/permissions';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user, signOut, userType } = useAuth();

  // Si no hay usuario, renderizar solo el contenido (para páginas públicas)
  if (!user) {
    return <>{children}</>;
  }

  const userInitials = user.displayName?.charAt(0) || user.email?.charAt(0) || 'U';
  const userTypeDisplay = userType?.name ? USER_TYPE_DISPLAY_NAMES[userType.name as keyof typeof USER_TYPE_DISPLAY_NAMES] : 'Usuario';

  return (
    <div className="min-h-screen bg-background">
      {/* Header/Navigation Bar */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo y título */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-primary">
                  AgroExtensión Digital
                </h1>
              </div>
              
              {/* Navegación principal */}
              <nav className="hidden md:ml-8 md:flex md:space-x-8">
                <a
                  href="/dashboard"
                  className="text-foreground hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Dashboard
                </a>
                {userType?.name === 'admin' && (
                  <a
                    href="/admin"
                    className="text-foreground hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Administración
                  </a>
                )}
              </nav>
            </div>

            {/* Controles del usuario */}
            <div className="flex items-center space-x-4">
              {/* Toggle de tema */}
              <ThemeToggle />
              
              {/* Información del usuario */}
              <div className="flex items-center space-x-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-foreground">
                    {user.displayName || 'Usuario'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {userTypeDisplay}
                  </p>
                </div>
                
                {/* Avatar del usuario */}
                <Avatar
                  initials={userInitials}
                  userType={userType?.name}
                  size="md"
                />
                
                {/* Menú de usuario */}
                <div className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={signOut}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Salir
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer opcional */}
      <footer className="bg-card border-t border-border mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <div className="text-sm text-muted-foreground">
              © 2025 AgroExtensión Digital. Todos los derechos reservados.
            </div>
            <div className="flex space-x-4 mt-4 sm:mt-0">
              <a
                href="/help"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Ayuda
              </a>
              <a
                href="/privacy"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Privacidad
              </a>
              <a
                href="/terms"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Términos
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default AppLayout;
