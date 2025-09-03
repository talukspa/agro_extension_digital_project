Implementing Authentication and Authorization for Next.js on Cloud Run
This guide outlines a robust and scalable solution for adding authentication (AuthN) and authorization (AuthZ) to a Next.js application deployed on Google Cloud Run. The recommended approach uses Firebase Authentication for handling user identity and a self-managed database (like Firestore) for controlling user permissions.

Recommended Solution: Firebase Auth + Your Database (e.g., Firestore)
This architecture provides an excellent separation of concerns. Firebase handles the complex and critical task of authentication (verifying who a user is), while your application's database handles authorization (defining what a verified user is allowed to do).

Architectural Flow:

Frontend Login: A user signs into your Next.js application using the client-side Firebase SDK. This can be through various providers like Google, Facebook, or a simple email and password.

ID Token Generation: Upon a successful login, Firebase securely provides the client with a JSON Web Token (JWT), known as an ID Token.

Authenticated API Request: The Next.js client sends this ID Token in the Authorization header (as a Bearer token) with every request to your backend API routes.

Backend Token Verification: Your Next.js backend, running on Cloud Run, receives the request. It uses the firebase-admin SDK to verify the ID Token. This is a fast and secure offline process that confirms the token's authenticity and integrity.

Authorization Check: After verifying the token, the backend extracts the user's unique Firebase ID (uid). It then queries your authorization database (e.g., a users collection in Firestore) using this uid to retrieve the user's specific roles or permissions.

Access Control: Based on the permissions fetched from your database, your API logic decides whether to grant or deny access to the requested resource.

Step-by-Step Implementation Guide
1. Project Setup
Create a Firebase Project: Go to the Firebase Console and create a new project. Ensure this project is linked to your Google Cloud Project with the ID agro-extension-digital-npe.

Enable Authentication: In your new project, navigate to the Authentication section and enable the sign-in providers you want to support (e.g., Google, Email/Password).

Set up Firestore: Go to the Firestore Database section and create your database. You will be working with the database named agro-extension-db.

Create User Collections: In Firestore, you'll work with the existing data model collections:

**Primary User Collections:**

1. **`business_profiles`** - Business owners and managers
   - **Document ID**: Business RUT (e.g., `76.432.187-4`)
   - **Firebase UID Mapping**: Add `firebase_uid` field to link Firebase Auth with business profile
   ```json
   {
     "rut": "76.432.187-4",
     "firebase_uid": "firebase-user-uid-here",
     "legal_name": "Exportadora de Ciruelas Paine",
     "owner_name": "Juan Rojas",
     "owner_email": "contacto@exportadorapaine.cl",
     "owner_phone": "+56987654321",
     "role": "business_owner",
     "commune": "Paine",
     "region": "Metropolitana",
     "business_size": "Microempresa",
     "process_type": "Producción Primaria"
   }
   ```

2. **`auditors`** - Auditors who review responses
   - **Document ID**: Auditor ID (e.g., `1`, `2`)
   - **Firebase UID Mapping**: Add `firebase_uid` field
   ```json
   {
     "auditor_id": 1,
     "firebase_uid": "firebase-auditor-uid-here",
     "auditor_name": "Carlos Ruiz",
     "auditor_email": "carlos.ruiz@auditcorp.com",
     "role": "auditor",
     "assigned_businesses": ["76.432.187-4"]
   }
   ```

3. **`admin_users`** - System administrators (new collection)
   - **Document ID**: Admin ID
   - **Firebase UID Mapping**: Add `firebase_uid` field
   ```json
   {
     "admin_id": "admin-1",
     "firebase_uid": "firebase-admin-uid-here",
     "admin_name": "System Administrator",
     "admin_email": "admin@agroextension.com",
     "role": "admin",
     "permissions": ["manage_users", "manage_standards", "view_all_responses"]
   }
   ```

2. Frontend Integration (Next.js Client-Side) 🔐
You'll use the firebase client SDK to manage user state. A common and effective pattern is to use a React Context to make the auth state available throughout your app.

Install the Firebase SDK:

npm install firebase

Create an Auth Context (/context/AuthContext.js): This component will manage the user's session.

import { useEffect, useState, createContext, useContext } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from '../lib/firebase'; // Your firebase client config file

const AuthContext = createContext({ user: null, loading: true });

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

Wrap Your App (/pages/_app.js):

import { AuthProvider } from '../context/AuthContext';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}

export default MyApp;

3. Backend Verification (Next.js Server-Side on Cloud Run) 🚀
Protect your API routes and server-rendered pages using Next.js Middleware. This is where you'll verify the ID token and check user roles.

Install the Firebase Admin SDK:

npm install firebase-admin

Initialize the Admin SDK: Create a server-side utility file. You'll need your Firebase service account credentials. Best Practice: Store these credentials as a secret in Google Secret Manager and access them in your Cloud Run environment.

Create Middleware (/middleware.js): This file will intercept requests to protected routes to verify the user's token and role. Updated to work with the agricultural standards data model.

import { NextResponse } from 'next/server';
import { adminAuth } from './lib/firebase-admin'; // Your admin SDK initialization file
import { db } from './lib/firebase-admin'; // Assuming Firestore is also initialized here

export async function middleware(req) {
  const authHeader = req.headers.get('authorization');
  const idToken = authHeader?.split('Bearer ')[1];

  if (!idToken) {
    return new Response(JSON.stringify({ error: 'Unauthorized: No token provided' }), { status: 401 });
  }

  try {
    // 1. AUTHENTICATION: Verify the token
    const decodedToken = await adminAuth.verifyIdToken(idToken);
    const { uid, email } = decodedToken;

    // 2. AUTHORIZATION: Determine user role and fetch permissions
    let userRole = null;
    let userData = null;
    let userId = null;

    // Check if user is a business owner
    const businessQuery = await db.collection('business_profiles')
      .where('firebase_uid', '==', uid)
      .limit(1)
      .get();

    if (!businessQuery.empty) {
      const businessDoc = businessQuery.docs[0];
      userData = businessDoc.data();
      userRole = 'business_owner';
      userId = businessDoc.id; // This will be the business RUT
    } else {
      // Check if user is an auditor
      const auditorQuery = await db.collection('auditors')
        .where('firebase_uid', '==', uid)
        .limit(1)
        .get();

      if (!auditorQuery.empty) {
        const auditorDoc = auditorQuery.docs[0];
        userData = auditorDoc.data();
        userRole = 'auditor';
        userId = auditorDoc.id; // This will be the auditor_id
      } else {
        // Check if user is an admin
        const adminQuery = await db.collection('admin_users')
          .where('firebase_uid', '==', uid)
          .limit(1)
          .get();

        if (!adminQuery.empty) {
          const adminDoc = adminQuery.docs[0];
          userData = adminDoc.data();
          userRole = 'admin';
          userId = adminDoc.id;
        }
      }
    }

    if (!userRole) {
      return new Response(JSON.stringify({ 
        error: 'Forbidden: User not registered in system' 
      }), { status: 403 });
    }

    const requestedPath = req.nextUrl.pathname;

    // Define role-based access control for agricultural standards system
    const allowedRoles = {
      '/api/admin/': ['admin'],
      '/api/business/': ['admin', 'business_owner'],
      '/api/audit/': ['admin', 'auditor'],
      '/api/standards/': ['admin', 'business_owner', 'auditor'], // All can view standards
      '/api/responses/': ['admin', 'business_owner', 'auditor'], // Context-dependent access
      '/api/business-profiles/': ['admin'],
      '/api/reports/': ['admin', 'auditor']
    };

    const isAllowed = Object.entries(allowedRoles).some(([path, roles]) =>
      requestedPath.startsWith(path) && roles.includes(userRole)
    );

    if (!isAllowed) {
      return new Response(JSON.stringify({ 
        error: `Forbidden: Role '${userRole}' cannot access '${requestedPath}'` 
      }), { status: 403 });
    }

    // Additional authorization for specific endpoints
    if (requestedPath.startsWith('/api/responses/')) {
      // Business owners can only access their own responses
      if (userRole === 'business_owner') {
        const businessRut = userId;
        // Check if the requested response belongs to this business
        // This would be implemented in the actual API route handler
      }
      
      // Auditors can only access responses assigned to them
      if (userRole === 'auditor') {
        const auditorId = parseInt(userId);
        // Check if the auditor is assigned to the requested response
        // This would be implemented in the actual API route handler
      }
    }

    // Attach user info to the request for use in API routes
    const requestHeaders = new Headers(req.headers);
    requestHeaders.set('x-user-id', userId);
    requestHeaders.set('x-user-role', userRole);
    requestHeaders.set('x-firebase-uid', uid);
    
    // Add business-specific headers for business owners
    if (userRole === 'business_owner') {
      requestHeaders.set('x-business-rut', userId);
      requestHeaders.set('x-business-name', userData.legal_name);
    }
    
    // Add auditor-specific headers for auditors
    if (userRole === 'auditor') {
      requestHeaders.set('x-auditor-id', userId);
      requestHeaders.set('x-assigned-businesses', JSON.stringify(userData.assigned_businesses || []));
    }

    return NextResponse.next({
      request: { headers: requestHeaders },
    });

  } catch (error) {
    console.error('Error verifying auth token:', error);
    return new Response(JSON.stringify({ error: 'Unauthorized: Invalid token' }), { status: 401 });
  }
}

// Define which paths the middleware should apply to
export const config = {
  matcher: [
    '/api/admin/:path*', 
    '/api/business/:path*', 
    '/api/audit/:path*',
    '/api/standards/:path*',
    '/api/responses/:path*',
    '/api/business-profiles/:path*',
    '/api/reports/:path*'
  ],
};

Process Breakdown: Manual vs. Automated Steps
To clarify the implementation process, here’s a breakdown of which steps require manual configuration in a web console versus which can be fully automated through code and scripting.

Manual / User Interaction Steps 👨‍💻
These are typically one-time setup actions that require you to navigate a user interface and make decisions.

1. Create a Firebase Project: This is done in the Firebase Console. You need to provide a project name and configure project settings.

2. Enable Authentication Providers: Inside the Firebase Authentication dashboard, you must manually click to enable and configure each sign-in method (Google, Facebook, Email/Password, etc.). This often involves providing API keys or secrets from other platforms.

3. Set up Firestore Database: You need to go to the Firestore section of the console and click a button to create the database, choosing its initial location and security mode (e.g., production or test).

4. Configure Firestore Security Rules: While the rules themselves are code, they must be manually deployed through the Firebase Console's text editor or via the Firebase CLI. The initial setup is typically done in the console.

5. Generate Firebase Service Account Credentials: To allow your backend to act as an administrator, you must navigate to the project settings in the Firebase Console, go to the "Service Accounts" tab, and click a button to generate a new private key. This key file must then be securely stored.

6. Store Credentials in a Secret Manager: For a production Cloud Run environment, you need to go to the Google Cloud Secret Manager console, create a new secret, and manually upload or paste the Firebase service account credentials.

Automated / Scriptable Steps ⚙️
These steps are handled entirely within your Next.js codebase and are deployed automatically with your application.

1. Install Dependencies: Installing firebase and firebase-admin is a scriptable step managed by your package manager (e.g., npm install).

2. Frontend Integration (Code):

Writing the Firebase client configuration file (/lib/firebase.js).

Creating the React Auth Context (/context/AuthContext.js).

Wrapping your application in the AuthProvider (/pages/_app.js).

3. Backend Verification (Code):

Writing the Firebase Admin SDK initialization logic (/lib/firebase-admin.js), which reads the credentials from the environment.

Implementing the Next.js Middleware (/middleware.js) to verify tokens and check permissions. This is pure code.

4. Creating User Documents in Firestore (Code): While the business_profiles and auditors collections exist with business data, the process of linking Firebase Auth users to existing profiles should be automated. This is typically handled by a server-side function.

**User Registration and Linking Process:**

For **Business Owners**:
```javascript
// API endpoint: /api/auth/link-business-profile
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { businessRut, firebaseUid } = req.body;

  try {
    // Verify the Firebase user exists
    const userRecord = await adminAuth.getUser(firebaseUid);
    
    // Update the business profile with Firebase UID
    const businessRef = db.collection('business_profiles').doc(businessRut);
    const businessDoc = await businessRef.get();
    
    if (!businessDoc.exists) {
      return res.status(404).json({ error: 'Business profile not found' });
    }

    // Link Firebase UID to business profile
    await businessRef.update({
      firebase_uid: firebaseUid,
      auth_setup_date: new Date().toISOString(),
      owner_email: userRecord.email // Sync email from Firebase Auth
    });

    res.status(200).json({ 
      message: 'Business profile linked successfully',
      businessRut,
      role: 'business_owner'
    });
  } catch (error) {
    console.error('Error linking business profile:', error);
    res.status(500).json({ error: 'Failed to link business profile' });
  }
}
```

For **Auditors**:
```javascript
// API endpoint: /api/auth/link-auditor-profile
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { auditorId, firebaseUid } = req.body;

  try {
    // Verify the Firebase user exists
    const userRecord = await adminAuth.getUser(firebaseUid);
    
    // Update the auditor profile with Firebase UID
    const auditorRef = db.collection('auditors').doc(auditorId.toString());
    const auditorDoc = await auditorRef.get();
    
    if (!auditorDoc.exists) {
      return res.status(404).json({ error: 'Auditor profile not found' });
    }

    // Link Firebase UID to auditor profile
    await auditorRef.update({
      firebase_uid: firebaseUid,
      auth_setup_date: new Date().toISOString(),
      auditor_email: userRecord.email // Sync email from Firebase Auth
    });

    res.status(200).json({ 
      message: 'Auditor profile linked successfully',
      auditorId,
      role: 'auditor'
    });
  } catch (error) {
    console.error('Error linking auditor profile:', error);
    res.status(500).json({ error: 'Failed to link auditor profile' });
  }
}
```

**Frontend Registration Flow:**
```javascript
// components/RegistrationForm.jsx
import { useState } from 'react';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../lib/firebase';

export function BusinessRegistrationForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    businessRut: '',
    registrationType: 'business' // or 'auditor'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // 1. Create Firebase Auth user
      const userCredential = await createUserWithEmailAndPassword(
        auth, 
        formData.email, 
        formData.password
      );
      
      const firebaseUid = userCredential.user.uid;

      // 2. Link to existing business/auditor profile
      const linkEndpoint = formData.registrationType === 'business' 
        ? '/api/auth/link-business-profile'
        : '/api/auth/link-auditor-profile';

      const linkPayload = formData.registrationType === 'business'
        ? { businessRut: formData.businessRut, firebaseUid }
        : { auditorId: formData.auditorId, firebaseUid };

      const response = await fetch(linkEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(linkPayload)
      });

      if (response.ok) {
        // Registration successful, redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        const error = await response.json();
        alert(`Registration failed: ${error.error}`);
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
        required
      />
      
      <select 
        value={formData.registrationType}
        onChange={(e) => setFormData({...formData, registrationType: e.target.value})}
      >
        <option value="business">Business Owner</option>
        <option value="auditor">Auditor</option>
      </select>

      {formData.registrationType === 'business' && (
        <input
          type="text"
          placeholder="Business RUT (e.g., 76.432.187-4)"
          value={formData.businessRut}
          onChange={(e) => setFormData({...formData, businessRut: e.target.value})}
          required
        />
      )}

      {formData.registrationType === 'auditor' && (
        <input
          type="number"
          placeholder="Auditor ID"
          value={formData.auditorId}
          onChange={(e) => setFormData({...formData, auditorId: e.target.value})}
          required
        />
      )}

      <button type="submit">Register</button>
    </form>
  );
}
```

5. Deployment: The entire Next.js application, including all the automated code, is deployed to Cloud Run via a script or command-line instruction. For your project, the command would be:

gcloud run deploy --project agro-extension-digital-npe
