import { NextRequest, NextResponse } from 'next/server';

// Define protected routes and their required roles
const PROTECTED_ROUTES = {
  '/dashboard': ['business_owner', 'auditor', 'admin'],
  '/business': ['business_owner', 'admin'],
  '/audits': ['business_owner', 'auditor', 'admin'],
  '/admin': ['admin'],
  '/profile': [], // Any authenticated user
} as const;

// Public routes that don't require authentication
const PUBLIC_ROUTES = [
  '/',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/unauthorized',
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

  // For protected routes, we'll handle authentication on the client side
  // The middleware will only redirect to login if no auth token is present
  const authToken = request.cookies.get('auth-token')?.value;
  
  if (!authToken) {
    // No auth token present, redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If token exists, let the request proceed
  // Authentication verification will happen on the client side
  return NextResponse.next();
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
