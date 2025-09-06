// ============================================
// REFACTORED FIRESTORE OPERATIONS
// ============================================
// This file has been refactored into organized modules by collection:
// - utils.ts - Shared utilities and Firebase re-exports
// - userTypes.ts - user_types collection operations
// - users.ts - users collection operations  
// - businesses.ts - business_profiles collection operations
// - businessUserRequests.ts - business_user_requests collection operations
// - auditors.ts - auditor_profiles collection operations
// - requests.ts - general user requests operations
//
// For better tree shaking and organization, import directly from modules:
// import { getUserProfile } from '@/lib/firebase/users';
//
// All functions are re-exported below for backward compatibility.
// ============================================

// Re-export all modules for backward compatibility
export * from './utils';
export * from './userTypes';
export * from './users';
export * from './businesses';
export * from './businessUserRequests';
export * from './auditors';
export * from './requests';
// import { createBusiness } from '@/lib/firebase/businesses';
// import { getUserTypes } from '@/lib/firebase/userTypes';
//
// This file maintains backward compatibility by re-exporting all functions.

// Re-export all functions to maintain backward compatibility
export * from './utils';
export * from './userTypes';
export * from './users';
export * from './businesses';
export * from './businessUserRequests';
export * from './auditors';
