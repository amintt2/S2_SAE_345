# Guide de Développement

Ce document fournit des informations pour les développeurs travaillant sur le projet e-commerce de skins CS:GO.

## Architecture du Projet

Le projet suit une architecture MVC (Modèle-Vue-Contrôleur) adaptée à Flask :

- **Modèle** : Représenté par les requêtes SQL dans les contrôleurs
- **Vue** : Templates Jinja2 dans le dossier `templates/`
- **Contrôleur** : Fichiers Python dans le dossier `controllers/`

## Organisation du Code

### Contrôleurs

Les contrôleurs sont organisés par fonctionnalité et par rôle d'utilisateur :

- `auth_security.py` : Gestion de l'authentification et de la sécurité
- `client_*.py` : Fonctionnalités accessibles aux clients
- `admin_*.py` : Fonctionnalités accessibles aux administrateurs
- `fixtures_load.py` : Initialisation de la base de données

### Templates

Les templates sont organisés de manière similaire aux contrôleurs :

- `admin/` : Templates pour l'interface administrateur
- `client/` : Templates pour l'interface client
- `auth/` : Templates pour l'authentification

### Base de Données

La connexion à la base de données est gérée par le fichier `connexion_db.py`. Les requêtes SQL sont intégrées directement dans les contrôleurs.

## Conventions de Codage

### Python

- Utiliser des noms de variables et de fonctions explicites
- Suivre la convention snake_case pour les noms de variables et de fonctions
- Commenter le code de manière appropriée
- Éviter les calculs en Python lorsque SQL peut être utilisé

### SQL

- Utiliser snake_case pour les noms de tables et de colonnes
- Nommer les clés étrangères avec le format `table_id`
- Préférer les requêtes SQL pour les calculs (sommes, moyennes, etc.)
- Utiliser des requêtes paramétrées pour éviter les injections SQL

### Templates

- Organiser les templates de manière hiérarchique
- Utiliser l'héritage de templates pour éviter la duplication de code
- Utiliser Tailwind CSS pour le style

## Workflow de Développement

1. **Comprendre les exigences** : Consulter le fichier `contexte.txt` et la documentation
2. **Développer localement** : Implémenter les fonctionnalités sur votre machine locale
3. **Tester** : Vérifier que les fonctionnalités fonctionnent comme prévu
4. **Déployer** : Déployer sur PythonAnywhere pour les tests en ligne

## Répartition des Tâches

Le projet est divisé en quatre parties principales, chacune attribuée à un étudiant :

1. **Étudiant 1** : Gestion des déclinaisons d'articles et du stock
2. **Étudiant 2** : Gestion des commentaires et des notes
3. **Étudiant 3** : Gestion des adresses d'expédition et de facturation
4. **Étudiant 4** : Gestion de la liste d'envies et de l'historique des articles consultés

## Conseils pour le Développement

- **Requêtes SQL** : Privilégier les requêtes SQL pour les calculs et les agrégations
- **Sessions** : Utiliser les sessions Flask pour stocker les informations temporaires
- **Sécurité** : Vérifier les entrées utilisateur et utiliser des requêtes paramétrées
- **Responsive Design** : S'assurer que l'interface est utilisable sur différents appareils
- **Tests** : Tester régulièrement les fonctionnalités implémentées

## Ressources Utiles

- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation Jinja2](https://jinja.palletsprojects.com/)
- [Documentation Tailwind CSS](https://tailwindcss.com/docs)
- [Documentation PyMySQL](https://pymysql.readthedocs.io/)
- [PythonAnywhere](https://help.pythonanywhere.com/)
