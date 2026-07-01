import { describe, it, expect } from 'vitest';
import { getErrorMessage } from './auth';

describe('getErrorMessage (Firebase code -> Spanish message)', () => {
  it('maps known auth error codes to friendly Spanish messages', () => {
    expect(getErrorMessage('auth/user-not-found')).toBe('No se encontró una cuenta con este email.');
    expect(getErrorMessage('auth/wrong-password')).toBe('Contraseña incorrecta.');
    expect(getErrorMessage('auth/email-already-in-use')).toBe('Ya existe una cuenta con este email.');
    expect(getErrorMessage('auth/weak-password')).toBe('La contraseña debe tener al menos 6 caracteres.');
    expect(getErrorMessage('auth/invalid-email')).toBe('El formato del email no es válido.');
  });

  it('returns a generic fallback for unknown codes', () => {
    expect(getErrorMessage('auth/some-unhandled-code')).toBe('Ocurrió un error inesperado. Intenta de nuevo.');
    expect(getErrorMessage('')).toBe('Ocurrió un error inesperado. Intenta de nuevo.');
  });
});
