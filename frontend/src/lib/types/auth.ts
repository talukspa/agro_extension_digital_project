// Types for the authorization system with admin approval
export interface UserType {
  id: string; // Matches document ID: 'admin', 'auditor', 'business_user'
  name: string; // Same as id: 'admin', 'auditor', 'business_user'  
  displayName: string; // 'Administrador', 'Auditor', 'Usuario de Empresa'
  description: string;
  permissions: string[];
  isActive: boolean;
  createdAt: Date;
  metadata?: Record<string, unknown>;
}

export interface User {
  uid: string;
  email: string;
  displayName: string;
  photoURL?: string;
  userTypeId?: string; // Reference to user_types collection: 'admin', 'auditor', 'business_user', 'business_owner'
  role?: 'business_user' | 'business_owner' | 'auditor' | 'admin'; // Simplified roles
  status: 'pending' | 'approved' | 'rejected' | 'suspended';
  businessProfileId?: string; // Reference to business profile if business_user
  auditorProfileId?: string; // Reference to auditor profile if auditor
  requestedBusinessId?: string; // Business user wants to join
  businessRole?: string; // Role within the business (manager, employee, etc.)
  requestedAt: Date;
  approvedAt?: Date;
  approvedBy?: string; // Admin who approved the user
  rejectedAt?: Date;
  rejectedBy?: string;
  rejectionReason?: string;
  isActive: boolean;
  createdAt: Date;
  lastLoginAt?: Date;
  metadata?: Record<string, unknown>;
}

export interface Business {
  id: string;
  businessName: string;
  businessType?: string;
  description?: string;
  location?: string;
  contactEmail?: string;
  contactPhone?: string;
  website?: string;
  email?: string;
  // Campos específicos de business_profiles
  legal_name?: string;
  rut?: string;
  region?: string;
  commune?: string;
  address?: string;
  business_size?: string;
  process_type?: string;
  digital_tools_experienced?: string[];
  digital_tools_used_at_work?: string[];
  owner?: any; // Estructura del propietario
  // Campos originales
  ownerId: string; // Required - ID del propietario de la empresa
  business_users: string[]; // Array of approved user UIDs
  pendingUsers?: string[]; // Array of pending user UIDs for approval
  status: 'pending' | 'approved' | 'rejected' | 'suspended';
  requestedAt: Date;
  approvedAt?: Date;
  approvedBy?: string; // Admin who approved the business
  rejectedAt?: Date;
  rejectedBy?: string;
  rejectionReason?: string;
  createdAt: Date;
  updatedAt?: Date;
  subscriptionTier: 'basic' | 'premium' | 'enterprise';
  isActive: boolean;
  metadata?: Record<string, unknown>;
}

export interface AuditorProfile {
  id: string;
  userId: string;
  certifications: string[];
  specializations: string[];
  status: 'pending' | 'approved' | 'rejected' | 'suspended';
  requestedAt: Date;
  approvedAt?: Date;
  approvedBy?: string;
  rejectedAt?: Date;
  rejectedBy?: string;
  rejectionReason?: string;
  isActive: boolean;
  createdAt: Date;
  metadata?: Record<string, unknown>;
}

export interface UserRequest {
  id: string;
  userId: string;
  userTypeId: string;
  requestType: 'user_approval' | 'business_creation' | 'auditor_registration';
  status: 'pending' | 'approved' | 'rejected';
  requestData: Record<string, unknown>;
  requestedAt: Date;
  reviewedAt?: Date;
  reviewedBy?: string;
  reviewNotes?: string;
  metadata?: Record<string, unknown>;
}

// New type for business user requests
export interface BusinessUserRequest {
  id: string;
  userId: string;
  businessId: string;
  requestedRole: string; // Role they want within the business
  message?: string; // Optional message from user
  status: 'pending' | 'approved' | 'rejected';
  requestedAt: Date;
  reviewedAt?: Date;
  reviewedBy?: string; // Admin or business owner who reviewed
  reviewNotes?: string;
}

export interface AuthContextType {
  user: User | null;
  userType: UserType | null;
  activeBusiness: Business | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, displayName?: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  switchBusiness: (businessId: string) => Promise<void>;
  refreshUserData: () => Promise<void>;
  requestBusinessCreation: (businessData: Partial<Business>) => Promise<void>;
  requestAuditorRegistration: (auditorData: Partial<AuditorProfile>) => Promise<void>;
}

export interface FirebaseCustomClaims {
  businessId?: string;
  role?: string;
  isActive?: boolean;
}

export interface AuthError {
  code: string;
  message: string;
}
