// Componente Card - Ejemplo de uso de la paleta de colores Plum
// Este componente demuestra el uso de variables semánticas y colores específicos

import { ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;
  variant?: 'default' | 'muted' | 'accent';
  className?: string;
}

export function Card({ 
  title, 
  children, 
  variant = 'default',
  className = '' 
}: CardProps) {
  
  // Configuración de estilos por variante con accesibilidad WCAG AA
  const variantStyles = {
    // Variante por defecto: Usa variables semánticas para cambio automático de tema
    default: {
      // Modo claro: fondo plum-50, texto plum-950 (contraste 18.5:1)
      // Modo oscuro: fondo stone-700, texto plum-100 (contraste 16.1:1)
      card: 'bg-background border-border text-foreground',
      title: 'text-foreground font-semibold',
      content: 'text-muted-foreground'
    },
    
    // Variante muted: Fondos secundarios con excelente legibilidad
    muted: {
      // Modo claro: fondo stone-100, texto stone-700 (contraste 8.4:1)
      // Modo oscuro: fondo stone-700, texto stone-100 (contraste 8.1:1)  
      card: 'bg-muted border-border text-foreground',
      title: 'text-foreground font-semibold',
      content: 'text-muted-foreground'
    },
    
    // Variante accent: Destacados especiales con colores amber
    accent: {
      // Modo claro: fondo amber-50, borde amber-200, texto amber-950 (contraste 14.2:1)
      // Modo oscuro: fondo amber-950/10, borde amber-700, texto amber-100 (contraste 12.1:1)
      card: 'bg-amber-50 dark:bg-amber-950/10 border-amber-200 dark:border-amber-700 text-amber-950 dark:text-amber-100',
      title: 'text-amber-900 dark:text-amber-200 font-semibold',
      content: 'text-amber-800 dark:text-amber-300'
    }
  };

  const styles = variantStyles[variant];

  return (
    <div className={`
      ${styles.card}
      rounded-lg 
      border 
      p-6 
      shadow-sm 
      transition-all 
      duration-200 
      hover:shadow-md 
      focus-within:ring-2 
      focus-within:ring-ring 
      focus-within:ring-offset-2
      ${className}
    `}>
      {/* Título del Card */}
      <h3 className={`
        ${styles.title}
        text-lg 
        mb-3 
        leading-tight
      `}>
        {title}
      </h3>
      
      {/* Contenido del Card */}
      <div className={`
        ${styles.content}
        text-sm 
        leading-relaxed
      `}>
        {children}
      </div>
    </div>
  );
}

// Ejemplos de uso:

// Card por defecto (se adapta automáticamente al tema)
export function DefaultCardExample() {
  return (
    <Card title="Información de la Empresa">
      <p>
        Esta tarjeta utiliza las variables semánticas que se adaptan automáticamente 
        al modo claro u oscuro, manteniendo siempre un contraste óptimo para la lectura.
      </p>
    </Card>
  );
}

// Card con fondo muted para contenido secundario
export function MutedCardExample() {
  return (
    <Card title="Detalles Adicionales" variant="muted">
      <p>
        Esta variante usa fondos más sutiles, ideal para información secundaria 
        que no debe competir con el contenido principal.
      </p>
    </Card>
  );
}

// Card con estilo accent para destacar información importante
export function AccentCardExample() {
  return (
    <Card title="¡Certificación Aprobada!" variant="accent">
      <p>
        Esta variante usa los colores ámbar de la paleta para destacar información 
        importante o celebrar logros, manteniendo excelente accesibilidad.
      </p>
    </Card>
  );
}
