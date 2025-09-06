// Constants and types for user roles and permissions
// This file defines the valid user types and their permissions as they exist in Firestore

/**
 * Valid user type IDs - these match the document IDs in the user_types collection
 */
export const USER_TYPES = {
  ADMIN: 'admin',
  AUDITOR: 'auditor', 
  BUSINESS_USER: 'business_user',
  BUSINESS_OWNER: 'business_owner'
} as const;

export type UserTypeId = typeof USER_TYPES[keyof typeof USER_TYPES];

/**
 * Display names for user types
 */
export const USER_TYPE_DISPLAY_NAMES = {
  [USER_TYPES.ADMIN]: 'Administrador',
  [USER_TYPES.AUDITOR]: 'Auditor',
  [USER_TYPES.BUSINESS_USER]: 'Usuario de Empresa',
  [USER_TYPES.BUSINESS_OWNER]: 'Propietario de Empresa'
} as const;

/**
 * User type descriptions
 */
export const USER_TYPE_DESCRIPTIONS = {
  [USER_TYPES.ADMIN]: 'Administrador del sistema con acceso completo a todas las funcionalidades',
  [USER_TYPES.AUDITOR]: 'Auditor certificado que puede revisar y validar certificaciones',
  [USER_TYPES.BUSINESS_USER]: 'Usuario de empresa que puede subir evidencia y realizar operaciones del proceso de certificación desde la perspectiva empresarial',
  [USER_TYPES.BUSINESS_OWNER]: 'Propietario de empresa que puede gestionar su negocio, aprobar usuarios y supervisar operaciones'
} as const;

/**
 * System permissions - these match the permissions defined in Firestore
 */
export const PERMISSIONS = {
  // Admin permissions
  MANAGE_USERS: 'manage_users',
  MANAGE_BUSINESSES: 'manage_businesses',
  MANAGE_AUDITORS: 'manage_auditors',
  APPROVE_REQUESTS: 'approve_requests',
  SYSTEM_SETTINGS: 'system_settings',
  VIEW_ALL_DATA: 'view_all_data',
  
  // Business owner permissions
  APPROVE_BUSINESS_USERS: 'approve_business_users',
  MANAGE_BUSINESS_SETTINGS: 'manage_business_settings',
  VIEW_BUSINESS_ANALYTICS: 'view_business_analytics',
  ASSIGN_USER_ROLES: 'assign_user_roles',
  
  // Business user permissions
  MANAGE_OWN_BUSINESS: 'manage_own_business',
  REQUEST_CERTIFICATIONS: 'request_certifications',
  UPLOAD_EVIDENCE: 'upload_evidence',
  VIEW_OWN_AUDITS: 'view_own_audits',
  MANAGE_BUSINESS_USERS: 'manage_business_users',
  SUBMIT_CERTIFICATION_REQUESTS: 'submit_certification_requests',
  TRACK_CERTIFICATION_PROGRESS: 'track_certification_progress',
  MANAGE_COMPANY_DOCUMENTS: 'manage_company_documents',
  VIEW_CERTIFICATION_REQUIREMENTS: 'view_certification_requirements',
  
  // Auditor permissions
  CONDUCT_AUDITS: 'conduct_audits',
  VALIDATE_EVIDENCE: 'validate_evidence',
  GENERATE_REPORTS: 'generate_reports',
  VIEW_ASSIGNED_BUSINESSES: 'view_assigned_businesses',
  MANAGE_AUDIT_SCHEDULE: 'manage_audit_schedule'
} as const;

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS];

/**
 * Permissions by user type - these should match what's in Firestore
 */
export const USER_TYPE_PERMISSIONS = {
  [USER_TYPES.ADMIN]: [
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.MANAGE_BUSINESSES,
    PERMISSIONS.MANAGE_AUDITORS,
    PERMISSIONS.APPROVE_REQUESTS,
    PERMISSIONS.SYSTEM_SETTINGS,
    PERMISSIONS.VIEW_ALL_DATA
  ],
  [USER_TYPES.BUSINESS_OWNER]: [
    PERMISSIONS.MANAGE_OWN_BUSINESS,
    PERMISSIONS.REQUEST_CERTIFICATIONS,
    PERMISSIONS.UPLOAD_EVIDENCE,
    PERMISSIONS.VIEW_OWN_AUDITS,
    PERMISSIONS.MANAGE_BUSINESS_USERS,
    PERMISSIONS.APPROVE_BUSINESS_USERS,
    PERMISSIONS.MANAGE_BUSINESS_SETTINGS,
    PERMISSIONS.VIEW_BUSINESS_ANALYTICS,
    PERMISSIONS.ASSIGN_USER_ROLES,
    PERMISSIONS.SUBMIT_CERTIFICATION_REQUESTS,
    PERMISSIONS.TRACK_CERTIFICATION_PROGRESS,
    PERMISSIONS.MANAGE_COMPANY_DOCUMENTS,
    PERMISSIONS.VIEW_CERTIFICATION_REQUIREMENTS
  ],
  [USER_TYPES.BUSINESS_USER]: [
    PERMISSIONS.MANAGE_OWN_BUSINESS,
    PERMISSIONS.REQUEST_CERTIFICATIONS,
    PERMISSIONS.UPLOAD_EVIDENCE,
    PERMISSIONS.VIEW_OWN_AUDITS,
    PERMISSIONS.MANAGE_BUSINESS_USERS,
    PERMISSIONS.SUBMIT_CERTIFICATION_REQUESTS,
    PERMISSIONS.TRACK_CERTIFICATION_PROGRESS,
    PERMISSIONS.MANAGE_COMPANY_DOCUMENTS,
    PERMISSIONS.VIEW_CERTIFICATION_REQUIREMENTS
  ],
  [USER_TYPES.AUDITOR]: [
    PERMISSIONS.CONDUCT_AUDITS,
    PERMISSIONS.VALIDATE_EVIDENCE,
    PERMISSIONS.GENERATE_REPORTS,
    PERMISSIONS.VIEW_ASSIGNED_BUSINESSES,
    PERMISSIONS.MANAGE_AUDIT_SCHEDULE
  ]
} as const;

/**
 * Helper function to check if a user type has a specific permission
 */
export function userTypeHasPermission(userType: UserTypeId, permission: Permission): boolean {
  const permissions = USER_TYPE_PERMISSIONS[userType] as readonly Permission[];
  return permissions?.includes(permission) ?? false;
}

/**
 * Helper function to get all permissions for a user type
 */
export function getUserTypePermissions(userType: UserTypeId): readonly Permission[] {
  return (USER_TYPE_PERMISSIONS[userType] as readonly Permission[]) ?? [];
}

/**
 * Helper function to check if a user type ID is valid
 */
export function isValidUserType(userType: string): userType is UserTypeId {
  return Object.values(USER_TYPES).includes(userType as UserTypeId);
}

/**
 * Route permissions - maps routes to required user types
 */
export const ROUTE_PERMISSIONS = {
  '/dashboard': [USER_TYPES.ADMIN, USER_TYPES.AUDITOR, USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER],
  '/business': [USER_TYPES.ADMIN, USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER],
  '/audits': [USER_TYPES.ADMIN, USER_TYPES.AUDITOR, USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER],
  '/admin': [USER_TYPES.ADMIN],
  '/profile': [USER_TYPES.ADMIN, USER_TYPES.AUDITOR, USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER] // Any authenticated user
} as const;

export type ProtectedRoute = keyof typeof ROUTE_PERMISSIONS;
