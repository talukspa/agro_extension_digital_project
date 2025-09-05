import { NextRequest, NextResponse } from 'next/server';
import { verifyAuthToken } from '@/lib/auth/server';
import { USER_TYPES } from '@/lib/types/permissions';

// Define protected routes and their required roles
const PROTECTED_ROUTES = {
  '/dashboard': [USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER, USER_TYPES.AUDITOR, USER_TYPES.ADMIN],
  '/business': [USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER, USER_TYPES.ADMIN],
  '/audits': [USER_TYPES.BUSINESS_USER, USER_TYPES.BUSINESS_OWNER, USER_TYPES.AUDITOR, USER_TYPES.ADMIN],
  '/admin': [USER_TYPES.ADMIN],
  '/profile': [], // Any authenticated user
} as const;

// Public routes that don't require authentication
const PUBLIC_ROUTES = [
  '/',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/api/auth',
  '/api/public'
];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static files and API routes (except protected ones)
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/auth') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Check if route is public
  const isPublicRoute = PUBLIC_ROUTES.some(route => 
    pathname === route || pathname.startsWith(route)
  );

  if (isPublicRoute) {
    return NextResponse.next();
  }

  // Get authentication token from cookies or headers
  const token = request.cookies.get('auth-token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '');

  if (!token) {
    // Redirect to login if no token
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  try {
    // Verify the token and get user claims
    const userClaims = await verifyAuthToken(token);
    
    if (!userClaims) {
      // Invalid token, redirect to login
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Check if route requires specific roles
    const requiredRoles = getRequiredRolesForPath(pathname);
    
    if (requiredRoles.length > 0) {
      const userRole = userClaims.role || '';
      
      if (!requiredRoles.includes(userRole)) {
        // User doesn't have required role, redirect to unauthorized page
        return NextResponse.redirect(new URL('/unauthorized', request.url));
      }
    }

    // Add user information to request headers for use in API routes
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', userClaims.uid);
    requestHeaders.set('x-user-role', userClaims.role || '');
    requestHeaders.set('x-business-id', userClaims.businessId || '');

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });

  } catch (error) {
    console.error('Auth middleware error:', error);
    
    // Token verification failed, redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }
}

function getRequiredRolesForPath(pathname: string): string[] {
  // Find the most specific matching route
  const matchingRoute = Object.keys(PROTECTED_ROUTES)
    .sort((a, b) => b.length - a.length) // Sort by length desc to match most specific first
    .find(route => pathname.startsWith(route));

  if (matchingRoute) {
    const roles = PROTECTED_ROUTES[matchingRoute as keyof typeof PROTECTED_ROUTES];
    return [...roles]; // Create a mutable copy of the readonly array
  }
  
  return [];
}

// Configure which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
