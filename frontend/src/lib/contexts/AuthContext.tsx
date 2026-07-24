'use client';

import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { auth } from '@/lib/firebase/config';
import { 
  signIn as firebaseSignIn, 
  signUp as firebaseSignUp,
  signInWithGoogle as firebaseSignInWithGoogle,
  signOut as firebaseSignOut 
} from '@/lib/firebase/auth';
import { 
  getUserProfile, 
  createUserProfile,
  getBusinessById,
  getUserTypeById,
  createBusiness,
  createAuditorProfile,
  createUserRequest
} from '@/lib/firebase/firestore';
import { User, Business, UserType, AuthContextType, AuditorProfile } from '@/lib/types/auth';
import { USER_TYPES } from '@/lib/types/permissions';
import { devLog } from '@/lib/utils/devLog';

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userType, setUserType] = useState<UserType | null>(null);
  const [activeBusiness, setActiveBusiness] = useState<Business | null>(null);
  const [loading, setLoading] = useState(true);

  // Holds the display name captured during an email/password sign-up so the profile
  // created by onAuthStateChanged uses it even if Firebase's updateProfile hasn't
  // propagated to firebaseUser.displayName yet (they race).
  const pendingDisplayNameRef = useRef<string | null>(null);

  // Initialize authentication state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      try {
        if (firebaseUser) {
          // User is signed in
          let userProfile = await getUserProfile(firebaseUser.uid);
          
          if (!userProfile) {
            // Create user profile if it doesn't exist - starts as pending
            // Do NOT assign a default userTypeId here so the onboarding flow
            // can detect a missing userType and redirect the user to choose one.
            const newUser: Partial<User> = {
              uid: firebaseUser.uid,
              email: firebaseUser.email || '',
              displayName: firebaseUser.displayName || pendingDisplayNameRef.current || '',
              photoURL: firebaseUser.photoURL || undefined,
              status: 'pending',
              isActive: false
            };
            await createUserProfile(newUser);
            pendingDisplayNameRef.current = null;
            userProfile = await getUserProfile(firebaseUser.uid);
          }

          setUser(userProfile);

          if (userProfile) {
            try {
              // Load user type information only if userTypeId exists
              if (userProfile.userTypeId) {
                const userTypeData = await getUserTypeById(userProfile.userTypeId);
                setUserType(userTypeData);
              } else {
                setUserType(null);
              }

              // Load associated business if user has one and is approved
              if (userProfile.businessProfileId && userProfile.status === 'approved') {
                devLog.debug('Loading business for user:', {
                  businessProfileId: userProfile.businessProfileId,
                  status: userProfile.status
                });
                const business = await getBusinessById(userProfile.businessProfileId);
                devLog.debug('Loaded business:', business);
                setActiveBusiness(business);
              } else {
                devLog.debug('No business to load:', {
                  businessProfileId: userProfile.businessProfileId,
                  status: userProfile.status
                });
                setActiveBusiness(null);
              }
            } catch (userTypeError) {
              devLog.error('Error loading user type or business data:', userTypeError);
              setUserType(null);
              setActiveBusiness(null);
            }
          }
        } else {
          // User is signed out
          setUser(null);
          setUserType(null);
          setActiveBusiness(null);
        }
      } catch (error) {
        devLog.error('Error during auth state change:', error);
        setUser(null);
        setUserType(null);
        setActiveBusiness(null);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  const signIn = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    try {
      await firebaseSignIn(email, password);
      // User state will be updated by the onAuthStateChanged listener
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const signUp = async (email: string, password: string, displayName?: string): Promise<void> => {
    setLoading(true);
    // Capture the name before creating the account so the profile-creation path in
    // onAuthStateChanged can use it (firebaseUser.displayName may not be set yet).
    pendingDisplayNameRef.current = displayName?.trim() || null;
    try {
      await firebaseSignUp(email, password, displayName);
      // User state will be updated by the onAuthStateChanged listener
    } catch (error) {
      pendingDisplayNameRef.current = null;
      setLoading(false);
      throw error;
    }
  };

  const signInWithGoogle = async (): Promise<void> => {
    setLoading(true);
    try {
      await firebaseSignInWithGoogle();
      // User state will be updated by the onAuthStateChanged listener
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const signOut = async (): Promise<void> => {
    setLoading(true);
    try {
      await firebaseSignOut();
      // User state will be updated by the onAuthStateChanged listener
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const switchBusiness = async (businessId: string): Promise<void> => {
    try {
      // Verify user has access to this business and is approved
      if (user?.businessProfileId === businessId && user.status === 'approved') {
        const business = await getBusinessById(businessId);
        setActiveBusiness(business);
        
        // Optionally persist the selection in localStorage
        localStorage.setItem('activeBusinessId', businessId);
      } else if (userType?.name === 'admin') {
        // Admins can access any business
        const business = await getBusinessById(businessId);
        setActiveBusiness(business);
      } else {
        throw new Error('No tienes acceso a esta empresa o tu cuenta no está aprobada');
      }
    } catch (error) {
      devLog.error('Error switching business:', error);
      throw error;
    }
  };

  const refreshUserData = async (): Promise<void> => {
    if (!user) return;

    try {
      const updatedUser = await getUserProfile(user.uid);
      if (updatedUser) {
        setUser(updatedUser);
        
        // Refresh user type
        if (updatedUser.userTypeId) {
          const userTypeData = await getUserTypeById(updatedUser.userTypeId);
          setUserType(userTypeData);
        } else {
          setUserType(null);
        }
        
        // Refresh business data if needed
        if (updatedUser.businessProfileId && updatedUser.status === 'approved') {
          const business = await getBusinessById(updatedUser.businessProfileId);
          setActiveBusiness(business);
        } else {
          setActiveBusiness(null);
        }
      }
    } catch (error) {
      devLog.error('Error refreshing user data:', error);
    }
  };

  const requestBusinessCreation = async (businessData: Partial<Business>): Promise<void> => {
    if (!user) {
      throw new Error('User must be authenticated to request business creation');
    }

    try {
      // Create business with pending status
      const businessId = await createBusiness({
        ...businessData,
        ownerId: user.uid,
        subscriptionTier: businessData.subscriptionTier || 'basic'
      } as Omit<Business, 'id' | 'createdAt' | 'requestedAt'>);

      // Create a request record for admin review
      await createUserRequest({
        userId: user.uid,
        userTypeId: 'business_owner',
        requestType: 'business_creation',
        status: 'pending',
        requestData: {
          businessId,
          businessName: businessData.businessName
        }
      });

      await refreshUserData();
    } catch (error) {
      devLog.error('Error requesting business creation:', error);
      throw error;
    }
  };

  const requestAuditorRegistration = async (auditorData: Partial<AuditorProfile>): Promise<void> => {
    if (!user) {
      throw new Error('User must be authenticated to request auditor registration');
    }

    try {
      // Create auditor profile with pending status
      const auditorId = await createAuditorProfile({
        ...auditorData,
        userId: user.uid
      } as Omit<AuditorProfile, 'id' | 'createdAt' | 'requestedAt'>);

      // Create a request record for admin review
      await createUserRequest({
        userId: user.uid,
        userTypeId: 'auditor',
        requestType: 'auditor_registration',
        status: 'pending',
        requestData: {
          auditorId,
          certifications: auditorData.certifications,
          specializations: auditorData.specializations
        }
      });

      await refreshUserData();
    } catch (error) {
      devLog.error('Error requesting auditor registration:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    userType,
    activeBusiness,
    loading,
    signIn,
    signUp,
    signInWithGoogle,
    signOut,
    switchBusiness,
    refreshUserData,
    requestBusinessCreation,
    requestAuditorRegistration
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
