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





Ramarque prof après livrable 2 :

# Bonne chose :
- Premier partie (Client) tout bon (Page accueil)




# Chose a améliorer :
- (Client) Ajouter des bouton ( style + et - ) pour incrementer et decrementer les quantités sur la page d'Acceuil.
- (Client) Ajouter le sous total dans la page de panier.
- (Client) Message pour afficher rupture de stock.
- (Client) Dire que la cantier est vider au lieux d'afficher 0
- (Client) Retier directement produis si = 0
- (Admin) Changer la position pour avoir les en cours en premier dans le tableau
- (Admin) Que des Valider pas de liver ou autre



# Chose a refaire :
- Pas de url for suivre les consigne et refaire les url pour utiliser les bonne route.