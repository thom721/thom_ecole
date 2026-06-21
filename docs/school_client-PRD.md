# PRD — school_client (Application desktop Lekol360)

## 1. Contexte et problème

Le personnel administratif, les caissiers et les enseignants des établissements ont besoin d'un poste de travail unique, installé localement, pour gérer le quotidien scolaire sans dépendre uniquement d'une interface web : saisie rapide, impression de documents, capture photo pour badges, et fonctionnement même avec une connexion réseau locale limitée. `school_client` est cette application desktop qui s'appuie sur l'API `ecole_nginx` — initialement Windows uniquement, désormais fonctionnelle sur Mac/Linux également.

## 2. Objectifs produit

1. Offrir une interface de gestion complète et rapide pour le personnel sur site (saisie, recherche, impression).
2. Permettre la génération immédiate de documents officiels (reçus, bulletins, badges) sans dépendre d'un serveur d'impression distant.
3. Sécuriser l'accès aux fonctions sensibles via authentification et permissions, avec une validation administrateur renforcée pour certaines actions.
4. Fournir un éditeur de badge intégré avec assistance par IA (détection de visage) pour accélérer la production des cartes étudiant/personnel.
5. Être distribuable comme exécutable Windows autonome, sans installation d'environnement Python par l'utilisateur final.
6. Fonctionner également sur Mac/Linux pour les établissements équipés en conséquence (objectif ajouté en cours de projet, voir section 7).

## 3. Utilisateurs cibles / personas

- **Personnel d'accueil/secrétariat** : inscrit les étudiants, édite les badges, imprime les attestations.
- **Caissier** : enregistre les paiements et ventes, imprime les reçus.
- **Professeur** : saisit les notes, fait l'appel.
- **Administrateur/Direction** : configure les paramètres (tarifs, années, classes, examens), consulte le dashboard, valide les actions sensibles, gère les rôles/permissions.

## 4. Fonctionnalités (epics & user stories)

### 4.1 Connexion & configuration poste
- En tant qu'utilisateur, je configure l'IP/domaine du serveur lors du premier lancement.
- En tant qu'utilisateur, je me connecte avec mes identifiants et reste connecté via un token stocké de façon chiffrée.
- En tant qu'administrateur, je dois valider certaines actions sensibles par une authentification admin supplémentaire.

### 4.2 Étudiants & classes
- En tant que personnel, je crée/modifie/recherche un étudiant et l'affecte à une classe.
- En tant que personnel, je change la classe d'un étudiant (changement de niveau, redoublement).

### 4.3 Paiements & ventes
- En tant que caissier, je configure les paramètres de paiement par classe (montant, devise, nombre d'échéances, frais accessoires).
- En tant que caissier, j'enregistre un paiement d'écolage et imprime immédiatement un reçu PDF (mise en page 3 reçus/page).
- En tant que caissier, j'enregistre une vente d'articles (uniformes, fournitures) avec plusieurs lignes et imprime un reçu de vente.
- En tant qu'administrateur, je configure les frais d'inscription et frais divers par niveau/année.

### 4.4 Notes & examens
- En tant que professeur, je configure les paramètres d'un examen (dates, coefficients) et saisis les notes des étudiants.
- En tant que personnel, je génère un bulletin scolaire (individuel ou en lot) en PDF.

### 4.5 Présences
- En tant que professeur, je fais l'appel d'une classe pour la journée.

### 4.6 Badges
- En tant que personnel, j'importe une photo (fichier ou capture caméra) et le système détecte automatiquement le visage pour le recadrage.
- En tant que personnel, j'ajuste manuellement zoom/rotation/position, avec undo/redo, avant export du badge en PNG ou PDF (lot recto/verso).

### 4.7 Rapports & exports
- En tant que direction, je génère un rapport global, un rapport pédagogique, un rapport de paiement ou un export Excel directement depuis l'application.
- En tant que personnel, j'imprime une attestation/liste d'inscription.

### 4.8 Prêts
- En tant qu'administrateur, je consulte les données nécessaires à l'octroi d'un prêt et suis son remboursement.

### 4.9 Tableau de bord
- En tant que direction, je visualise des graphiques (paiements, inscriptions) et des indicateurs clés à l'ouverture de l'application.

### 4.10 Personnel & rôles
- En tant qu'administrateur, je gère les comptes professeurs/personnel et consulte les journaux d'activité (logs).

### 4.11 Abonnement & renouvellement
- En tant qu'administrateur, je consulte le statut de mon abonnement (actif/expiré, clé actuelle, jours restants) et l'historique complet des activations.
- En tant qu'administrateur, je vois apparaître un bouton Renouveler dès qu'il reste 15 jours ou moins avant expiration, qui m'amène sur le site de paiement avec mon établissement déjà identifié (par le mac du serveur, pas du poste que j'utilise).

## 5. Hors périmètre actuel (constaté dans le code)

- Mode totalement hors-ligne avec synchronisation différée : prototype présent (`Sync_data.py`/`Sync_to_api.py`) mais non activé en production — l'app dépend d'une connexion au serveur.
- Cache SQLite local complet : non finalisé.

## 6. Risques / dette technique identifiée

- `Controllers/Main.py` (~14k lignes) et `Models/enregistrement.py` (~28k lignes) concentrent une grande partie de la logique métier — risque de maintenabilité et de couplage fort à isoler progressivement.
- Nombreux fichiers et dossiers dupliqués ("copy", anciennes versions d'UI) à nettoyer pour clarifier la version de référence.
- Dépendance à des certificats SSL stockés localement sur le poste — procédure de déploiement/rotation à documenter.
- Packaging dual (Nuitka + PyInstaller) : décider d'un outil unique pour limiter la dette de configuration.
- **Modules HTTP dupliqués** : la logique « URL de base + endpoint » est réimplémentée indépendamment dans au moins 8 fichiers (`Config.py`, `Models/ApiHandler.py`, `Models/enregistrement.py`, `Models/fetch_data.py`, `Models/AsyncDataHandler.py`, `Helper/Check_data.py`, plus des variantes mortes). C'est cette duplication qui a permis au bug de préfixe `/v1` manquant de passer inaperçu dans plusieurs fichiers à la fois — à factoriser pour éviter une récidive.
- Fichiers morts confirmés non importés par l'app (`Models/AsyncDataHandlerPdf.py`, `Models/AsyncRequestHandler.py`, `Models/AsyncRequestHandler1.py`, `Models/connection.py`, `Helper/Check.py`, `Helper/Check_and_insert.py`, `Helper/Check_db.py`, `Helper/Sync_data.py`, la classe `CertificateManager` dans `Controllers/Main.py`) — candidats à suppression lors d'un prochain nettoyage.

## 7 bis. Mise à jour — abonnement & renouvellement (livré)

- Nouvel onglet Abonnement (admin uniquement) + bouton Renouveler conditionnel, ouvrant le site `infini-software` (voir `docs/infini-software-PRD.md`) avec l'établissement pré-identifié.
- **Bug réel corrigé en cours de build** : le mac envoyé au site de paiement était initialement celui du poste client local (`get_mac_address()`), pas celui du serveur — aurait fait échouer toute identification dès qu'un admin ouvre l'onglet depuis un poste différent du serveur. Le mac vient désormais de la réponse API (`v1/abonnement`), jamais d'une détection locale.
- Lien de renouvellement actuellement pointé en dur sur l'instance locale d'`infini-software` (tests de bout en bout) — à reconfigurer vers le domaine de production avant livraison.

## 7. Mise à jour — support Mac/Linux (livré)

- Suppression des imports Windows-only morts (`win32api`/`win32print`) qui empêchaient le module de se charger du tout hors Windows.
- Chemins `%APPDATA%`/`%LOCALAPPDATA%` rendus cross-platform sans changer le comportement Windows.
- `requirements.txt` : dépendances Windows-only (`pywin32`, `pefile`, etc.) marquées conditionnelles (`sys_platform == "win32"`).
- Confiance SSL cross-platform via `truststore` (consulte le Keychain Mac / ca-certificates Linux au lieu du seul bundle `certifi`).
- **Bug réel, indépendant de la plateforme, découvert pendant les tests** : préfixe `/api/v1/` manquant dans plusieurs constructions d'URL côté client (le serveur n'expose aucune route sous `/api/` nu), et `request_certificate_ss()` appelait `/asking` en POST alors que la route serveur est en GET — confirmés et corrigés après vérification directe contre le serveur réel.
