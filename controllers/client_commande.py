#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['GET', 'POST'])
def client_commande_valide():
    curseur = get_db().cursor()
    identifiant_client = session['id_user']
    
    # Get cart items first to check if the cart is empty
    sql = '''
        SELECT 
            ligne_panier.declinaison_id, 
            ligne_panier.quantite, 
            declinaison.prix_declinaison,
            skin.nom_skin AS designation,
            skin.id_skin AS id_article,
            type_skin.libelle_type_skin,
            usure.libelle_usure,
            special.libelle_special,
            declinaison.stock,
            ligne_panier.quantite * declinaison.prix_declinaison AS prix_ligne
        FROM ligne_panier
        JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
        JOIN skin ON declinaison.skin_id = skin.id_skin
        JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
        JOIN usure ON declinaison.usure_id = usure.id_usure
        JOIN special ON declinaison.special_id = special.id_special
        WHERE ligne_panier.utilisateur_id = %s
    '''
    curseur.execute(sql, (identifiant_client,))
    articles_panier = curseur.fetchall()
    
    # Check if cart is empty
    if not articles_panier:
        flash(u'Votre panier est vide', 'alert-warning')
        return redirect('/client/article/show')
    
    # Check for favorite addresses
    sql = ''' 
        SELECT * FROM adresse WHERE utilisateur_id = %s AND est_favori = 1 AND est_valide = 1
    '''
    curseur.execute(sql, (identifiant_client,))
    adresses = curseur.fetchall()
    
    # Check if there are any favorite addresses
    if not adresses:
        flash(u'Aucune adresse favorite trouvée. Veuillez en créer une.', 'alert-warning')
        return redirect('/client/coordonnee/add_adresse')
    
    # Get all valid addresses for the user
    sql = ''' 
        SELECT * FROM adresse WHERE utilisateur_id = %s AND est_valide = 1
    '''
    curseur.execute(sql, (identifiant_client,))
    adresses = curseur.fetchall()
    
    # Calculate total price
    if len(articles_panier) >= 1:
        sql = '''
            SELECT SUM(ligne_panier.quantite * declinaison.prix_declinaison) AS prix_total
            FROM ligne_panier
            JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
            WHERE ligne_panier.utilisateur_id = %s
        '''
        curseur.execute(sql, (identifiant_client,))
        prix_total = curseur.fetchone()['prix_total']
    else:
        prix_total = None
        
    # Find the favorite address to preselect in the form
    id_adresse_fav = 0
    for adresse in adresses:
        if adresse['est_favori'] == 1:
            id_adresse_fav = adresse['id_adresse']
            break
        
    # etape 2 : selection des adresses
    return render_template('client/boutique/panier_validation_adresses.html'
                           , adresses=adresses
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , validation=1
                           , est_favori=1
                           , id_adresse_fav=id_adresse_fav
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    curseur = get_db().cursor()
    identifiant_client = session['id_user']
    
    # Si le bouton "Mettre à jour les adresses" a été cliqué
    if request.form.get('valider_adresses') == '1':
        # Affichage de la page avec les adresses sélectionnées
        sql = '''
            SELECT 
                ligne_panier.*,
                skin.nom_skin AS designation,
                skin.id_skin AS id_article,
                type_skin.libelle_type_skin,
                usure.libelle_usure,
                special.libelle_special,
                declinaison.stock,
                ligne_panier.quantite * declinaison.prix_declinaison AS prix_ligne
            FROM ligne_panier
            JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
            JOIN skin ON declinaison.skin_id = skin.id_skin
            JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            JOIN usure ON declinaison.usure_id = usure.id_usure
            JOIN special ON declinaison.special_id = special.id_special
            WHERE ligne_panier.utilisateur_id = %s
        '''
        curseur.execute(sql, (identifiant_client,))
        articles_panier = curseur.fetchall()
        
        # Récupération des adresses valides
        sql = '''
            SELECT 
                adresse.*
            FROM adresse
            WHERE adresse.utilisateur_id = %s AND adresse.est_valide = 1
            ORDER BY adresse.est_favori DESC, adresse.date_utilisation DESC
        '''
        curseur.execute(sql, (identifiant_client,))
        adresses = curseur.fetchall()
        
        # Prix total (calculé en SQL)
        sql = '''
            SELECT SUM(ligne_panier.quantite * declinaison.prix_declinaison) AS prix_total
            FROM ligne_panier
            JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
            WHERE ligne_panier.utilisateur_id = %s
        '''
        curseur.execute(sql, (identifiant_client,))
        prix_total = curseur.fetchone()['prix_total'] or 0  # Utilisation de OR pour éviter les None
        
        # Trouver l'adresse favorite en Python
        id_adresse_fav = 0
        for adresse in adresses:
            if adresse['est_favori'] == 1:
                id_adresse_fav = adresse['id_adresse']
                break
        
        # Réafficher la page avec les valeurs mises à jour
        flash(u'Adresses mises à jour avec succès', 'alert-success')
        return render_template('client/boutique/panier_validation_adresses.html',
                           adresses=adresses,
                           articles_panier=articles_panier,
                           prix_total=prix_total,
                           validation=1,
                           est_favori=1,
                           id_adresse_fav=id_adresse_fav,
                           request=request)
    
    # Si on finalise la commande (l'utilisateur a cliqué sur "Finaliser")
    
    # Récupérer les adresses sélectionnées
    identifiant_adresse_livraison = request.form.get('adresse_livraison_id')
    identifiant_adresse_facturation = request.form.get('adresse_facturation_id')
    
    # Vérification en Python des adresses sélectionnées
    if not identifiant_adresse_livraison or not identifiant_adresse_facturation:
        flash(u'Veuillez sélectionner des adresses de livraison et facturation', 'alert-warning')
        return redirect('/client/commande/valide')
    
    # Vérifier que les adresses sont valides
    sql = '''
        SELECT adresse.id_adresse, adresse.est_valide
        FROM adresse
        WHERE adresse.id_adresse IN (%s, %s)
        AND adresse.utilisateur_id = %s
    '''
    # Ensure IDs are distinct for the IN clause if they are the same, 
    # but it's better to handle this in Python logic after fetching.
    curseur.execute(sql, (identifiant_adresse_livraison, identifiant_adresse_facturation, identifiant_client))
    adresses_verifiees = curseur.fetchall()
    
    # Vérification en Python - revised logic
    returned_ids = {addr['id_adresse'] for addr in adresses_verifiees}
    adresse_livraison_ok = int(identifiant_adresse_livraison) in returned_ids
    adresse_facturation_ok = int(identifiant_adresse_facturation) in returned_ids

    if not adresse_livraison_ok or not adresse_facturation_ok:
        flash(u'Une des adresses sélectionnées n\'existe pas ou ne vous appartient pas.', 'alert-warning')
        return redirect('/client/commande/valide')
    
    # Check if all verified addresses are actually valid (est_valide == 1)
    adresses_valides = all(adresse['est_valide'] == 1 for adresse in adresses_verifiees)
    if not adresses_valides:
        flash(u'Une des adresses sélectionnées n\'est pas valide', 'alert-warning')
        return redirect('/client/commande/valide')
    
    # Vérifier que le panier n'est pas vide
    sql = '''
        SELECT COUNT(*) AS nb_articles
        FROM ligne_panier
        WHERE ligne_panier.utilisateur_id = %s
    '''
    curseur.execute(sql, (identifiant_client,))
    nb_articles = curseur.fetchone()['nb_articles']
    
    if nb_articles == 0:
        flash(u'Votre panier est vide', 'alert-warning')
        return redirect('/client/article/show')
    
    # Création de la commande
    sql = '''
        INSERT INTO commande(date_achat, etat_id, utilisateur_id, adresse_livraison_id, adresse_facturation_id) 
        VALUES (NOW(), 1, %s, %s, %s)
    '''
    curseur.execute(sql, (identifiant_client, identifiant_adresse_livraison, identifiant_adresse_facturation))
    
    # Récupération de l'identifiant de la commande
    sql = '''SELECT LAST_INSERT_ID() AS id_commande'''
    curseur.execute(sql)
    identifiant_commande = curseur.fetchone()['id_commande']
    
    # Mettre à jour les dates d'utilisation des adresses
    sql = '''
        UPDATE adresse
        SET adresse.date_utilisation = NOW()
        WHERE adresse.id_adresse IN (%s, %s)
    '''
    curseur.execute(sql, (identifiant_adresse_livraison, identifiant_adresse_facturation))
    
    # Mettre à jour l'adresse favorite (réinitialisation puis définition)
    sql = '''
        UPDATE adresse
        SET adresse.est_favori = 0
        WHERE adresse.utilisateur_id = %s
    '''
    curseur.execute(sql, (identifiant_client,))
    
    sql = '''
        UPDATE adresse
        SET adresse.est_favori = 1
        WHERE adresse.id_adresse = %s
    '''
    curseur.execute(sql, (identifiant_adresse_livraison,))
    
    # Transfert des articles du panier vers la commande
    sql = '''
        INSERT INTO ligne_commande(declinaison_id, commande_id, prix, quantite)
        SELECT ligne_panier.declinaison_id, %s, declinaison.prix_declinaison, ligne_panier.quantite
        FROM ligne_panier
        JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
        WHERE ligne_panier.utilisateur_id = %s
    '''
    curseur.execute(sql, (identifiant_commande, identifiant_client))
    
    # Suppression des articles du panier
    sql = '''
        DELETE FROM ligne_panier 
        WHERE ligne_panier.utilisateur_id = %s
    '''
    curseur.execute(sql, (identifiant_client,))
    
    get_db().commit()
    flash(u'Commande validée avec succès', 'alert-success')
    
    return redirect('/client/commande/show')


@client_commande.route('/client/commande/show')
def client_commande_show():
    curseur = get_db().cursor()
    identifiant_client = session['id_user']
    
    # Récupération des commandes
    sql = '''
        SELECT 
            commande.id_commande AS identifiant_commande,
            commande.date_achat,
            COALESCE(SUM(ligne_commande.quantite), 0) AS nombre_articles,
            COALESCE(SUM(ligne_commande.prix * ligne_commande.quantite), 0) AS prix_total_commande,
            etat.libelle_etat,
            etat.id_etat AS identifiant_etat
        FROM commande
        LEFT JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
        LEFT JOIN etat ON commande.etat_id = etat.id_etat
        WHERE commande.utilisateur_id = %s
        GROUP BY commande.id_commande, commande.date_achat, etat.libelle_etat, etat.id_etat
        ORDER BY commande.date_achat DESC
    '''
    curseur.execute(sql, (identifiant_client,))
    commandes = curseur.fetchall()

    articles_commande = None
    informations_adresses_commande = None
    identifiant_commande = request.args.get('id_commande')
    
    if identifiant_commande:
        # Récupération des articles de la commande
        sql = '''
            SELECT 
                skin.nom_skin AS nom_article,
                skin.image AS image_article,
                type_skin.libelle_type_skin,
                usure.libelle_usure,
                special.libelle_special,
                ligne_commande.quantite AS quantite_article,
                ligne_commande.prix AS prix_unitaire,
                (ligne_commande.prix * ligne_commande.quantite) AS prix_total_ligne
            FROM ligne_commande
            JOIN declinaison ON ligne_commande.declinaison_id = declinaison.id_declinaison
            JOIN skin ON declinaison.skin_id = skin.id_skin
            JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            JOIN usure ON declinaison.usure_id = usure.id_usure
            JOIN special ON declinaison.special_id = special.id_special
            WHERE ligne_commande.commande_id = %s
        '''
        curseur.execute(sql, (identifiant_commande,))
        articles_commande = curseur.fetchall()
        
        # Récupération des adresses
        sql = '''
            SELECT 
                adresse_livraison.nom AS nom_livraison,
                adresse_livraison.rue AS rue_livraison,
                adresse_livraison.code_postal AS code_postal_livraison,
                adresse_livraison.ville AS ville_livraison,
                adresse_facturation.nom AS nom_facturation,
                adresse_facturation.rue AS rue_facturation,
                adresse_facturation.code_postal AS code_postal_facturation,
                adresse_facturation.ville AS ville_facturation,
                commande.adresse_livraison_id AS identifiant_adresse_livraison,
                commande.adresse_facturation_id AS identifiant_adresse_facturation,
                CASE 
                    WHEN commande.adresse_livraison_id = commande.adresse_facturation_id 
                    THEN 'adresse_identique' 
                    ELSE 'adresse_differente' 
                END AS adresse_identique
            FROM commande
            JOIN adresse AS adresse_livraison ON commande.adresse_livraison_id = adresse_livraison.id_adresse
            JOIN adresse AS adresse_facturation ON commande.adresse_facturation_id = adresse_facturation.id_adresse
            WHERE commande.id_commande = %s
            AND commande.utilisateur_id = %s
        '''
        curseur.execute(sql, (identifiant_commande, identifiant_client))
        informations_adresses_commande = curseur.fetchone()
        
    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=informations_adresses_commande)

