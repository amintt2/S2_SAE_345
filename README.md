# Projet E-Commerce Flask - Skins CS:GO

Bienvenue dans le projet E-Commerce pour la vente de skins CS:GO.

Ce projet est une application web construite avec Flask et MySQL, permettant aux utilisateurs de parcourir, acheter et gérer des skins CS:GO, avec une interface d'administration dédiée.

## Documentation Détaillée

Pour une documentation complète sur l'architecture, l'installation, la structure de la base de données et les fonctionnalités, veuillez consulter le dossier `/docs` :

- **[Documentation Principale](./docs/README.md)**
- [Liste des Fonctionnalités](./docs/fonctionnalites.md)
- [Guide de Développement](./docs/guide_developpement.md)
- [Structure de la Base de Données](./docs/structure_bdd.md)

## Démarrage Rapide

1.  Clonez le dépôt.
2.  Configurez un environnement virtuel Python.
3.  Installez les dépendances : `pip install -r requirements.txt`
4.  Configurez les variables d'environnement dans un fichier `.env` (voir `docs/README.md` pour les détails).
5.  Démarrez l'application : `python app.py`
6.  Initialisez la base de données via `http://localhost:5000/base/init` (si nécessaire).

Les comptes par défaut sont disponibles dans `docs/README.md`.

# SAE1.03-1.04


## Lexique : 
✅ Done
🏗️ In Progress
⏳ Not Started
👤 Assigned to (with initials)

## Livrable 2
Le livrable 2 comprend:

### 🌐 Fonctionnalités Front Office (Client) 
- Affichage des articles et panier (même vue) 👤 Maxime MIGUET / Timothé SANDT
  - Prix total du panier ✅
  - Stock restant ✅
  - Filtrage par catégorie ✅
- Gestion du panier 👤 Timothé SANDT
  - Ajout/modification des quantités ✅
  - Suppression d'articles ✅
  - Validation et génération de commande 🏗️
- Espace client 👤 Constant SUCHET
  - Visualisation des commandes ✅
  - Détail des commandes ✅
  - Suivi de l'état des commandes 🏗️

### 🔧 Fonctionnalités Back Office (Vendeur)
- Gestion des commandes 👤 Constant SUCHET
  - Liste complète des commandes ✅
  - Détail des commandes (articles, prix, client) ✅
  - Modification de l'état des commandes ✅
- Gestion du stock 👤 Tahar Amin Touzi
  - Visualisation du stock 🏗️
  - Modification du stock 🏗️
  - Vérification de disponibilité 🏗️

### 📝 Notes importantes
- Application testable sur PythonAnywhere
- Gestion des sessions pour les filtres
- Vérification des stocks via SQL
- Paniers distincts par client


## Setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

Créer le fichier .env avec vos informations de connection mysql
```
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
```

Reamrque du prof :
Remetre le filtre inisial du prof 
il veux moins de truc a cocher.
Garde en memoir le filtre et ne retire rien meme si il est modifier
filtre texte obligatoire. 





# Remarques du professeur après livrable 2

## ✅ Points positifs
- **Partie Client** : Interface d'accueil très satisfaisante

## 🔧 Améliorations requises

### Côté Client
- **Gestion des quantités** : Ajouter des boutons **+** et **-** pour incrémenter/décrémenter les quantités sur la page d'accueil
- **Affichage panier** : 
  - Ajouter le **sous-total** dans la page panier
  - Afficher "**Panier vide**" au lieu de 0
  - **Supprimer automatiquement** les produits quand quantité = 0
- **Stocks** : Afficher clairement un message de **rupture de stock**

### Côté Admin
- **Affichage commandes** :
  - **Réorganiser** le tableau pour avoir les commandes en cours en premier ( order by )
  - Simplifier les états : uniquement "**Validé**" (pas de "Livré" ou autres)

## ⚠️ Points à refaire
- **Routing** : Ne pas utiliser `url_for()`, suivre les conventions de routing et refaire les URLs selon les bonnes pratiques