// Re-export Firebase configuration - Solo autenticación
export { auth } from './config';
export { default as app } from './config';

// Types
export type { User } from 'firebase/auth';

// Re-export all functions from organized modules for backward compatibility
// This allows existing imports to continue working while providing better organization

// Utils
export * from './utils';

// User Types Operations
export * from './userTypes';

// User Operations  
export * from './users';

// Business Operations
export * from './businesses';

// Business User Requests Operations
export * from './businessUserRequests';

// Auditor Operations
export * from './auditors';

// Legacy compatibility - keep original firestore.ts available as fallback
// Individual modules can be imported directly for better tree shaking:
// import { getUserProfile } from '@/lib/firebase/users';
// import { createBusiness } from '@/lib/firebase/businesses';
// import { getUserTypes } from '@/lib/firebase/userTypes';