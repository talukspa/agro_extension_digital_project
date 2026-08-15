This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Authentication & Route Protection

This app has **no server-side auth middleware** and no API routes. Authentication is
handled entirely on the client via Firebase Auth (tokens live in IndexedDB, not cookies).

Route protection is enforced in two layers:

- **Client-side:** the `ProtectedRoute` component (`src/components/ProtectedRoute.tsx`)
  guards every protected page. It redirects unauthenticated users to `/login`, unapproved
  users to `/pending-approval`, and users lacking the required role to `/unauthorized`.
- **Server-side (source of truth):** Firestore and Firebase Storage security rules
  (defined outside this repo). Client-side guards are UX only and must never be trusted
  for authorization.

There is intentionally **no `src/middleware.ts`**. A previous cookie-based (`auth-token`)
middleware gate was removed because Firebase never sets that cookie, so the gate either
redirect-looped or protected nothing. Do not reintroduce it without a real server-side
token verification (e.g. Firebase Admin in an API route or edge function).

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
