import { User } from '@/lib/types/auth';
import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  setDoc, 
  updateDoc, 
  query, 
  where, 
  orderBy, 
  serverTimestamp,
  db
} from './utils';
import { validateDb, cleanUndefinedValues } from './utils';

// ============================================
// USER OPERATIONS
// ============================================

export const createUserProfile = async (user: Partial<User>): Promise<void> => {
  validateDb();
  
  if (!user.uid) {
    throw new Error('User UID is required to create user profile');
  }
  
  const baseUser: any = {
    uid: user.uid,
    email: user.email || '',
    displayName: user.displayName || '',
    photoURL: user.photoURL || '',
    status: user.status || 'pending',
    isActive: user.isActive || false,
    createdAt: serverTimestamp(),
    lastLoginAt: serverTimestamp(),
    metadata: user.metadata || {}
  };

  // Only include optional fields when provided
  if (user.userTypeId) baseUser.userTypeId = user.userTypeId;
  if (user.businessProfileId) baseUser.businessProfileId = user.businessProfileId;

  const cleanedUser = cleanUndefinedValues(baseUser);
  
  const userRef = doc(db, 'users', user.uid);
  await setDoc(userRef, cleanedUser);
};

export const getUserProfile = async (uid: string): Promise<User | null> => {
  validateDb();
  
  const userRef = doc(db, 'users', uid);
  const userSnap = await getDoc(userRef);
  
  if (userSnap.exists()) {
    const data = userSnap.data();
    return {
      ...data,
      uid: userSnap.id,
      createdAt: data.createdAt?.toDate(),
      lastLoginAt: data.lastLoginAt?.toDate(),
      requestedAt: data.requestedAt?.toDate(),
      approvedAt: data.approvedAt?.toDate(),
      rejectedAt: data.rejectedAt?.toDate()
    } as User;
  }
  
  return null;
};

export const updateUserProfile = async (uid: string, updates: Partial<User>): Promise<void> => {
  validateDb();
  
  const userRef = doc(db, 'users', uid);
  const cleanedUpdates = cleanUndefinedValues({
    ...updates,
    updatedAt: serverTimestamp()
  });
  
  await updateDoc(userRef, cleanedUpdates);
};

export const approveUser = async (uid: string, approvedBy: string): Promise<void> => {
  validateDb();
  
  const userRef = doc(db, 'users', uid);
  await updateDoc(userRef, {
    status: 'approved',
    isActive: true,
    approvedAt: serverTimestamp(),
    approvedBy
  });
};

export const rejectUser = async (uid: string, rejectedBy: string, reason?: string): Promise<void> => {
  validateDb();
  
  const userRef = doc(db, 'users', uid);
  await updateDoc(userRef, {
    status: 'rejected',
    isActive: false,
    rejectedAt: serverTimestamp(),
    rejectedBy,
    rejectionReason: reason
  });
};

export const getPendingUsers = async (): Promise<User[]> => {
  validateDb();
  
  const usersRef = collection(db, 'users');
  const q = query(usersRef, where('status', '==', 'pending'), orderBy('createdAt'));
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    uid: doc.id,
    createdAt: doc.data().createdAt?.toDate(),
    lastLoginAt: doc.data().lastLoginAt?.toDate(),
    requestedAt: doc.data().requestedAt?.toDate(),
    approvedAt: doc.data().approvedAt?.toDate(),
    rejectedAt: doc.data().rejectedAt?.toDate()
  } as User));
};

export const getUserByEmail = async (email: string): Promise<User | null> => {
  const usersRef = collection(db, 'users');
  const q = query(usersRef, where('email', '==', email));
  const snapshot = await getDocs(q);
  
  if (!snapshot.empty) {
    const docSnap = snapshot.docs[0];
    const data = docSnap.data();
    return {
      ...data,
      uid: docSnap.id,
      createdAt: data.createdAt?.toDate(),
      lastLoginAt: data.lastLoginAt?.toDate(),
      requestedAt: data.requestedAt?.toDate(),
      approvedAt: data.approvedAt?.toDate(),
      rejectedAt: data.rejectedAt?.toDate()
    } as User;
  }
  
  return null;
};
