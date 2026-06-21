# Infini Software — Site Web

## Installation

```bash
npm install
npm run dev
```

## Structure du projet

```
src/
├── main.js                 # Point d'entrée
├── App.vue                 # Layout principal + transitions
├── router/
│   └── index.js            # Toutes les routes Vue Router
├── views/
│   ├── HomeView.vue        # Page d'accueil
│   ├── StoreView.vue       # Store / Applications
│   ├── AboutView.vue       # À propos de nous
│   ├── ContactView.vue     # Contact
│   ├── PrivacyView.vue     # Politique de confidentialité
│   ├── TermsView.vue       # Conditions générales
│   └── AdminView.vue       # Admin (placeholder)
├── components/
│   ├── AppNavbar.vue       # Barre de navigation
│   ├── AppFooter.vue       # Pied de page
│   └── DemoModal.vue       # Modal demande de démo
├── composables/
│   └── useReveal.js        # Animation scroll reveal
├── stores/
│   ├── apps.js             # Données des applications
│   └── demo.js             # État du modal démo
└── assets/
    └── main.css            # Tailwind + composants CSS
```

## Technologies

- **Vue 3** + Composition API
- **Vue Router 4** — navigation avec transitions slide-up
- **Tailwind CSS 3** — styling utility-first
- **Vite 5** — bundler ultra-rapide
