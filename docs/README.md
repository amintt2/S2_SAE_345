# Documentation du Projet E-Commerce de Skins CS:GO

## Aperçu du Projet

Ce projet est un site e-commerce spécialisé dans la vente de skins CS:GO. L'application suit une architecture client-serveur utilisant Flask comme framework web et MySQL comme base de données. Le système est conçu avec deux rôles d'utilisateurs principaux :

- **Client** : Utilisateurs réguliers qui peuvent parcourir les produits, ajouter des articles au panier, passer des commandes et gérer leur compte
- **Admin** : Administrateurs qui peuvent gérer les produits, consulter les commandes et gérer les opérations backend

L'application implémente un flux de travail e-commerce complet comprenant la navigation des produits avec filtrage, la gestion du panier d'achat, le traitement des commandes, l'authentification des utilisateurs et les fonctionnalités d'administration.

## Architecture Technique

### Framework et Bibliothèques
- **Backend** : Python Flask
- **Base de données** : MySQL avec connecteur PyMySQL
- **Frontend** : HTML, Tailwind CSS, templates Jinja2
- **Authentification** : Implémentation personnalisée avec hachage de mot de passe
- **Variables d'environnement** : dotenv pour la gestion de la configuration

### Structure du Projet
- **app.py** : Point d'entrée principal de l'application et enregistrement des routes
- **connexion_db.py** : Gestion de la connexion à la base de données
- **controllers/** : Contient tous les gestionnaires de routes organisés par fonctionnalité
  - **auth_security.py** : Fonctions d'authentification et de sécurité
  - **client_*.py** : Fonctionnalités destinées aux clients
  - **admin_*.py** : Fonctionnalités d'administration
  - **fixtures_load.py** : Initialisation de la base de données et données de test
- **templates/** : Templates HTML organisés par rôle d'utilisateur et fonctionnalité
  - **admin/** : Templates d'interface administrateur
  - **client/** : Templates d'interface client
  - **auth/** : Templates d'authentification
- **static/** : Ressources statiques (images, CSS, JavaScript)

## Structure de la Base de Données

La base de données suit un modèle relationnel avec les tables clés suivantes :

1. **utilisateur** : Comptes utilisateurs avec informations d'authentification
2. **skin** : Table principale des produits contenant les skins CS:GO
3. **type_skin** : Catégories de produits (AK-47, AWP, Knife, etc.)
4. **usure** : Niveaux d'usure pour les skins (Neuf, Très peu usée, etc.)
5. **special** : Attributs spéciaux (StatTrak™, Souvenir, etc.)
6. **declinaison** : Variations de produits combinant skin, niveau d'usure et attributs spéciaux
7. **commande** : Commandes passées par les utilisateurs
8. **ligne_commande** : Lignes de commande
9. **ligne_panier** : Articles du panier d'achat
10. **adresse** : Adresses des utilisateurs pour l'expédition et la facturation
11. **etat** : Suivi de l'état des commandes
12. **commentaire** : Avis et commentaires sur les produits
13. **note** : Évaluations des produits
14. **liste_envie** : Fonctionnalité de liste de souhaits
15. **historique** : Historique de navigation des produits

La conception de la base de données implémente des contraintes de clé étrangère appropriées pour maintenir l'intégrité des données entre les tables liées.

## Installation et Configuration

### Prérequis
- Python 3.x
- MySQL
- pip (gestionnaire de paquets Python)

### Installation
1. Cloner le dépôt
   ```bash
   git clone https://github.com/amintt2/S2_SAE_345.git
   cd S2_SAE_345
   ```

2. Créer un environnement virtuel
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installer les dépendances
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement
   Créer un fichier `.env` à la racine du projet avec les informations suivantes :
   ```
   DB_HOST=localhost
   DB_USER=votre_utilisateur
   DB_PASSWORD=votre_mot_de_passe
   DB_NAME=nom_de_votre_base
   ```

5. Initialiser la base de données
   ```bash
   # Accéder à l'URL suivante après avoir démarré l'application
   http://localhost:5000/base/init
   ```

6. Démarrer l'application
   ```bash
   python app.py
   ```

## Utilisation

### Accès à l'application
- **Interface client** : http://localhost:5000/client/article/show
- **Interface admin** : http://localhost:5000/admin/article/show

### Comptes par défaut
- **Admin** : 
  - Login : admin
  - Mot de passe : admin
- **Client** : 
  - Login : client
  - Mot de passe : client
- **Client2** : 
  - Login : client2
  - Mot de passe : client2

## Documentation Supplémentaire

- [Liste des fonctionnalités](./fonctionnalites.md) - Fonctionnalités implémentées et à venir
- [Guide de développement](./guide_developpement.md) - Guide pour les développeurs
- [Structure de la base de données](./structure_bdd.md) - Détails sur le schéma de la base de données
