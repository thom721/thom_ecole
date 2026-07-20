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
- En tant qu'utilisateur habilité ("Supprimer note"), je supprime les notes d'un mois pour tout un niveau/classe/année, ou pour un seul étudiant de cette classe si je précise son identifiant (§7 septies).

### 4.3 Présences
- En tant que professeur/personnel, je fais l'appel quotidien par classe.
- En tant que direction, je consulte les statistiques de présence du jour et l'historique par classe/étudiant.

### 4.4 Finances
- En tant qu'administrateur, je configure les paramètres de paiement (montant, devise, nombre d'échéances, accessoires) par niveau.
- En tant que caissier, j'enregistre un paiement d'écolage et le système met à jour le statut (mois payés/bloqués).
- En tant que caissier, j'enregistre une vente d'articles (uniforme, fournitures) avec plusieurs lignes.
- En tant que comptable, j'enregistre une dépense ou une autre transaction ponctuelle.
- En tant qu'administrateur, je peux gérer des prêts (loans) avec taux d'intérêt et suivi de remboursement.
- En tant qu'administrateur, je gère la paie du personnel — salaire fixe ou calculé à l'heure par cours/année académique, versements partiels, bilan mensuel (§7 quater).
- En tant que caissier/admin, j'accorde une dérogation manuelle et réversible au blocage de paiement d'arriéré (année précédente impayée) pour un étudiant, avec motif et ordonnateur obligatoires (§7 sexies).

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

## 7 ter. Mise à jour — contrôle d'accès par onglets et déconnexion forcée (livré)

### Contrôle d'accès par onglets (`accessible_tabs`)

- **Paramètres** (`Parametres.vue`) : les sous-onglets (niveaux, examens, frais, etc.) sont désormais filtrés par `settings.xxx` dans `tab_ids` — si aucun sous-onglet n'est coché dans Vues pour le rôle de l'utilisateur, la page est entièrement vide. Les boutons Ajouter/Modifier/Supprimer sont cachés si l'utilisateur n'a pas la permission `"Ajouter parametre"` (calculée dans le computed `canWrite`).
- **Dashboard** (`Dashboard.vue`) : les sections PaiementsStats, DashboardStudentStats et le détail par classe sont conditionnés par `canSeeSubTab('home.xxx')` — un utilisateur sans accès à "Suivi de paiement" ne voit pas ce bloc, même si le Dashboard parent lui est accordé.
- **Trésorerie** (`Tresorerie.vue`) : les quatre sous-onglets (Ventes, Dépenses, Prêts, Autres transactions) sont filtrés par `vente.xxx` dans `tab_ids` ; si le sous-onglet actif disparaît lors d'un changement de droits, la vue bascule automatiquement sur le premier visible.
- **Communauté** (`Communaute.vue`) : idem pour `communaute.evenements`, `communaute.actualites`, `communaute.annonces`.
- **Profile** (`adProfile.vue`) : section Vues (configuration des onglets accessibles par rôle) correctement gardée par `canSeeSection('profile.vues')`.
- **Correctif `shouldShowMenuItem`** (`AdminLayout.vue`) : la branche `'Profile'` retournait `true` sans passer par la vérification `tab_ids`, court-circuitant le contrôle pour les autres items. Corrigé.

### Déconnexion forcée sur modification des onglets

- **Web** : `auth.js` expose `startTabWatcher()` / `stopTabWatcher()` — interroge `/verify-token` toutes les 2 minutes et compare la signature `tab_ids` avec le snapshot pris à la connexion. Si elle a changé, `tabsModified = true`. `AdminLayout.vue` détecte ce changement via un `watch`, affiche une bannière amber avec compte à rebours de 10 secondes (Teleport vers `<body>`) et force la déconnexion/redirection vers `/login` à l'expiration.
- **Flutter** : mêmes mécanismes dans `auth_state.dart` (`startTabWatcher`/`stopTabWatcher`, `Timer.periodic` 2 min) et `app_shell.dart` (écoute `addListener`, dialog `_TabsModifiedDialog` avec compte à rebours 10 s). La dialog propose un bouton "Se déconnecter maintenant" pour ne pas attendre.

### Ajout de Communauté (web et Flutter)

- `ALL_NAV` (`adProfile.vue`) et `NAV_TAB_ID` / `ROUTE_TAB_ID` (`AdminLayout.vue`, `router/index.js`) : `'Communauté'` ajouté avec ses 3 sous-items (`evenements`, `actualites`, `annonces`).
- Flutter : `NavItem('communaute', ...)` ajouté à `kMainNavItems` ; `'communaute': [3 sous-items]` ajouté à `kSubNavItems`.

## 7 quater. Mise à jour — Payroll horaire, Pointage et double rôle Personnel/Professeur (livré)

Fonctionnalité ajoutée sur demande explicite (absente de `school_client` et du web) — voir `docs/ecole_nginx.md` §9 pour le détail technique complet.

- En tant qu'administrateur, je verse un salaire fixe (préremplissable depuis le profil de l'employé) ou calculé à l'heure (cours × taux configuré par année académique, `ParametrePayroll`), avec versements partiels possibles et un solde restant suivi automatiquement.
- En tant qu'administrateur, je pointe l'arrivée/le départ du personnel (Professeur et Personnel) et je consulte un total d'heures de référence par mois — affiché mais jamais injecté automatiquement dans le calcul de salaire, puisqu'un professeur peut enseigner plusieurs cours à des taux différents.
- En tant qu'administrateur, si un membre du Personnel a aussi le rôle `teacher`/`Enseignant` (assigné depuis le formulaire Personnel **ou** depuis l'onglet Rôles de Profile), il devient automatiquement assignable dans Programme comme un professeur — sans compte de connexion supplémentaire — et peut recevoir soit son salaire fixe Personnel, soit une rémunération liée à ses cours, au choix au moment du versement.
- En tant qu'administrateur, si un Professeur avec son propre compte reçoit un rôle non-enseignant (Comptable, Secrétaire général, Responsable pédagogique...) depuis l'onglet Rôles, il apparaît automatiquement aussi dans la liste Personnel (fiche "casquette administrative" liée, symétrique du cas précédent) avec un salaire fixe Personnel distinct de sa paie de professeur — toujours sans compte de connexion supplémentaire.
- En tant qu'administrateur, je consulte un bilan mensuel tous professeurs (montant dû/versé/solde par mois) et un historique de tous les changements de salaire fixe (augmentations/baisses) sur une période donnée.
- En tant qu'administrateur, j'imprime l'emploi du temps d'une classe (fonctionnalité reconstruite depuis zéro — le bouton existait sur le web mais appelait une route inexistante côté serveur) et la charge d'enseignement d'un professeur (décompte de cours/classes assignés, pas une durée en heures — donnée non fiable dans `Programme.heure` aujourd'hui).

## 7 quinquies. Mise à jour — permissions d'impression et parité web (livré)

Voir `docs/ecole_nginx.md` §10 pour le détail technique complet (bug racine du dropdown Programme, bug de journalisation, mapping exact des permissions).

- En tant qu'administrateur, je restreins qui peut imprimer quoi (reçus de paiement/vente, bulletins, registres d'inscription, rapports pédagogiques, autres rapports) via 6 permissions dédiées (Profile → Permissions) — ces permissions existaient déjà dans le système mais n'étaient vérifiées nulle part ; désormais appliquées côté serveur (toute route PDF/Excel) et côté client (chaque bouton Imprimer).
- En tant qu'administrateur, toute création/modification de versement de salaire (Payroll) est désormais journalisée dans l'historique des actions (Log), comme les paiements, ventes et dépenses le sont déjà.
- En tant qu'administrateur, je retrouve sur le web les mêmes fonctionnalités de gestion du personnel/professeurs que sur le bureau : activer/désactiver un compte et réinitialiser un mot de passe directement depuis le formulaire de modification, salaire fixe (et type de paiement pour un professeur), et un indicateur visuel quand une fiche Personnel/Professeur est une "casquette" liée à l'autre (double rôle).
- En tant qu'administrateur, je gère un catalogue de produits (ajout, catégories) depuis Trésorerie → Produits sur le web, et j'imprime la charge d'enseignement d'un professeur ainsi que le rapport Payroll/l'historique des salaires depuis les pages Cours et Rapport du web — fonctionnalités déjà disponibles côté bureau, absentes du web jusqu'ici.

## 7 sexies. Mise à jour — dérogation d'arriéré (livré)

Voir `docs/ecole_nginx.md` §11 pour le détail technique complet (modèle `AnnulationArriere`, routes, règle de blocage). Web (`Paiements.vue`) et Flutter (`derogation_arriere_dialog.dart`) exposent le même flux.

- En tant que caissier, je suis bloqué pour enregistrer un nouveau paiement d'écolage tant qu'un solde impayé existe pour l'année académique **précédente** de cet étudiant (pas d'autres années plus anciennes) — sauf première inscription, gap year, ou dérogation active.
- En tant que caissier/admin habilité ("Annuler arriéré"), j'accorde une dérogation manuelle et réversible sur la ligne de paiement bloquée : type "tout le reste" (solde calculé automatiquement) ou montant précis, avec ordonnateur (nom + fonction), motif et acceptation d'un texte d'engagement obligatoires. L'historique de paiement original n'est jamais modifié — seule l'existence d'une dérogation active lève le blocage.
- Avant de choisir le montant, le bouton de dérogation affiche le **solde restant dû** (avec sa devise) et l'**historique complet** des dérogations déjà accordées/révoquées pour cet étudiant et cette année — ajouté après coup (endpoint `GET /annulation-arriere` initialement muet sur ce contexte), pour éviter de créer une dérogation "à l'aveugle".
- En tant que caissier/admin habilité, je peux révoquer une dérogation active à tout moment (motif obligatoire) — rétablit immédiatement le blocage.
- Toute création/révocation est journalisée (Log) avec le motif, l'ordonnateur et le rôle de l'exécutant au moment de l'action (snapshot, indépendant d'un changement de rôle ultérieur).

## 7 septies. Mise à jour — suppression de notes restreinte à un étudiant (livré)

Voir `docs/ecole_nginx.md` §12 pour le détail technique complet. Web (`Notes.vue`) et Flutter (`notes_screen.dart::_DeleteNotesDialog`) exposent le même flux — la suppression groupée par niveau/classe/année/mois existait déjà des deux côtés, seul un critère optionnel supplémentaire est ajouté.

- En tant qu'utilisateur habilité ("Supprimer note"), je peux restreindre la suppression à un seul étudiant de la classe choisie via son identifiant, plutôt qu'à toute la classe.
- Champ laissé vide : comportement identique à avant cet ajout, aucune régression sur la suppression groupée existante.

## 7. Mise à jour — installation multiplateforme (livré)

Objectif ajouté en cours de projet : rendre `ecole_nginx` installable sur Mac et Linux en plus de Windows, sans modifier le comportement de l'installateur Windows existant.

- **Mode headless** (`scripts/start.sh`) : MySQL + API + nginx entièrement en Docker Compose.
- **Mode GUI natif** (`app_gui.py`) : reproduit l'architecture Windows (API embarquée dans le process de la fenêtre de contrôle) ; seuls MySQL et nginx restent en conteneurs Docker. Auto-installation de Docker si absent (Homebrew sur Mac, script officiel sur Linux).
- **Licence** : nouveau module `app/Helper/license_check.py` (HMAC + MAC + Fernet), strictement cantonné à `sys.platform != "win32"` pour ne jamais affecter le flux Windows.
- **HTTPS local** : CA + certificat auto-signés pour `aplekol360.local`, générés par un conteneur `certgen`, à installer dans le magasin de confiance du poste via `scripts/setup-local-https.sh`. Le certificat serveur doit rester sous 825 jours de validité (exigence Apple/macOS), contrairement à la CA elle-même.
- **Risque résiduel** : la fenêtre Dashboard de Docker Desktop ne doit jamais s'ouvrir automatiquement (utiliser `docker desktop start --detach`, pas `open -a Docker`) pour ne pas dupliquer la fenêtre de contrôle native.
