import { AuditorProfile } from '@/lib/types/auth';
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
import { validateDb } from './utils';

// ============================================
// AUDITOR OPERATIONS
// ============================================

export const createAuditorProfile = async (auditorData: Omit<AuditorProfile, 'id' | 'createdAt' | 'requestedAt'>): Promise<string> => {
  validateDb();
  
  const auditorRef = doc(collection(db, 'auditor_profiles'));
  await setDoc(auditorRef, {
    ...auditorData,
    status: 'pending', // Requires admin approval
    requestedAt: serverTimestamp(),
    createdAt: serverTimestamp(),
    isActive: false // Only active after approval
  });
  
  return auditorRef.id;
};

export const getAuditorProfile = async (auditorId: string): Promise<AuditorProfile | null> => {
  try {
    validateDb();
    
    if (!auditorId) {
      console.warn('getAuditorProfile called with empty auditorId');
      return null;
    }
    
    const auditorRef = doc(db, 'auditor_profiles', auditorId);
    const auditorSnap = await getDoc(auditorRef);
    
    if (auditorSnap.exists()) {
      const data = auditorSnap.data();
      return {
        ...data,
        id: auditorSnap.id,
        createdAt: data.createdAt?.toDate(),
        requestedAt: data.requestedAt?.toDate(),
        approvedAt: data.approvedAt?.toDate(),
        rejectedAt: data.rejectedAt?.toDate()
      } as AuditorProfile;
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching auditor profile:', error);
    return null;
  }
};

export const updateAuditorProfile = async (auditorId: string, updates: Partial<AuditorProfile>): Promise<void> => {
  validateDb();
  
  const auditorRef = doc(db, 'auditor_profiles', auditorId);
  await updateDoc(auditorRef, {
    ...updates,
    updatedAt: serverTimestamp()
  });
};

export const approveAuditor = async (auditorId: string, approvedBy: string): Promise<void> => {
  validateDb();
  
  // Get auditor profile to find the user
  const auditorRef = doc(db, 'auditor_profiles', auditorId);
  const auditorSnap = await getDoc(auditorRef);
  
  if (!auditorSnap.exists()) {
    throw new Error('Auditor profile not found');
  }
  
  const auditorData = auditorSnap.data();
  const userId = auditorData.userId;
  
  // Update auditor profile status
  await updateDoc(auditorRef, {
    status: 'approved',
    isActive: true,
    approvedAt: serverTimestamp(),
    approvedBy
  });
  
  // Also approve the user if they are still pending
  if (userId) {
    try {
      const userRef = doc(db, 'users', userId);
      const userSnap = await getDoc(userRef);
      
      if (userSnap.exists()) {
        const userData = userSnap.data();
        if (userData.status === 'pending') {
          await updateDoc(userRef, {
            status: 'approved',
            isActive: true,
            approvedAt: serverTimestamp(),
            approvedBy
          });
        }
      }
    } catch (error) {
      console.error('Error approving auditor user:', error);
      // Don't throw error here - auditor approval should still succeed
    }
  }
};

export const rejectAuditor = async (auditorId: string, rejectedBy: string, reason?: string): Promise<void> => {
  validateDb();
  
  // Get auditor profile to find the user
  const auditorRef = doc(db, 'auditor_profiles', auditorId);
  const auditorSnap = await getDoc(auditorRef);
  
  if (!auditorSnap.exists()) {
    throw new Error('Auditor profile not found');
  }
  
  const auditorData = auditorSnap.data();
  const userId = auditorData.userId;
  
  // Update auditor profile status
  await updateDoc(auditorRef, {
    status: 'rejected',
    isActive: false,
    rejectedAt: serverTimestamp(),
    rejectedBy,
    rejectionReason: reason
  });
  
  // Also reject the user if they are still pending
  if (userId) {
    try {
      const userRef = doc(db, 'users', userId);
      const userSnap = await getDoc(userRef);
      
      if (userSnap.exists()) {
        const userData = userSnap.data();
        if (userData.status === 'pending') {
          await updateDoc(userRef, {
            status: 'rejected',
            isActive: false,
            rejectedAt: serverTimestamp(),
            rejectedBy,
            rejectionReason: reason || 'Auditor application rejected'
          });
        }
      }
    } catch (error) {
      console.error('Error rejecting auditor user:', error);
      // Don't throw error here - auditor rejection should still succeed
    }
  }
};

export const getPendingAuditors = async (): Promise<AuditorProfile[]> => {
  validateDb();
  
  const auditorsRef = collection(db, 'auditor_profiles');
  const q = query(auditorsRef, where('status', '==', 'pending'), orderBy('requestedAt'));
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    id: doc.id,
    createdAt: doc.data().createdAt?.toDate(),
    requestedAt: doc.data().requestedAt?.toDate()
  } as AuditorProfile));
};

export const getApprovedAuditors = async (): Promise<AuditorProfile[]> => {
  validateDb();
  
  const auditorsRef = collection(db, 'auditor_profiles');
  const q = query(
    auditorsRef, 
    where('status', '==', 'approved'), 
    where('isActive', '==', true),
    orderBy('approvedAt')
  );
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    id: doc.id,
    createdAt: doc.data().createdAt?.toDate(),
    requestedAt: doc.data().requestedAt?.toDate(),
    approvedAt: doc.data().approvedAt?.toDate()
  } as AuditorProfile));
};
