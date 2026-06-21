# PRD — infini-software (vitrine, licences & paiements)

## 1. Contexte et problème

`infini-software` est l'éditeur du logiciel scolaire **Lekol360** (porté par `ecole_nginx`/`school_client`). Chaque installation doit pouvoir s'enregistrer auprès de l'éditeur, et l'établissement doit pouvoir renouveler sa licence (payer pour prolonger la validité de sa clé d'activation) sans intervention manuelle de l'éditeur. Avant ce projet, le site n'avait ni backend, ni mécanisme de paiement, ni réception réelle de la télémétrie d'installation — seul un script de génération de clé existait, non branché à quoi que ce soit.

## 2. Objectifs produit

1. Recevoir et conserver les informations d'enregistrement envoyées par chaque installation `ecole_nginx` au moment de la création de son premier compte admin.
2. Permettre à un établissement de renouveler sa licence en ligne : choisir une durée, payer (carte, MonCash, NatCash), recevoir une nouvelle clé d'activation.
3. Donner à l'éditeur une vue d'administration : historique de toutes les installations, statut (suspendu/actif), historique des clés et paiements.
4. Permettre à l'éditeur de configurer le prix mensuel et le taux de change du jour (USD→HTG) sans déploiement de code.
5. Garantir que l'identification du client lors d'un paiement est fiable, même si l'admin de l'établissement initie le paiement depuis un appareil différent du serveur de l'école (téléphone, autre poste).

## 3. Utilisateurs cibles / personas

- **Administrateur établissement scolaire** : reçoit une alerte de renouvellement dans `school_client`, paie en ligne, récupère sa nouvelle clé.
- **Staff infini-software (éditeur)** : consulte la liste des clients, leur historique, suspend/réactive un client, ajuste le prix et le taux de change.
- **Visiteur du site public** : consulte la vitrine (store, à propos, contact) — hors périmètre de cette mise à jour.

## 4. Fonctionnalités (epics & user stories)

### 4.1 Enregistrement d'installation
- En tant que système (`ecole_nginx`), j'envoie nom/prénom/email/mac à la création du premier compte admin, pour que l'éditeur sache qu'une nouvelle installation existe.

### 4.2 Renouvellement de licence
- En tant qu'administrateur d'établissement, j'ouvre la page de renouvellement depuis `school_client` (mon installation est déjà identifiée par mac, je ne peux pas la modifier).
- En tant qu'administrateur d'établissement, si j'arrive sur le site sans passer par `school_client` (ex. depuis mon téléphone), je peux saisir moi-même l'adresse MAC de mon serveur (visible dans Lekol360 → Gestion du serveur → Licence) et la faire vérifier avant de payer.
- En tant qu'administrateur, je choisis une durée (1/2/3/6/12 mois) et un moyen de paiement, et je vois le montant total avant de payer.
- En tant qu'administrateur, je paie par carte et le montant reste dans la devise de base (USD) ; si je paie par MonCash/NatCash, le montant est converti en HTG au taux du jour.
- En tant qu'administrateur, après paiement confirmé, je reçois ma nouvelle clé d'activation et sa date d'expiration.

### 4.3 Administration
- En tant que staff infini-software, je me connecte avec un compte admin dédié (créé en CLI, pas par une page d'inscription publique).
- En tant que staff, je consulte la liste de tous les clients, leur statut, et l'historique détaillé (clés + paiements) de chacun.
- En tant que staff, je peux suspendre ou réactiver un client.
- En tant que staff, je configure le prix mensuel, la devise de base, et le taux de change du jour USD→HTG.

## 5. Hors périmètre actuel (constaté dans le code)

- Paiement par carte (Stripe) : explicitement mis en attente, squelette `NotImplementedError` en place.
- Paiement NatCash : non implémenté, faute de documentation API fiable — nécessite que l'éditeur fournisse la doc officielle ou un accès au portail développeur.
- Confirmation de paiement automatique (webhook fournisseur) : non implémentée — la confirmation est déclenchée manuellement par l'utilisateur (« J'ai terminé le paiement »), ce qui suppose qu'il revient sur la page après avoir payé.
- Authentification du client final (école) pour consulter son propre historique côté site public : seule l'identification par mac existe, pas de compte/mot de passe établissement.
- Nettoyage de l'ancien scaffold Laravel/Inertia (`js/Pages`, `views/app.blade.php`) : dead code non utilisé par le site actif, non traité dans cette itération.

## 6. Risques / dette technique identifiée

- **MonCash non vérifié en conditions réelles** : l'intégration suit la documentation publique mais n'a jamais tourné avec de vrais identifiants marchand — à valider avant toute mise en production, en particulier les noms exacts de champs/endpoints qui peuvent avoir évolué.
- **Pas de webhook de confirmation** : un utilisateur qui ferme la page après paiement sans cliquer sur « J'ai terminé » n'obtient pas sa clé automatiquement ; à revoir si le volume de support associé devient significatif.
- **SQLite mono-fichier** (`infini.db`) : suffisant à l'échelle actuelle, migration vers Postgres/MySQL à prévoir si le nombre de clients ou de transactions concurrentes augmente.
- **Identification par mac sans secret** : `verifier-mac` et la création de paiement n'exigent qu'une adresse MAC (non secrète par nature) — acceptable pour ce produit (le pire cas est qu'un tiers paie à la place du client, sans accès à des données sensibles), mais à reconsidérer si le modèle de données du `Client` s'enrichit de données plus sensibles à l'avenir.
- **Deux mécanismes de licence non synchronisés côté `ecole_nginx`** (historique `log_actives` vs. fichier d'essai local `license_check.py`) — un renouvellement réussi côté `infini-software` ne met pas à jour automatiquement le fichier local ; à connecter si l'incohérence entre les deux affichages (onglet Abonnement vs. fenêtre Gestion du serveur) devient gênante.

## 7. Mise à jour — backend, paiement & administration (livré)

- Backend FastAPI complet ajouté (n'existait pas avant) : modèles, routes d'enregistrement/paiement/administration, authentification admin JWT.
- Calcul du prix entièrement serveur (jamais fourni par l'appelant) — carte = devise de base, autres fournisseurs = conversion HTG au taux du jour configuré par l'admin ; durée et `days_valid` dérivés dynamiquement du nombre de mois choisi.
- Page de renouvellement publique avec double chemin d'identification (lien de confiance verrouillé vs. saisie manuelle vérifiée), pour couvrir le cas d'un admin payant depuis un appareil différent du serveur de l'école.
- Tableau d'administration (clients, historique, activer/suspendre, configuration tarifaire).
- Script de génération de clé corrigé (bug d'inversion des valeurs retournées) et rendu configurable par variable d'environnement.
