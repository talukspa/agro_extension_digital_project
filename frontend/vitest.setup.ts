import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// Provide fake Firebase env vars so any accidental real config import does not throw.
process.env.NEXT_PUBLIC_FIREBASE_API_KEY = 'test-api-key';
process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = 'test.firebaseapp.com';
process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID = 'test-project';
process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'test.appspot.com';
process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = 'test-sender';
process.env.NEXT_PUBLIC_FIREBASE_APP_ID = 'test-app-id';

// Global Firebase mock: never touch real Firebase services in tests.
// `@/lib/firebase/config` throws at import time when env vars are missing and
// otherwise initializes a live Firebase app, so we stub its exports everywhere.
vi.mock('@/lib/firebase/config', () => ({
  auth: { currentUser: null },
  db: {},
  storage: {},
  default: {},
}));
