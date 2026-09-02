# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Vue 3 + Vite frontend for **IUSTH** (Institut Universitaire des Sciences et des Technologies d'Haïti). It is the public marketing/admission site plus three authenticated portals (Admin, Teacher/Professeur, Student/Étudiant), all served from one SPA. It talks to the FastAPI backend in the sibling `../app` directory (see `../PRD.md` for the overall system spec — that PRD describes the general école-management product and does not know about this university-specific portal).

## Commands

```sh
npm run dev              # start dev server (vite)
npm run build             # production build
npm run preview           # preview a production build

npm run test:unit         # vitest (jsdom) — single file: npx vitest run src/path/to/file.spec.js
npm run test:e2e          # playwright e2e — first run: npx playwright install
npm run test:e2e -- --project=chromium
npm run test:e2e -- tests/example.spec.js

npm run lint              # runs lint:oxlint then lint:eslint (both --fix)
```

## Architecture

### Four portals, one router

`src/router/index.js` mounts four top-level layouts, each its own subtree:

- `PublicLayout.vue` (`/`) — marketing site: Accueil, Formations, Admission, Événements, À Propos, Contact. No auth.
- `AdminLayout.vue` (`/admin/...`) — role-gated via `meta.role` (admin, Caissier, Responsable financier, Responsable des admissions, Responsable pédagogique, Comptable...).
- `TeacherLayout.vue` (`/professeur-...`) — `meta: { requiresAuth: true, role: 'teacher' }`.
- `StudentLayout.vue` (`/student/...`) — `meta: { requiresAuth: true, role: 'student' }`.

The nav guard at the bottom of `router/index.js` checks `to.meta.requiresAuth` / `to.meta.role` against `useAuthStore()`, and force-redirects to `first.connexion` if `password_changed_at` is empty (first-login password change flow).

### API calls: plain axios, not the `services/` files

`src/main.js` sets `axios.defaults.baseURL = import.meta.env.VITE_APP_BASE_URL` and attaches `Authorization: Bearer <token>` globally from `localStorage.getItem('auth-token')`. Almost every view does `import axios from 'axios'` and calls relative paths (`axios.get('/mes-classes-etudiants')`) directly against that global config.

`src/services/api.js` and `src/services/appi.js` exist but are **not** the real convention — `api.js` has a hardcoded LAN URL and `appi.js` has a stale CORS comment block; only `stores/auth.js` imports one of them. Don't route new code through either file — follow the plain-`axios` pattern used everywhere else.

Backend routes live under `/api/v1/...` in FastAPI, but `VITE_APP_BASE_URL` (e.g. `https://edu.infini-software.cloud/ecole360`) is proxied so the frontend calls paths **without** the `/api/v1` prefix (e.g. `/mes-classes-etudiants`, not `/api/v1/mes-classes-etudiants`) — the reverse proxy strips/rewrites it server-side.

### CMS-editable public sections

Public pages (Home, À Propos, Formations, Contact, Événements) mix hand-coded sections with admin-editable blocks rendered by `GenericSection.vue`, driven by `composables/usePageSections.js` (CRUD against `PageSection`, see `../app/Routes/RPageSections.py`). `PAGE_ZONES` in that composable maps an `ordre` integer to a named insertion point per page (`genericSectionsInZone(N)` in each view) — to add a new droppable zone, add an entry there and drop a `<GenericSection v-for="gs in genericSectionsInZone(N)" ...>` at the matching spot in the template. The six original homepage sections (stats/cycles/features/activities/testimonials/values) predate this system and keep their own bespoke markup instead of going through `GenericSection`.

Admin-only edit affordances (buttons to add/reorder/hide a section) are gated by `authStore.isAdmin` and rendered inline in the public views themselves — there's no separate admin CMS page.

### `*copy*` / ` - Copy` files are dead drafts — ignore them

A large fraction of `src/views/` (Teacher, Student, admin, public) has duplicate files suffixed `copy`, `copy 2`, `copy 6`, etc., or living in sibling directories like `views/Teacher - Copy/`, `views/admin copy/`, `views/public - Copy/`. **None of these are imported by the router.** They're abandoned iterations. When searching for "where is X rendered", always check `router/index.js` first to confirm which file is actually live, and exclude `*copy*` from greps — otherwise you'll edit a file nobody sees.

### Role dashboards were largely static mockups

The Teacher/Student/Admin dashboard-style views (stat cards, "classes" lists, calendars, tables) were originally built as static UI mockups with hardcoded fixture data and only partially wired to the backend. Several have since been connected to real endpoints, but before trusting any number/list on a dashboard view, check whether it's actually bound to a fetched ref or still a literal array in `<script setup>` — this codebase has a documented history of both patterns coexisting in the same file.

### Styling

Tailwind CSS 4 (`@tailwindcss/vite` plugin, no separate `tailwind.config.js` build step beyond the one present). The public/marketing pages use a light theme with a gold/navy palette (`text-gold`, `.gold-line`, `#0B1F3A` navy, `#1A7A6E` teal accents, `font-serif` for headings) and a `.reveal` scroll-in-animation class (see `composables/useReveal.js`). The Teacher/Student portals use a separate dark theme (`#0b0f14`/`#171b26` panels, `#c9a84c` gold). Match whichever palette the file you're editing already uses — they are not unified.

### Auth store

`stores/auth.js` (Pinia) holds `user` (nested as `user.user.*` from the API response shape) and role flags (`isAdmin`, `isTeacher`, etc. via `storeToRefs`). Login token key in localStorage is `auth-token` (not `token` — an older `token` key shows up in `services/api.js`'s dead interceptor, don't follow it).
