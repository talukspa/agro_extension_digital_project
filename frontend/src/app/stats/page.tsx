"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/Button";
import { Avatar } from "@/components/ui/Avatar";
import { USER_TYPE_DISPLAY_NAMES, USER_TYPES } from "@/lib/types/permissions";
import { useTheme } from "@/lib/contexts/ThemeContext";

function StatsContent() {
  const { user, userType, activeBusiness, loading: authLoading, signOut } = useAuth();
  const { theme, setTheme, currentTheme, toggleTheme } = useTheme();
  const router = useRouter();

  // Estados locales para la página
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const userInitials = user?.displayName?.charAt(0) || user?.email?.charAt(0) || 'U';
  const userTypeDisplay = userType?.name ? USER_TYPE_DISPLAY_NAMES[userType.name as keyof typeof USER_TYPE_DISPLAY_NAMES] : 'Usuario';

  return (
    <div className="min-h-screen bg-background">
      {/* Header/Navigation Bar - Siguiendo el patrón del proyecto */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo, título y navegación */}
            <div className="flex items-center">
              {/* Menú hamburguesa */}
              <div className="relative mr-4 menu-container">
                <button
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="flex items-center justify-center w-10 h-10 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
                  aria-label="Abrir menú de navegación"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  </svg>
                </button>

                {/* Dropdown del menú */}
                {isMenuOpen && (
                  <div className="absolute top-12 left-0 w-48 bg-background border border-border rounded-lg shadow-lg z-50">
                    <div className="py-2">
                      <a
                        href="/dashboard"
                        className="block px-4 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-muted transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        📊 Dashboard
                      </a>
                      <a
                        href="/survey"
                        className="block px-4 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-muted transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        📋 Encuesta de Estándares
                      </a>
                      <div className="block px-4 py-2 text-sm text-primary bg-muted/50 font-medium">
                        📈 Estadísticas
                      </div>
                      {userType?.name === 'admin' && (
                        <a
                          href="/admin"
                          className="block px-4 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-muted transition-colors"
                          onClick={() => setIsMenuOpen(false)}
                        >
                          ⚙️ Administración
                        </a>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-primary">
                  AgroExtensión Digital
                </h1>
                <p className="text-xs text-muted-foreground">
                  Estadísticas de Encuestas
                </p>
              </div>
            </div>

            {/* Controles del usuario */}
            <div className="flex items-center space-x-4">
              {/* Información del negocio activo */}
              {!authLoading && activeBusiness && (
                <div className="hidden lg:block border-r border-border pr-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-foreground">
                      {activeBusiness.legal_name || activeBusiness.businessName}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      RUT: {activeBusiness.rut}
                    </p>
                  </div>
                </div>
              )}
              
              {/* Usuario autenticado */}
              {!authLoading && user && (
                <>
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
                  
                  {/* Botón de cerrar sesión */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={signOut}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Salir
                  </Button>
                </>
              )}
              
              {/* Toggle de tema - Solo emoji */}
              <button
                onClick={toggleTheme}
                className="w-10 h-10 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring flex items-center justify-center"
                aria-label="Cambiar tema"
                title={`Tema actual: ${theme === 'light' ? 'Claro' : theme === 'dark' ? 'Oscuro' : 'Sistema'}`}
              >
                <span className="text-lg">
                  {theme === 'light' ? '☀️' : theme === 'dark' ? '🌙' : '💻'}
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground">Estadísticas de Encuestas</h2>
          <p className="text-muted-foreground mt-2">
            Análisis y métricas de las encuestas de estándares completadas
          </p>
        </div>

        {/* Placeholder para contenido futuro */}
        <div className="bg-card border border-border rounded-lg p-8 shadow-sm">
          <div className="text-center">
            <div className="mb-4">
              <svg
                className="mx-auto w-16 h-16 text-muted-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Página en Desarrollo
            </h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Aquí se mostrarán las estadísticas detalladas de las encuestas completadas, 
              incluyendo gráficos, métricas y análisis de tendencias.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => router.back()}
                variant="outline"
                className="px-6 py-2"
              >
                ← Volver
              </Button>
              <Button
                onClick={() => router.push('/survey')}
                className="px-6 py-2"
              >
                📋 Ir a Encuestas
              </Button>
            </div>
            
            {/* Información adicional para desarrolladores */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-8 p-4 bg-muted/20 border border-muted rounded-lg">
                <h4 className="text-sm font-medium text-foreground mb-2">
                  💡 Información de Desarrollo
                </h4>
                <p className="text-xs text-muted-foreground">
                  Esta página estará disponible en: <code className="bg-muted px-1 rounded">/stats</code>
                  <br />
                  Futuras funcionalidades: gráficos de completion rate, distribución de respuestas, 
                  análisis temporal, comparativas entre estándares, etc.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function StatsPage() {
  return (
    <ProtectedRoute
      requiredUserTypes={[USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER, USER_TYPES.ADMIN]}
      requireApproval={true}
    >
      <StatsContent />
    </ProtectedRoute>
  );
}