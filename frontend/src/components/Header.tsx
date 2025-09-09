'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/contexts/AuthContext';
import { ThemeToggle, ThemeToggleCompact } from './ThemeToggle';
import { Button } from './ui/Button';

interface HeaderProps {
  variant?: 'public' | 'authenticated';
  compact?: boolean;
}

export function Header({ variant = 'public', compact = false }: HeaderProps) {
  const { user, signOut } = useAuth();

  return (
    <header className="bg-background border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center">
              <svg className="h-5 w-5 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
              </svg>
            </div>
            <span className="ml-2 text-xl font-bold text-foreground">
              Agro Extension Digital
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            {variant === 'public' && !user && (
              <>
                <Link href="/login">
                  <Button variant="ghost">
                    Iniciar Sesión
                  </Button>
                </Link>
                <Link href="/register">
                  <Button>
                    Registrarse
                  </Button>
                </Link>
              </>
            )}

            {variant === 'authenticated' && user && (
              <>
                <Link href="/dashboard">
                  <Button variant="ghost">
                    Dashboard
                  </Button>
                </Link>
                <Button variant="ghost" onClick={() => signOut()}>
                  Cerrar Sesión
                </Button>
              </>
            )}

            {/* Theme Toggle */}
            {compact ? <ThemeToggleCompact /> : <ThemeToggle />}
          </div>
        </div>
      </div>
    </header>
  );
}

// Componente simplificado para páginas de login/register
export function SimpleHeader() {
  return (
    <div className="fixed top-4 right-4 z-50">
      <ThemeToggleCompact />
    </div>
  );
}
