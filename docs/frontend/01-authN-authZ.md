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

Create a users Collection: In Firestore, create a collection named users. Each document in this collection will have an ID that matches a user's Firebase uid. Inside each document, you can store custom authorization fields for your different user types:

{
  "role": "business_owner",
  "displayName": "John Doe",
  "companyId": "company-123"
}

Another user might have "role": "auditor" or "role": "admin".

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

Create Middleware (/middleware.js): This file will intercept requests to protected routes to verify the user's token and role.

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
    const { uid } = decodedToken;

    // 2. AUTHORIZATION: Fetch user permissions from Firestore
    const userDoc = await db.collection('users').doc(uid).get();
    if (!userDoc.exists) {
       return new Response(JSON.stringify({ error: 'Forbidden: User not found' }), { status: 403 });
    }

    const userRole = userDoc.data().role;
    const requestedPath = req.nextUrl.pathname;

    // Define which roles can access which paths
    const allowedRoles = {
        '/api/admin/': ['admin'],
        '/api/business/': ['admin', 'business_owner'],
        '/api/audit/': ['admin', 'auditor']
    };

    const isAllowed = Object.entries(allowedRoles).some(([path, roles]) =>
        requestedPath.startsWith(path) && roles.includes(userRole)
    );

    if (!isAllowed) {
        return new Response(JSON.stringify({ error: 'Forbidden: Insufficient permissions for this role' }), { status: 403 });
    }

    // Attach user info to the request for use in API routes
    const requestHeaders = new Headers(req.headers);
    requestHeaders.set('x-user-id', uid);
    requestHeaders.set('x-user-role', userRole);

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
  matcher: ['/api/admin/:path*', '/api/business/:path*', '/api/audit/:path*'],
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

4. Creating User Documents in Firestore (Code): While the users collection is set up manually, the process of adding a new user document to Firestore when a user signs up for the first time should be automated. This is typically handled by a server-side function (e.g., a Cloud Function triggered on user creation or an API endpoint in your Next.js app).

5. Deployment: The entire Next.js application, including all the automated code, is deployed to Cloud Run via a script or command-line instruction. For your project, the command would be:

gcloud run deploy --project agro-extension-digital-npe
