# Fonctionnalités du Projet E-Commerce

Ce document liste les fonctionnalités implémentées et celles qui restent à développer dans le projet, conformément au fichier contexte.txt.

*Note : Cette liste est basée sur les fichiers contrôleurs présents (`/controllers`) et la documentation initiale. Le statut détaillé (✅, ⚠️, ❌) de chaque sous-fonctionnalité n'a pas été vérifié par une analyse approfondie du code récent.*

## Fonctionnalités Implémentées

### Système d'Authentification
- ✅ Inscription et connexion des utilisateurs
- ✅ Contrôle d'accès basé sur les rôles (client/admin)
- ✅ Hachage des mots de passe pour la sécurité
- ✅ Gestion des sessions

### Fonctionnalités Client (Front Office)

#### Navigation des Produits
- ✅ Affichage des articles disponibles avec images et détails
- ✅ Filtrage des articles par type, fourchette de prix et nom
- ✅ Affichage des déclinaisons de produits

#### Panier d'Achat
- ✅ Ajout de produits au panier avec déclinaisons spécifiques
- ✅ Mise à jour des quantités
- ✅ Suppression d'articles
- ✅ Affichage du total du panier
- ✅ Vérification du stock disponible

#### Traitement des Commandes
- ✅ Validation du panier générant une commande
- ✅ Affichage des commandes (nombre d'articles, nom du client, date, prix total)
- ✅ Affichage des détails d'une commande
- ✅ Visualisation de l'état de la commande

### Fonctionnalités Admin (Back Office)

#### Gestion des Produits
- ✅ Ajout, modification et suppression de produits
- ✅ Gestion des déclinaisons de produits
- ✅ Mise à jour des niveaux de stock
- ✅ Gestion des catégories de produits

#### Gestion des Commandes
- ✅ Affichage de toutes les commandes
- ✅ Mise à jour de l'état des commandes
- ✅ Affichage des détails des commandes
- ✅ Visualisation du stock de chaque article

## Fonctionnalités Partiellement Implémentées ou En Cours

### Gestion des Déclinaisons (Étudiant 1)
- ⚠️ Gestion du stock pour des articles de déclinaison différente
- ⚠️ Affichage du nombre de déclinaisons des articles
- ⚠️ Interface pour choisir la déclinaison lors de l'ajout au panier
- ⚠️ Gestion de la suppression/modification de déclinaisons déjà commandées

### Système de Commentaires et Notes (Étudiant 2)
- ⚠️ Affichage du nombre de commentaires et de la note moyenne
- ⚠️ Système permettant aux clients ayant acheté un article de laisser un avis
- ⚠️ Limitation à 3 commentaires par article par utilisateur
- ⚠️ Affichage chronologique des commentaires

### Gestion des Adresses (Étudiant 3)
- ⚠️ Sélection d'adresse pour passer une commande
- ⚠️ Gestion des adresses favorites
- ⚠️ Limitation à 4 adresses "fonctionnelles" par utilisateur
- ⚠️ Vérification du format du code postal

### Liste d'Envies et Historique (Étudiant 4)
- ⚠️ Ajout/suppression des articles dans la liste d'envies
- ⚠️ Organisation des articles dans la liste d'envies
- ⚠️ Historique des articles consultés
- ⚠️ Limitation de l'historique à 6 articles différents

## Fonctionnalités à Implémenter

### Gestion des Déclinaisons (Étudiant 1)
- ❌ Affichage du stock restant avec une ou plusieurs déclinaisons de l'article
- ❌ Décrémentation du stock lors de l'ajout au panier
- ❌ Interface administrateur pour consulter le stock des articles par déclinaison
- ❌ Interface pour ajouter/modifier/supprimer de nouvelles déclinaisons
- ❌ Gestion de 2 déclinaisons avec 2 propriétés différentes
- ❌ Gestion de la "taille unique" ou "couleur unique"
- ❌ Visualisation de données sur les stocks (coût du stock par déclinaison, nombre d'articles en stock)

### Système de Commentaires et Notes (Étudiant 2)
- ❌ Interface administrateur pour voir les nouveaux commentaires
- ❌ Possibilité pour l'administrateur de répondre aux commentaires
- ❌ Système de validation des commentaires par l'administrateur
- ❌ Visualisation de données sur les commentaires par catégorie
- ❌ Interface avancée pour visualiser les commentaires par article dans une catégorie

### Gestion des Adresses (Étudiant 3)
- ❌ Affichage d'un tableau d'adresses avec statut (favorite, non valide)
- ❌ Affichage du nombre de commandes par adresse
- ❌ Gestion avancée de la suppression/modification d'adresses utilisées dans les commandes
- ❌ Interface pour modifier les informations de l'utilisateur
- ❌ Visualisation de données sur les adresses (ventes par département, chiffre d'affaire)
- ❌ Affichage d'une carte avec les ventes par département

### Liste d'Envies et Historique (Étudiant 4)
- ❌ Retrait automatique des articles commandés de la liste d'envies
- ❌ Affichage du nombre d'autres clients ayant un article dans leur liste d'envies
- ❌ Stockage du nombre de consultations d'un article
- ❌ Retrait des articles de l'historique au bout d'un mois
- ❌ Visualisation de données sur les listes d'envies et l'historique

## Exigences Techniques et Contraintes

- ❌ Pas d'utilisation de la fonction url_for pour gérer une route
- ❌ Pas d'utilisation de route paramétrée /route/<id> au lieu des routes avec paramètres GET /route?id=
- ❌ Pas de calcul en Python (somme, moyenne) au lieu d'une utilisation de SQL
- ❌ Pas d'utilisation des mots clés "WITH" ou "TRY" en Python
- ❌ Pas de boucle Python dans le fichier app.py
- ❌ Pas d'utilisation de JavaScript
- ❌ Pas d'utilisation de module Python non vu en TP
- ❌ Pas d'utilisation de code non maîtrisé
