import { UserType } from '@/lib/types/auth';
import { USER_TYPE_DISPLAY_NAMES } from '@/lib/types/permissions';
import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  setDoc, 
  query, 
  orderBy, 
  serverTimestamp,
  db
} from './utils';
import { validateDb, waitForFirestore } from './utils';

// ============================================
// USER TYPES OPERATIONS
// ============================================

export const getUserTypes = async (): Promise<UserType[]> => {
  validateDb();
  
  const userTypesRef = collection(db, 'user_types');
  const q = query(userTypesRef, orderBy('name'));
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => {
    const data = doc.data();
    const userTypeId = doc.id as keyof typeof USER_TYPE_DISPLAY_NAMES;
    return {
      id: doc.id,
      name: data.name,
      displayName: data.display_name || data.displayName || USER_TYPE_DISPLAY_NAMES[userTypeId] || '', // Map display_name to displayName with fallback
      description: data.description || '',
      permissions: data.permissions || [],
      isActive: data.isActive !== false, // Default to true
      createdAt: data.created_at?.toDate() || data.createdAt?.toDate() || new Date(),
      metadata: data.metadata || {}
    } as UserType;
  });
};

export const getUserTypeById = async (userTypeId: string): Promise<UserType | null> => {
  try {
    // Wait for Firestore to be ready
    const isReady = await waitForFirestore();
    if (!isReady) {
      console.error('Firestore not ready after waiting');
      return null;
    }
    
    validateDb();
    
    if (!userTypeId) {
      console.warn('getUserTypeById called with empty userTypeId');
      return null;
    }
    
    const userTypeRef = doc(db, 'user_types', userTypeId);
    const userTypeSnap = await getDoc(userTypeRef);
    
    if (userTypeSnap.exists()) {
      const data = userTypeSnap.data();
      const userTypeKey = userTypeId as keyof typeof USER_TYPE_DISPLAY_NAMES;
      return {
        id: userTypeSnap.id,
        name: data.name,
        displayName: data.display_name || data.displayName || USER_TYPE_DISPLAY_NAMES[userTypeKey] || '', // Map display_name to displayName with fallback
        description: data.description || '',
        permissions: data.permissions || [],
        isActive: data.isActive !== false, // Default to true
        createdAt: data.created_at?.toDate() || data.createdAt?.toDate() || new Date(),
        metadata: data.metadata || {}
      } as UserType;
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching user type:', error);
    return null;
  }
};

export const createUserType = async (userType: Omit<UserType, 'id' | 'createdAt'>): Promise<string> => {
  validateDb();
  
  const userTypeRef = doc(collection(db, 'user_types'));
  await setDoc(userTypeRef, {
    ...userType,
    createdAt: serverTimestamp()
  });
  
  return userTypeRef.id;
};
