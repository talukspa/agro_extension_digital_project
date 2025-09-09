'use client';

import { useTheme } from '@/lib/contexts/ThemeContext';
import { useState, useEffect } from 'react';

export function ThemeToggle() {
  const { theme, setTheme, currentTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-10 h-10 rounded-lg border border-border bg-muted animate-pulse" />
    );
  }

  const themes = [
    { value: 'light', label: 'Claro', icon: '☀️', description: 'Tema claro' },
    { value: 'dark', label: 'Oscuro', icon: '🌙', description: 'Tema oscuro' },
    { value: 'system', label: 'Sistema', icon: '💻', description: 'Seguir sistema' }
  ] as const;

  const currentThemeConfig = themes.find(t => t.value === theme) || themes[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
        aria-label="Cambiar tema"
        title={`Tema actual: ${currentThemeConfig.label}`}
      >
        <span className="text-lg">{currentThemeConfig.icon}</span>
        <span className="hidden sm:inline text-sm font-medium">
          {currentThemeConfig.label}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Overlay para cerrar al hacer click fuera */}
          <div 
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown menu */}
          <div className="absolute right-0 mt-2 w-48 bg-background border border-border rounded-lg shadow-lg z-20">
            <div className="py-1">
              {themes.map((themeOption) => (
                <button
                  key={themeOption.value}
                  onClick={() => {
                    setTheme(themeOption.value);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-4 py-3 text-sm hover:bg-muted transition-colors flex items-center gap-3 ${
                    theme === themeOption.value
                      ? 'bg-muted text-foreground'
                      : 'text-muted-foreground'
                  }`}
                >
                  <span className="text-lg">{themeOption.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium">{themeOption.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {themeOption.description}
                      {themeOption.value === 'system' && (
                        <span> • Actual: {currentTheme === 'dark' ? 'Oscuro' : 'Claro'}</span>
                      )}
                    </div>
                  </div>
                  {theme === themeOption.value && (
                    <svg
                      className="w-4 h-4 text-primary"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Versión compacta solo con iconos para espacios reducidos
export function ThemeToggleCompact() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-10 h-10 rounded-lg border border-border bg-muted animate-pulse" />
    );
  }

  const getNextTheme = () => {
    switch (theme) {
      case 'light': return 'dark';
      case 'dark': return 'system';
      case 'system': return 'light';
      default: return 'light';
    }
  };

  const getThemeIcon = () => {
    switch (theme) {
      case 'light': return '☀️';
      case 'dark': return '🌙';
      case 'system': return '💻';
      default: return '☀️';
    }
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light': return 'Claro';
      case 'dark': return 'Oscuro';
      case 'system': return 'Sistema';
      default: return 'Claro';
    }
  };

  return (
    <button
      onClick={() => setTheme(getNextTheme())}
      className="p-2 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
      aria-label={`Cambiar tema (actual: ${getThemeLabel()})`}
      title={`Cambiar tema (actual: ${getThemeLabel()})`}
    >
      <span className="text-lg">{getThemeIcon()}</span>
    </button>
  );
}
