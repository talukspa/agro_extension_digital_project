import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { User as FirebaseUser } from 'firebase/auth';

// --- Mocks -----------------------------------------------------------------

// Capture the onAuthStateChanged callback so the test can drive auth state.
let authStateCallback: ((user: FirebaseUser | null) => void) | null = null;

vi.mock('firebase/auth', () => ({
  onAuthStateChanged: (_auth: unknown, cb: (user: FirebaseUser | null) => void) => {
    authStateCallback = cb;
    return () => {
      authStateCallback = null;
    };
  },
}));

// Firebase auth wrapper (signUp/signIn/etc). signUp resolves; the real profile
// write happens in AuthContext's onAuthStateChanged handler.
const firebaseSignUp = vi.fn().mockResolvedValue({ user: { uid: 'user-1' } });
vi.mock('@/lib/firebase/auth', () => ({
  signIn: vi.fn().mockResolvedValue(undefined),
  signUp: (...args: unknown[]) => firebaseSignUp(...args),
  signInWithGoogle: vi.fn().mockResolvedValue(undefined),
  signOut: vi.fn().mockResolvedValue(undefined),
}));

// Firestore profile operations.
const getUserProfile = vi.fn();
const createUserProfile = vi.fn().mockResolvedValue(undefined);
vi.mock('@/lib/firebase/firestore', () => ({
  getUserProfile: (...args: unknown[]) => getUserProfile(...args),
  createUserProfile: (...args: unknown[]) => createUserProfile(...args),
  getBusinessById: vi.fn().mockResolvedValue(null),
  getUserTypeById: vi.fn().mockResolvedValue(null),
  createBusiness: vi.fn(),
  createAuditorProfile: vi.fn(),
  createUserRequest: vi.fn(),
}));

import { AuthProvider, useAuth } from './AuthContext';

function SignUpButton({ displayName }: { displayName?: string }) {
  const { signUp } = useAuth();
  return (
    <button onClick={() => signUp('new@user.com', 'password123', displayName)}>
      sign up
    </button>
  );
}

// Simulate a freshly created Firebase user whose displayName has NOT yet
// propagated (the race the fix guards against).
function firebaseUser(overrides: Partial<FirebaseUser> = {}): FirebaseUser {
  return {
    uid: 'user-1',
    email: 'new@user.com',
    displayName: null,
    photoURL: null,
    ...overrides,
  } as FirebaseUser;
}

describe('AuthContext signUp -> profile creation', () => {
  beforeEach(() => {
    authStateCallback = null;
    firebaseSignUp.mockClear();
    getUserProfile.mockReset();
    createUserProfile.mockClear();
  });

  it('persists the displayName provided at registration into the created profile', async () => {
    // No profile exists yet, then return the created profile on the re-read.
    getUserProfile
      .mockResolvedValueOnce(null)
      .mockResolvedValueOnce({
        uid: 'user-1',
        email: 'new@user.com',
        displayName: 'Juan Pérez',
        status: 'pending',
      });

    render(
      <AuthProvider>
        <SignUpButton displayName="Juan Pérez" />
      </AuthProvider>,
    );

    // Register.
    await userEvent.click(screen.getByText('sign up'));
    expect(firebaseSignUp).toHaveBeenCalledWith('new@user.com', 'password123', 'Juan Pérez');

    // Firebase fires auth state change with a user whose displayName is still null.
    await act(async () => {
      authStateCallback?.(firebaseUser({ displayName: null }));
    });

    await waitFor(() => expect(createUserProfile).toHaveBeenCalledTimes(1));

    // The bug: displayName was dropped. The fix threads it via pendingDisplayNameRef.
    const createdProfile = createUserProfile.mock.calls[0][0];
    expect(createdProfile.displayName).toBe('Juan Pérez');
    expect(createdProfile.uid).toBe('user-1');
    expect(createdProfile.status).toBe('pending');
  });

  it('prefers the Firebase user displayName when it is already present', async () => {
    getUserProfile
      .mockResolvedValueOnce(null)
      .mockResolvedValueOnce({ uid: 'user-1', status: 'pending' });

    render(
      <AuthProvider>
        <SignUpButton displayName="Typed Name" />
      </AuthProvider>,
    );

    await userEvent.click(screen.getByText('sign up'));

    await act(async () => {
      authStateCallback?.(firebaseUser({ displayName: 'Propagated Name' }));
    });

    await waitFor(() => expect(createUserProfile).toHaveBeenCalledTimes(1));
    expect(createUserProfile.mock.calls[0][0].displayName).toBe('Propagated Name');
  });

  it('does not create a profile when one already exists', async () => {
    getUserProfile.mockResolvedValue({ uid: 'user-1', status: 'approved' });

    render(
      <AuthProvider>
        <SignUpButton />
      </AuthProvider>,
    );

    await act(async () => {
      authStateCallback?.(firebaseUser({ displayName: 'Existing' }));
    });

    await waitFor(() => expect(getUserProfile).toHaveBeenCalled());
    expect(createUserProfile).not.toHaveBeenCalled();
  });
});
