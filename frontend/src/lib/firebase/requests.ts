import { 
  collection, 
  doc, 
  setDoc, 
  updateDoc,
  getDocs,
  query,
  where,
  orderBy,
  serverTimestamp
} from 'firebase/firestore';
import { validateDb, db } from './utils';
import type { UserRequest } from '@/lib/types/auth';

// ============================================
// GENERAL REQUESTS OPERATIONS
// ============================================

export const createUserRequest = async (request: Omit<UserRequest, 'id' | 'requestedAt'>): Promise<string> => {
  validateDb();
  
  const requestRef = doc(collection(db, 'user_requests'));
  await setDoc(requestRef, {
    ...request,
    requestedAt: serverTimestamp()
  });
  
  return requestRef.id;
};

export const getPendingRequests = async (): Promise<UserRequest[]> => {
  validateDb();
  
  const requestsRef = collection(db, 'user_requests');
  const q = query(requestsRef, where('status', '==', 'pending'), orderBy('requestedAt'));
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    id: doc.id,
    requestedAt: doc.data().requestedAt?.toDate(),
    reviewedAt: doc.data().reviewedAt?.toDate()
  } as UserRequest));
};

export const approveRequest = async (requestId: string, reviewedBy: string, notes?: string): Promise<void> => {
  validateDb();
  
  const requestRef = doc(db, 'user_requests', requestId);
  await updateDoc(requestRef, {
    status: 'approved',
    reviewedAt: serverTimestamp(),
    reviewedBy,
    reviewNotes: notes
  });
};

export const rejectRequest = async (requestId: string, reviewedBy: string, notes?: string): Promise<void> => {
  validateDb();
  
  const requestRef = doc(db, 'user_requests', requestId);
  await updateDoc(requestRef, {
    status: 'rejected',
    reviewedAt: serverTimestamp(),
    reviewedBy,
    reviewNotes: notes
  });
};
