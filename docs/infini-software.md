# infini-software — Documentation technique

## 1. Vue d'ensemble

`infini-software` est le site externe (hors du dépôt scolaire `lekol360`/`ecole_nginx`) qui porte trois rôles : vitrine commerciale, réception de la télémétrie d'installation (premier compte admin créé par une installation `ecole_nginx`), et gestion des licences/abonnements (génération de clé, paiement, suspension). Avant ce projet, seul un script `backend/genere_key.py` existait (génération de clé en CLI, jamais branché à rien) ; le reste (backend FastAPI complet, page de renouvellement, configuration tarifaire) a été construit en cours de projet.

## 2. Stack technique

| Domaine | Technologie |
|---|---|
| Frontend actif | Vue 3 (Composition API, `<script setup>`) + Vue Router 4 + Vite 6 + Tailwind CSS 3 |
| Backend | FastAPI + SQLAlchemy 2.0 + SQLite (fichier `backend/infini.db`) |
| Auth admin | bcrypt (hash) + PyJWT (token, 12h) |
| Appels HTTP backend→fournisseurs | httpx (async) |
| Appels HTTP frontend→backend | `fetch` natif (pas d'axios — aucune dépendance HTTP n'existait déjà dans ce projet) |

> Le dépôt contient aussi `js/Pages`, `views/app.blade.php`, `css/app.css`, `dist/` : restes d'un ancien scaffold Laravel/Jetstream+Inertia, **non utilisés** par le site actif (`package.json` ne liste que Vue/Vite, aucune dépendance PHP/Laravel). Le site réellement servi est `src/` (voir `README.md`). Candidats à suppression lors d'un futur nettoyage.

## 3. Architecture

```
infini-software/
├── src/                        # Site Vue actif
│   ├── views/
│   │   ├── HomeView.vue, StoreView.vue, AboutView.vue, ContactView.vue, ...
│   │   ├── AdminView.vue        # Login + dashboard clients + config tarifaire
│   │   └── RenouvellerView.vue  # Page de paiement/renouvellement (public)
│   ├── router/index.js          # /, /store, /admin, /renouveler, ...
│   └── stores/                  # Pinia (apps, demo) — sans rapport avec l'auth admin
├── vite.config.js               # server.port: 5180, strictPort: true (voir section 6)
└── backend/
    ├── app/
    │   ├── main.py               # FastAPI app, CORS *, monte install/licence/admin
    │   ├── database.py          # SQLite (infini.db)
    │   ├── models.py             # Client, LicenceKey, Payment, AdminUser, PricingConfig
    │   ├── schemas.py            # Pydantic
    │   ├── security.py / deps.py # bcrypt + JWT, dépendance get_current_admin
    │   ├── pricing.py            # get_or_create_pricing_config, calculer_montant
    │   ├── payments/             # base.py (interface + factory), moncash.py, natcash.py, stripe_provider.py
    │   └── routes/
    │       ├── install.py        # POST /api/save-data
    │       ├── licence.py        # /tarif, /verifier-mac, /payer, /payer/confirmer
    │       └── admin.py          # /login, /clients, /config
    ├── genere_key.py             # Génération de clé HMAC-SHA256 + base32 (corrigé, voir section 5)
    ├── create_admin.py           # CLI bootstrap du premier compte admin
    ├── seed_test_data.py         # Seed de test (mirroring log_actives de lekol360)
    └── requirements.txt, .env.example, .gitignore
```

## 4. Modèle de données (`backend/app/models.py`)

- **`Client`** : une installation `ecole_nginx` enregistrée, clé naturelle = `mac` (unique). `nom`/`prenom`/`email` reçus au premier compte admin. `suspended` (bool, géré par l'admin infini-software).
- **`LicenceKey`** : historique des clés générées pour un client (`key`, `expiration_date`, `days_valid`, `payment_id` optionnel).
- **`Payment`** : `provider` (`moncash`/`natcash`/`stripe`), `amount`/`currency` calculés serveur (jamais fournis par l'appelant), `status` (`pending`/`success`/`failed`), `days_valid` (persisté au moment du paiement, plus de défaut séparé à la confirmation).
- **`AdminUser`** : compte du staff infini-software (pas le client/école).
- **`PricingConfig`** : une seule ligne (créée à la demande), `monthly_price` + `currency` (devise de base, ex. USD) + `exchange_rate_usd_htg` (taux du jour, saisi manuellement par l'admin).

## 5. Flux fonctionnels

### 5.1 Enregistrement à l'installation
`POST /api/save-data` (appelé par `ecole_nginx/gui/first_account.py` et `scripts/create-first-admin.sh` lors de la création du premier compte admin) — upsert d'un `Client` par `mac`.

### 5.2 Génération de clé (`genere_key.py`)
HMAC-SHA256(`KEY_SECRET`, mac+date_expiration+jours+secret) → base32 → 16 caractères formatés en groupes de 4. **Bug corrigé** : le script CLI (`if __name__ == "__main__"`) inversait les variables retournées (`expiration_date, key, days_valid = generate_activation_key(...)` alors que la fonction renvoie `(key, expiration_date, days_valid)`) — la clé et la date affichées étaient échangées. `SECRET_KEY` lit désormais `KEY_SECRET` depuis l'environnement (défaut conservé pour compatibilité).

### 5.3 Renouvellement (`RenouvellerView.vue` + `/api/licence/*`)
1. **Identification du client** — deux chemins :
   - **Lien de confiance** : `school_client` ouvre `/renouveler?mac=...` avec le mac du **serveur** (lu depuis `GET v1/abonnement` côté `ecole_nginx`, jamais détecté localement sur le poste client — un même serveur a plusieurs postes autorisés). Le champ mac est alors verrouillé (lecture seule).
   - **Accès direct** (ex. admin sur son téléphone, sans passer par `school_client`) : champ mac éditable, avec un bouton « Vérifier » et une indication pour aller lire l'adresse MAC dans Lekol360 → Gestion du serveur → Licence.
   - Dans les deux cas, `GET /api/licence/verifier-mac?mac=...` (public, sans authentification, ne renvoie que `{exists, suspended}` — aucune donnée personnelle) valide le mac avant d'afficher le formulaire de paiement.
2. **Calcul du prix** — `GET /api/licence/tarif` (public) renvoie la config courante pour l'aperçu. Le prix réel est toujours recalculé côté serveur dans `POST /api/licence/payer` à partir de `months` et du fournisseur choisi : carte (Stripe) → reste dans la devise de base ; tout autre fournisseur (MonCash, NatCash) → converti en HTG au taux du jour. `days_valid = months * 30`.
3. **Paiement** — `POST /api/licence/payer` crée un `Payment` (`pending`), appelle `provider.create_payment(...)`, renvoie une `redirect_url` si applicable.
4. **Confirmation** — pas de webhook : l'utilisateur clique « J'ai terminé le paiement » → `GET /api/licence/payer/confirmer?payment_id=...` → `provider.verify_payment(...)` → si vrai, génère une nouvelle clé (`genere_key.generate_activation_key`) et crée le `LicenceKey`.

### 5.4 Administration (`AdminView.vue`, admin-only)
Login email/mot de passe (bcrypt + JWT 12h) → liste des clients, historique par client (clés + paiements), boutons Activer/Suspendre, formulaire de configuration tarifaire (prix mensuel, devise, taux de change).

## 6. Fournisseurs de paiement (`backend/app/payments/`)

- **MonCash** (`moncash.py`) : implémenté d'après le flux REST documenté publiquement par Digicel (OAuth2 client_credentials → `CreatePayment` → redirection → `RetrieveTransactionPayment`). **Non vérifié avec de vrais identifiants marchand** — `MONCASH_CLIENT_ID`/`MONCASH_CLIENT_SECRET` sont vides dans `.env.example`. À valider contre la documentation officielle à jour avant mise en production.
- **NatCash** (`natcash.py`) : `NotImplementedError` volontaire — aucune référence fiable de l'API marchand disponible ; nécessite la documentation officielle ou un accès au portail développeur NatCash.
- **Stripe** (`stripe_provider.py`) : `NotImplementedError` volontaire, explicitement mis en attente (demande utilisateur).

## 7. Configuration & ports

- `vite.config.js` : `server.port: 5180, strictPort: true` — port fixé après un incident où le port par défaut (5173) était déjà pris par un autre projet, et un `pkill` trop large a accidentellement tué le mauvais process.
- `backend/.env` (copié depuis `.env.example`, jamais commité) : `JWT_SECRET`, `KEY_SECRET`, identifiants MonCash/NatCash/Stripe.
- `create_admin.py` : seul moyen de créer/réinitialiser un compte admin (pas de route HTTP d'auto-inscription, volontairement).
- `seed_test_data.py` : reproduit l'historique réel de `log_actives` (lekol360) dans `infini.db` pour un mac de test, plus une entrée volontairement expirée — usage développement uniquement, à ne jamais lancer contre une base de production.

## 8. Lien avec `ecole_nginx` / `school_client`

Le mac est l'identifiant pivot entre les trois projets : `ecole_nginx` l'enregistre (`/api/save-data` au premier compte admin) et l'expose (`/api/v1/abonnement`), `school_client` le relaie sans le détecter localement, `infini-software` le vérifie avant tout paiement (`/api/licence/verifier-mac`) et l'utilise pour générer la clé. Le bouton Renouveler de `school_client` pointe actuellement sur l'instance locale (`http://localhost:5180/`) pour les tests de bout en bout — à reconfigurer vers `https://www.infini-software.cloud` avant mise en production.
