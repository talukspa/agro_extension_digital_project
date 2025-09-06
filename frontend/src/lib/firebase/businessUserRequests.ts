import { User, BusinessUserRequest } from '@/lib/types/auth';
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
  addDoc,
  db
} from './utils';
import { validateDb } from './utils';

// ============================================
// BUSINESS USER MANAGEMENT
// ============================================

export const requestBusinessAccess = async (
  userId: string, 
  businessId: string, 
  role: string = 'employee',
  message?: string
): Promise<void> => {
  const requestRef = doc(collection(db, 'business_user_requests'));
  await setDoc(requestRef, {
    userId,
    businessId,
    role,
    message: message || '',
    status: 'pending',
    requestedAt: serverTimestamp()
  });
};

export const getBusinessUserRequests = async (): Promise<BusinessUserRequest[]> => {
  const requestsRef = collection(db, 'business_user_requests');
  const q = query(requestsRef, where('status', '==', 'pending'), orderBy('requestedAt'));
  const snapshot = await getDocs(q);
  
  return snapshot.docs.map(doc => ({
    ...doc.data(),
    id: doc.id,
    requestedAt: doc.data().requestedAt?.toDate()
  } as BusinessUserRequest));
};

export const approveBusinessUser = async (
  requestId: string, 
  reviewedBy: string
): Promise<void> => {
  // Get the request details
  const requestRef = doc(db, 'business_user_requests', requestId);
  const requestSnap = await getDoc(requestRef);
  
  if (!requestSnap.exists()) {
    throw new Error('Business user request not found');
  }
  
  const requestData = requestSnap.data();
  const { userId, businessId, role } = requestData;
  
  // Add user to business
  const businessRef = doc(db, 'business_profiles', businessId);
  const businessSnap = await getDoc(businessRef);
  
  if (businessSnap.exists()) {
    const businessData = businessSnap.data();
    const currentUsers = businessData.business_users || [];
    
    // Add user if not already in the list
    if (!currentUsers.some((user: any) => user.userId === userId)) {
      const updatedUsers = [...currentUsers, {
        userId,
        role,
        addedAt: new Date(),
        addedBy: reviewedBy,
        isActive: true
      }];
      
      await updateDoc(businessRef, {
        business_users: updatedUsers
      });
    }
  }
  
  // Update user profile
  const userRef = doc(db, 'users', userId);
  await updateDoc(userRef, {
    businessProfileId: businessId,
    status: 'approved',
    isActive: true,
    approvedAt: serverTimestamp(),
    approvedBy: reviewedBy
  });
  
  // Update request status
  await updateDoc(requestRef, {
    status: 'approved',
    reviewedAt: serverTimestamp(),
    reviewedBy
  });
};

export const rejectBusinessUser = async (
  requestId: string, 
  reviewedBy: string, 
  notes?: string
): Promise<void> => {
  // Get the request details
  const requestRef = doc(db, 'business_user_requests', requestId);
  const requestSnap = await getDoc(requestRef);
  
  if (!requestSnap.exists()) {
    throw new Error('Business user request not found');
  }
  
  const requestData = requestSnap.data();
  const { userId } = requestData;
  
  // Update user profile to rejected
  const userRef = doc(db, 'users', userId);
  await updateDoc(userRef, {
    status: 'rejected',
    isActive: false,
    rejectedAt: serverTimestamp(),
    rejectedBy: reviewedBy,
    rejectionReason: notes || 'Business access request rejected'
  });
  
  // Update request status
  await updateDoc(requestRef, {
    status: 'rejected',
    reviewedAt: serverTimestamp(),
    reviewedBy,
    reviewNotes: notes
  });
};

export const removeBusinessUser = async (
  businessId: string, 
  userId: string, 
  removedBy: string
): Promise<void> => {
  // Remove user from business
  const businessRef = doc(db, 'business_profiles', businessId);
  const businessSnap = await getDoc(businessRef);
  
  if (businessSnap.exists()) {
    const businessData = businessSnap.data();
    const currentUsers = businessData.business_users || [];
    
    // Remove user from the list
    const updatedUsers = currentUsers.filter((user: any) => user.userId !== userId);
    
    await updateDoc(businessRef, {
      business_users: updatedUsers
    });
  }
  
  // Update user profile
  const userRef = doc(db, 'users', userId);
  await updateDoc(userRef, {
    businessProfileId: null,
    removedAt: serverTimestamp(),
    removedBy
  });
};

export const getBusinessUsers = async (businessId: string): Promise<User[]> => {
  const businessRef = doc(db, 'business_profiles', businessId);
  const businessSnap = await getDoc(businessRef);
  
  if (!businessSnap.exists()) {
    return [];
  }
  
  const businessData = businessSnap.data();
  const businessUsers = businessData.business_users || [];
  
  // Fetch user profiles for each business user
  const userProfiles = await Promise.all(
    businessUsers.map(async (businessUser: any) => {
      try {
        const userRef = doc(db, 'users', businessUser.userId);
        const userSnap = await getDoc(userRef);
        
        if (userSnap.exists()) {
          const userData = userSnap.data();
          return {
            ...userData,
            uid: userSnap.id,
            role: businessUser.role,
            addedAt: businessUser.addedAt,
            createdAt: userData.createdAt?.toDate(),
            lastLoginAt: userData.lastLoginAt?.toDate()
          } as User & { role?: string; addedAt?: any };
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
      
      return null;
    })
  );
  
  // Filter out null values
  return userProfiles.filter(user => user !== null) as User[];
};
