/**
 * Validador de RUT chileno
 */

export interface RutValidationResult {
  isValid: boolean;
  formattedRut?: string;
  error?: string;
}

/**
 * Limpia el RUT removiendo puntos, guiones y espacios
 */
export const cleanRut = (rut: string): string => {
  return rut.replace(/[.\-\s]/g, '').toUpperCase();
};

/**
 * Formatea el RUT agregando puntos y guión
 */
export const formatRut = (rut: string): string => {
  const cleanedRut = cleanRut(rut);
  
  if (cleanedRut.length < 2) return cleanedRut;
  
  const rutNumber = cleanedRut.slice(0, -1);
  const dv = cleanedRut.slice(-1);
  
  // Agregar puntos cada 3 dígitos
  const formattedNumber = rutNumber.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
  
  return `${formattedNumber}-${dv}`;
};

/**
 * Calcula el dígito verificador de un RUT
 */
export const calculateDV = (rutNumber: string): string => {
  let sum = 0;
  let multiplier = 2;
  
  // Recorrer el RUT de derecha a izquierda
  for (let i = rutNumber.length - 1; i >= 0; i--) {
    sum += parseInt(rutNumber[i]) * multiplier;
    multiplier = multiplier === 7 ? 2 : multiplier + 1;
  }
  
  const remainder = 11 - (sum % 11);
  
  if (remainder === 11) return '0';
  if (remainder === 10) return 'K';
  return remainder.toString();
};

/**
 * Valida si un RUT es válido
 */
export const validateRut = (rut: string): RutValidationResult => {
  if (!rut || rut.trim() === '') {
    return {
      isValid: false,
      error: 'El RUT es requerido'
    };
  }
  
  const cleanedRut = cleanRut(rut);
  
  // Verificar longitud mínima y máxima
  if (cleanedRut.length < 8 || cleanedRut.length > 9) {
    return {
      isValid: false,
      error: 'El RUT debe tener entre 8 y 9 caracteres'
    };
  }
  
  // Verificar que solo contenga números y K
  if (!/^\d{7,8}[0-9K]$/.test(cleanedRut)) {
    return {
      isValid: false,
      error: 'El RUT solo puede contener números y el dígito verificador K'
    };
  }
  
  const rutNumber = cleanedRut.slice(0, -1);
  const providedDV = cleanedRut.slice(-1);
  
  // Verificar que la parte numérica sea válida
  if (!/^\d+$/.test(rutNumber)) {
    return {
      isValid: false,
      error: 'La parte numérica del RUT no es válida'
    };
  }
  
  // Calcular y verificar el dígito verificador
  const calculatedDV = calculateDV(rutNumber);
  
  if (providedDV !== calculatedDV) {
    return {
      isValid: false,
      error: 'El dígito verificador no es válido'
    };
  }
  
  return {
    isValid: true,
    formattedRut: formatRut(cleanedRut)
  };
};

/**
 * Hook para manejar la validación de RUT en tiempo real
 */
export const useRutValidation = () => {
  const validateAndFormat = (inputRut: string): { value: string; error: string } => {
    if (!inputRut) {
      return { value: '', error: '' };
    }
    
    const validation = validateRut(inputRut);
    
    if (validation.isValid) {
      return { 
        value: validation.formattedRut || '', 
        error: '' 
      };
    } else {
      return { 
        value: inputRut, // Mantener el valor original si hay error
        error: validation.error || 'RUT inválido' 
      };
    }
  };
  
  return { validateAndFormat };
};
