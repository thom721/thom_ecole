# PRD — flutter_version (Client desktop Lekol360, réécriture Flutter)

## 1. Contexte et problème

`school_client` (PySide6/Python) est le client desktop historique de Lekol360, mais son code concentre une dette importante (`Controllers/Main.py` ~14k lignes, `Models/enregistrement.py` ~28k lignes, packaging dual Nuitka/PyInstaller — voir `docs/school_client-PRD.md` §6) et reste coûteux à étendre. `flutter_version` est une réécriture complète du même client, consommant la même API `ecole_nginx`, avec deux objectifs simultanés : **fidélité fonctionnelle** au bureau existant (mêmes écrans, mêmes règles métier, mêmes routes API) et **modernisation du rendu** (esthétique reprise du frontend web `ecole_nginx/frontend` — `AdminLayout.vue` — plutôt que du Qt natif du bureau). Méthodologie de travail établie pour ce projet : ne jamais styliser/câbler une fonctionnalité sans avoir d'abord vérifié son comportement réel dans `school_client` (recherche du composant Qt par son CSS-ID) et dans `ecole_nginx` (route/permission réelle) — jamais par supposition.

## 2. Objectifs produit

1. Offrir une alternative desktop (Windows/Mac/Linux, via les cibles Flutter natives déjà scaffoldées dans `windows/`, `macos/`, `linux/`) au client PySide6, sans régression fonctionnelle sur les flux critiques (paiements, ventes, notes, présences, rapports).
2. Reproduire fidèlement les règles métier et permissions déjà imposées par `ecole_nginx`, plutôt que de les réinventer côté client.
3. Adopter une UI plus moderne et cohérente avec le web (`AdminLayout.vue`) tout en conservant les libellés et la hiérarchie du menu du bureau (`kMainNavItems`/`kSecondaryNavItems`, `lib/screens/shell/app_shell.dart`).
4. Étendre — pas seulement reproduire — les mécanismes de sécurité existants quand des limites réelles sont identifiées (ex : flux d'autorisation par PIN, voir §7 ter).
5. Conserver une architecture client plus simple à maintenir que le bureau : un seul module HTTP (`lib/core/api_client.dart`, `Dio`) au lieu des ~8 implémentations dupliquées identifiées dans `school_client` (`docs/school_client-PRD.md` §6).

## 3. Utilisateurs cibles / personas

Identiques à `school_client` (même backend, même matrice rôle→permissions) : Personnel d'accueil/secrétariat, Caissier, Responsable financier, Comptable, Professeur, Responsable des admissions, Responsable pédagogique, Administrateur/Direction. La visibilité du menu est strictement pilotée par le rôle (`AuthState.roleNavItems`, `lib/state/auth_state.dart:30-75`) — ex. un `teacher` ne voit que Notes/Présences/Profile/Actualiser, un `Caissier` voit Paiement/Finances/Rapport/Étudiant/Profile, seul `admin` voit la totalité du menu (Administration, Promus, Log, Abonnement inclus).

## 4. Fonctionnalités (epics & user stories)

Périmètre constaté dans `lib/screens/shell/app_shell.dart` : **chaque entrée du menu principal et secondaire a un écran réel** (aucun ne retombe sur `PlaceholderScreen`, qui ne sert que de garde-fou pour un id de nav inconnu) — la couverture fonctionnelle du bureau est donc déjà large.

### 4.1 Connexion & configuration poste
- En tant qu'utilisateur, je configure l'IP/domaine du serveur au premier lancement (`lib/core/ip_storage.dart`, utilisé par `login_screen.dart`).
- En tant qu'utilisateur, je me connecte avec mes identifiants (`auth/login`, `login_as: as_desktop` — même valeur spéciale que `school_client` pour que le serveur accepte tout `userable_type`).
- En tant qu'utilisateur, mon token reste stocké de façon persistante (`lib/core/token_storage.dart`) entre les lancements.

### 4.2 Dashboard
- En tant que direction, je visualise à l'ouverture un tableau de bord (effectifs, paiements, graphiques — `fl_chart`) équivalent à celui du bureau.

### 4.3 Administration, Étudiants, Professeurs, Cours, Promus
- En tant qu'administrateur/personnel, je gère les étudiants (dossier, recherche, changement de classe), les professeurs, les cours, et je déclenche les promotions de fin d'année — mêmes routes que `school_client`/`ecole_nginx`.
- En tant que personnel, j'édite le badge d'un étudiant avec capture caméra (USB via `camera_macos`, ou IP — `lib/screens/etudiant/badge_screen.dart`, équivalent de `toggle_camera()`/`active_camera_ip()` du bureau). **Écart volontaire** : pas de détection automatique de visage par IA ici (présente côté bureau, voir §5) — le recadrage reste manuel.

### 4.4 Notes & Présences
- En tant que professeur, je saisis les notes par cours/évaluation et fais l'appel quotidien (`note_state.dart`, `presence_state.dart`), avec les mêmes contraintes de séquence que l'API impose déjà.

### 4.5 Paiement
- En tant que caissier, j'enregistre un paiement d'écolage, j'imprime un reçu PDF, et je consulte le détail d'un dossier de paiement (versements, retours).
- En tant que rôle sans la permission "Supprimer paiement" (Caissier, etc.), je peux quand même effectuer un **retour de paiement** en saisissant un motif (20-150 caractères) et, si besoin, le PIN d'un admin/Comptable — voir §7 ter pour le détail du mécanisme.

### 4.6 Finances (Vente, Produits, Dépenses, Prêts, Payroll, Autres transactions)
- En tant que caissier, je compose une vente à partir d'un catalogue de produits enregistrés (clic pour ajouter au panier, quantité +/-) — **écart volontaire et explicite** par rapport au bureau, qui saisit nom/catégorie/prix en texte libre à chaque ligne (`vente_composer_screen.dart`).
- En tant que caissier, je clique sur une ligne du tableau des ventes pour rouvrir ce même panneau en mode édition, modifier les lignes ou en supprimer une, sous réserve d'autorisation (§7 ter) — reproduit `on_row_clicked_vente_()`/`vente_show()` du bureau (`Controllers/Main.py:5240-5253`).
- En tant que comptable, j'enregistre une dépense ou une autre transaction ponctuelle, je gère des prêts (taux, remboursement) et la paie du personnel (payroll).
- Toute suppression de vente/dépense/transaction, et toute modification d'une vente/dépense/transaction déjà enregistrée, suit désormais le même flux motif + autorisation que le retour de paiement (§7 ter).

### 4.7 Rapports
- En tant que direction, je génère les mêmes rapports PDF/Excel que le bureau (financier, pédagogique, paiement, export).

### 4.8 Profile, Rôles & Permissions
- En tant qu'utilisateur, je modifie mes informations et mon mot de passe (`lib/screens/profile/profile_screen.dart`, repris du web `adProfile.vue` faute d'équivalent sur le bureau).
- En tant qu'administrateur, je gère les rôles et l'assignation de permissions (`role_assignment_tab.dart`, `permission_assignment_tab.dart`).
- En tant qu'admin/Comptable, je définis ou modifie mon PIN d'autorisation à 6 chiffres depuis mon profil (§7 ter).

### 4.9 Log
- En tant qu'administrateur, je consulte le journal d'activité, avec pour chaque entrée le motif (`reason`) et l'auteur de l'autorisation distincts de l'auteur de l'action quand applicable (§7 ter).

### 4.10 Paramètres
- En tant qu'administrateur, je configure examens, facultés, années académiques, classes, paramètres de paiement, frais et frais divers.

### 4.11 Abonnement
- En tant qu'administrateur, je consulte le statut de mon abonnement et son historique (même route `GET /api/v1/abonnement` que `school_client`, voir `docs/ecole_nginx-PRD.md` §4.7).

## 5. Hors périmètre actuel (constaté dans le code)

- **Détection de visage par IA** pour le recadrage de badge : présente côté `school_client`, absente ici (aucune dépendance ML/vision dans `pubspec.yaml`) — le recadrage est manuel.
- **Mode hors-ligne / cache local** : comme `school_client`, aucune synchronisation différée ; dépendance totale à la connexion au serveur.
- **Flux d'autorisation par PIN (§7 ter)** : câblé uniquement sur Paiement/Vente/Dépense/Transaction (les actions explicitement demandées) — pas encore étendu à d'autres suppressions/modifications sensibles de l'app si elles existent ailleurs (étudiants, notes...).
- **Frontend web Vue.js (`ecole_nginx/frontend`)** : n'a aucune intégration du flux PIN — seuls le bureau et `flutter_version` l'exposent actuellement.

## 6. Risques / dette technique identifiée

- Aucun test automatisé (`test/`) constaté au-delà du squelette par défaut `flutter create` — la fidélité au bureau repose pour l'instant sur la revue manuelle et `flutter analyze`.
- Couplage fort entre certains écrans et leur `State` Provider correspondant (1:1, ex. `VenteTab`↔`VenteState`) : cohérent avec le choix d'architecture (Provider + ChangeNotifier), mais à surveiller si le nombre d'écrans continue de croître.

## 7. Mise à jour — build multiplateforme (état)

Les répertoires `windows/`, `macos/`, `linux/` sont déjà scaffoldés (cibles Flutter natives activées) — un pipeline CI dédié à la production d'exécutables pour les trois plateformes reste à mettre en place (hors périmètre de ce document, à traiter séparément si demandé).

## 7 bis. Mise à jour — panneau de vente, parité d'édition (livré)

- Clic sur une ligne du tableau des ventes (`vente_tab.dart`) → ouverture du panneau de composition en mode édition (`VenteComposerScreen(editing: ...)`), pré-rempli via `GET order-vente/{vente}` — reproduit le flux du bureau (`on_row_clicked_vente_()`/`vente_show()`).
- **Bug corrigé** : l'ancien bouton de suppression par ligne du tableau principal utilisait `Vente.order_itemId` (un code à 6 chiffres généré sur la vente elle-même) comme s'il s'agissait de l'id réel d'un `OrderItem` — il ne supprimait jamais la bonne ligne. La suppression se fait désormais à l'intérieur du panneau, sur l'id réel de chaque ligne.
- Décrémenter une ligne déjà enregistrée jusqu'à 0 (boutons +/- ou saisie manuelle de quantité) déclenche désormais le même flux motif + autorisation qu'une suppression explicite, au lieu de retirer silencieusement la ligne sans contrôle.
- **Bug corrigé** : ouvrir le panneau en mode édition levait `setState() or markNeedsBuild() called during build` (`VenteState.clearCart()`/`loadForEdit()` appelés depuis `initState()`, qui appellent `notifyListeners()` pendant la construction du widget). Corrigé en reportant ces appels après le premier frame (`WidgetsBinding.instance.addPostFrameCallback`).
- **Bug corrigé — plafond de stock absent en édition** : `GET order-vente/{vente}` (`RVente.py show_order_items`) ne renvoyait pas `produit_id` dans sa réponse, donc une ligne rechargée en édition n'était jamais reliée à sa fiche produit et n'avait aucun plafond de stock (`stockDisponible`). Corrigé en deux temps : la route renvoie désormais `produit_id`, et `VenteState.applyStockCaps()` (appelée juste après `loadForEdit()`, dans `vente_composer_screen.dart`) résout `stockDisponible` pour chaque ligne depuis le catalogue déjà chargé (`ProduitState.items`).
- **Bug corrigé — suppression de ligne de vente impossible** : `DELETE /order_item` (`destroy_order_item`, `RVente.py:238-240`) typait `order_item_id`/`vente_id` en `int`, alors que `OrderItem.id`/`Vente.id` sont des UUID (`CHAR(36)`) — toute suppression échouait avec une erreur de validation Pydantic (`"Input should be a valid integer, unable to parse string as an integer"`). Pré-existant, jamais exercé avant l'ajout du panneau d'édition (aucune UI n'appelait cette route auparavant). Corrigé en retypant les deux paramètres en `str`.

## 7 ter. Mise à jour — autorisation par PIN (double approbation) (livré)

Voir `ecole_nginx/PRD.md` §4.3 "S5" pour le détail complet du mécanisme côté serveur (`verify_dual_auth`/`DualAuthChecker`, `User.code_pin`, `Log.reason`/`Log.authorization_id`, contrainte de non-divulgation sur l'unicité des PIN). Côté `flutter_version` :

- `lib/core/dual_auth.dart` centralise le flux : `runWithPinApproval()` (rejoue l'action avec un `approval_token` obtenu via `POST auth/autorisation-access-pin` si le serveur répond 202) et `showReasonDialog()` (motif obligatoire, 20-150 caractères).
- Câblé sur : retour de paiement (`paiement_detail_screen.dart`), suppression de ligne de vente/dépense/transaction, modification d'une vente/dépense/transaction déjà enregistrée.
- **Bug corrigé** : le bouton Reçu de `paiement_detail_screen.dart` ignorait silencieusement l'erreur retournée par `printRecu()` — aucune erreur n'était jamais affichée à l'utilisateur en cas d'échec. Corrigé en affichant désormais un SnackBar sur erreur.
- **Bug critique corrigé (le flux entier était inopérant)** : `Dio` ne lève **jamais** d'exception pour un statut 2xx — sa `validateStatus` par défaut (`status >= 200 && status < 300`) traite un **202** comme un succès ordinaire. Or toute la détection du sentinel `kApprovalRequiredError` (dans `paiement_state.dart`, `vente_state.dart`, `depense_state.dart`, `transaction_state.dart` — 7 occurrences) était écrite dans le bloc `catch`, jamais atteint pour un 202 : aucune suppression/modification ne demandait donc jamais de PIN pour un rôle sans permission, et aucune erreur n'était affichée — la requête semblait simplement "réussir" sans qu'aucune action n'ait eu lieu côté serveur (`DualAuthChecker` ayant bloqué la route avant d'exécuter quoi que ce soit). Corrigé en vérifiant `response.statusCode == 202` directement après l'`await`, sur le chemin de succès, plutôt que dans le `catch`.
- **Reçu de paiement (`PaiementState.printRecu`)** : `Process.run('open'/'cmd'/'xdg-open', ...)` n'échoue jamais avec une exception sur un exit code non nul — un PDF correctement téléchargé mais qu'aucun lecteur par défaut n'arrivait à ouvrir passait donc pour un succès muet (aucune erreur, aucun visualiseur ne s'ouvre). Corrigé en vérifiant `ProcessResult.exitCode` et en renvoyant l'erreur réelle (`stderr`) si non nul. **Le même motif existe, non corrigé, dans** `vente_state.dart` (`printRecu`), `note_state.dart`, `rapport_state.dart`, `students_state.dart`, `badge_screen.dart` — à appliquer si le même symptôme (PDF généré mais rien ne s'ouvre, sans erreur) y est observé.
- Nouvelle carte "PIN d'autorisation" dans le profil (`profile_screen.dart`), visible uniquement pour les rôles admin/Comptable.
