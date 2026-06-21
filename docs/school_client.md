# school_client — Documentation technique

## 1. Vue d'ensemble

`school_client` est l'application desktop Lekol360 utilisée dans les établissements scolaires pour piloter le quotidien de l'école : inscriptions, paiements, notes, présences, badges, rapports. Elle communique avec le backend `ecole_nginx` via API REST et accède aussi directement à la base MySQL distante via SSL. Historiquement Windows uniquement ; rendue fonctionnelle sur Mac/Linux également (voir section 8).

## 2. Stack technique

| Domaine | Technologie |
|---|---|
| GUI | PySide6 (Qt6) — UI générée depuis des fichiers `.ui` (Qt Designer) |
| Réseau | `requests`, `QNetworkAccessManager` (appels asynchrones avec signaux Qt) |
| Base de données | PyMySQL (connexion directe MySQL distante via SSL), asyncmy en option |
| Documents | WeasyPrint (vendored), Jinja2 (templates HTML→PDF), pdfkit |
| Vision/Badges | OpenCV, MediaPipe (détection de visage), pyzbar (QR codes) |
| Sécurité | `cryptography` (Fernet pour le token JWT stocké localement), bcrypt |
| Graphiques | matplotlib (intégré aux vues Qt) |
| Packaging | Nuitka (build standalone onefile), PyInstaller (alternative) |

## 3. Architecture (pattern MVC)

```
school_client/
├── app.py                 # Entrée app, verrou anti double-instance (QLocalServer)
├── Config.py               # Config API (URL de base, headers)
├── Controllers/Main.py      # Contrôleur principal (~14k lignes) — toute la logique UI/métier
├── Controllers/Validator.py # Validation des formulaires
├── Controllers/Camera/      # Worker caméra (QThread)
├── Views/main_view.py       # UI générée Qt Designer (~12k lignes)
├── Models/
│   ├── db.py                  # Connexion MySQL thread-safe (SSL)
│   ├── ApiHandler.py           # Requêtes HTTP synchrones
│   ├── AsyncDataHandler.py     # Requêtes HTTP asynchrones (signaux Qt)
│   ├── AsyncDataHandlerPdf.py  # Téléchargement binaire (PDF/Excel)
│   ├── fetch_data.py            # Lecture de données (GET)
│   └── enregistrement.py        # Écriture de données (POST/PUT/PATCH, ~28k lignes)
├── Helper/
│   ├── Token_manager.py         # Stockage chiffré (Fernet) du token JWT dans QSettings
│   ├── Ip_manager.py             # Configuration IP/domaine serveur
│   ├── AuthorizationHelper.py    # Vérification permissions (requête SQL locale)
│   ├── AdminAuthorization.py     # Double-authentification pour actions sensibles
│   ├── Sync_data.py / Sync_to_api.py  # Prototype de cache offline (non finalisé)
│   ├── Components/               # Dialogues métier (paiements, frais, classes, années, examens, facultés)
│   └── HandlerHerror/             # Extraction des messages d'erreur API
├── Badge/Badge.py            # Éditeur de badge (recto/verso, détection visage IA, export PDF)
├── Resources/*.ui             # Fichiers Qt Designer
├── templates/*.html           # Templates Jinja2 pour reçus/rapports PDF
├── WeasyPrint/, weasy_runtime/ # WeasyPrint vendored + runtime (évite dépendance système)
└── build/, *.spec              # Sorties et configs de packaging (Nuitka/PyInstaller)
```

Flux de données type :
```
Action utilisateur → Controllers/Main.py → AsyncDataHandler (signal) → API distante (HTTPS)
                                                        ↓ réponse JSON/PDF
                                          Main.py (slots succès/erreur) → mise à jour de la vue
```

> Dossiers `Controllers copy/`, `Helper copy/`, `templates - Copy/`, `cont/*copy*.py` : anciennes versions/brouillons, à ne pas utiliser comme référence.

## 4. Fonctionnalités principales

- **Étudiants** : CRUD, recherche live, changement de classe, statut.
- **Classes & niveaux** : création/édition, association aux facultés, listes d'appel.
- **Paiements** : configuration des tarifs par classe/niveau (montants, échéances, accessoires), saisie des paiements, génération de reçu PDF, suivi des montants dus.
- **Frais** : frais d'inscription et frais divers configurables.
- **Notes & examens** : configuration des examens, saisie des notes, génération de bulletins.
- **Programmes/facultés** : gestion des sections et de l'affectation cours/profs/classes.
- **Personnel** : gestion des professeurs et du personnel administratif, logs d'audit.
- **Badges** : éditeur complet (import image ou capture caméra, détection automatique du visage par IA, recadrage, rotation, undo/redo, export PNG/PDF par lot).
- **Documents/rapports** : reçus de paiement et de vente, attestations d'inscription, rapports pédagogiques et financiers, export Excel — rendus via templates Jinja2 + WeasyPrint.
- **Prêts (loans)** : consultation des données étudiants pour prêts, suivi de remboursement.
- **Tableau de bord** : graphiques matplotlib (paiements, inscriptions), cartes de synthèse.
- **Configuration serveur** : choix IP/domaine, gestion des certificats SSL client.
- **Abonnement** (admin uniquement, ajout récent) : onglet construit entièrement à l'exécution dans `Controllers/Main.py` (jamais dans `Views/main_view.py`, généré par Qt Designer et écrasé à chaque recompilation) — statut courant + cartes d'historique (date d'activation, d'expiration, statut Actif/Expiré calculé localement), alimenté par `GET v1/abonnement`. Bouton **Renouveler** affiché automatiquement quand il reste ≤15 jours, qui ouvre le site `infini-software` (`docs/infini-software.md`) avec le **mac du serveur** (renvoyé par cette même route, pas celui du poste client qui a ouvert l'onglet — un même serveur peut avoir plusieurs postes clients autorisés, voir `ClientInfo`).

## 5. Authentification & autorisation côté client

1. Login email/mot de passe → API retourne token + rôles/permissions.
2. Token chiffré (Fernet, clé dans `QSettings`) et stocké localement (`auth-token`).
3. Chaque requête API ajoute `Authorization: Bearer <token>` ; un 401 déclenche déconnexion + retour à l'écran de login.
4. Vérification des permissions via requête SQL locale (jointure `permissions` / `role_has_permissions` / `model_has_roles` / `model_has_permissions`).
5. Actions sensibles : popup de double-authentification admin (`AdminAuthorization`), avec header `X-Authorization-Required` / `X-Approval-Token`.
6. Connexion MySQL via certificats SSL stockés dans `%APPDATA%/.ecole_360/.certs/` sous Windows (comportement inchangé), ou l'équivalent cross-platform (`~/Library/Application Support/.ecole_360/.certs` sur Mac, `~/.local/share/.ecole_360/.certs` sur Linux — voir `get_local_data_dir()` dans `utils/imports.py`) ; utilisateur `user_pyside` avec certs, sinon `ssl_reader` générique.

## 6. Stockage local

- Pas d'ORM : requêtes SQL brutes via PyMySQL vers la base distante.
- `QSettings` (registre Windows) pour token chiffré, IP serveur, type d'adresse, clé de chiffrement.
- Cache offline SQLite (`Sync_data.py`) : prototype non finalisé, l'app fonctionne en mode direct-API.
- Fichiers locaux : certificats SSL, `badge_config.json`, cache temporaire des images de badge.

## 7. Packaging & distribution

- Build standalone via **Nuitka** (`--standalone --onefile --enable-plugin=pyside6`) générant `app.exe`.
- Alternative **PyInstaller** (`app.spec`).
- Installateur Windows (Inno Setup) avec lanceur dédié (`Lekol360_Launcher.exe`) + `app.exe`.
- Verrou anti double-instance via `QLocalServer`.
- Logs de crash : `nuitka-crash-report.xml`, `faulthandler.log`.

## 8. Support Mac/Linux (ajout récent)

Correctifs apportés pour que `app.py` tourne sur Mac/Linux en plus de Windows, sans changer le comportement Windows :

- **Imports Windows-only morts supprimés** : `import win32api`/`import win32print` en tête de `Controllers/Main.py` plantaient le chargement du module entier sur Mac/Linux (ils n'étaient utilisés que dans du code commenté).
- **Chemins `%APPDATA%`/`%LOCALAPPDATA%`** : nouveaux helpers cross-platform `get_user_data_dir()`/`get_local_data_dir()` dans `utils/imports.py` ; comportement Windows strictement inchangé.
- **Élévation admin** (`ctypes.windll`) : gardée derrière `if sys.platform == "win32":` dans `run_as_admin()` (`Controllers/Main.py`), affiche un message au lieu de planter sur Mac/Linux.
- **`requirements.txt`** : `pywin32`, `pypiwin32`, `pywin32-ctypes`, `pefile`, `win32_setctime` marqués `; sys_platform == "win32"` pour ne plus faire échouer `pip install` sur Mac/Linux.
- **Confiance SSL** : `requests`/`certifi` ne consulte pas le magasin de confiance système (Keychain Mac, ca-certificates Linux). Ajout de `truststore.inject_into_ssl()` au démarrage de `app.py` (hors Windows uniquement) pour que la CA locale installée côté serveur (`scripts/setup-local-https.sh`) soit reconnue.
- **Préfixe d'API manquant (`/v1`)** : `Config.py`, `Models/ApiHandler.py`, `Models/enregistrement.py`, `Models/fetch_data.py`, `Helper/Check_data.py` construisaient une URL de base `.../api/` alors que toutes les routes du serveur sont sous `/api/v1/...` — bug réel indépendant de la plateforme (confirmé : le serveur retourne 404 sur toute requête sans `/v1`). `Models/AsyncDataHandler.py` n'était pas concerné (le préfixe `v1/` est déjà inclus dans chacun de ses appels `_send_request("v1/...")`).
- **`request_certificate_ss()`** (`Controllers/Main.py`) : appelait `/asking` en `POST` avec un corps JSON alors que la route serveur est en `GET` avec `mac_address` en paramètre de requête (confirmé par test direct : POST → 405, GET → réponse attendue).
- **`get_mac_address()`** : tentait `getmac` (binaire Windows uniquement) avant de retomber sur `uuid.getnode()` — fonctionnait déjà via le fallback, mais bruyait la console sur Mac/Linux ; ignore désormais directement `getmac` hors Windows.

## 9. Abonnement & renouvellement (ajout récent)

- Nouvel onglet **Abonnement** (admin uniquement), construit dynamiquement dans `Controllers/Main.py` (`_setup_abonnement_page`, `show_data_in_abonnement`) pour ne jamais toucher au fichier généré par Qt Designer.
- **Piège identifié et corrigé** : le bouton Renouveler utilisait initialement `self.get_mac_address()` — le mac du **poste client** qui a ouvert l'onglet, pas celui du serveur. Comme un même serveur peut avoir plusieurs postes autorisés (`ClientInfo`/"Postes clients"), c'était le mauvais identifiant pour le site de paiement. Corrigé : le mac est désormais lu depuis la réponse de `GET v1/abonnement` (`self.abonnement_data['mac']`, renvoyé par le serveur via `get_host_mac()`), jamais détecté localement.
- Le lien ouvert (`QDesktopServices.openUrl`) pointe **temporairement** vers le site `infini-software` en local (`http://localhost:5180/`, port Vite fixé) pour les tests de bout en bout — à remettre vers `https://www.infini-software.cloud` avant mise en production.
