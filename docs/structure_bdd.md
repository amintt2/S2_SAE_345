# Structure de la Base de Données

Ce document détaille la structure de la base de données utilisée dans le projet e-commerce de skins CS:GO.

## Schéma Général

La base de données est conçue pour gérer un site e-commerce complet avec des fonctionnalités de gestion des utilisateurs, des produits, des commandes, des commentaires, et plus encore.

## Tables Principales

### utilisateur
Table des utilisateurs du système.

| Colonne | Type | Description |
|---------|------|-------------|
| id_utilisateur | INT AUTO_INCREMENT | Identifiant unique de l'utilisateur (PK) |
| login | VARCHAR(255) | Nom d'utilisateur |
| email | VARCHAR(255) | Adresse email |
| nom | VARCHAR(255) | Nom complet |
| password | VARCHAR(255) | Mot de passe hashé |
| role | VARCHAR(50) | Rôle (ROLE_client, ROLE_admin) |
| est_actif | TINYINT(1) | Statut d'activation du compte |

### skin
Table principale des produits (skins CS:GO).

| Colonne | Type | Description |
|---------|------|-------------|
| id_skin | INT AUTO_INCREMENT | Identifiant unique du skin (PK) |
| nom_skin | VARCHAR(50) | Nom du skin |
| disponible | TINYINT(1) | Disponibilité du skin |
| prix_skin | DECIMAL(10,2) | Prix de base du skin |
| type_skin_id | INT | Type de skin (FK vers type_skin) |
| image | VARCHAR(255) | Chemin de l'image |
| description | TEXT | Description du skin |

### type_skin
Catégories de skins (AK-47, AWP, etc.).

| Colonne | Type | Description |
|---------|------|-------------|
| id_type_skin | INT AUTO_INCREMENT | Identifiant unique du type (PK) |
| libelle_type_skin | VARCHAR(50) | Nom du type de skin |

### usure
Niveaux d'usure des skins.

| Colonne | Type | Description |
|---------|------|-------------|
| id_usure | INT AUTO_INCREMENT | Identifiant unique du niveau d'usure (PK) |
| libelle_usure | VARCHAR(50) | Description du niveau d'usure |

### special
Attributs spéciaux des skins (StatTrak™, Souvenir).

| Colonne | Type | Description |
|---------|------|-------------|
| id_special | INT AUTO_INCREMENT | Identifiant unique de l'attribut spécial (PK) |
| libelle_special | VARCHAR(50) | Description de l'attribut spécial |

### declinaison
Variations spécifiques des skins (combinaison de skin, usure, attribut spécial).

| Colonne | Type | Description |
|---------|------|-------------|
| id_declinaison | INT AUTO_INCREMENT | Identifiant unique de la déclinaison (PK) |
| stock | INT | Quantité en stock |
| prix_declinaison | DECIMAL(10,2) | Prix spécifique à cette déclinaison |
| image | VARCHAR(255) | Image spécifique à cette déclinaison |
| special_id | INT | Attribut spécial (FK vers special) |
| usure_id | INT | Niveau d'usure (FK vers usure) |
| skin_id | INT | Skin de base (FK vers skin) |

### etat
États possibles des commandes.

| Colonne | Type | Description |
|---------|------|-------------|
| id_etat | INT AUTO_INCREMENT | Identifiant unique de l'état (PK) |
| libelle_etat | VARCHAR(50) | Description de l'état (En cours, Validée, etc.) |

## Tables de Relation

### commande
Commandes passées par les utilisateurs.

| Colonne | Type | Description |
|---------|------|-------------|
| id_commande | INT AUTO_INCREMENT | Identifiant unique de la commande (PK) |
| date_achat | DATE | Date de la commande |
| etat_id | INT | État de la commande (FK vers etat) |
| utilisateur_id | INT | Utilisateur ayant passé la commande (FK vers utilisateur) |
| adresse_livraison_id | INT | Adresse de livraison (FK vers adresse) |
| adresse_facturation_id | INT | Adresse de facturation (FK vers adresse) |

### ligne_commande
Détails des articles dans une commande.

| Colonne | Type | Description |
|---------|------|-------------|
| declinaison_id | INT | Déclinaison commandée (PK, FK vers declinaison) |
| commande_id | INT | Commande associée (PK, FK vers commande) |
| prix | DECIMAL(10,2) | Prix au moment de la commande |
| quantite | INT | Quantité commandée |

### ligne_panier
Articles dans le panier d'un utilisateur.

| Colonne | Type | Description |
|---------|------|-------------|
| declinaison_id | INT | Déclinaison dans le panier (PK, FK vers declinaison) |
| utilisateur_id | INT | Utilisateur propriétaire du panier (PK, FK vers utilisateur) |
| quantite | INT | Quantité dans le panier |
| date_ajout | DATETIME | Date d'ajout au panier |

### adresse
Adresses des utilisateurs pour la livraison et la facturation.

| Colonne | Type | Description |
|---------|------|-------------|
| id_adresse | INT AUTO_INCREMENT | Identifiant unique de l'adresse (PK) |
| nom | VARCHAR(255) | Nom associé à l'adresse |
| rue | VARCHAR(255) | Rue |
| code_postal | VARCHAR(255) | Code postal |
| ville | VARCHAR(255) | Ville |
| date_utilisation | DATETIME | Date de dernière utilisation |
| utilisateur_id | INT | Utilisateur propriétaire (FK vers utilisateur) |

## Tables d'Interaction Utilisateur

### commentaire
Commentaires des utilisateurs sur les produits.

| Colonne | Type | Description |
|---------|------|-------------|
| utilisateur_id | INT | Utilisateur ayant commenté (PK, FK vers utilisateur) |
| skin_id | INT | Skin commenté (PK, FK vers skin) |
| date_publication | DATETIME | Date du commentaire (PK) |
| commentaire | TEXT | Contenu du commentaire |
| valide | TINYINT(1) | Statut de validation du commentaire |

### note
Notes attribuées aux produits par les utilisateurs.

| Colonne | Type | Description |
|---------|------|-------------|
| utilisateur_id | INT | Utilisateur ayant noté (PK, FK vers utilisateur) |
| skin_id | INT | Skin noté (PK, FK vers skin) |
| note | INT | Note attribuée |

### liste_envie
Liste de souhaits des utilisateurs.

| Colonne | Type | Description |
|---------|------|-------------|
| skin_id | INT | Skin dans la liste (PK, FK vers skin) |
| utilisateur_id | INT | Utilisateur propriétaire (PK, FK vers utilisateur) |
| date_update | DATETIME | Date d'ajout/mise à jour (PK) |

### historique
Historique de consultation des produits.

| Colonne | Type | Description |
|---------|------|-------------|
| skin_id | INT | Skin consulté (PK, FK vers skin) |
| utilisateur_id | INT | Utilisateur ayant consulté (PK, FK vers utilisateur) |
| date_consultation | DATETIME | Date de consultation (PK) |

## Diagramme de Relations

Le schéma de la base de données suit une structure relationnelle où :

- Un **utilisateur** peut avoir plusieurs **commandes**, **adresses**, **commentaires**, **notes**, et des articles dans sa **liste d'envies** et son **historique**
- Un **skin** appartient à un **type_skin** et peut avoir plusieurs **déclinaisons**
- Une **déclinaison** combine un **skin**, un niveau d'**usure** et un attribut **special**
- Une **commande** contient plusieurs **lignes de commande**, chacune liée à une **déclinaison**
- Un **panier** (représenté par **ligne_panier**) contient des **déclinaisons** pour un **utilisateur**

## Contraintes d'Intégrité

- Clés étrangères pour maintenir l'intégrité référentielle
- Contraintes de clé primaire composée pour les tables de relation
- Contraintes de non-nullité sur les champs obligatoires

## Initialisation de la Base de Données

La base de données peut être initialisée avec des données de test via la route `/base/init` qui exécute le script dans `controllers/fixtures_load.py`.
