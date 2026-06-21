# PRD — ecole_nginx (API Lekol360)

## 1. Contexte et problème

Les établissements scolaires gèrent manuellement ou via des outils disparates : inscriptions, paiements d'écolage, notes, présences, personnel et communication. **Lekol360** centralise ces processus dans une plateforme unique. `ecole_nginx` est le moteur backend qui porte toute la logique métier et les données, consommé par le client desktop (`school_client`) installé dans les établissements.

## 2. Objectifs produit

1. Fournir une source de vérité unique pour les données académiques, financières et RH d'un établissement.
2. Sécuriser l'accès aux données selon des rôles et permissions granulaires.
3. Automatiser la génération de documents officiels (bulletins, reçus, attestations, rapports).
4. Permettre le contrôle des licences d'utilisation par établissement/poste (clé d'activation liée à l'adresse MAC).
5. Offrir un canal de contenu éditorial (actualités, événements, formations) consultable publiquement.

## 3. Utilisateurs cibles / personas

- **Administrateur établissement** : configure années académiques, niveaux, classes, tarifs, rôles et permissions.
- **Caissier/Comptable** : enregistre les paiements, ventes, dépenses ; consulte les rapports financiers.
- **Professeur** : saisit les notes, prend les présences, consulte ses programmes de cours.
- **Personnel administratif** : gère les inscriptions, dossiers étudiants, documents soumis.
- **Direction** : consulte le dashboard, les statistiques, valide les promotions de fin d'année.
- **Visiteur (site public)** : consulte actualités, événements, formations proposées par l'école.

## 4. Fonctionnalités (epics & user stories)

### 4.1 Gestion académique
- En tant qu'administrateur, je peux créer une année académique, des niveaux, classes et facultés.
- En tant qu'administrateur, je peux inscrire un étudiant dans une classe pour une année donnée.
- En tant que professeur, je peux être affecté à un programme (cours × classe × créneau horaire).

### 4.2 Gestion des notes et évaluations
- En tant que professeur, je saisis les notes des étudiants par cours, avec validation de séquence (impossible de saisir une période ultérieure avant la précédente).
- En tant que direction, je peux consulter les moyennes et générer un bulletin PDF.

### 4.3 Présences
- En tant que professeur/personnel, je fais l'appel quotidien par classe.
- En tant que direction, je consulte les statistiques de présence du jour et l'historique par classe/étudiant.

### 4.4 Finances
- En tant qu'administrateur, je configure les paramètres de paiement (montant, devise, nombre d'échéances, accessoires) par niveau.
- En tant que caissier, j'enregistre un paiement d'écolage et le système met à jour le statut (mois payés/bloqués).
- En tant que caissier, j'enregistre une vente d'articles (uniforme, fournitures) avec plusieurs lignes.
- En tant que comptable, j'enregistre une dépense ou une autre transaction ponctuelle.
- En tant qu'administrateur, je peux gérer des prêts (loans) avec taux d'intérêt et suivi de remboursement.

### 4.5 Promotions de fin d'année
- En tant que direction, je déclenche la promotion en masse des étudiants vers la classe/année supérieure, avec calcul automatique de la moyenne pondérée par coefficients.

### 4.6 Sécurité et gestion des utilisateurs
- En tant qu'utilisateur, je me connecte via email/identifiant + mot de passe et reçois un token JWT.
- En tant qu'utilisateur, je peux réinitialiser mon mot de passe via un code OTP envoyé par email.
- En tant qu'administrateur, je définis des rôles et permissions, et les assigne aux utilisateurs.
- En tant que système, toute action sensible (modification de paiement, suppression d'étudiant) est journalisée avec l'état avant/après et l'auteur.
- En tant qu'administrateur, certaines actions sensibles nécessitent une double-authentification (autorisation admin).

### 4.7 Licence & activation
- En tant qu'éditeur du logiciel, je peux limiter l'usage du client desktop par poste via une clé d'activation liée à l'adresse MAC, avec durée de validité.
- En tant qu'administrateur établissement, je consulte le statut de mon abonnement (actif/expiré, clé actuelle, jours restants) et l'historique complet des activations depuis `school_client` (`GET /api/v1/abonnement`, réservé aux admins).
- En tant que système, j'expose le `mac` du serveur via cette même route pour que le site de paiement `infini-software` puisse identifier sans ambiguïté quel établissement renouvelle, y compris quand l'admin se connecte au site depuis un autre poste/appareil que le serveur (voir `docs/infini-software-PRD.md`).

### 4.8 Documents et rapports
- En tant que caissier, je génère un reçu de paiement ou de vente en PDF.
- En tant que direction, je génère un rapport financier global, un rapport de paiement, un rapport pédagogique, ou un export Excel.
- En tant que personnel, je génère une attestation/liste d'inscription.

### 4.9 Contenu éditorial (CMS léger)
- En tant qu'administrateur, je publie des actualités et événements (avec ciblage d'audience : public/classe/professeurs) et des formations, avec upload d'image.
- En tant que visiteur du site public, je consulte les actualités, événements et formations publiés.

### 4.10 Tableau de bord
- En tant que direction, je consulte un dashboard avec effectifs, paiements du jour/année, répartition par classe/genre.

## 5. Hors périmètre actuel (constaté dans le code)

- Synchronisation cloud multi-établissements via WireGuard : infrastructure présente (`HeartAuto`, `ClientInfo`) mais pas pleinement activée.
- Authentification à deux facteurs : champ prévu (`two_factor_secret`) mais non exploité par les routes actuelles.
- CORS restreint en production (actuellement ouvert à `*`).

## 6. Risques / dette technique identifiée

- Nombreux fichiers dupliqués/brouillons (`*copy*.py`, specs multiples) à nettoyer pour éviter toute confusion sur la version de référence.
- CORS ouvert à toutes origines.
- **Tables `sym_*` (SymmetricDS) — confirmé** : le dump SQL réel contient 237 triggers `AFTER INSERT/UPDATE/DELETE` (un jeu de 3 par table, sur la quasi-totalité des tables), tous définis avec `DEFINER='repl'@'10.10.0.1'` et un nom de base codé en dur (`lemignon`, l'ancien nom de la base). Sur une base où cet utilisateur MySQL n'existe pas, **toute écriture sur n'importe quelle table échoue** (`1449 The user specified as a definer ... does not exist`). À clarifier d'urgence : si une réplication multi-site est réellement utilisée en production, le serveur de réplication doit avoir cet utilisateur configuré ; sinon ces triggers doivent être supprimés de la base de production également (supprimés sans risque de la base de test Docker créée pour la validation cross-platform).

## 7 bis. Mise à jour — abonnement & renouvellement (livré)

- Nouvelle route `GET /api/v1/abonnement` (admin uniquement) : statut courant (actif/expiré, clé, date d'expiration, jours restants) + historique complet, plus le `mac` du serveur. Consommée par le nouvel onglet Abonnement de `school_client` et par le flux de renouvellement du site `infini-software`.
- Bug corrigé sur `AskingResponse` (`/asking`) qui provoquait un 500 systématique et empêchait la transmission du bundle de certificats SSL au client (voir `docs/ecole_nginx.md` section 6 ter).
- Confirmé : deux mécanismes de licence séparés coexistent (historique `log_actives` en base vs. fichier d'essai local chiffré `license_check.py`) — à unifier si l'incohérence d'affichage entre les deux écrans (Abonnement vs. fenêtre Gestion du serveur) devient gênante en usage réel.

## 7. Mise à jour — installation multiplateforme (livré)

Objectif ajouté en cours de projet : rendre `ecole_nginx` installable sur Mac et Linux en plus de Windows, sans modifier le comportement de l'installateur Windows existant.

- **Mode headless** (`scripts/start.sh`) : MySQL + API + nginx entièrement en Docker Compose.
- **Mode GUI natif** (`app_gui.py`) : reproduit l'architecture Windows (API embarquée dans le process de la fenêtre de contrôle) ; seuls MySQL et nginx restent en conteneurs Docker. Auto-installation de Docker si absent (Homebrew sur Mac, script officiel sur Linux).
- **Licence** : nouveau module `app/Helper/license_check.py` (HMAC + MAC + Fernet), strictement cantonné à `sys.platform != "win32"` pour ne jamais affecter le flux Windows.
- **HTTPS local** : CA + certificat auto-signés pour `aplekol360.local`, générés par un conteneur `certgen`, à installer dans le magasin de confiance du poste via `scripts/setup-local-https.sh`. Le certificat serveur doit rester sous 825 jours de validité (exigence Apple/macOS), contrairement à la CA elle-même.
- **Risque résiduel** : la fenêtre Dashboard de Docker Desktop ne doit jamais s'ouvrir automatiquement (utiliser `docker desktop start --detach`, pas `open -a Docker`) pour ne pas dupliquer la fenêtre de contrôle native.
