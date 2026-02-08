# Frontend Implementation Knowledge Base

## Overview
This document serves as the central knowledge source for the Dental Practice Management Frontend. It synthesizes the implementation strategy, architectural decisions, and current state of the codebase, ensuring continuity for future development.

## 🏗 Architecture & Strategy

### Core Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (Strict Mode)
- **Styling**: Vanilla CSS Modules with CSS Variables (Design Tokens) to ensure a premium, lightweight, and maintainable design system without framework lock-in.
- **State Management**: 
  - **Server State**: `SWR` hooks (e.g., `useSchedule`, `usePatients`) for reactive data fetching and caching.
  - **App State**: React Context (`AuthContext`) for global session management.

### Key Architectural Decisions
1.  **3-Panel Layout**: The app enforces a strict "IconRail | ListPanel | DetailPanel" layout optimized for iPad landscape use. This is implemented via reusable layout components in `src/components/layout/`.
2.  **Authentication**: 
    - Managed via `AuthContext.tsx`.
    - JWTs are stored in memory for security, avoiding `localStorage` vulnerabilities.
    - Session persistence is handled via a lightweight initialization check on app load.
3.  **Type Safety**: 
    - All API interactions are typed via `src/types/api.ts`, strictly mirroring the backend's Pydantic schemas.
    - We use a custom `client.ts` fetch wrapper to enforce these types and handle auth headers automatically.

## 💻 Local Development & Learnings

### Getting Started
```bash
cd frontend
npm run dev
```
The application runs on `http://localhost:3000`.

### Backend Connection
- **Configuration**: The app uses `process.env.NEXT_PUBLIC_API_URL`.
- **Default**: Pre-configured to connect to the live GCP backend (`https://dental-backend-963321342744.us-central1.run.app/api/v1`). 
- **Local Backend**: To switch to a local backend, create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.

### Critical Learnings & Gotchas
- **Schema Validation**: The backend is strict. We discovered that the `Patient` schema does **not** include a `gender` field, contrary to initial mockups. Attempting to access it will cause type errors in the build.
- **Build Strictness**: The `npm run build` process runs strict TypeScript checks. Ensure all `params` used queries are properly cast (e.g., `as Record<string, unknown>`) when using the `buildQueryString` utility, as generic types can sometimes be inferred too broadly as `any` or `never`.
- **Port Conflicts**: Ensure port 3000 is free or Next.js will fail to start.

## 🧩 Implementation Status

### ✅ Completed Flows
- **Authentication**: Login and Registration pages (`src/app/(auth)/`).
- **Schedule**: View daily appointments, navigate dates, view patient details (`src/app/(main)/schedule`).
- **Patient Management**: Search patients by last name, view patient cards (`src/app/(main)/patients`).
- **Charting**: A modal-based charting interface (`src/app/(main)/charting/[visitId]`) allowing clinical note entry with "Note Types" and "Quick Phrases".

### 🚧 Known Gaps & Next Steps
These features were deferred or identified as next steps:

1.  **Tasks View**: The navigation icon exists, but the view is a placeholder. Needs integration with `useTasks` hook.
2.  **Edit Capabilities**: Patient profile and Visit details are currently "Read Only". The "Edit" buttons are visual placeholders.
3.  **Billing**: Fully supported by `client.ts` but no UI exists yet.
4.  **Notifications**: Explicitly deferred for MVP.
5.  **Offline Support**: No Service Worker implementation yet.

## 📂 Key File Map
- `src/lib/api/`: Typed API modules (source of truth for backend interaction).
- `src/components/ui/`: Atomic design elements (Button, Input, Modal).
- `src/app/globals.css`: Design tokens (Colors, Typography, Spacing).
