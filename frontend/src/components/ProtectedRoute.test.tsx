import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';

// --- Mocks -----------------------------------------------------------------

const push = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push, replace: vi.fn(), prefetch: vi.fn() }),
}));

const useAuth = vi.fn();
vi.mock('@/lib/contexts/AuthContext', () => ({
  useAuth: () => useAuth(),
}));

import ProtectedRoute from './ProtectedRoute';

type AuthState = {
  user: unknown;
  userType: unknown;
  loading: boolean;
};

function setAuth(state: Partial<AuthState>) {
  useAuth.mockReturnValue({
    user: null,
    userType: null,
    loading: false,
    ...state,
  });
}

const approvedUser = { uid: 'u1', status: 'approved', displayName: 'A' };

describe('ProtectedRoute', () => {
  beforeEach(() => {
    push.mockClear();
    useAuth.mockReset();
    window.history.pushState({}, '', '/survey');
  });

  it('shows a loading indicator while auth is resolving', () => {
    setAuth({ loading: true });
    render(
      <ProtectedRoute>
        <div>secret</div>
      </ProtectedRoute>,
    );
    expect(screen.getByText('Verificando permisos...')).toBeInTheDocument();
    expect(screen.queryByText('secret')).not.toBeInTheDocument();
  });

  it('redirects unauthenticated users to /login with a returnTo param', () => {
    setAuth({ user: null, loading: false });
    render(
      <ProtectedRoute>
        <div>secret</div>
      </ProtectedRoute>,
    );
    expect(push).toHaveBeenCalledWith('/login?returnTo=%2Fsurvey');
    expect(screen.queryByText('secret')).not.toBeInTheDocument();
  });

  it('redirects unapproved users to /pending-approval', () => {
    setAuth({ user: { uid: 'u1', status: 'pending' }, loading: false });
    render(
      <ProtectedRoute>
        <div>secret</div>
      </ProtectedRoute>,
    );
    expect(push).toHaveBeenCalledWith('/pending-approval');
    expect(screen.queryByText('secret')).not.toBeInTheDocument();
  });

  it('redirects approved users with the wrong role to /unauthorized', () => {
    setAuth({
      user: approvedUser,
      userType: { name: 'auditor' },
      loading: false,
    });
    render(
      <ProtectedRoute requiredUserTypes={['admin']}>
        <div>secret</div>
      </ProtectedRoute>,
    );
    expect(push).toHaveBeenCalledWith('/unauthorized');
    expect(screen.queryByText('secret')).not.toBeInTheDocument();
  });

  it('renders children for an approved user with an allowed role', () => {
    setAuth({
      user: approvedUser,
      userType: { name: 'admin' },
      loading: false,
    });
    render(
      <ProtectedRoute requiredUserTypes={['admin']}>
        <div>secret</div>
      </ProtectedRoute>,
    );
    expect(screen.getByText('secret')).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });

  it('renders children for an approved user when no specific role is required', () => {
    setAuth({ user: approvedUser, userType: { name: 'business_user' }, loading: false });
    render(
      <ProtectedRoute>
        <div>secret</div>
      </ProtectedRoute>,
    );
    expect(screen.getByText('secret')).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });
});
