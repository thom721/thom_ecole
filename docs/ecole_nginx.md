# ecole_nginx — Documentation technique

## 1. Vue d'ensemble

`ecole_nginx` est le backend API REST de la plateforme de gestion scolaire **Lekol360**. Il expose l'ensemble des fonctionnalités métier (gestion académique, financière, RH, contenu éditorial) consommées par le client desktop `school_client` et potentiellement par d'autres front-ends (web public).

## 2. Stack technique

| Domaine | Technologie |
|---|---|
| Framework web | FastAPI 0.126 (ASGI), Uvicorn 0.38, Starlette 0.50 |
| ORM / Base de données | SQLAlchemy 2.0.45, MySQL 8.0 (via PyMySQL), base `lekol360` |
| Migrations | Alembic 1.17.2 (`app/alembic1/`) |
| Auth | PyJWT 2.10 (JWT HS256), bcrypt / argon2-cffi (hash mots de passe), python-jose |
| Validation | Pydantic 2.12 + pydantic-settings |
| Email | fastapi-mail (SMTP titan.email) |
| Génération documents | WeasyPrint (HTML→PDF), CairoSVG, openpyxl (Excel), Pillow |
| Autres | Pandas/Numpy (rapports), python-multipart (uploads) |

## 3. Architecture des dossiers (`app/`)

```
app/
├── Models/        # Entités SQLAlchemy (MModels, MFinancials, MSystems, MRelations, MFormation, MPageSection)
├── Routes/         # Endpoints FastAPI groupés par domaine, + Routes/pdf/ pour la génération de documents
├── Schemas/        # Modèles Pydantic (validation/sérialisation), un fichier par domaine
├── services/        # Logique métier (auth, events, formations, seed)
├── Helper/          # Chiffrement, contexte d'audit, calculs, génération PDF
├── dependencies/    # Dépendances FastAPI (auth, rôles, permissions)
├── Middleware/       # LoginMiddleWare
├── Observers/        # Pattern Observer pour l'audit automatique
├── config/Config.py  # Configuration centrale (JWT, SMTP, etc.)
├── database.py       # Engine SQLAlchemy + sessionmaker
└── main.py            # Point d'entrée FastAPI
```

Fichiers de dump SQL à la racine (`16_05_2026.sql`, `16_05_2026_fixed.sql`) et `gtk_runtime/` (dépendances GTK pour WeasyPrint sous Windows).

> Plusieurs fichiers "copy"/variantes obsolètes existent (`database copy.py`, `main copy 2.py`, `Controllers - Copy/`, specs PyInstaller multiples) — ce sont des brouillons issus d'itérations de compilation, à ignorer ou nettoyer.

## 4. Modèle de données (principales entités)

**Pédagogie** : `AnneeAcademique`, `Niveau`, `Faculte`, `Classe`, `Etudiant`, `Cours`, `Professeur`, `Personnel`.

**Relations pédagogiques** : `ClasseEtudiant`, `EtudiantFaculte`, `ClasseFaculte`, `Programme`, `Note`, `CoursEtudiant`, `Presence`, `Responsable`, `PieceSoumise`.

**Finances** : `Paiement`, `ParametrePaiement`, `FraisInscription`, `FraisDivers`, `PaiementStatut`, `Vente`, `OrderItem`, `Depense`, `OtherTransaction`, `Loan`, `LoanRepayment`, `ParamExam`, `Payroll`, `PayrollVersement`, `ParametrePayroll`, `SalaireHistorique`.

**RH / présence personnel** : `Pointage` (arrivée/départ, `MRelations.py`) — mirror de `Presence` (élèves) mais avec deux horodatages au lieu d'un booléen ; source d'heures pour le payroll horaire des professeurs.

**Utilisateurs & sécurité** : `User`, `Role`, `Permission`, `ModelHasRole`, `ModelHasPermission`, `RoleHasPermission`, `BlacklistedToken`, `PasswordResetCode`, `PasswordResetToken`.

**Système & audit** : `Log` (audit trail complet avant/après), `LogActive` (licence/activation), `ClientInfo` (sync poste client via adresse MAC), `HeartAuto` (clés RSA / WireGuard), `Profile`, `DirectConfig`.

**Contenu éditorial** : `Event`, `News`, `Category`, `Formation`, `PageSection`.

## 5. API — domaines fonctionnels (prefix `/api/v1`)

- **Auth** : login, refresh/vérification de token, reset password par OTP email, logout (blacklist), double-authentification admin pour actions sensibles.
- **Étudiants** : CRUD, recherche, inscription, génération du reçu d'inscription.
- **Classes / Niveaux / Facultés** : affectation, statistiques, combinaisons niveau↔classe.
- **Paiements** : enregistrement, historique par étudiant, paramètres de paiement par niveau (montants, échéances, accessoires).
- **Frais d'inscription / Frais divers** : CRUD.
- **Ventes & dépenses** : commandes multi-articles, suivi de statut, dépenses administratives.
- **Notes & cours** : saisie des notes par cours/étudiant, consultation par cours ou par étudiant.
- **Présences** : appel par classe, statistiques journalières/historiques.
- **Promotions** : promotion en masse vers l'année/classe suivante, calcul de moyenne pondérée.
- **Académique RH** : professeurs, personnel (création avec compte utilisateur associé). Voir §9 pour le mécanisme de "casquette enseignante" (Personnel ↔ Professeur).
- **Payroll** (`RPayroll.py`, absent de `school_client` et du web, ajouté sur demande explicite) : versements de salaire fixe ou horaire (`Payroll`/`PayrollVersement`, versements partiels possibles, mirror du module Prêts), taux horaire par cours/année (`ParametrePayroll`, CRUD dans `RParametrePayroll.py`), bilan mensuel tous professeurs (`GET /payroll/bilan-mensuel`), résolution employé→identité de paie (`GET /payroll/professeur-info`, voir §9).
- **Pointage** (`RPointage.py`) : arrivée/départ du personnel (Professeur + Personnel), historique par personne/mois — source d'heures pour le payroll horaire. Horodatages fixés en heure d'Haïti (`America/Port-au-Prince`, `zoneinfo`), pas l'heure système du serveur.
- **Historique des salaires** (`SalaireHistorique`) : journal automatique de tout changement de `salaire_fixe` (Professeur ou Personnel), écrit depuis `RAcademic.py` et `RRolePermission.py` (voir §9) — sert le rapport "Historique des salaires".
- **Programmes** : association professeur/cours/classe/horaire.
- **Rôles & permissions** : RBAC complet (assignation rôle/permission à un utilisateur).
- **Client Info / Licence** : enregistrement MAC, autorisation, dernière clé d'activation.
- **Abonnement** (`GET /api/v1/abonnement`, admin uniquement) : statut courant + historique complet des activations (`LogActive`), plus le `mac` du serveur (`get_host_mac()`) — utilisé par `school_client` pour afficher l'onglet Abonnement et identifier le bon client lors d'un renouvellement sur le site `infini-software` (voir `docs/infini-software.md`). Remplace l'usage de l'ancienne route `/licence/derniere-cle`, restée en place mais cassée (filtre sur une colonne `f_key` jamais alimentée).
- **Logs** : consultation de l'audit trail.
- **Contenu** : events, news, catégories, formations, sections de page d'accueil (CMS basique avec upload d'image).
- **Dashboard** : statistiques agrégées (effectifs, paiements jour/année, combos pour formulaires), health check.
- **PDF/Excel** (`Routes/pdf/`) : reçu de paiement, bulletin (simple et groupé), rapport global, rapport de paiement, rapport pédagogique, reçu de vente, export Excel, emploi du temps par classe (`RHoraireReport.py:print_horaire` — reconstruit depuis zéro, `/print-horaire` n'existait nulle part côté backend malgré un bouton présent sur le web), charge d'enseignement par professeur (`print_programme_professeur` — décompte de cours/classes assignés, pas une durée en heures : `Programme.heure` n'a de vraie valeur que dans 2 lignes sur 548 en pratique), rapport Payroll par intervalle de dates (`PayrollReport.py`, filtre Global/Professeur/Personnel), historique des salaires (`SalaireHistoriqueReport.py`).

## 6. Sécurité

- **JWT HS256**, expiration ~8 jours (1520 min), header `Authorization: Bearer`.
- **Hash des mots de passe** : bcrypt (avec compatibilité format Laravel `$2y$`→`$2b$`).
- **RBAC** : tables `roles`/`permissions` + tables de jonction ; vérification hiérarchique user→rôle→permission via `dependencies/Dependencie.py`.
- **Blacklist de tokens** pour le logout.
- **Audit trail automatique** (pattern Observer) sur `User`, `Paiement`, `Etudiant`, `OtherTransaction`, `Vente`, `Depense`, `ParametrePaiement` — capture avant/après + IP.
- **Licence/activation** : `ClientInfo` (MAC), `LogActive` (clé, jours restants), `HeartAuto` (clés RSA, config WireGuard) — l'infrastructure de sync cloud existe mais une partie est non activée dans le code actuel.
- **Deux mécanismes de licence distincts et non reliés entre eux** (point de confusion identifié en cours de projet) : (1) `LogActive`/`log_actives` (MySQL) = historique d'activation **métier**, alimenté par `POST /api/v1/log-activate`, exposé via `/api/v1/abonnement` ; (2) `app/Helper/license_check.py` = essai local (Fernet, fichier `~/.ecole_360/license.json` ou volume Docker), vérifié par `gui/service_window.py` (fenêtre "Gestion du serveur"), totalement indépendant de la base de données. Les deux doivent être tenus synchronisés manuellement si on veut que l'état affiché soit cohérent entre l'onglet Abonnement de `school_client` et le panneau Licence de la fenêtre de gestion du serveur.
- **`get_host_mac()` mis en cache (bug réel corrigé)** : `uuid.getnode()` seul n'est pas stable sur Mac — il renvoie l'adresse d'une interface réseau quelconque parmi celles actives au moment de l'appel (Wi-Fi, pont virtuel, hotspot personnel...), qui peut changer d'un appel à l'autre selon l'état réseau (Wi-Fi déconnecté/reconnecté → interface différente énumérée en premier), et macOS randomise en plus l'adresse Wi-Fi visible par réseau ("Private Wi-Fi Address"). Constaté en conditions réelles : `school_client` et `ecole_nginx` ont détecté deux mac différents sur la même machine selon l'état Wi-Fi (`AC:DE:48:00:11:22` vs `7E:43:41:C2:15:98`), créant un doublon dans `client_infos` et menaçant de rendre l'abonnement infini-software "introuvable" si le mac serveur changeait après coup. Corrigé : `get_host_mac()` détecte une fois puis persiste la valeur dans un fichier local (`MAC_CACHE_FILE`, même dossier que `LICENSE_FILE`) — toujours prioritaire : `HOST_MAC_ADDRESS` (env, mode Docker) > cache local > détection `uuid.getnode()`.
- **Rate limiting** (middleware custom dans `app/main.py`, pas de dépendance externe type slowapi) : limites par route (`/api/v1/auth/login` 10/min, `/api/v1/password-reset-request` 5/min, `/api/v1/password-reset-verify` 10/min, 100/min par défaut ailleurs), purge périodique des entrées IP/route obsolètes pour éviter une fuite mémoire.
- CORS actuellement ouvert (`*`) — à restreindre en production.

## 6 ter. Bug corrigé — `AskingResponse` (`/asking`, `/client-authorisation-connect/{mac}`)

`app/Schemas/SClientInfos.py` : le champ `data` était typé `Optional[Dict[str, Any]]` alors que la route `/asking` (`app/Routes/RClientInfos.py`) renvoie tantôt un dict (`/client-authorisation-connect/{mac}`), tantôt une string/`""` (`/asking`, le `certi_key`) — ce qui provoquait un `ResponseValidationError` (500) systématique dès qu'un client appelait `/asking` sans `certi_key` enregistré. Le champ `certy_ss` (toujours le nom utilisé par les routes qui construisent `AskingResponse(...)`) était par ailleurs nommé `ss_certi` dans le schéma — mismatch silencieux qui faisait que le bundle de certificats SSL n'était jamais transmis au client (`school_client` lit `data['certy_ss']`). Corrigé : `data: Optional[Any]`, champ renommé `certy_ss`.

## 6 bis. Performance

- Les routes PDF/Excel (`Routes/pdf/*`) et `Etudiants.py` sont passées d'`async def` à `def` : FastAPI les exécute alors dans un threadpool plutôt que de bloquer la boucle d'événements pendant la génération WeasyPrint/openpyxl.
- `AuthorizationService.user_has_permission()` (`app/services/ServiceAuth.py`) : remplacé deux requêtes séparées (permissions directes + via rôle, comparées en Python) par une seule requête SQL `UNION` + `EXISTS`.
- Démarrage (`app/main.py`) : bascule correcte entre `Base.metadata.create_all()` + `alembic stamp head` (base vide) et `alembic upgrade head` (base existante) — l'ancien code référençait un fichier `alembic.ini` inexistant et avait la logique de migration commentée.

## 7. Configuration & déploiement

- Variables d'environnement (`.env`) : `BASE_URL2`, `STORAGE_PATH`, secrets JWT, SMTP, et désormais `DB_HOST`/`DB_PORT`/`DB_USER`/`DB_PASSWORD`/`DB_NAME` (lus par `app/database.py`, valeurs par défaut identiques à l'ancienne config Windows codée en dur — aucun changement de comportement si absents du `.env`).
- MySQL : `mysql+pymysql://.../lekol360`, pool size=10, max_overflow=20 ; retry de connexion configurable (`DB_CONNECT_RETRIES`/`DB_CONNECT_RETRY_DELAY`, utile pour Docker).
- Documentation interactive : `/docs` (Swagger), `/redoc`.
- Fichiers statiques montés sous `/static`.
- WeasyPrint nécessite GTK (`gtk_runtime/` fourni pour Windows ; setup différent sous Linux/Mac dans `main.py`).
- Pensé pour être servi derrière Nginx (nom du projet) + Uvicorn.
- **Installation Mac/Linux/Windows** (ajout récent, voir section 8) : Docker Compose pour MySQL/nginx + soit un service API headless (`scripts/start.sh`), soit une fenêtre native PySide6 avec API embarquée (`app_gui.py`), équivalente à l'installateur Windows (`Controllers/Main_run.py` + `app.py`).

## 8. Installation cross-platform (Docker + GUI native)

Ajouté pour permettre l'installation sur Mac/Linux sans rien casser sur l'installateur Windows existant (`app.py` → `Controllers/Main_run.py`, inchangé) :

- **`Dockerfile`** : image `python:3.10-slim` + dépendances système WeasyPrint, sert l'API sur le port 9001.
- **`docker-compose.yml`** : services `mysql` (port hôte **3307**, pas 3306, pour ne pas entrer en conflit avec un MySQL natif déjà présent sur la machine), `certgen` (génère une CA + certificat serveur auto-signés pour `aplekol360.local`, validité du certificat serveur limitée à 825 jours pour rester conforme aux exigences Apple/Mac), `nginx` (reverse proxy HTTPS, proxy vers `host.docker.internal:9001` — fonctionne aussi bien avec l'API en conteneur qu'en natif), `app` (API en conteneur, mode headless uniquement).
- **`scripts/start.sh`** : mode headless, démarre tous les services Docker y compris l'API.
- **`scripts/setup-local-https.sh`** : ajoute `aplekol360.local` à `/etc/hosts` et installe la CA générée dans le magasin de confiance du système (Keychain Mac / ca-certificates Linux) — nécessite `sudo`, à exécuter manuellement.
- **`scripts/activate-license.sh`** : activation de licence en CLI pour le mode headless.
- **`app_gui.py` + `gui/service_window.py`** : mode GUI natif (recommandé sur poste avec écran) — l'API FastAPI tourne en thread natif dans ce process (comme `app.exe` sur Windows), MySQL/nginx restent en Docker. Auto-installe Docker si absent (Homebrew sur Mac, script officiel `get.docker.com` sur Linux) et démarre le moteur Docker sans ouvrir sa fenêtre Dashboard (`docker desktop start --detach`). Fenêtre de contrôle équivalente à `Controllers/ShowControl.py` (services Docker, licence, autorisation des postes clients).
- **`app/Helper/license_check.py`** : licence portable (HMAC-SHA256 + MAC + chiffrement Fernet), équivalent non-Windows de `Helper/server_key_generate.py` ; vérifiée au démarrage uniquement si `sys.platform != "win32"` (zéro impact sur le comportement Windows).
- **Réplication SymmetricDS (`sym_*`)** : confirmé — le dump SQL réel contenait des triggers `AFTER INSERT/UPDATE/DELETE` sur quasiment toutes les tables (`SYM_ON_*_FOR_TRG_*`), tous définis avec `DEFINER='repl'@'10.10.0.1'` et référençant la base `lemignon` (ancien nom). Sans cet utilisateur MySQL ni la base `lemignon`, toute écriture échoue. Supprimés de la base de test Docker (`lekol360`) ; à clarifier si une vraie réplication multi-site est encore utilisée en production avant de les supprimer d'une base réelle.

## 9. Payroll horaire, Pointage et double rôle Personnel/Professeur (livré)

Fonctionnalité ajoutée sur demande explicite, sans référence bureau/web (comme Payroll/Prêts). Contexte : le payroll n'avait aucune notion de salaire de base ni de calcul horaire, et le modèle de données ne permettait pas à une même personne d'être à la fois Professeur et Personnel.

- **Salaire fixe + calcul horaire** : `Professeur.type_paiement` (`fixe`/`horaire`) + `salaire_fixe`, `Personnel.salaire_fixe` (pas de `type_paiement` — toujours fixe, pas de notion de cours/heures). `ParametrePayroll` (cours × année académique, `AnneeAcademique.id` — même convention que `Programme.annee_academique`) donne le taux/heure ; `Payroll.montant_du`/`remaining_balance`/`details_horaires` (snapshot figé du calcul) suivent le même pattern que `Loan`/`LoanRepayment` pour les versements partiels.
- **Pointage** (`Pointage`, `RPointage.py`) : source d'heures de référence, affichée dans le formulaire de versement mais jamais injectée automatiquement dans le calcul (un professeur peut enseigner plusieurs cours à des taux différents — répartir le total pointé entre eux reste une décision manuelle de l'admin).
- **Double rôle Personnel → Professeur ("casquette enseignante")** : `Professeur.personnel_id` (nullable, unique) marque une fiche Professeur comme liée à un Personnel qui a le rôle `teacher`/`Enseignant` — **aucun `User` propre** n'est créé pour cette fiche (le Personnel garde son seul compte de connexion). Synchronisée automatiquement (`RAcademic.py:_sync_shadow_professeur`) depuis **deux chemins** qui peuvent tous les deux changer le rôle d'un utilisateur : le formulaire Personnel (`store_personnel`) ET l'onglet Rôles de Profile (`RRolePermission.py:assign_role_to_user`) — les deux appellent la même fonction partagée. Un rôle retiré désactive la fiche (`status=False`, jamais supprimée — préserve l'historique Programme/Payroll) ; la réattribuer réactive la même fiche sans dupliquer. La fiche affiche le **vrai email** du Personnel (pas de placeholder synthétique) : sans risque, l'authentification passe par `User.email` (table séparée), jamais par `Professeur.email`.
- **Double rôle Professeur → Personnel ("casquette administrative", symétrique)** : `Personnel.professeur_id` (nullable, unique) — mécanisme miroir pour un Professeur **avec son propre compte de connexion** qui reçoit un rôle non-enseignant (ex. Comptable, Secrétaire général, Responsable pédagogique). `RAcademic.py:_sync_shadow_personnel` + `_role_is_personnel` (tout rôle hors `_ROLES_NON_PERSONNEL` = `teacher`/`Enseignant`/`admin`/`user`/`student`) créent/mettent à jour la fiche Personnel liée depuis `RRolePermission.py:assign_role_to_user` uniquement (`ProfesseurRequest` ne porte pas de champ rôle — un professeur ne change de rôle que depuis l'onglet Rôles). Contrairement au sens Personnel→Professeur, `Personnel` n'a pas de colonne `status` : pas d'équivalent "désactiver" si le rôle repasse à enseignant, la fiche déjà créée reste simplement telle quelle.
- **Piège des emails partagés entre fiche réelle et fiche casquette** : les deux mécanismes ci-dessus font exprès de donner à la fiche "casquette" le même email que l'identité réelle — les vérifications d'unicité d'email de `store_professeur`/`store_personnel` (qui excluent normalement seulement la ligne éditée elle-même) doivent donc aussi exclure explicitement la fiche liée (`Professeur.personnel_id`/`Personnel.professeur_id`, et le `User` de l'identité réelle), sinon modifier l'une ou l'autre fiche se bloque elle-même avec "Cet email est déjà utilisé."
- **Résolution employé → identité de paie** (`GET /payroll/professeur-info`) : un Personnel avec une fiche liée peut avoir **deux salaires distincts** (fixe Personnel + rémunération de sa fiche professeur, ex. salaire de base + heures supplémentaires d'enseignement) — la route renvoie `has_linked_professeur`/`personnel_salaire_fixe` en plus de l'identité "professeur" par défaut, pour que le client propose un choix plutôt que de trancher silencieusement.
- **Piège vécu en conditions réelles** : modifier les rôles d'un compte actif (retrait du rôle `admin` en assignant uniquement `teacher`/`Enseignant` via l'onglet Rôles, qui **remplace** tous les rôles au lieu de les additionner) fait perdre l'accès admin immédiatement après reconnexion — comportement RBAC correct, mais surprenant ; restauration via un nouvel appel à `assign_role_to_user` avec la liste complète des rôles voulus.
- **`SalaireHistorique`** : journal de tout changement de `salaire_fixe` (Professeur ou Personnel), écrit depuis les deux mêmes chemins que la synchronisation de rôle. `created_at` en précision microseconde (`DATETIME(6)`) — sans ça, deux changements dans la même seconde ne pouvaient pas être triés de façon fiable pour le rapport chronologique.
- **Bug Flutter récurrent, plusieurs fois rencontré sur ce chantier** : `DropdownButtonFormField.initialValue` n'est lu qu'à la création du widget — si le champ se construit avant que sa liste d'options (chargée en arrière-plan) soit prête, il se fige sur "aucune sélection" et ignore silencieusement toute valeur correcte calculée lors des rebuilds suivants. Touché : formulaire Programme (Cours/Professeur/Niveau/Classe/Année) et formulaire Payroll horaire (Année académique). Fix systématique : une `Key` qui change une fois la liste chargée (ex. `ValueKey('cours-${id}-${liste.length}')`), forçant Flutter à recréer le widget avec la bonne valeur au lieu de le laisser bloqué sur son état initial.

## 10. Permissions d'impression, correctifs d'audit et parité web (livré)

- **Vrai bug racine du dropdown Programme "toujours vide"** (rapporté à 3 reprises, "corrigé" à tort côté Flutter à chaque fois) : le schéma Pydantic `ProgrammeResponse` (`programme_schema.py`) déclarait `professeur_id`/`Cours_id`, mais la requête de `GET /programme` (liste) construisait le dict avec `profId`/`coursId`/`classId` — FastAPI validant la réponse à travers ce schéma, les clés non déclarées étaient **silencieusement supprimées** et les champs déclarés-mais-jamais-remplis retombaient à `null`, sur **chaque ligne, à chaque appel**, indépendamment de tout état Flutter. Les 3 correctifs Flutter précédents (`ValueKey` sur les dropdowns) réglaient un vrai problème de staleness pour Niveau/Faculté/Classe/Année, mais Cours/Professeur étaient morts à l'arrivée dès la réponse HTTP. Corrigé en déclarant `profId`/`coursId`/`classId` (`Optional[str]`) dans le schéma.
- **Permissions d'impression, jamais réellement appliquées** : 6 permissions (`Imprimer paiement`, `Imprimer vente`, `Imprimer rapport`, `Imprimer rapport pedagogique`, `Imprimer bulletin`, `Imprimer enregistrement`) existaient en base (seed `Initialisation.py`) mais n'étaient vérifiées par **aucune route** PDF/Excel, n'étaient câblées sur **aucun bouton** côté client, et n'étaient assignées à **aucun rôle ni utilisateur** (même l'admin). `/print-recu` (reçu de paiement) n'avait même aucune authentification. Désormais `check_permission("Imprimer ...")` sur chaque route `app/Routes/pdf/*.py` + `Etudiants.py:impression_fiche`, mapping : `Imprimer paiement` → reçu paiement seul ; `Imprimer vente` → reçu vente seul ; `Imprimer bulletin` → bulletin simple/en masse ; `Imprimer enregistrement` → reçu d'inscription + registre ; `Imprimer rapport pedagogique` → rapports pédagogiques + décision de fin d'année + horaire/charge d'enseignement ; `Imprimer rapport` → tout le reste (global, financier, payroll, historique salaires, exports Excel restants). Les 6 permissions ont été accordées au rôle `admin` (23 permissions existantes préservées) — les accorder à d'autres rôles est une décision métier laissée à l'admin de l'école via Profile → Permissions.
- **Bug de journalisation (`Log`) découvert en implémentant ce qui précède** : `GlobalModelObserver.log_activity` (`app/Observers/global_observer.py`) appelait `self.db.commit()` **à l'intérieur** d'un événement mapper `after_insert`/`after_update` — qui se déclenche en plein flush d'un `commit()` déjà en cours. Reproduit sur `Depense` (déjà enregistré en production) : `ResourceClosedError: This transaction is closed`. Corrigé en retirant ce `commit()` imbriqué (un simple `self.db.add(log_entry)` suffit, l'objet est balayé par le flush déjà en cours). `Payroll`/`PayrollVersement` (celui-ci désormais avec `ObservableMixin`) sont enregistrés dans `main.py` au démarrage — leurs créations/versements apparaissent maintenant dans `Log`, comme Paiement/Vente/Depense.
- **Parité web (Vue) avec le client desktop**, plusieurs fonctionnalités existant côté serveur/Flutter mais jamais exposées côté web :
  - `Tresorerie.vue` : nouvel onglet **Produits** (CRUD complet + création de catégorie à la volée) — l'entrée `vente.produits` existait déjà dans la configuration des vues (`adProfile.vue`) mais aucun onglet ne la consommait.
  - `Cours.vue` : nouveau bouton/modal **Charge d'enseignement** (`GET /print-programme-professeur`). En le câblant, bug pré-existant découvert : le bouton **Imprimer horaire**, déjà présent, appelait `window.open()` directement sur l'URL de l'API — sans le header `Authorization`, jamais fonctionnel avec une route protégée (cassé par le durcissement des permissions ci-dessus, qui a transformé un problème latent en échec systématique). Les deux boutons utilisent désormais le motif déjà établi ailleurs dans l'app (`Rapport.vue:submitPdf`) : `axios` + `Authorization: Bearer` + `responseType: 'blob'`.
  - `Professeur.vue`/`Administration.vue` : badges **"via Personnel"**/**"via Professeur"** à côté du nom, reflétant les fiches "casquette" du double rôle (§9) — les champs `personnel_id`/`professeur_id` étaient déjà dans les réponses API, seul l'indicateur visuel manquait.
  - Modals d'édition Personnel/Professeur : section **Actif/Inactif** (même route `PATCH active-personnel`/`active-teacher` que le badge de la liste), **réinitialisation de mot de passe** (`PATCH change-password-personnel`/`change-password-teacher` — routes existantes, jamais exposées côté web), et champ **salaire fixe** (+ **type de paiement** pour Professeur). Bug pré-existant corrigé au passage : l'édition d'un professeur appelait `PUT /professeur/{id}`, une route qui n'existe pas côté serveur (`store_professeur` est un unique `POST` gérant création et modification via un `id` dans le corps) — toute modification de professeur échouait donc en 404.
  - `Rapport.vue` : nouvelles cartes **Rapport Payroll** (`POST /print-payroll-report`) et **Historique des salaires** (`POST /print-salaire-historique-report`), mêmes filtres que côté Flutter.
