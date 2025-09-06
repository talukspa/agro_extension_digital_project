# Firebase Configuration

This directory contains Firebase configuration files for the Agro Extension Digital frontend.

## Files

- `config.ts`: Client-side Firebase configuration and initialization
- `firestore.ts`: Firestore-specific utilities and types
- `server.ts`: Server-side Firebase Admin configuration (if needed)
- `index.ts`: Main exports for Firebase services

## Usage

```typescript
import { auth, db, storage } from '@/lib/firebase';

// Authentication
const user = auth.currentUser;

// Firestore
const docRef = doc(db, 'collection', 'document');

// Storage
const storageRef = ref(storage, 'path/to/file');
```

## Environment Variables

Make sure to set up the following environment variables in `.env.local`:

- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`
- `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`
- `FIRESTORE_DATABASE_ID`
