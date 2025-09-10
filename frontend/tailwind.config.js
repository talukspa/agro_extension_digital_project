/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // CSS Variables para modo claro/oscuro
        background: "rgb(var(--background) / <alpha-value>)",
        foreground: "rgb(var(--foreground) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        "muted-foreground": "rgb(var(--muted-foreground) / <alpha-value>)",
        primary: "rgb(var(--primary) / <alpha-value>)",
        "primary-foreground": "rgb(var(--primary-foreground) / <alpha-value>)",
        secondary: "rgb(var(--secondary) / <alpha-value>)",
        "secondary-foreground": "rgb(var(--secondary-foreground) / <alpha-value>)",
        accent: "rgb(var(--accent) / <alpha-value>)",
        "accent-foreground": "rgb(var(--accent-foreground) / <alpha-value>)",
        border: "rgb(var(--border) / <alpha-value>)",
        ring: "rgb(var(--ring) / <alpha-value>)",
        
        // Componentes adicionales
        card: "rgb(var(--card) / <alpha-value>)",
        "card-foreground": "rgb(var(--card-foreground) / <alpha-value>)",
        popover: "rgb(var(--popover) / <alpha-value>)",
        "popover-foreground": "rgb(var(--popover-foreground) / <alpha-value>)",
        
        // Estados semánticos - Variables CSS
        success: "rgb(var(--success) / <alpha-value>)",
        "success-foreground": "rgb(var(--success-foreground) / <alpha-value>)",
        "success-background": "rgb(var(--success-background) / <alpha-value>)",
        warning: "rgb(var(--warning) / <alpha-value>)",
        "warning-foreground": "rgb(var(--warning-foreground) / <alpha-value>)",
        "warning-background": "rgb(var(--warning-background) / <alpha-value>)",
        error: "rgb(var(--error) / <alpha-value>)",
        "error-foreground": "rgb(var(--error-foreground) / <alpha-value>)",
        "error-background": "rgb(var(--error-background) / <alpha-value>)",
        
        // Tipos de usuario - Variables CSS  
        "admin-color": "rgb(var(--admin-color) / <alpha-value>)",
        "auditor-color": "rgb(var(--auditor-color) / <alpha-value>)",
        "business-color": "rgb(var(--business-color) / <alpha-value>)",
        
        // Paleta Principal - Plum (Ciruela)
        plum: {
          50: '#fdf4ff',   // Crema muy suave - interior fresco
          100: '#fae8ff',  // Crema rosado - carne fresca
          200: '#f3d2ff',  // Lavanda suave - transición
          300: '#e9b3ff',  // Púrpura claro - piel joven
          400: '#d891f2',  // Púrpura medio - maduración
          500: '#c471ed',  // Púrpura vibrante - ciruela fresca madura ⭐ PRIMARY
          600: '#a855f7',  // Púrpura profundo - comenzando a deshidratar
          700: '#9333ea',  // Púrpura rico - semi-deshidratada
          800: '#7e22ce',  // Púrpura muy oscuro - deshidratada ⭐ PRIMARY DARK
          900: '#6b21a8',  // Púrpura intenso - completamente deshidratada
          950: '#4c1d95',  // Púrpura profundo - concentrado
        },
        
        // Colores Secundarios - Amber (Ámbar/Dorado)
        amber: {
          50: '#fffbeb',   // Crema dorada muy suave
          100: '#fef3c7',  // Dorado muy claro - interior jugoso
          200: '#fde68a',  // Dorado claro - jugo fresco
          300: '#fcd34d',  // Dorado medio - concentración
          400: '#fbbf24',  // Dorado vibrante - caramelización ⭐ ACCENT
          500: '#f59e0b',  // Ámbar profundo - azúcar concentrado
          600: '#d97706',  // Ámbar oscuro - caramelo rico
          700: '#b45309',  // Marrón dorado - deshidratación
          800: '#92400e',  // Marrón profundo - concentrado
          900: '#78350f',  // Marrón muy oscuro - caramelizado
          950: '#451a03',  // Marrón intenso - esencia concentrada
        },
        
        // Colores Neutros - Stone (Tierra)
        stone: {
          50: '#fafaf9',   // Blanco cálido - papel natural
          100: '#f5f5f4',  // Gris muy claro - pergamino
          200: '#e7e5e4',  // Gris claro - arena fina
          300: '#d6d3d1',  // Gris medio claro - piedra lisa
          400: '#a8a29e',  // Gris medio - tierra seca
          500: '#78716c',  // Gris - corteza
          600: '#57534e',  // Gris oscuro - tierra húmeda ⭐ SECONDARY
          700: '#44403c',  // Gris muy oscuro - corteza rugosa
          800: '#292524',  // Casi negro - tierra rica
          900: '#1c1917',  // Negro cálido - humus profundo
          950: '#0c0a09',  // Negro intenso - tierra volcánica
        },
        
        // Colores de Estado
        success: {
          50: '#f0fdf4',   // Verde muy claro - hoja tierna
          100: '#dcfce7',  // Verde claro
          200: '#bbf7d0',  // Verde suave
          300: '#86efac',  // Verde medio
          400: '#4ade80',  // Verde vibrante
          500: '#22c55e',  // Verde - hoja madura ⭐ SUCCESS
          600: '#16a34a',  // Verde profundo
          700: '#15803d',  // Verde oscuro - hoja perenne
          800: '#166534',  // Verde muy oscuro
          900: '#14532d',  // Verde intenso
        },
        
        warning: {
          50: '#fffbeb',   // Reutiliza amber-50
          100: '#fef3c7',  // Reutiliza amber-100
          200: '#fde68a',  // Reutiliza amber-200
          300: '#fcd34d',  // Reutiliza amber-300
          400: '#fbbf24',  // Reutiliza amber-400
          500: '#f59e0b',  // Reutiliza amber-500 ⭐ WARNING
          600: '#d97706',  // Reutiliza amber-600
          700: '#b45309',  // Reutiliza amber-700
          800: '#92400e',  // Reutiliza amber-800
          900: '#78350f',  // Reutiliza amber-900
        },
        
        error: {
          50: '#fef2f2',   // Rojo muy claro
          100: '#fee2e2',  // Rojo claro
          200: '#fecaca',  // Rojo suave
          300: '#fca5a5',  // Rojo medio claro
          400: '#f87171',  // Rojo medio
          500: '#ef4444',  // Rojo vibrante ⭐ ERROR
          600: '#dc2626',  // Rojo profundo
          700: '#b91c1c',  // Rojo oscuro
          800: '#991b1b',  // Rojo muy oscuro
          900: '#7f1d1d',  // Rojo intenso
        },
        
        // Compatibilidad con configuración anterior
        fresh: {
          50: '#f0fdf4',   // Reutiliza success-50
          100: '#dcfce7',  // Reutiliza success-100
          200: '#bbf7d0',  // Reutiliza success-200
          300: '#86efac',  // Reutiliza success-300
          400: '#4ade80',  // Reutiliza success-400
          500: '#22c55e',  // Reutiliza success-500
          600: '#16a34a',  // Reutiliza success-600
          700: '#15803d',  // Reutiliza success-700
          800: '#166534',  // Reutiliza success-800
          900: '#14532d',  // Reutiliza success-900
        },
        
        dehydrated: {
          50: '#fffbeb',   // Reutiliza amber-50
          100: '#fef3c7',  // Reutiliza amber-100
          200: '#fde68a',  // Reutiliza amber-200
          300: '#fcd34d',  // Reutiliza amber-300
          400: '#fbbf24',  // Reutiliza amber-400
          500: '#f59e0b',  // Reutiliza amber-500
          600: '#d97706',  // Reutiliza amber-600
          700: '#b45309',  // Reutiliza amber-700
          800: '#92400e',  // Reutiliza amber-800
          900: '#78350f',  // Reutiliza amber-900
        },
      },
    },
  },
  plugins: [],
}
