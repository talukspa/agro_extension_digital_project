import { Business } from '@/lib/types/auth';
import { USER_TYPES } from '@/lib/types/permissions';
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
// BUSINESS OPERATIONS
// ============================================

export const createBusiness = async (business: Omit<Business, 'id' | 'createdAt' | 'requestedAt' | 'business_users'>): Promise<string> => {
  const businessRef = doc(collection(db, 'business_profiles'));
  await setDoc(businessRef, {
    ...business,
    business_users: [], // Initialize empty array
    pendingUsers: [], // Initialize empty array
    status: 'pending', // Requires admin approval
    requestedAt: serverTimestamp(),
    createdAt: serverTimestamp(),
    isActive: false // Only active after approval
  });
  
  return businessRef.id;
};

export const getBusiness = async (businessId: string): Promise<Business | null> => {
  try {
    validateDb();
    
    if (!businessId) {
      console.warn('getBusiness called with empty businessId');
      return null;
    }
    
    // First try to get from 'businesses' collection (new structure)
    const businessRef = doc(db, 'businesses', businessId);
    const businessSnap = await getDoc(businessRef);
    
    if (businessSnap.exists()) {
      const data = businessSnap.data();
      return {
        ...data,
        id: businessSnap.id,
        createdAt: data.createdAt?.toDate(),
        requestedAt: data.requestedAt?.toDate(),
        approvedAt: data.approvedAt?.toDate(),
        rejectedAt: data.rejectedAt?.toDate()
      } as Business;
    }
    
    // Fallback to 'business_profiles' collection (legacy)
    const profileRef = doc(db, 'business_profiles', businessId);
    const profileSnap = await getDoc(profileRef);
    
    if (profileSnap.exists()) {
      const data = profileSnap.data();
      return {
        ...data,
        id: profileSnap.id,
        createdAt: data.createdAt?.toDate(),
        requestedAt: data.requestedAt?.toDate(),
        approvedAt: data.approvedAt?.toDate(),
        rejectedAt: data.rejectedAt?.toDate()
      } as Business;
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching business:', error);
    return null;
  }
};

export const getAllBusinesses = async (): Promise<Business[]> => {
  const businessesRef = collection(db, 'business_profiles');
  const q = query(businessesRef, where('status', '==', 'approved'), where('isActive', '==', true), orderBy('businessName'));
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    id: doc.id,
    createdAt: doc.data().createdAt?.toDate(),
    requestedAt: doc.data().requestedAt?.toDate()
  } as Business));
};

export const updateBusiness = async (businessId: string, updates: Partial<Business>): Promise<void> => {
  const businessRef = doc(db, 'business_profiles', businessId);
  await updateDoc(businessRef, updates);
};

export const approveBusiness = async (businessId: string, approvedBy: string): Promise<void> => {
  // Get business to find the owner
  const businessRef = doc(db, 'business_profiles', businessId);
  const businessSnap = await getDoc(businessRef);
  
  if (!businessSnap.exists()) {
    throw new Error('Business not found');
  }
  
  const businessData = businessSnap.data();
  const ownerId = businessData.ownerId;
  
  // Update business status
  await updateDoc(businessRef, {
    status: 'approved',
    isActive: true,
    approvedAt: serverTimestamp(),
    approvedBy
  });
  
  // Also approve the business owner if they are still pending
  if (ownerId) {
    try {
      const userRef = doc(db, 'users', ownerId);
      const userSnap = await getDoc(userRef);
      
      if (userSnap.exists()) {
        const userData = userSnap.data();
        // Only update if user is still pending and is business_owner
        if (userData.status === 'pending' && userData.userTypeId === USER_TYPES.BUSINESS_OWNER) {
          await updateDoc(userRef, {
            status: 'approved',
            isActive: true,
            approvedAt: serverTimestamp(),
            approvedBy
          });
        }
      }
    } catch (error) {
      console.error('Error approving business owner:', error);
      // Don't throw error here - business approval should still succeed
    }
  }
};

export const rejectBusiness = async (businessId: string, rejectedBy: string, reason?: string): Promise<void> => {
  // Get business to find the owner
  const businessRef = doc(db, 'business_profiles', businessId);
  const businessSnap = await getDoc(businessRef);
  
  if (!businessSnap.exists()) {
    throw new Error('Business not found');
  }
  
  const businessData = businessSnap.data();
  const ownerId = businessData.ownerId;
  
  // Update business status
  await updateDoc(businessRef, {
    status: 'rejected',
    isActive: false,
    rejectedAt: serverTimestamp(),
    rejectedBy,
    rejectionReason: reason
  });
  
  // Also reject the business owner if they are still pending
  if (ownerId) {
    try {
      const userRef = doc(db, 'users', ownerId);
      const userSnap = await getDoc(userRef);
      
      if (userSnap.exists()) {
        const userData = userSnap.data();
        // Only update if user is still pending and is business_owner
        if (userData.status === 'pending' && userData.userTypeId === USER_TYPES.BUSINESS_OWNER) {
          await updateDoc(userRef, {
            status: 'rejected',
            isActive: false,
            rejectedAt: serverTimestamp(),
            rejectedBy,
            rejectionReason: reason || 'Business application rejected'
          });
        }
      }
    } catch (error) {
      console.error('Error rejecting business owner:', error);
      // Don't throw error here - business rejection should still succeed
    }
  }
};

export const getPendingBusinesses = async (): Promise<Business[]> => {
  const businessesRef = collection(db, 'business_profiles');
  const q = query(businessesRef, where('status', '==', 'pending'), orderBy('requestedAt'));
  const snapshot = await getDocs(q);
  
  // Fetch owner information for each business
  const businessesWithOwnerInfo = await Promise.all(
    snapshot.docs.map(async (businessDoc) => {
      const businessData = businessDoc.data();
      let ownerInfo = null;
      
      if (businessData.ownerId) {
        try {
          const ownerRef = doc(db, 'users', businessData.ownerId);
          const ownerSnap = await getDoc(ownerRef);
          if (ownerSnap.exists()) {
            const ownerData = ownerSnap.data() as any;
            ownerInfo = {
              uid: ownerSnap.id,
              displayName: ownerData.displayName || '',
              email: ownerData.email || '',
              status: ownerData.status || 'unknown'
            };
          }
        } catch (error) {
          console.error('Error fetching owner info:', error);
        }
      }
      
      return {
        ...businessData,
        id: businessDoc.id,
        createdAt: businessData.createdAt?.toDate(),
        requestedAt: businessData.requestedAt?.toDate(),
        ownerInfo
      } as Business & { ownerInfo?: any };
    })
  );
  
  return businessesWithOwnerInfo;
};

export const getUserBusinesses = async (userId: string): Promise<Business[]> => {
  // For business owners, get businesses where they are the owner
  const businessesRef = collection(db, 'business_profiles');
  const q = query(
    businessesRef, 
    where('ownerId', '==', userId), 
    where('isActive', '==', true),
    orderBy('businessName')
  );
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    id: doc.id,
    createdAt: doc.data().createdAt?.toDate(),
    requestedAt: doc.data().requestedAt?.toDate(),
    approvedAt: doc.data().approvedAt?.toDate()
  } as Business));
};

// Alias for backward compatibility
export const getBusinessById = async (businessId: string): Promise<Business | null> => {
  return await getBusiness(businessId);
};
