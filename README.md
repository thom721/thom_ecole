# Lekol360 — Guide de l'utilisateur

Bienvenue dans Lekol360, le logiciel de gestion de votre école : inscriptions,
notes, présences, paiements, salaires du personnel, rapports...

Ce guide explique comment installer l'application et comment l'utiliser au
quotidien. Aucune connaissance technique n'est nécessaire.

## 1. Comment fonctionne Lekol360 ?

Lekol360 a deux parties :

- **Le serveur** : le "cerveau" du logiciel, installé une seule fois sur
  l'ordinateur principal de l'école (celui qui reste allumé). C'est lui qui
  garde toutes les données (étudiants, notes, paiements...).
- **L'application** (le "client") : le programme que chaque personne ouvre
  sur son propre ordinateur pour utiliser Lekol360. Elle se connecte au
  serveur à travers le réseau de l'école.

Concrètement : un technicien installe le serveur une seule fois ; ensuite,
chaque poste de travail (secrétariat, caisse, direction...) installe
simplement l'application et se connecte.

## 2. Installation

### 2.1 Installer le serveur (une seule fois)

Cette étape est généralement faite par la personne qui met en place
Lekol360 pour l'école (technicien ou éditeur du logiciel) :

1. Ouvrir l'application de contrôle du serveur sur l'ordinateur principal.
2. Au tout premier démarrage, l'application installe automatiquement les
   quelques composants dont elle a besoin — cela peut prendre quelques
   minutes, une seule fois.
3. Si c'est la toute première installation de l'école, des fenêtres
   s'affichent pour créer le tout premier compte administrateur (nom,
   prénom, email, mot de passe) — à faire une seule fois.
4. Laisser cette fenêtre ouverte : tant qu'elle est ouverte, le serveur
   fonctionne et les autres ordinateurs peuvent se connecter.

### 2.2 Installer l'application sur un poste de travail

Sur chaque ordinateur qui doit utiliser Lekol360 :

1. Installer l'application fournie pour le système de l'ordinateur (Mac,
   Windows ou Linux) — comme n'importe quel logiciel.
2. Ouvrir l'application : l'écran de connexion apparaît.
3. Si c'est la première fois que cet ordinateur se connecte au serveur de
   l'école, indiquer au logiciel où le trouver (voir §2.3 ci-dessous) —
   sinon, passer directement à la connexion (§2.4).

### 2.3 Indiquer l'adresse du serveur (une seule fois par ordinateur)

Sur l'écran de connexion, sous le champ mot de passe, cliquer sur **"show
ip"** pour faire apparaître le champ "Modifier l'ip" :

1. Demander à l'administrateur du réseau l'adresse IP de l'ordinateur qui
   sert de serveur (ex. `192.168.0.110`).
2. La saisir dans le champ, puis cliquer sur **"Modifier"**.
3. Le système d'exploitation peut demander le mot de passe administrateur
   de CET ordinateur (pas celui du compte Lekol360) : c'est normal,
   l'application a besoin de cette autorisation une seule fois pour
   enregistrer l'adresse du serveur. Accepter pour continuer.
4. Un message confirme que l'adresse a été enregistrée.

Cette étape n'est à refaire que si l'adresse du serveur change (nouvel
ordinateur serveur, changement de réseau...).

### 2.4 Se connecter

- Saisir l'email et le mot de passe du compte fourni par l'administrateur
  de l'école.
- En cas d'oubli du mot de passe, contacter l'administrateur : lui seul
  peut réinitialiser un accès depuis Profile → Mon compte.

### 2.5 Changement de mot de passe à la première connexion

Pour tout nouveau compte (y compris le tout premier compte administrateur),
l'application demande automatiquement de choisir un nouveau mot de passe
juste après la toute première connexion, avant d'accéder au reste du
logiciel : saisir un nouveau mot de passe, puis le confirmer. Cette étape
n'apparaît qu'une seule fois par compte — les connexions suivantes vont
directement à l'application.

## 3. Présentation de l'application

Le menu de gauche donne accès à toutes les sections. Selon son rôle, une
personne ne voit que les sections pour lesquelles elle a une autorisation
(configurable par l'administrateur, voir §3.13).

### 3.1 Dashboard

Vue d'ensemble à l'ouverture de l'application : effectifs, paiements du
mois, statistiques générales de l'école.

### 3.2 Administration

Gestion du personnel non-enseignant (secrétariat, comptabilité, direction,
surveillance...) : ajout, modification, rôle et salaire fixe de chaque
membre du personnel.

### 3.3 Étudiant

- Inscrire un nouvel étudiant, modifier son dossier.
- Importer une liste d'étudiants en une fois.
- Imprimer le diplôme, le certificat ou la carte de badge d'un étudiant.

### 3.4 Promus

Liste des étudiants admis en fin d'année et suivi de leur passage au niveau
supérieur.

### 3.5 Professeur

Gestion des professeurs : ajout, modification, matières enseignées,
manière dont chacun est payé (salaire fixe ou à l'heure selon les cours
donnés).

### 3.6 Cours

- **Matières** : liste des cours proposés par l'école.
- **Programme** : quel professeur enseigne quelle matière, dans quelle
  classe, à quel moment.

### 3.7 Notes

- Saisir ou modifier les notes d'une classe pour une matière et une
  période données.
- Imprimer le bulletin d'un étudiant, ou les bulletins de toute une classe
  d'un coup.

### 3.8 Présences

- **Appel du jour** : marquer chaque étudiant présent ou absent.
- **Historique** : consulter les présences des jours précédents.
- **Statistiques** : taux de présence par classe ou par étudiant.
- **Pointage** : heure d'arrivée/de départ du personnel et des
  professeurs.

### 3.9 Paiement

Enregistrer un versement d'un étudiant (frais de scolarité, accessoires...)
et imprimer le reçu correspondant.

### 3.10 Finances

- **Vente** : ventes de fournitures/uniformes, avec reçu imprimable.
- **Produits** : catalogue des articles vendus par l'école.
- **Dépenses** : dépenses courantes de l'établissement.
- **Prêts** : prêts accordés, avec suivi des remboursements.
- **Payroll** : versement des salaires (personnel et professeurs), fixe ou
  calculé selon les heures de cours données.
- **Transactions** : autres mouvements financiers divers.

### 3.11 Rapport

Génère des documents imprimables (PDF ou Excel) pour une période choisie :
rapport financier global, registre des inscriptions, bulletin pédagogique,
décision de fin d'année, rapport de salaires, etc.

### 3.12 Profile

- **Mon compte** : modifier ses propres informations et son mot de passe.
- **Rôles** : (réservé aux administrateurs) créer des rôles et décider ce
  que chaque rôle peut faire.
- **Permissions** : (réservé aux administrateurs) autoriser une action
  précise (ajouter, modifier, supprimer, imprimer, voir) pour un rôle ou
  une personne en particulier.
- **Vues** : (réservé aux administrateurs) choisir quelles sections du
  menu sont visibles pour chaque rôle.

### 3.13 Paramètres

Réglages de référence utilisés dans tout le logiciel : examens, facultés,
années académiques, classes, méthodes de paiement, frais et frais divers.

### 3.14 Log

Historique de toutes les actions effectuées dans le logiciel (qui a créé,
modifié ou supprimé quoi, et quand) — utile pour retrouver l'origine d'un
changement.

### 3.15 Abonnement

État de l'abonnement/licence de l'école et historique des activations.

### 3.16 Actualiser et À Propos

"Actualiser" recharge les listes de référence (classes, années, matières...)
sans changer d'écran — utile si une donnée modifiée par quelqu'un d'autre
n'apparaît pas encore. "À Propos" présente l'éditeur du logiciel, Infini
Software.

## 4. Questions fréquentes

**Je ne vois pas certaines sections du menu.**
C'est normal : chaque personne ne voit que ce que son rôle autorise.
Demander à un administrateur d'ajuster les permissions (Profile → Rôles/
Permissions/Vues).

**Le bouton "Imprimer" ne fonctionne pas / rien ne se passe.**
Vérifier que la personne a bien la permission d'impression correspondante
(Profile → Permissions). Sinon, un message l'indique clairement.

**"Impossible de se connecter" au démarrage de l'application.**
Vérifier que l'ordinateur principal (le serveur) est bien allumé et que
son application de contrôle est ouverte. Si le problème persiste sur un
poste précis (ex. après un changement de réseau), reconfigurer l'adresse
du serveur sur ce poste via "show ip" (§2.3).

**Comment ajouter un nouvel utilisateur (secrétaire, professeur...) ?**
Depuis Administration (personnel) ou Professeur, selon le cas — un compte
de connexion peut être créé au moment de l'ajout.

**Qui contacter en cas de problème technique ?**
Le technicien ou l'éditeur du logiciel (Infini Software), pas cette
documentation.
