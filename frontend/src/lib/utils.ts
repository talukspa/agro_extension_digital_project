// Utilidades generales para la aplicación
// Incluye funciones helper para clases CSS y manipulación de strings

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combina clases CSS de forma inteligente, resolviendo conflictos de Tailwind
 * @param inputs - Array de clases CSS o valores condicionales
 * @returns String con clases CSS combinadas y optimizadas
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Formatea un nombre para mostrar con mayúscula inicial
 * @param name - Nombre a formatear
 * @returns Nombre formateado
 */
export function formatDisplayName(name: string): string {
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Convierte un string a formato slug (URL-friendly)
 * @param text - Texto a convertir
 * @returns String en formato slug
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remover acentos
    .replace(/[^a-z0-9\s-]/g, '') // Remover caracteres especiales
    .trim()
    .replace(/\s+/g, '-') // Espacios a guiones
    .replace(/-+/g, '-'); // Múltiples guiones a uno solo
}

/**
 * Valida formato de email
 * @param email - Email a validar
 * @returns true si el email es válido
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Valida RUT chileno
 * @param rut - RUT a validar (con o sin puntos y guión)
 * @returns true si el RUT es válido
 */
export function isValidRUT(rut: string): boolean {
  // Remover puntos y guión, convertir a mayúsculas
  const cleanRUT = rut.replace(/[.-]/g, '').toUpperCase();
  
  // Verificar formato básico
  if (!/^[0-9]+[0-9K]$/.test(cleanRUT)) {
    return false;
  }
  
  // Separar número y dígito verificador
  const number = cleanRUT.slice(0, -1);
  const checkDigit = cleanRUT.slice(-1);
  
  // Calcular dígito verificador
  let sum = 0;
  let multiplier = 2;
  
  for (let i = number.length - 1; i >= 0; i--) {
    sum += parseInt(number[i]) * multiplier;
    multiplier = multiplier === 7 ? 2 : multiplier + 1;
  }
  
  const remainder = sum % 11;
  const expectedDigit = remainder === 0 ? '0' : remainder === 1 ? 'K' : (11 - remainder).toString();
  
  return checkDigit === expectedDigit;
}

/**
 * Formatea RUT para mostrar (con puntos y guión)
 * @param rut - RUT a formatear
 * @returns RUT formateado o string vacío si es inválido
 */
export function formatRUT(rut: string): string {
  const cleanRUT = rut.replace(/[.-]/g, '');
  
  if (!isValidRUT(cleanRUT)) {
    return '';
  }
  
  const number = cleanRUT.slice(0, -1);
  const checkDigit = cleanRUT.slice(-1);
  
  // Agregar puntos cada 3 dígitos desde la derecha
  const formattedNumber = number.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  
  return `${formattedNumber}-${checkDigit}`;
}

/**
 * Trunca texto a una longitud específica
 * @param text - Texto a truncar
 * @param maxLength - Longitud máxima
 * @returns Texto truncado con ellipsis si es necesario
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength).trim() + '...';
}

/**
 * Genera un ID único simple para elementos del DOM
 * @param prefix - Prefijo opcional para el ID
 * @returns ID único
 */
export function generateId(prefix: string = 'id'): string {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Convierte bytes a formato legible
 * @param bytes - Número de bytes
 * @param decimals - Número de decimales a mostrar
 * @returns String formateado (ej: "1.5 MB")
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Debounce function para optimizar búsquedas y llamadas a APIs
 * @param func - Función a ejecutar
 * @param wait - Tiempo de espera en milisegundos
 * @returns Función debounced
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
