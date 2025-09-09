# Business Profiles Migration - September 8, 2025

## Overview
This document describes the migration performed on the `business_profiles` collection to restructure owner information and remove obsolete fields.

## Migration Summary

**Date**: September 8, 2025  
**Script**: `migrate_business_profiles.py`  
**Documents Affected**: 21 business profiles  
**Users Created**: 21 business_owner users  

## Changes Applied

### 1. Removed Obsolete Fields
- ❌ `business_users` (array) - Was empty in all documents
- ❌ `pendingUsers` (array) - Was empty in all documents  
- ❌ `owner_name` (string) - Migrated to embedded object
- ❌ `owner_email` (string) - Migrated to embedded object
- ❌ `owner_phone` (string) - Migrated to embedded object
- ❌ `owner_role` (string) - Migrated to embedded object

### 2. Added New Structure
- ✅ `owner` (object) - Embedded business owner information

```typescript
interface BusinessOwner {
  email: string;
  name: string;
  phone: string;
  role: string;
  userType: 'business_owner';
  status: 'active';
  createdAt: Timestamp;
  lastLogin: null;
}
```

### 3. Created Corresponding Users
For each business profile, a corresponding user document was created in the `users` collection:

```typescript
interface BusinessOwnerUser {
  uid: string;                    // Generated unique ID (MD5 hash of email + RUT)
  email: string;                  // From owner_email
  displayName: string;            // From owner_name
  photoURL: string;               // Empty initially
  userTypeId: 'business_owner';   // New user type
  status: 'approved';             // Auto-approved
  isActive: boolean;              // true
  createdAt: Timestamp;           // Migration timestamp
  lastLoginAt: null;              // null initially
}
```

## Migration Statistics

| Metric | Count |
|--------|-------|
| Business Profiles Processed | 21 |
| Business Profiles Migrated | 21 |
| Business Owner Users Created | 21 |
| Errors | 0 |

## Files Generated

- `business_profiles_migration_log_20250908_230528.json` - Complete migration log with details
- `business_profiles_current_schema.json` - Pre-migration schema analysis
- `users_current_schema.json` - Users collection schema analysis

## User ID Generation

Business owner user IDs are generated using MD5 hash of:
```
email.toLowerCase().trim() + "_" + business_rut
```

This ensures:
- Deterministic IDs (same email + RUT = same ID)
- Uniqueness across the system
- No dependency on Firebase Auth UIDs

## Schema Compliance

The created users follow the existing `users` collection schema exactly:
- Uses `displayName` instead of `name`
- Uses `userTypeId` instead of `userType`
- Includes all required fields: `uid`, `email`, `displayName`, `photoURL`, `userTypeId`, `status`, `isActive`, `createdAt`, `lastLoginAt`
- Follows the same patterns as existing users

## Verification Commands

```bash
# Verify business profiles structure
cd data_model && uv run get_business_profiles_schema.py

# Verify users collection
cd data_model && uv run get_users_schema.py

# Check migration logs
cat data_model/business_profiles_migration_log_20250908_230528.json | jq '.stats'
```

## Rollback Considerations

If rollback is needed:
1. Remove the 21 created business_owner users from `users` collection
2. Restore the `owner_*` fields from the migration log
3. Re-add empty `business_users` and `pendingUsers` arrays
4. Remove the `owner` embedded objects

The migration log contains all original data needed for rollback.

## Impact on Frontend

The frontend should be updated to:
1. Access owner information via `business_profile.owner` instead of `business_profile.owner_*`
2. Handle the new `business_owner` user type
3. Update any queries that referenced the removed fields

## Impact on Backend Services

Backend services should be updated to:
1. Use the new embedded `owner` object structure
2. Recognize `business_owner` as a valid `userTypeId`
3. Handle authentication for business_owner users
4. Update any business logic that relied on the old `owner_*` fields
