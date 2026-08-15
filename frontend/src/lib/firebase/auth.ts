import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword, 
  signOut as firebaseSignOut,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  updateProfile,
  User,
  UserCredential
} from 'firebase/auth';
import { auth } from './config';

export interface AuthError {
  code: string;
  message: string;
}

export const signUp = async (
  email: string,
  password: string,
  displayName?: string
): Promise<UserCredential> => {
  try {
    const credential = await createUserWithEmailAndPassword(auth, email, password);

    // Firebase email/password signups have no displayName by default. Set it on the
    // Firebase Auth user so downstream code (AuthContext profile creation) can read it.
    const trimmedName = displayName?.trim();
    if (trimmedName) {
      await updateProfile(credential.user, { displayName: trimmedName });
    }

    return credential;
  } catch (error) {
    const firebaseError = error as { code: string; message: string };
    throw {
      code: firebaseError.code,
      message: firebaseError.message
    } as AuthError;
  }
};

export const signIn = async (email: string, password: string): Promise<UserCredential> => {
  try {
    return await signInWithEmailAndPassword(auth, email, password);
  } catch (error) {
    const firebaseError = error as { code: string; message: string };
    throw {
      code: firebaseError.code,
      message: firebaseError.message
    } as AuthError;
  }
};

export const signOut = async (): Promise<void> => {
  try {
    await firebaseSignOut(auth);
  } catch (error) {
    const firebaseError = error as { code: string; message: string };
    throw {
      code: firebaseError.code,
      message: firebaseError.message
    } as AuthError;
  }
};

export const signInWithGoogle = async (): Promise<UserCredential> => {
  try {
    const provider = new GoogleAuthProvider();
    // Agregar scopes si necesitas información adicional del perfil
    provider.addScope('profile');
    provider.addScope('email');
    
    return await signInWithPopup(auth, provider);
  } catch (error) {
    const firebaseError = error as { code: string; message: string };
    throw {
      code: firebaseError.code,
      message: firebaseError.message
    } as AuthError;
  }
};

export const getCurrentUser = (): User | null => {
  return auth.currentUser;
};

export const onAuthStateChange = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(auth, callback);
};

export const getErrorMessage = (errorCode: string): string => {
  switch (errorCode) {
    case 'auth/user-not-found':
      return 'No se encontró una cuenta con este email.';
    case 'auth/wrong-password':
      return 'Contraseña incorrecta.';
    case 'auth/email-already-in-use':
      return 'Ya existe una cuenta con este email.';
    case 'auth/weak-password':
      return 'La contraseña debe tener al menos 6 caracteres.';
    case 'auth/invalid-email':
      return 'El formato del email no es válido.';
    case 'auth/too-many-requests':
      return 'Demasiados intentos fallidos. Intenta de nuevo más tarde.';
    case 'auth/popup-closed-by-user':
      return 'La ventana de autenticación fue cerrada antes de completar el proceso.';
    case 'auth/cancelled-popup-request':
      return 'El proceso de autenticación fue cancelado.';
    case 'auth/popup-blocked':
      return 'La ventana emergente fue bloqueada por el navegador. Por favor, permite ventanas emergentes para este sitio.';
    case 'auth/operation-not-allowed':
      return 'El método de autenticación no está habilitado. Contacta al administrador.';
    case 'auth/account-exists-with-different-credential':
      return 'Ya existe una cuenta con el mismo email pero con un método de autenticación diferente.';
    default:
      return 'Ocurrió un error inesperado. Intenta de nuevo.';
  }
};
