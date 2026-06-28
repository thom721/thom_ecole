# Product Requirements Document (PRD)
## École Nginx - Système de Gestion Scolaire

**Version**: 1.0
**Date**: 15 Mai 2026
**Statut**: En production

---

## 1. Vue d'ensemble du produit

### 1.1 Description
École Nginx (Le Mignon School Management System) est une plateforme complète de gestion d'établissements scolaires développée pour les écoles francophones, particulièrement en Haïti. C'est une application Windows autonome qui intègre un serveur backend Python, une interface web moderne et un système de gestion de base de données MySQL sécurisé.

### 1.2 Vision
Fournir une solution tout-en-un pour la gestion administrative, pédagogique et financière des établissements scolaires, avec un accent sur la simplicité d'utilisation, la sécurité et la génération automatisée de rapports.

### 1.3 Objectifs principaux
- Centraliser la gestion des étudiants, enseignants, classes et cours
- Automatiser la gestion des paiements et la comptabilité scolaire
- Faciliter le suivi académique (notes, présences, bulletins)
- Générer automatiquement des rapports PDF professionnels
- Protéger les données avec chiffrement et authentification robuste
- Fonctionner en mode autonome sans dépendances cloud

---

## 2. Utilisateurs cibles

### 2.1 Personas

#### Administrateur scolaire
- **Rôle**: Directeur, secrétaire général
- **Besoins**: Vue d'ensemble complète, gestion des utilisateurs, rapports financiers
- **Niveau technique**: Basique à intermédiaire

#### Personnel comptable
- **Rôle**: Comptable, caissier
- **Besoins**: Enregistrement paiements, suivi des frais, rapports financiers
- **Niveau technique**: Basique

#### Enseignant
- **Rôle**: Professeur
- **Besoins**: Saisie des notes, gestion des présences, consultation des classes
- **Niveau technique**: Basique

#### Personnel administratif
- **Rôle**: Secrétariat
- **Besoins**: Gestion dossiers étudiants, inscriptions, génération documents
- **Niveau technique**: Basique

---

## 3. Fonctionnalités principales

### 3.1 Gestion des étudiants

#### F1.1 - Dossier étudiant complet
**Priorité**: Critique
**Description**: Création et gestion de profils étudiants avec informations complètes

**Critères d'acceptation**:
- Informations personnelles (nom, prénom, date de naissance, photo)
- Numéro d'identification unique
- Coordonnées (adresse, téléphone, email)
- Informations familiales (responsables légaux)
- Affectation à une classe et faculté
- Statut de l'étudiant (actif, inactif, diplômé)
- Historique académique

**Données requises**:
```
- identifiant (auto-généré)
- nom, prenom, sexe
- date_naissance, lieu_naissance
- adresse_complete, telephone, email
- photo (base64)
- responsable_id (lien vers table responsables)
- classe_id, faculte_id
- annee_academique_id
- statut
```

#### F1.2 - Recherche et filtrage
**Priorité**: Élevée
**Description**: Système de recherche avancé des étudiants

**Fonctionnalités**:
- Recherche par nom, prénom, identifiant
- Filtrage par classe, niveau, faculté, statut
- Tri multi-critères
- Pagination (25/50/100 résultats par page)
- Export des résultats en Excel

#### F1.3 - Import/Export de données
**Priorité**: Moyenne
**Description**: Import massif d'étudiants via fichiers Excel

**Formats supportés**: .xlsx, .xls
**Validations**: Format, doublons, champs obligatoires

---

### 3.2 Gestion financière

#### F2.1 - Enregistrement des paiements
**Priorité**: Critique
**Description**: Système de suivi des paiements mensuels des étudiants

**Structure de paiement**:
```json
{
  "paiement": {
    "etudiant_id": "UUID",
    "annee_academique_id": "UUID",
    "montant_total": 50000,
    "montant_paye": 15000,
    "balance": 35000,
    "aide_financiere": 5000,
    "mensualites": [
      {
        "mois": "Septembre",
        "montant_du": 5000,
        "montant_paye": 5000,
        "statut": "payé"
      },
      {
        "mois": "Octobre",
        "montant_du": 5000,
        "montant_paye": 3000,
        "statut": "partiel"
      }
    ],
    "historique": [
      {
        "date": "2024-09-15",
        "montant": 5000,
        "methode": "cash",
        "reference": "REF001"
      }
    ]
  }
}
```

**Fonctionnalités**:
- Paiement mensuel ou en avance
- Détection automatique du prochain mois à payer
- Calcul automatique des balances
- Support multi-devises (GDES par défaut)
- Historique complet des transactions
- Génération automatique de reçus PDF

#### F2.2 - Paramétrage des frais
**Priorité**: Élevée
**Description**: Configuration des frais par niveau et faculté

**Paramètres configurables**:
- Frais d'inscription
- Frais de scolarité mensuelle
- Frais divers (uniforme, livres, activités)
- Pénalités de retard
- Réductions et bourses

#### F2.3 - Rapports financiers
**Priorité**: Élevée
**Description**: Génération de rapports financiers détaillés

**Types de rapports**:
- Rapport global des paiements (par période)
- Rapport par classe/niveau
- Liste des impayés
- Prévisions de trésorerie
- Export comptable

---

### 3.3 Gestion académique

#### F3.1 - Gestion des classes et niveaux
**Priorité**: Critique
**Description**: Organisation hiérarchique des classes

**Structure**:
```
Niveau (ex: Secondaire 1)
  └─ Classe (ex: S1-A, S1-B)
      └─ Étudiants
```

**Fonctionnalités**:
- Création/modification de niveaux
- Création de classes avec capacité maximale
- Affectation d'étudiants aux classes
- Réaffectation en cas de changement
- Historique des classes par étudiant

#### F3.2 - Gestion des cours
**Priorité**: Élevée
**Description**: Configuration des matières et affectations

**Données**:
- Nom du cours
- Code du cours
- Coefficient
- Professeur assigné
- Classe(s) concernée(s)
- Volume horaire
- Type (obligatoire, optionnel)

#### F3.3 - Saisie des notes
**Priorité**: Critique
**Description**: Enregistrement et calcul des notes

**Fonctionnalités**:
- Saisie par matière et période
- Support de multiples types d'évaluation (devoirs, examens, participation)
- Calcul automatique des moyennes (avec coefficients)
- Validation avant publication
- Modification avec traçabilité

**Paramètres d'examen**:
- Note maximale
- Note de passage
- Coefficient par type d'évaluation
- Pondération par trimestre/semestre

#### F3.4 - Gestion des présences
**Priorité**: Moyenne
**Description**: Suivi de l'assiduité des étudiants

**Fonctionnalités**:
- Prise de présence quotidienne ou par cours
- Marquage: Présent, Absent, Retard, Absence justifiée
- Calcul du taux de présence
- Alertes pour absentéisme excessif
- Rapports de présence par période

---

### 3.4 Génération de documents

#### F4.1 - Bulletins de notes (Report Cards)
**Priorité**: Critique
**Description**: Génération automatique de bulletins scolaires au format PDF

**Contenu**:
- Informations étudiant (photo, identité, classe)
- Notes par matière avec moyennes
- Moyennes générales par période
- Rang dans la classe
- Appréciations des professeurs
- Mention et décision du conseil (admission, redoublement)
- Signature numérique de l'établissement

**Format**: PDF professionnel avec logo et mise en page personnalisable

#### F4.2 - Reçus de paiement
**Priorité**: Critique
**Description**: Génération automatique de reçus après chaque paiement

**Contenu**:
- Numéro de reçu unique
- Date et heure du paiement
- Informations étudiant
- Détail du paiement (montant, méthode, référence)
- Balance restante
- Période couverte
- Signature et cachet

#### F4.3 - Autres rapports PDF
**Priorité**: Moyenne
**Description**: Collection de rapports administratifs

**Types disponibles**:
- Liste d'inscriptions
- Rapport de paiements global
- Rapports pédagogiques
- Certificats de scolarité
- Attestations diverses
- Listes de classes

---

### 3.5 Gestion des utilisateurs et permissions

#### F5.1 - Système RBAC (Role-Based Access Control)
**Priorité**: Critique
**Description**: Contrôle d'accès basé sur les rôles avec affichage conditionnel des menus

**Règle de base**: L'utilisateur doit avoir au minimum le rôle "User" pour accéder à l'interface personnel.

---

**Rôles prédéfinis et leurs accès**:

##### 0. User (Utilisateur de base)
**Description**: Rôle minimal pour tout utilisateur authentifié. Ce rôle seul ne permet qu'un accès très limité.

**Modules accessibles**:
- ✅ **Profile**: Gestion de son propre profil uniquement
  - Modification de ses informations personnelles
  - Changement de mot de passe
  - Gestion de son avatar/photo

**Restrictions**:
- ❌ Aucun accès au Dashboard
- ❌ Aucun accès aux Étudiants
- ❌ Aucun accès aux Paiements
- ❌ Aucun accès à la Trésorerie
- ❌ Aucun accès aux Notes
- ❌ Aucun accès aux Présences
- ❌ Aucun accès aux Cours
- ❌ Aucun accès aux Professeurs
- ❌ Aucun accès aux Rapports
- ❌ Aucun accès aux Paramètres
- ❌ Aucun accès à la gestion des Utilisateurs

**Comportement**:
- À la connexion, l'utilisateur avec uniquement le rôle "User" est redirigé vers sa page de profil
- Un message l'informe qu'il doit contacter l'administrateur pour obtenir des permissions supplémentaires
- Le menu de navigation n'affiche que l'option "Mon Profil"

**Note importante**:
> Ce rôle est destiné aux comptes en attente d'attribution de rôle métier. Tout utilisateur actif devrait avoir au moins un rôle supplémentaire (Caissier, Responsable financier, etc.)

---

##### 1. Caissier (si uniquement caissier)
**Modules accessibles**:
- ✅ **Paiement**: Consultation et enregistrement des paiements
- ✅ **Trésorerie**: Consultation de la trésorerie
- ✅ **Rapport**: Génération et consultation des rapports financiers
- ✅ **Étudiant**: Consultation et recherche d'étudiants (pour enregistrer paiements)
- ✅ **Profile**: Gestion de son propre profil (SANS la partie gestion des rôles)

**Restrictions**:
- ❌ Pas d'accès aux paramètres système
- ❌ Pas d'accès aux modules pédagogiques (notes, cours, présences)
- ❌ Pas de gestion des utilisateurs
- ⚠️ Profile: Section "Rôles et permissions" masquée

---

##### 2. Responsable financier
**Modules accessibles**:
- ✅ **Paiement**: Gestion complète des paiements
- ✅ **Trésorerie**: Gestion complète de la trésorerie
- ✅ **Rapport**: Tous les rapports financiers
- ✅ **Étudiant**: Consultation et gestion des dossiers étudiants

**Permissions spécifiques**:
- Validation des paiements
- Gestion des frais et paramètres de paiement
- Export des données financières
- Rapports de trésorerie détaillés

**Restrictions**:
- ❌ Pas d'accès aux notes et présences
- ❌ Pas de gestion des cours
- ❌ Pas de gestion des utilisateurs

---

##### 3. Responsable des admissions
**Modules accessibles**:
- ✅ **Étudiant**: Gestion complète des étudiants (CRUD)
- ✅ **Inscription**: Gestion des inscriptions
- ✅ **Documents**: Génération de documents d'inscription

**Permissions spécifiques**:
- Création/modification/suppression d'étudiants
- Gestion des responsables légaux
- Affectation aux classes
- Import/export des données étudiants
- Génération de certificats de scolarité

**Restrictions**:
- ❌ Pas d'accès aux paiements
- ❌ Pas d'accès aux notes
- ❌ Pas d'accès à la trésorerie

---

##### 4. Responsable pédagogique
**Modules accessibles**:
- ✅ **Dashboard**: Vue d'ensemble (infos paiement masquées ⭐)
- ✅ **Rapport**: Rapports pédagogiques uniquement
- ✅ **Cours**: Gestion complète des cours et matières
- ✅ **Étudiant**: Consultation des dossiers étudiants
- ✅ **Paramètre**: Consultation UNIQUEMENT (lecture seule)
- ✅ **Notes**: Gestion complète des notes
- ✅ **Présences**: Gestion complète des présences

**Restrictions spécifiques**:
- ⭐ **Dashboard**: Montants financiers affichés en étoiles (*****)
- 🔒 **Paramètre**: Mode lecture seule (pas de modification autorisée)
- ❌ **Paiement**: Aucun accès
- ❌ **Trésorerie**: Aucun accès

**Permissions spécifiques**:
- Validation des notes
- Configuration des examens
- Gestion du calendrier académique
- Rapports pédagogiques (bulletins, statistiques de classe)

---

##### 5. Comptable
**Modules accessibles**:
- ✅ **Trésorerie**: Gestion complète
- ✅ **Rapport**: Tous les rapports (financiers et généraux)
- ✅ **Dashboard**: Tableau de bord complet avec infos financières
- ✅ **Étudiant**: Consultation des dossiers étudiants
- ✅ **Paramètre**: Gestion des paramètres financiers
- ✅ **Paiement**: Consultation et validation des paiements
- ✅ **Professeurs**: Consultation des enseignants (pour gestion salaires)

**Permissions spécifiques**:
- Gestion des dépenses
- Gestion des transactions diverses
- Paramétrage des frais de scolarité
- Export comptable
- Rapports financiers avancés
- Gestion des salaires (si module activé)

**Restrictions**:
- ❌ Pas de gestion des notes
- ❌ Pas de gestion des cours
- ❌ Pas de gestion des utilisateurs

---

##### 6. Admin / Super Admin
**Modules accessibles**:
- ✅ **TOUS LES MODULES** selon les permissions attribuées

**Principe**:
- L'administrateur a accès à tous les modules
- Les accès spécifiques sont définis par les **permissions granulaires**
- Un admin peut avoir des permissions restreintes selon la configuration
- Le Super Admin a TOUTES les permissions sans restriction

**Permissions complètes disponibles**:
```python
Permissions = [
    # Étudiants
    "view_students", "create_students", "edit_students", "delete_students",
    "import_students", "export_students",

    # Paiements
    "view_payments", "create_payments", "edit_payments", "delete_payments",
    "validate_payments", "refund_payments",

    # Notes
    "view_grades", "create_grades", "edit_grades", "delete_grades",
    "validate_grades", "publish_grades",

    # Présences
    "view_attendance", "mark_attendance", "edit_attendance",

    # Rapports
    "view_reports", "generate_reports", "export_reports",
    "view_financial_reports", "view_academic_reports",

    # Cours et classes
    "view_courses", "create_courses", "edit_courses", "delete_courses",
    "view_classes", "create_classes", "edit_classes", "delete_classes",

    # Professeurs
    "view_teachers", "create_teachers", "edit_teachers", "delete_teachers",

    # Trésorerie
    "view_treasury", "manage_expenses", "manage_transactions",

    # Administration
    "manage_users", "manage_roles", "manage_permissions",
    "manage_settings", "manage_academic_year",
    "view_logs", "view_audit_trail",

    # Système
    "system_backup", "system_restore", "system_configuration"
]
```

---

**Matrice de droits par rôle**:

| Module | User | Caissier | Resp. Financier | Resp. Admissions | Resp. Pédagogique | Comptable | Admin |
|--------|------|----------|-----------------|------------------|-------------------|-----------|-------|
| **Dashboard** | ❌ | ❌ | ❌ | ❌ | ✅ (masqué $) | ✅ | ✅ |
| **Étudiant** | ❌ | 👁️ | ✅ | ✅ | 👁️ | 👁️ | ✅ |
| **Paiement** | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Trésorerie** | ❌ | 👁️ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Notes** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Présences** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Cours** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Professeurs** | ❌ | ❌ | ❌ | ❌ | ❌ | 👁️ | ✅ |
| **Rapport** | ❌ | 💰 | 💰 | ❌ | 📚 | ✅ | ✅ |
| **Paramètre** | ❌ | ❌ | ❌ | ❌ | 👁️ | 💰 | ✅ |
| **Profile** | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Utilisateurs** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Légende**:
- ✅ Accès complet (lecture + écriture)
- 👁️ Lecture seule
- ❌ Aucun accès
- ⚠️ Accès partiel (profile sans gestion rôles)
- 💰 Rapports financiers uniquement
- 📚 Rapports pédagogiques uniquement
- (masqué $) Données financières affichées en *****

---

**Implémentation technique**:

**Frontend (Vue.js)**:
```javascript
// Exemple de directive pour masquer/afficher selon rôle
const userRole = store.getters.getUserRole;
const userPermissions = store.getters.getUserPermissions;

// Dans les composants Vue
computed: {
  canViewPayments() {
    return ['Caissier', 'Responsable financier', 'Comptable', 'Admin']
      .includes(this.userRole);
  },

  shouldMaskFinancials() {
    return this.userRole === 'Responsable pédagogique';
  },

  canEditParameters() {
    return this.userRole !== 'Responsable pédagogique'
      && this.userPermissions.includes('manage_settings');
  }
}
```

**Backend (FastAPI)**:
```python
# Décorateur de vérification de rôle
@router.get("/paiement")
async def get_payments(
    current_user: User = Depends(require_role(["Caissier", "Responsable financier", "Comptable", "Admin"]))
):
    # Logique métier
    pass

# Vérification granulaire de permission
@router.post("/etudiant")
async def create_student(
    current_user: User = Depends(require_permission("create_students"))
):
    # Logique métier
    pass
```

#### F5.2 - Authentification JWT
**Priorité**: Critique
**Description**: Authentification sécurisée avec tokens

**Fonctionnalités**:
- Login avec email/username et mot de passe
- Tokens JWT avec expiration configurable
- Refresh tokens pour sessions prolongées
- Blacklist de tokens (logout)
- Vérification de permissions avant chaque action

#### F5.3 - Audit et logs
**Priorité**: Élevée
**Description**: Traçabilité complète des actions

**Informations enregistrées**:
- Utilisateur et rôle
- Action effectuée (create, update, delete, view)
- Table et ID de l'enregistrement
- Anciennes et nouvelles valeurs (pour update)
- Adresse IP et timestamp
- Contexte de la requête

---

### 3.6 Configuration et paramétrage

#### F6.1 - Paramètres de l'établissement
**Priorité**: Élevée
**Description**: Configuration globale de l'école

**Paramètres**:
- Nom de l'établissement
- Logo et en-tête de documents
- Coordonnées (adresse, téléphone, email, site web)
- Numéro d'agrément
- Devise utilisée
- Année académique active
- Langue de l'interface

#### F6.2 - Années académiques
**Priorité**: Critique
**Description**: Gestion des cycles scolaires

**Fonctionnalités**:
- Création d'années académiques (ex: 2024-2025)
- Définition des périodes (trimestres/semestres)
- Activation d'une année comme "courante"
- Clôture d'année avec archivage
- Historique complet

---

## 4. Exigences techniques

### 4.1 Architecture

#### Stack technologique
**Backend**:
- Langage: Python 3.10+
- Framework API: FastAPI 0.126.0
- Serveur ASGI: Uvicorn (8 workers)
- ORM: SQLAlchemy 2.0.45
- Migrations: Alembic

**Frontend**:
- Framework: Vue.js 3.5.27
- Build tool: Vite
- UI: Tailwind CSS 4.1.18
- State: Pinia 3.0.4
- Routing: Vue Router 5.0.1

**Base de données**:
- SGBD: MySQL 8.0.41
- Port: 3307
- Connexions SSL/TLS obligatoires
- Certificats CA, serveur, client

**Infrastructure**:
- Web server: Nginx 1.26.3
- Ports: 80 (HTTP), 443 (HTTPS), 9001 (API)
- Services Windows: MySQLEcole, NginxAplekol

**Desktop**:
- GUI: PySide6 (Qt6)
- Build: Nuitka (compilation Python → C++ → EXE)
- Format: Exécutable Windows standalone

#### Architecture logicielle
```
┌─────────────────────────────────────────┐
│   Interface Utilisateur (Vue.js)        │
│   - Composants réactifs                 │
│   - Formulaires validés                 │
│   - Tableaux avec pagination            │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS
               │
┌──────────────▼──────────────────────────┐
│   Web Server (Nginx)                    │
│   - Reverse proxy                       │
│   - SSL/TLS termination                 │
│   - Fichiers statiques                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   API REST (FastAPI)                    │
│   - Routes (45+ fichiers)               │
│   - Middleware (auth, rate limit, CORS) │
│   - Dépendances (validation)            │
│   - Contrôleurs métier                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   ORM (SQLAlchemy)                      │
│   - Modèles (30+ tables)                │
│   - Relations                           │
│   - Validation                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Base de données (MySQL)               │
│   - Tables normalisées                  │
│   - Index optimisés                     │
│   - Contraintes d'intégrité             │
└─────────────────────────────────────────┘
```

### 4.2 Schéma de base de données

#### Tables principales (30+)

**Académique**:
- `annee_academique`: Années scolaires
- `niveau`: Niveaux d'enseignement
- `classe`: Classes
- `etudiant`: Étudiants
- `professeur`: Enseignants
- `cours`: Matières
- `faculte`: Facultés/départements
- `classe_etudiant`: Affectations classe-étudiant
- `cours_etudiant`: Inscriptions aux cours
- `responsable`: Tuteurs/parents

**Évaluations**:
- `note`: Notes des étudiants
- `param_exam`: Paramètres d'examen
- `presence`: Présences
- `promus`: Passages de classe

**Financier**:
- `paiement`: Paiements étudiants (JSON)
- `parametre_paiement`: Configuration frais
- `frais_inscription`: Frais d'inscription
- `frais_divers`: Autres frais
- `other_transaction`: Transactions diverses
- `paiement_statut`: Statuts de paiement
- `depenses`: Dépenses
- `vente`: Inventaire/ventes

**Système**:
- `user`: Utilisateurs
- `role`: Rôles
- `permission`: Permissions
- `role_has_permission`: Associations rôle-permission
- `profile`: Profils utilisateurs
- `log`: Journaux d'audit
- `blacklisted_token`: Tokens invalidés
- `password_reset_code`: Codes de réinitialisation

#### Relations clés
```sql
-- Un étudiant peut avoir plusieurs paiements
etudiant (1) ──── (N) paiement

-- Un étudiant appartient à une classe
etudiant (N) ──── (1) classe

-- Une classe appartient à un niveau
classe (N) ──── (1) niveau

-- Un cours peut être assigné à plusieurs classes
cours (N) ──── (N) classe

-- Un professeur enseigne plusieurs cours
professeur (1) ──── (N) cours

-- Un étudiant a plusieurs notes
etudiant (1) ──── (N) note

-- Un utilisateur a un rôle
user (N) ──── (1) role
```

### 4.3 Sécurité

#### S1 - Chiffrement des données
**Priorité**: Critique

**Méthodes**:
- Mots de passe: BCrypt (work factor 12+)
- Base de données: Connexion SSL/TLS obligatoire
- Clés de licence: Chiffrement Fernet
- Données sensibles: AES-256
- Tokens: JWT avec signature HMAC-SHA256

**Certificats SSL**:
```
C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs\
├── ca-cert.pem        # Autorité de certification
├── server-cert.pem    # Certificat serveur
├── server-key.pem     # Clé privée serveur
├── client-cert.pem    # Certificat client
└── client-key.pem     # Clé privée client
```

#### S2 - Protection contre les attaques
**Mécanismes**:
- **SQL Injection**: ORM SQLAlchemy (requêtes paramétrées)
- **XSS**: Validation Pydantic + sanitization frontend
- **CSRF**: Tokens JWT stateless
- **Rate Limiting**: 100 requêtes/minute par IP
- **Brute Force**: Limitation tentatives login + captcha optionnel
- **Session Hijacking**: Tokens expirables + blacklist

#### S3 - Audit et conformité
**Traçabilité**:
- Tous les changements de données enregistrés dans `log`
- Conservation: Adresse IP, user_id, timestamp, before/after values
- Rapports d'audit générables
- Non-répudiation des actions

#### S4 - Sécurité d'affichage conditionnel (UI/UX)
**Priorité**: Critique
**Description**: Contrôle d'affichage des éléments d'interface selon le rôle et les permissions

**Principe de sécurité en couches**:
1. **Frontend**: Masquage des éléments UI (ergonomie)
2. **Backend**: Validation stricte des permissions (sécurité réelle)

> ⚠️ **Important**: Le masquage frontend NE CONSTITUE PAS une sécurité. Il améliore l'expérience utilisateur en cachant les options inaccessibles. La vraie sécurité est appliquée côté backend avec vérification des permissions avant chaque action.

---

**Implémentation Frontend (Vue.js)**:

**1. Store Pinia - Gestion du rôle utilisateur**:
```javascript
// stores/auth.js
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    role: null,
    permissions: []
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.role,
    userPermissions: (state) => state.permissions,

    // Vérifications de rôle
    isBaseUser: (state) => state.role === 'User',
    isCaissier: (state) => state.role === 'Caissier',
    isResponsableFinancier: (state) => state.role === 'Responsable financier',
    isResponsableAdmissions: (state) => state.role === 'Responsable des admissions',
    isResponsablePedagogique: (state) => state.role === 'Responsable pédagogique',
    isComptable: (state) => state.role === 'Comptable',
    isAdmin: (state) => state.role === 'Admin' || state.role === 'Super Admin',

    // Vérification si l'utilisateur a un rôle métier (pas juste "User")
    hasBusinessRole: (state) => {
      return state.role !== 'User' && state.role !== null;
    },

    // Vérifications d'accès aux modules
    canAccessDashboard: (state) => {
      if (state.role === 'User') return false;
      return ['Responsable pédagogique', 'Comptable', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessEtudiants: (state) => {
      if (state.role === 'User') return false;
      return true; // Tous les autres rôles peuvent au moins consulter
    },

    canAccessPaiement: (state) => {
      if (state.role === 'User') return false;
      return ['Caissier', 'Responsable financier', 'Comptable', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessTresorerie: (state) => {
      if (state.role === 'User') return false;
      return ['Caissier', 'Responsable financier', 'Comptable', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessNotes: (state) => {
      if (state.role === 'User') return false;
      return ['Responsable pédagogique', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessPresences: (state) => {
      if (state.role === 'User') return false;
      return ['Responsable pédagogique', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessCours: (state) => {
      if (state.role === 'User') return false;
      return ['Responsable pédagogique', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessProfesseurs: (state) => {
      if (state.role === 'User') return false;
      return ['Comptable', 'Admin', 'Super Admin']
        .includes(state.role);
    },

    canAccessRapports: (state) => {
      if (state.role === 'User') return false;
      return !['User'].includes(state.role);
    },

    // Vérifications spéciales
    shouldMaskFinancials: (state) => {
      return state.role === 'Responsable pédagogique';
    },

    canEditParameters: (state) => {
      return state.role !== 'Responsable pédagogique'
        && ['Comptable', 'Admin', 'Super Admin'].includes(state.role);
    },

    canManageRoles: (state) => {
      return state.role !== 'Caissier'
        && (state.role === 'Admin' || state.role === 'Super Admin');
    },

    // Vérification de permission spécifique
    hasPermission: (state) => (permission) => {
      if (state.role === 'Super Admin') return true;
      return state.permissions.includes(permission);
    }
  },

  actions: {
    setUser(userData) {
      this.user = userData.user;
      this.token = userData.token;
      this.role = userData.user.role;
      this.permissions = userData.user.permissions || [];

      // Sauvegarder dans localStorage
      localStorage.setItem('auth_token', userData.token);
      localStorage.setItem('user_role', userData.user.role);
      localStorage.setItem('user_permissions', JSON.stringify(this.permissions));
    },

    logout() {
      this.user = null;
      this.token = null;
      this.role = null;
      this.permissions = [];
      localStorage.clear();
    }
  }
});
```

**2. Composant Navigation - Affichage conditionnel**:
```vue
<!-- components/Sidebar.vue -->
<template>
  <nav class="sidebar">
    <!-- Message pour utilisateur avec rôle "User" uniquement -->
    <div v-if="authStore.isBaseUser" class="alert alert-warning p-4 m-4">
      <i class="fas fa-info-circle"></i>
      <p class="font-semibold">Accès limité</p>
      <p class="text-sm">
        Votre compte n'a pas encore de rôle métier attribué.
        Contactez l'administrateur pour obtenir les accès nécessaires.
      </p>
    </div>

    <!-- Dashboard -->
    <router-link
      v-if="authStore.canAccessDashboard"
      to="/dashboard"
      class="nav-item"
    >
      <i class="fas fa-chart-line"></i>
      Dashboard
    </router-link>

    <!-- Étudiants (tous sauf User de base) -->
    <router-link
      v-if="authStore.canAccessEtudiants"
      to="/etudiants"
      class="nav-item"
    >
      <i class="fas fa-users"></i>
      Étudiants
    </router-link>

    <!-- Paiement -->
    <router-link
      v-if="authStore.canAccessPaiement"
      to="/paiements"
      class="nav-item"
    >
      <i class="fas fa-money-bill"></i>
      Paiements
    </router-link>

    <!-- Trésorerie -->
    <router-link
      v-if="authStore.canAccessTresorerie"
      to="/tresorerie"
      class="nav-item"
    >
      <i class="fas fa-vault"></i>
      Trésorerie
    </router-link>

    <!-- Notes -->
    <router-link
      v-if="authStore.canAccessNotes"
      to="/notes"
      class="nav-item"
    >
      <i class="fas fa-graduation-cap"></i>
      Notes
    </router-link>

    <!-- Présences -->
    <router-link
      v-if="authStore.canAccessPresences"
      to="/presences"
      class="nav-item"
    >
      <i class="fas fa-calendar-check"></i>
      Présences
    </router-link>

    <!-- Cours -->
    <router-link
      v-if="authStore.canAccessCours"
      to="/cours"
      class="nav-item"
    >
      <i class="fas fa-book"></i>
      Cours
    </router-link>

    <!-- Professeurs -->
    <router-link
      v-if="authStore.canAccessProfesseurs"
      to="/professeurs"
      class="nav-item"
    >
      <i class="fas fa-chalkboard-teacher"></i>
      Professeurs
    </router-link>

    <!-- Rapports -->
    <router-link
      v-if="authStore.canAccessRapports"
      to="/rapports"
      class="nav-item"
    >
      <i class="fas fa-file-pdf"></i>
      Rapports
    </router-link>

    <!-- Paramètres -->
    <router-link
      v-if="authStore.canEditParameters || authStore.isResponsablePedagogique"
      to="/parametres"
      class="nav-item"
    >
      <i class="fas fa-cog"></i>
      Paramètres
      <i v-if="!authStore.canEditParameters" class="fas fa-lock text-xs"></i>
    </router-link>

    <!-- Utilisateurs (Admin uniquement) -->
    <router-link
      v-if="authStore.isAdmin"
      to="/utilisateurs"
      class="nav-item"
    >
      <i class="fas fa-users-cog"></i>
      Utilisateurs
    </router-link>

    <!-- Profile - TOUJOURS visible pour TOUS les rôles (y compris User) -->
    <router-link
      to="/profile"
      class="nav-item"
    >
      <i class="fas fa-user"></i>
      Mon Profil
    </router-link>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>
```

**3. Masquage des données financières (Responsable pédagogique)**:
```vue
<!-- components/Dashboard.vue -->
<template>
  <div class="dashboard">
    <div class="stats-grid">
      <!-- Total paiements -->
      <div class="stat-card">
        <h3>Total des paiements</h3>
        <p class="amount">
          {{ authStore.shouldMaskFinancials ? '*****' : formatCurrency(totalPaiements) }}
        </p>
      </div>

      <!-- Balance -->
      <div class="stat-card">
        <h3>Balance restante</h3>
        <p class="amount">
          {{ authStore.shouldMaskFinancials ? '*****' : formatCurrency(balance) }}
        </p>
      </div>

      <!-- Statistiques pédagogiques (toujours visibles) -->
      <div class="stat-card">
        <h3>Nombre d'étudiants</h3>
        <p class="amount">{{ totalEtudiants }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();

const formatCurrency = (value) => {
  return new Intl.NumberFormat('fr-HT', {
    style: 'currency',
    currency: 'HTG'
  }).format(value);
};
</script>
```

**4. Mode lecture seule pour les paramètres**:
```vue
<!-- pages/Parametres.vue -->
<template>
  <div class="parametres">
    <h1>Paramètres de l'école</h1>

    <!-- Alerte mode lecture seule -->
    <div v-if="!canEdit" class="alert alert-info">
      <i class="fas fa-lock"></i>
      Vous êtes en mode lecture seule. Vous ne pouvez pas modifier les paramètres.
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Champs de formulaire -->
      <input
        v-model="params.nom_ecole"
        :disabled="!canEdit"
        type="text"
        class="form-input"
      />

      <!-- Bouton de sauvegarde -->
      <button
        v-if="canEdit"
        type="submit"
        class="btn btn-primary"
      >
        Enregistrer
      </button>
    </form>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const canEdit = computed(() => authStore.canEditParameters);

const handleSubmit = () => {
  if (!canEdit.value) {
    alert('Vous n\'avez pas les permissions pour modifier ces paramètres.');
    return;
  }
  // Logique de sauvegarde
};
</script>
```

**5. Masquage de la section Rôles dans le profil (Caissier)**:
```vue
<!-- pages/Profile.vue -->
<template>
  <div class="profile">
    <h1>Mon Profil</h1>

    <!-- Informations personnelles -->
    <section class="profile-section">
      <h2>Informations personnelles</h2>
      <!-- ... -->
    </section>

    <!-- Rôles et permissions (masqué pour Caissier) -->
    <section
      v-if="authStore.canManageRoles"
      class="profile-section"
    >
      <h2>Rôles et permissions</h2>
      <p>Rôle actuel: {{ authStore.userRole }}</p>
      <ul>
        <li v-for="perm in authStore.userPermissions" :key="perm">
          {{ perm }}
        </li>
      </ul>
    </section>

    <!-- Paramètres du compte -->
    <section class="profile-section">
      <h2>Sécurité</h2>
      <!-- Changement de mot de passe -->
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>
```

**6. Protection des routes et redirection (Utilisateur "User")**:
```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true } // Accessible par TOUS les utilisateurs authentifiés
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      requiresBusinessRole: true // Pas accessible au rôle "User" de base
    }
  },
  {
    path: '/etudiants',
    name: 'Etudiants',
    component: () => import('@/pages/Etudiants.vue'),
    meta: {
      requiresAuth: true,
      requiresBusinessRole: true
    }
  },
  // ... autres routes
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Guard de navigation globale
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // Vérifier si la route requiert une authentification
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login');
  }

  // Vérifier si la route requiert un rôle métier
  if (to.meta.requiresBusinessRole && authStore.isBaseUser) {
    // Rediriger vers le profil avec un message
    return next({
      path: '/profile',
      query: {
        message: 'Vous devez avoir un rôle métier pour accéder à cette page'
      }
    });
  }

  // Redirection automatique après login
  if (to.path === '/login' && authStore.isAuthenticated) {
    // Si l'utilisateur a juste le rôle "User", rediriger vers profile
    if (authStore.isBaseUser) {
      return next('/profile');
    }
    // Sinon, rediriger vers le dashboard
    return next('/dashboard');
  }

  next();
});

export default router;
```

**7. Page de profil avec message pour utilisateur "User"**:
```vue
<!-- pages/Profile.vue -->
<template>
  <div class="profile">
    <h1>Mon Profil</h1>

    <!-- Message spécial pour utilisateur avec rôle "User" uniquement -->
    <div v-if="authStore.isBaseUser" class="alert alert-info mb-6">
      <div class="flex items-center">
        <i class="fas fa-info-circle text-2xl mr-4"></i>
        <div>
          <p class="font-semibold text-lg">Accès limité</p>
          <p class="mt-2">
            Votre compte n'a actuellement que le rôle "User" de base.
            Pour accéder aux autres fonctionnalités du système, veuillez contacter
            l'administrateur pour qu'il vous attribue un rôle approprié :
          </p>
          <ul class="list-disc ml-6 mt-2">
            <li>Caissier - pour la gestion des paiements</li>
            <li>Responsable financier - pour la trésorerie</li>
            <li>Responsable des admissions - pour la gestion des étudiants</li>
            <li>Responsable pédagogique - pour les notes et cours</li>
            <li>Comptable - pour la comptabilité complète</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Afficher le message de la query si présent -->
    <div v-if="route.query.message" class="alert alert-warning mb-6">
      <i class="fas fa-exclamation-triangle"></i>
      {{ route.query.message }}
    </div>

    <!-- Informations personnelles -->
    <section class="profile-section">
      <h2>Informations personnelles</h2>
      <div class="form-group">
        <label>Nom complet</label>
        <input v-model="profile.name" type="text" class="form-input" />
      </div>
      <div class="form-group">
        <label>Email</label>
        <input v-model="profile.email" type="email" class="form-input" />
      </div>
      <div class="form-group">
        <label>Téléphone</label>
        <input v-model="profile.phone" type="tel" class="form-input" />
      </div>
    </section>

    <!-- Rôles et permissions (masqué pour Caissier et User) -->
    <section
      v-if="authStore.canManageRoles"
      class="profile-section"
    >
      <h2>Rôles et permissions</h2>
      <p>Rôle actuel: <span class="font-semibold">{{ authStore.userRole }}</span></p>
      <ul class="list-disc ml-6 mt-2">
        <li v-for="perm in authStore.userPermissions" :key="perm">
          {{ perm }}
        </li>
      </ul>
    </section>

    <!-- Paramètres du compte - TOUJOURS visible -->
    <section class="profile-section">
      <h2>Sécurité</h2>
      <button @click="showChangePasswordModal = true" class="btn btn-primary">
        <i class="fas fa-key"></i>
        Changer mon mot de passe
      </button>
    </section>

    <!-- Bouton de sauvegarde -->
    <div class="mt-6">
      <button @click="saveProfile" class="btn btn-primary">
        <i class="fas fa-save"></i>
        Enregistrer les modifications
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const route = useRoute();
const profile = ref({
  name: '',
  email: '',
  phone: ''
});

const showChangePasswordModal = ref(false);

const saveProfile = () => {
  // Logique de sauvegarde
  console.log('Sauvegarde du profil:', profile.value);
};

onMounted(() => {
  // Charger les données du profil
  profile.value = {
    name: authStore.user?.name || '',
    email: authStore.user?.email || '',
    phone: authStore.user?.phone || ''
  };
});
</script>
```

---

**Implémentation Backend (FastAPI)**:

**1. Middleware de vérification de rôle**:
```python
# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from app.Models.MModels import User
from app.database import get_db
from sqlalchemy.orm import Session
import jwt

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extrait l'utilisateur du token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )


def require_role(allowed_roles: List[str]):
    """Décorateur pour vérifier le rôle de l'utilisateur"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.name if current_user.role else None

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles autorisés: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker


def require_permission(permission: str):
    """Décorateur pour vérifier une permission spécifique"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Super Admin a toutes les permissions
        if current_user.role and current_user.role.name == "Super Admin":
            return current_user

        # Vérifier si l'utilisateur a la permission
        user_permissions = [
            perm.name for perm in current_user.role.permissions
        ] if current_user.role else []

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' requise"
            )

        return current_user

    return permission_checker


def require_any_permission(permissions: List[str]):
    """Vérifier si l'utilisateur a au moins une des permissions"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role and current_user.role.name == "Super Admin":
            return current_user

        user_permissions = [
            perm.name for perm in current_user.role.permissions
        ] if current_user.role else []

        if not any(perm in user_permissions for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Une des permissions requises: {', '.join(permissions)}"
            )

        return current_user

    return permission_checker
```

**2. Application dans les routes**:
```python
# app/Routes/RPaiement.py
from fastapi import APIRouter, Depends
from app.dependencies.auth import require_role, require_permission

router = APIRouter(prefix="/api/v1/paiement", tags=["Paiements"])

# Accessible par: Caissier, Responsable financier, Comptable, Admin
@router.get("/")
async def get_paiements(
    current_user: User = Depends(
        require_role(["Caissier", "Responsable financier", "Comptable", "Admin", "Super Admin"])
    )
):
    """Liste des paiements"""
    # Logique métier
    pass


# Création de paiement avec permission granulaire
@router.post("/")
async def create_paiement(
    paiement_data: PaiementCreate,
    current_user: User = Depends(require_permission("create_payments"))
):
    """Créer un nouveau paiement"""
    # Logique métier
    pass


# app/Routes/RNotes.py
# Accessible uniquement par: Responsable pédagogique, Admin
@router.get("/")
async def get_notes(
    current_user: User = Depends(
        require_role(["Responsable pédagogique", "Admin", "Super Admin"])
    )
):
    """Liste des notes"""
    pass


# app/Routes/RParametres.py
@router.get("/")
async def get_parametres(
    current_user: User = Depends(get_current_user)  # Tous peuvent voir
):
    """Consulter les paramètres"""
    pass


@router.put("/")
async def update_parametres(
    params_data: ParametresUpdate,
    current_user: User = Depends(
        require_role(["Comptable", "Admin", "Super Admin"])
    )  # Responsable pédagogique ne peut pas modifier
):
    """Modifier les paramètres"""
    pass


# app/Routes/RProfile.py
# Accessible par TOUS les utilisateurs authentifiés (y compris "User")
@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user)  # Tous les rôles, y compris "User"
):
    """Obtenir son propre profil - accessible à TOUS les utilisateurs"""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.name if current_user.role else "User",
        "permissions": [perm.name for perm in current_user.role.permissions] if current_user.role else []
    }


@router.put("/me")
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user)  # Tous peuvent modifier leur profil
):
    """Modifier son propre profil - accessible à TOUS les utilisateurs"""
    # L'utilisateur ne peut modifier que ses propres informations
    current_user.name = profile_data.name
    current_user.email = profile_data.email
    current_user.phone = profile_data.phone

    db.commit()
    return {"message": "Profil mis à jour avec succès"}


@router.post("/me/change-password")
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)  # Tous peuvent changer leur mot de passe
):
    """Changer son propre mot de passe - accessible à TOUS les utilisateurs"""
    # Vérifier l'ancien mot de passe
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect"
        )

    # Mettre à jour avec le nouveau mot de passe
    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()

    return {"message": "Mot de passe modifié avec succès"}


# app/Routes/REtudiants.py
# Accessible par tous SAUF "User" de base
@router.get("/")
async def get_etudiants(
    current_user: User = Depends(get_current_user)
):
    """Liste des étudiants"""
    # Vérifier que l'utilisateur n'est pas juste "User"
    if current_user.role.name == "User":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez avoir un rôle métier pour accéder aux étudiants"
        )

    # Logique métier
    pass
```

**3. Masquage des données côté API (optionnel)**:
```python
# app/Routes/RDashboard.py
from pydantic import BaseModel
from typing import Optional

class DashboardStats(BaseModel):
    total_etudiants: int
    total_paiements: Optional[str] = None  # Peut être "****" ou valeur
    balance: Optional[str] = None

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user)
):
    """Statistiques du dashboard"""

    stats = {
        "total_etudiants": db.query(Etudiant).count()
    }

    # Masquer les données financières pour Responsable pédagogique
    if current_user.role.name == "Responsable pédagogique":
        stats["total_paiements"] = "*****"
        stats["balance"] = "*****"
    else:
        stats["total_paiements"] = str(
            db.query(func.sum(Paiement.montant_paye)).scalar() or 0
        )
        stats["balance"] = str(
            db.query(func.sum(Paiement.balance)).scalar() or 0
        )

    return stats
```

**4. Logging des tentatives d'accès non autorisées**:
```python
# app/dependencies/auth.py (ajout)
from app.Models.MSystems import Log

def require_role(allowed_roles: List[str]):
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        user_role = current_user.role.name if current_user.role else None

        if user_role not in allowed_roles:
            # Logger la tentative d'accès non autorisée
            log = Log(
                user_id=current_user.id,
                action="UNAUTHORIZED_ACCESS_ATTEMPT",
                table_name="N/A",
                details=f"Rôle '{user_role}' a tenté d'accéder à une ressource requérant: {allowed_roles}",
                ip_address=request.client.host
            )
            db.add(log)
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles autorisés: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker
```

---

**Tests de sécurité recommandés**:

1. **Test d'accès direct par URL**: Vérifier qu'un utilisateur non autorisé ne peut pas accéder à une route en tapant l'URL directement
2. **Test de manipulation de token**: Vérifier qu'un token modifié est rejeté
3. **Test d'élévation de privilèges**: Vérifier qu'un utilisateur ne peut pas s'auto-attribuer des permissions
4. **Test de session expirée**: Vérifier que l'accès est bloqué après expiration du token
5. **Test de role spoofing**: Vérifier qu'un utilisateur ne peut pas usurper le rôle d'un autre

---

#### S5 - Autorisation par PIN (double approbation)
**Priorité**: Critique
**Statut**: Implémenté (backend `ecole_nginx` + client `flutter_version`), Vue.js web non câblé

**Description**: Permet à un rôle n'ayant pas une permission donnée d'effectuer
quand même l'action (retour de paiement, suppression de vente/dépense/
transaction, modification de vente/dépense/transaction), à condition qu'un
admin ou un Comptable fournisse son PIN à 6 chiffres en guise d'approbation.
L'objectif : un Caissier seul, sans admin disponible, peut quand même
exécuter une action sensible si un admin/Comptable distant lui communique
verbalement son PIN, sans avoir besoin de se connecter lui-même.

**Mécanisme (`app/dependencies/Dependencie.py:227-281`, `verify_dual_auth`/
`DualAuthChecker`)**:
1. Si l'utilisateur connecté a déjà la permission requise → l'action passe
   directement (`{"user_id": current_user.id, "admin_id": None}`).
2. Sinon → la route renvoie **HTTP 202** avec les en-têtes
   `X-Authorization-Required` / `X-Require-Admin-Auth`.
3. Le client demande alors un PIN à l'utilisateur, l'échange contre un
   `approval_token` (JWT de courte durée — 1 minute, `type=approval_grant`)
   via `POST /auth/autorisation-access-pin`, puis rejoue la requête initiale
   avec l'en-tête `X-Approval-Token`.
4. La route valide le token, vérifie que l'admin/Comptable identifié a bien
   la permission, puis exécute l'action en enregistrant **les deux
   identités** : `UserContext` (qui a agi) et `AdminAuthorization` (qui a
   approuvé) — `Log.authorization_id` distingue les deux.

**Données**:
- `User.code_pin` : hash bcrypt du PIN (même format que `User.password`,
  compatibilité `$2y$`/`$2b$` via `CryptAndDecript`/`AuthorizationService`).
  Réservé aux rôles `admin`/`Comptable` (`PATCH /user/pin`,
  `RAcademic.py:1474`).
- `Log.reason` : motif obligatoire (20 à 150 caractères) saisi par
  l'utilisateur pour tout retour/suppression — propagé via `ReasonContext`
  (`app/Helper/context.py`) jusqu'à `global_observer.py log_activity()`.
- `Log.authorization_id` : pré-existant, maintenant alimenté de bout en
  bout — l'admin/Comptable qui a fourni le PIN, distinct de l'auteur réel
  de l'action.

**Contrainte de sécurité explicite — unicité des PIN sans divulgation** :
chaque PIN doit identifier un seul admin/Comptable sans ambiguïté (la
recherche d'approbateur s'arrête au premier dont le PIN correspond). À la
création/modification d'un PIN, le serveur vérifie qu'aucun autre
admin/Comptable n'utilise déjà ce PIN — mais **ne révèle jamais** que le
refus est dû à une collision : le message renvoyé est volontairement
identique à celui d'un PIN simplement invalide (`"Code PIN incorrect,
choisissez-en un autre."`). Révéler la vraie raison permettrait à un tiers
de déduire qu'un PIN donné est déjà pris par quelqu'un d'autre
(énumération) — interdit explicitement par le donneur d'ordre.

**Actions couvertes** :
- Retour de paiement (`POST /delete-paiement`, `Returns.py`) — accessible à
  tous les rôles, plus seulement admin/Comptable.
- Suppression d'une ligne de vente (`DELETE /order_item`, `RVente.py`).
- Suppression d'une dépense (`GET /delete-depense`, `RVente.py`).
- Suppression d'une "autre transaction" (`DELETE /transactions/{id}`,
  `RTransaction.py`).
- Modification d'une vente / dépense (branche update de `POST /vente` et
  `POST /depense`, `RVente.py`) et d'une "autre transaction"
  (`PATCH /edit-other-transaction/{id}`, `RTransaction.py`).

**Côté client `flutter_version`** : `lib/core/dual_auth.dart` centralise le
flux (`runWithPinApproval()`, `showReasonDialog()`) ; câblé sur les écrans
Paiement, Vente (y compris le nouveau panneau d'édition ouvert au clic sur
une ligne), Dépense et Transaction. **Le frontend web Vue.js
(`ecole_nginx/frontend`) n'a aucune intégration de ce flux** — à faire si le
web doit un jour exposer ces mêmes actions à des rôles non-admin.

---

### 4.4 Performances

#### P1 - Temps de réponse
**Cibles**:
- Requêtes API simples: < 200ms (95e percentile)
- Requêtes complexes (rapports): < 2s
- Génération PDF: < 3s
- Chargement page web: < 1.5s

**Optimisations**:
- Index sur colonnes fréquemment recherchées
- Pagination obligatoire (max 100 résultats)
- Eager loading des relations SQLAlchemy
- Cache statique Nginx
- Compression gzip

#### P2 - Scalabilité
**Capacité**:
- Jusqu'à 10,000 étudiants par base
- 100+ utilisateurs simultanés
- 50,000+ transactions de paiement par an
- 1M+ enregistrements de notes

**Architecture**:
- Pool de connexions DB (min: 5, max: 20)
- Workers Uvicorn: 8 (configurable selon CPU)
- Keep-alive HTTP: 75 secondes

#### P3 - Disponibilité
**Objectif**: 99.5% uptime pendant heures scolaires

**Mécanismes**:
- Health check endpoint: `/api/v1/health`
- Logs d'erreur détaillés
- Système de backup automatique (à configurer)
- Service Windows avec démarrage automatique

---

### 4.5 Compatibilité

**Système d'exploitation**:
- Windows 10 (64-bit) minimum
- Windows 11 (64-bit)
- Windows Server 2016+

**Navigateurs web** (frontend):
- Chrome 90+ (recommandé)
- Firefox 88+
- Edge 90+
- Safari 14+ (non testé)

**Résolution d'écran**:
- Minimum: 1366x768
- Recommandé: 1920x1080 ou supérieur

**Matériel minimum**:
- Processeur: Intel Core i3 ou équivalent
- RAM: 8 GB
- Disque: 10 GB espace libre
- Réseau: Ethernet ou WiFi

---

## 5. Système de licence et activation

### 5.1 Mécanisme de protection

#### Génération de clé
**Algorithme**:
```python
# Clé basée sur adresse MAC + date d'expiration
mac_address = get_mac_address()
expiration_date = datetime.now() + timedelta(days=30)
secret_key = "MASTER_SECRET_KEY"

# Génération signature HMAC
message = f"{mac_address}|{expiration_date.isoformat()}"
signature = hmac.sha256(message, secret_key)
activation_key = format_as_xxxx_xxxx_xxxx_xxxx(signature)
```

**Format de clé**: `ABCD-EFGH-IJKL-MNOP`

#### Validation
**Processus au démarrage**:
1. Lecture de la clé depuis le registre Windows
2. Déchiffrement Fernet
3. Extraction de l'adresse MAC et date d'expiration
4. Vérification MAC actuelle = MAC enregistrée
5. Vérification date actuelle < date d'expiration
6. Autorisation de lancement si valide

**Stockage**:
- Localisation: Registre Windows (QSettings)
- Chiffrement: Fernet (clé dérivée de MAC)
- Chemin: `HKEY_CURRENT_USER\Software\EcoleServer\`

#### Expiration
- Durée par défaut: 30 jours
- Avertissement: 7 jours avant expiration
- Blocage: Application ne démarre plus après expiration
- Renouvellement: Nouvelle clé requise

### 5.2 Installation

#### Workflow d'installation
```
1. Vérification privilèges admin
2. Vérification installation existante
3. Saisie clé d'activation
4. Validation clé
5. Sauvegarde licence chiffrée
6. Installation MySQL → C:\Program Files\ecole-serve\
7. Configuration SSL certificates
8. Création services Windows (MySQLEcole, NginxAplekol)
9. Initialisation base de données (Alembic migrations)
10. Configuration firewall
11. Lancement services
12. Démarrage API FastAPI
13. Ouverture interface web
```

#### Fichiers installés
```
C:\Program Files\ecole-serve\
├── app.exe                    # Application principale
├── mysql-8.0.41-winx64\       # Serveur MySQL
│   ├── bin\                   # Exécutables MySQL
│   ├── data\                  # Bases de données
│   └── certs\                 # Certificats SSL
├── nginx-1.26.3\              # Serveur web
├── api\                       # Frontend Vue.js (build)
└── uploads\                   # Fichiers uploadés
```

#### Services Windows créés
- **MySQLEcole**: Base de données (port 3307)
- **NginxAplekol**: Serveur web (ports 80, 443)

---

## 6. Flux utilisateurs (User Flows)

### 6.1 Flux d'inscription d'un nouvel étudiant

```
1. Administrateur se connecte → Dashboard
2. Navigation: Menu "Étudiants" → "Nouveau"
3. Formulaire d'inscription:
   a. Informations personnelles (nom, prénom, sexe, date naissance)
   b. Coordonnées (adresse, téléphone)
   c. Photo (upload ou webcam)
   d. Informations responsable légal
   e. Sélection classe et faculté
   f. Année académique active (pré-sélectionnée)
4. Validation formulaire (champs requis)
5. Génération automatique ID étudiant
6. Sauvegarde dans base de données
7. Confirmation + option d'imprimer fiche d'inscription
```

### 6.2 Flux d'enregistrement de paiement

```
1. Caissier se connecte → Dashboard
2. Recherche étudiant (par nom ou ID)
3. Sélection étudiant → Affichage dossier financier
4. Système affiche:
   - Montant total scolarité annuelle
   - Montant déjà payé
   - Balance restante
   - Prochain mois à payer (automatique)
   - Aide financière le cas échéant
5. Saisie du paiement:
   - Montant reçu
   - Méthode (cash, chèque, virement)
   - Référence (optionnel)
6. Système calcule:
   - Distribution sur mois suivants
   - Nouvelle balance
   - Mise à jour statut mensualités
7. Validation paiement
8. Génération automatique reçu PDF
9. Impression ou envoi email
10. Enregistrement dans log d'audit
```

### 6.3 Flux de génération de bulletin

```
1. Enseignant/Admin se connecte
2. Navigation: "Bulletins" → Sélection période (trimestre/semestre)
3. Sélection classe ou étudiant individuel
4. Vérification: Toutes les notes sont saisies
5. Si incomplet → Alerte + liste des notes manquantes
6. Si complet → Génération bulletin:
   a. Récupération notes par matière
   b. Calcul moyennes (avec coefficients)
   c. Calcul rang dans classe
   d. Ajout appréciations
   e. Génération PDF avec template
7. Prévisualisation PDF
8. Options:
   - Télécharger
   - Imprimer
   - Envoyer par email (si configuré)
   - Générer en masse pour toute la classe
```

---

## 7. Exigences non-fonctionnelles

### 7.1 Disponibilité
- **Uptime**: 99.5% pendant heures scolaires (7h-18h)
- **Maintenance**: Fenêtre recommandée dimanche 22h-2h
- **Démarrage**: Services démarrent automatiquement au boot Windows

### 7.2 Fiabilité
- **Sauvegarde**: Backup automatique MySQL quotidien (à configurer)
- **Intégrité données**: Contraintes FK, transactions ACID
- **Récupération**: RPO < 24h, RTO < 2h

### 7.3 Utilisabilité
- **Apprentissage**: Utilisateur basique opérationnel en < 2h formation
- **Interface**: Française, intuitive, responsive
- **Accessibilité**: Contraste suffisant, tailles texte ajustables
- **Documentation**: Manuel utilisateur et vidéos tutoriels (à créer)

### 7.4 Maintenabilité
- **Code**: Commentaires en français, structure modulaire
- **Logs**: Niveau configurable (debug, info, warning, error)
- **Monitoring**: Health check, métriques système
- **Mises à jour**: Migration Alembic pour changements DB

### 7.5 Portabilité
- **Packaging**: Exécutable standalone (pas d'installation Python)
- **Dépendances**: Toutes incluses dans build Nuitka
- **Configuration**: Fichiers .env et config.ini modifiables

---

## 8. Contraintes et limitations

### 8.1 Contraintes techniques
- **OS**: Windows uniquement (dépendances PySide6, services Windows)
- **Architecture**: x64 uniquement
- **Privilèges**: Installation requiert droits administrateur
- **Réseau**: Port 80/443 doivent être libres

### 8.2 Contraintes légales
- **Licence**: Système d'activation requis
- **Durée**: 30 jours par activation
- **Transfert**: Clé liée à machine (MAC address)
- **RGPD**: Données personnelles étudiants (responsabilité établissement)

### 8.3 Limitations connues
- **Offline**: Pas de synchronisation cloud (version actuelle)
- **Multi-site**: Base de données locale uniquement
- **Mobile**: Pas d'application mobile native
- **Langues**: Interface française uniquement
- **Internationalization**: Devise GDES hardcodée (modifiable code)

### 8.4 Bugs résolus récemment (journal)
- **`PATCH /user/pin` plantait systématiquement** (`RAcademic.py:1474`,
  `set_user_pin`) : `Exception("User non authentifié lors du log")` levée
  par `global_observer.py log_activity()` (ligne 118) à chaque
  enregistrement/modification de PIN. Cause : la route ne posait jamais
  `UserContext.set_user_id(current_user.id)` avant `db.commit()`, alors que
  `log_activity()` l'exige pour toute mutation suivie par l'observer
  (sauf pendant `ActionContext == "Connect Autorisation"`). Corrigé en
  ajoutant cet appel en tête de la fonction, comme dans toutes les autres
  routes de mutation. **Rappel opérationnel** : `app_gui.py` exécute l'API
  dans un thread uvicorn embarqué sans `--reload` — toute modification de
  code backend exige de quitter complètement l'app (menu barre système →
  "Quitter") puis de la relancer pour être prise en compte ; il n'existe
  pas de bouton "redémarrer l'API" dans `gui/service_window.py`.

---

## 9. Dépendances

### 9.1 Dépendances externes

#### Python (112 packages)
**Critiques**:
- fastapi==0.126.0
- sqlalchemy==2.0.45
- pydantic==2.12.3
- uvicorn==0.25.0
- pymysql==1.1.1
- bcrypt==4.2.1
- pyjwt==2.10.1
- weasyprint==64.2
- pyside6==6.9.0

**Complètes**: Voir `requirements.txt`

#### Frontend (npm)
**Critiques**:
- vue@3.5.27
- vite@6.0.21
- tailwindcss@4.1.18
- axios@1.13.5
- pinia@3.0.4
- vue-router@5.0.1

**Complètes**: Voir `package.json`

### 9.2 Services système
- **MySQL 8.0.41**: SGBD
- **Nginx 1.26.3**: Reverse proxy et serveur statique
- **Windows Services API**: Gestion services

### 9.3 Bibliothèques runtime
- **GTK Runtime**: Pour génération PDF (WeasyPrint)
- **Qt6 Runtime**: Interface PySide6
- **MSVC Redistributable**: Runtime C++ (inclus dans build)

---

## 10. Métriques de succès

### 10.1 KPIs techniques
- Temps de réponse API p95 < 200ms
- Taux d'erreur < 0.1%
- Uptime > 99.5%
- Temps génération PDF < 3s

### 10.2 KPIs fonctionnels
- Temps moyen enregistrement étudiant < 3 min
- Temps moyen enregistrement paiement < 1 min
- Taux d'adoption utilisateurs > 90% (formation)
- Satisfaction utilisateurs > 4/5

### 10.3 KPIs business
- Réduction temps tâches administratives: -50%
- Erreurs saisie paiements: -80%
- Génération bulletins: automatisation 100%
- ROI: < 6 mois

---

## 11. Roadmap et évolutions futures

### Version 1.0 (Actuelle)
✅ Gestion étudiants, classes, cours
✅ Gestion paiements et comptabilité
✅ Saisie notes et présences
✅ Génération bulletins et reçus
✅ Système RBAC complet
✅ Application desktop Windows

### Version 1.1 (Q3 2026)
- [ ] Application mobile (Android/iOS) pour consultation
- [ ] Notifications push (paiements, absences)
- [ ] Messagerie intégrée (école ↔ parents)
- [ ] Module SMS automatisé

### Version 1.2 (Q4 2026)
- [ ] Synchronisation multi-sites (cloud optionnel)
- [ ] Tableau de bord analytique avancé
- [ ] API publique pour intégrations tierces
- [ ] Module de planning/emploi du temps

### Version 2.0 (2027)
- [ ] Module e-learning intégré
- [ ] Portail parent avec login
- [ ] Bibliothèque/médiathèque numérique
- [ ] Module RH (gestion personnel)
- [ ] Support multi-langues (anglais, espagnol)

---

## 12. Annexes

### A. Glossaire

| Terme | Définition |
|-------|------------|
| **Étudiant** | Apprenant inscrit dans l'établissement |
| **Classe** | Groupe d'étudiants d'un même niveau |
| **Niveau** | Palier d'enseignement (ex: CM2, Seconde) |
| **Faculté** | Département ou filière (ex: Scientifique, Littéraire) |
| **Cours** | Matière enseignée (ex: Mathématiques, Histoire) |
| **Mensualité** | Fraction mensuelle des frais de scolarité |
| **Balance** | Montant restant à payer |
| **Bulletin** | Document récapitulatif des notes (report card) |
| **Présence** | Enregistrement de la présence en classe |
| **Année académique** | Cycle scolaire annuel (ex: 2024-2025) |
| **GDES** | Gourde Haïtienne (devise) |
| **RBAC** | Role-Based Access Control (contrôle accès par rôles) |
| **JWT** | JSON Web Token (jeton d'authentification) |
| **ORM** | Object-Relational Mapping (SQLAlchemy) |

### B. Références techniques
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/
- Vue.js 3: https://vuejs.org/
- PySide6: https://doc.qt.io/qtforpython-6/
- MySQL 8.0: https://dev.mysql.com/doc/

### C. Contacts
**Développement**: [À compléter]
**Support**: [À compléter]
**Documentation**: [À compléter]

---

## 13. Historique des révisions

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 1.0 | 2026-05-15 | Analyse Claude | Création initiale du PRD |
| 1.1 | 2026-06-28 | Claude (session) | Ajout S5 (autorisation par PIN / double approbation, §4.3) ; journal de bug §8.4 (`PATCH /user/pin` corrigé) |

---

**Note**: Ce document est destiné à évoluer. Toute modification doit être documentée dans l'historique des révisions ci-dessus.
