# GitHub Copilot Instructions - AgroExtensión Digital

## 🏗️ Architecture Overview

This is a **multi-tenant agricultural extension platform** with microservices architecture:

- **Frontend**: Next.js 15 + TypeScript + Firebase Auth + Tailwind CSS
- **Backend**: Python FastAPI microservices (agents, webhooks)
- **Database**: Google Firestore with multi-tenant design
- **Infrastructure**: Google Cloud Run + Terraform/Terragrunt IaC
- **Package Management**: `uv` for Python, `pnpm` for Node.js

## 🔧 Essential Development Patterns

### Python Scripts Execution
Always use `uv run` for Python scripts:
```bash
cd data_model && uv run verify_user_types_final.py
cd agents && uv run python main.py
```

### User Type System (Critical Pattern)
The system has **3 user types** with consistent ID format across frontend/backend:
- `admin`: System administrator
- `auditor`: Certification auditor  
- `business_user`: Company user who uploads evidence

**Key Files:**
- `frontend/src/lib/types/permissions.ts` - Type constants & validation
- `data_model/verify_basic_types_sync.py` - Backend/frontend sync verification
- Firestore collection: `user_types` (document_id = id = name)

### Multi-tenant Firebase Pattern
```typescript
// Always use these patterns for user type imports
import { USER_TYPES, type UserTypeId } from '@/lib/types/permissions';

// Route protection
const PROTECTED_ROUTES = {
  '/dashboard': [USER_TYPES.BUSINESS_USER, USER_TYPES.AUDITOR, USER_TYPES.ADMIN],
  '/admin': [USER_TYPES.ADMIN]
};
```

### Database Migration Scripts
Located in `data_model/`, always verify sync after changes:
```bash
uv run verify_basic_types_sync.py  # Check frontend/backend alignment
uv run normalize_user_types_format.py  # Fix ID format consistency
```

## 🎯 Project-Specific Conventions

### Frontend Structure
- **AuthContext**: Central auth state with multi-tenant business switching
- **ProtectedRoute**: Component with `requiredUserTypes: UserTypeId[]`
- **Middleware**: Route-level protection using `USER_TYPES` constants
- **Firebase Config**: Uses custom claims for business association

### Backend Structure
- **Firestore Collections**: `user_types`, `users`, `businesses`, `auditor_profiles`
- **ID Format**: Consistent document_id = id = name pattern
- **Authentication**: Firebase Auth with custom claims

### Infrastructure Patterns
- **Environments**: NPE (dev) and PRD with shared common.yaml
- **Terragrunt**: Hierarchical configuration in `cicd/stacks/`
- **Container Registry**: Shared NPE project for both environments

## 🚦 Critical Integration Points

### Firebase-Firestore Connection
- Project: `agro-extension-digital-npe`
- Database: `agro-extension-db`
- Authentication: Application Default Credentials pattern

### Python Dependencies
- Agents: LangChain + Google ADK + LangGraph
- Webhooks: FastAPI + Pydantic v2 + HTTPX
- All use Python 3.12 (exact version required)

### Development Environment
- **Dev Containers**: Primary development method
- **VS Code**: Configured with proper extensions
- **Authentication**: `gcloud auth application-default login`

## ⚠️ Common Pitfalls to Avoid

1. **User Type Misalignment**: Always verify frontend `USER_TYPES` match Firestore documents
2. **Python Version**: Must use exactly Python 3.12 (not 3.12+)
3. **ID Format**: Firestore user_types requires document_id = id = name consistency
4. **Route Protection**: Use `UserTypeId[]` not `string[]` for type safety
5. **uv Commands**: Never use `python` directly, always `uv run python`

## 🔍 Key Debugging Commands

```bash
# Verify user types consistency
cd data_model && uv run verify_basic_types_sync.py

# Check Firestore collections
cd data_model && uv run list_collections.py

# Frontend development
cd frontend && pnpm dev

# Agent testing
cd agents && uv run python main.py --log-level DEBUG
```

## 📁 Essential File References

- `frontend/src/lib/types/permissions.ts` - Type system source of truth
- `frontend/src/lib/contexts/AuthContext.tsx` - Multi-tenant auth logic
- `data_model/USER_ROLES_MIGRATION_README.md` - Database migration guide
- `cicd/stacks/common.yaml` - Infrastructure shared config
- `README.md` - Comprehensive project documentation
