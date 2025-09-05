'use client';

import { useAuth } from '@/lib/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';
import { USER_TYPES, type UserTypeId, isValidUserType } from '@/lib/types/permissions';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredUserTypes?: UserTypeId[]; // 'admin', 'auditor', 'business_user', 'business_owner'
  requireApproval?: boolean; // Whether the user needs to be approved
  fallbackUrl?: string;
  showUnauthorized?: boolean;
}

export default function ProtectedRoute({ 
  children, 
  requiredUserTypes = [], 
  requireApproval = true,
  fallbackUrl = '/login',
  showUnauthorized = true 
}: ProtectedRouteProps) {
  const { user, userType, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        // User not authenticated, redirect to login
        const currentPath = window.location.pathname;
        router.push(`${fallbackUrl}?returnTo=${encodeURIComponent(currentPath)}`);
        return;
      }

      // Check if user needs approval and is not approved
      if (requireApproval && user.status !== 'approved') {
        router.push('/pending-approval');
        return;
      }

      if (requiredUserTypes.length > 0) {
        // Check if user has any of the required user types
        const userTypeName = userType?.name;
        const hasRequiredType = userTypeName && isValidUserType(userTypeName) && requiredUserTypes.includes(userTypeName);

        if (!hasRequiredType) {
          if (showUnauthorized) {
            router.push('/unauthorized');
          } else {
            router.push(fallbackUrl);
          }
          return;
        }
      }
    }
  }, [user, userType, loading, requiredUserTypes, requireApproval, router, fallbackUrl, showUnauthorized]);

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando permisos...</p>
        </div>
      </div>
    );
  }

  // Don't render children if user is not authenticated
  if (!user) {
    return null;
  }

  // Check approval status
  if (requireApproval && user.status !== 'approved') {
    return null;
  }

  // Check user type requirements
  if (requiredUserTypes.length > 0) {
    const userTypeName = userType?.name;
    const hasRequiredType = userTypeName && isValidUserType(userTypeName) && requiredUserTypes.includes(userTypeName);
    
    if (!hasRequiredType) {
      return null;
    }
  }

  return <>{children}</>;
}

// Higher-order component version
export function withProtection<P extends object>(
  Component: React.ComponentType<P>,
  requiredUserTypes?: UserTypeId[],
  requireApproval?: boolean
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute requiredUserTypes={requiredUserTypes} requireApproval={requireApproval}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}
