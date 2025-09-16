/**
 * Utilidad de logging condicional para development
 * Solo muestra logs en desarrollo, silencioso en producción
 */

const isDevelopment = process.env.NODE_ENV === 'development';

export const devLog = {
  log: (...args: any[]) => {
    if (isDevelopment) {
      console.log(...args);
    }
  },
  
  debug: (...args: any[]) => {
    if (isDevelopment) {
      console.debug(...args);
    }
  },
  
  info: (...args: any[]) => {
    if (isDevelopment) {
      console.info(...args);
    }
  },
  
  warn: (...args: any[]) => {
    // Warnings siempre se muestran
    console.warn(...args);
  },
  
  error: (...args: any[]) => {
    // Errors siempre se muestran
    console.error(...args);
  },
  
  // Para casos donde necesitamos logging en producción para errores críticos
  critical: (...args: any[]) => {
    console.error('[CRITICAL]', ...args);
  }
};

// Para backward compatibility
export default devLog;