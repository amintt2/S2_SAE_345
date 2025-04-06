#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
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
    
    # First check if there are favorite addresses
    sql = '''SELECT COUNT(*) as count FROM adresse WHERE utilisateur_id = %s AND est_favori = 1 AND est_valide = 1'''
    curseur.execute(sql, (identifiant_client,))
    address_count = curseur.fetchone()['count']
    
    # If no favorite addresses, redirect to address creation
    if address_count == 0:
        flash(u'Aucune adresse favorite trouvée. Veuillez en créer une.', 'alert-warning')
        return redirect('/client/coordonnee/add_adresse')
    
    # Récupération des informations d'adresse
    identifiant_adresse_livraison = request.form.get('adresse_livraison_id', None)
    adresse_identique = request.form.get('adresse_identique', None)
    
    # Check if coming directly from cart (not from address selection)
    if not identifiant_adresse_livraison:
        # Redirect to address selection first
        return redirect('/client/commande/valide')
    
    # Vérifier que l'adresse de livraison appartient bien à l'utilisateur et est valide
    sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s AND est_valide = 1"
    curseur.execute(sql, (identifiant_adresse_livraison, identifiant_client))
    adresse_livraison = curseur.fetchone()
    
    if not adresse_livraison:
        flash(u'L\'adresse de livraison sélectionnée n\'est pas valide.', 'alert-warning')
        return redirect('/client/commande/valide')
    
    # Si l'adresse de facturation est identique à l'adresse de livraison
    if adresse_identique == 'adresse_identique':
        identifiant_adresse_facturation = identifiant_adresse_livraison
    else:
        identifiant_adresse_facturation = request.form.get('adresse_facturation_id', None)
        
        # Vérifier que l'adresse de facturation appartient bien à l'utilisateur et est valide
        sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s AND est_valide = 1"
        curseur.execute(sql, (identifiant_adresse_facturation, identifiant_client))
        adresse_facturation = curseur.fetchone()
        
        if not adresse_facturation:
            flash(u'L\'adresse de facturation sélectionnée n\'est pas valide.', 'alert-warning')
            return redirect('/client/commande/valide')
    
    # Récupération des articles du panier
    requete_sql = ''' 
        SELECT  ligne_panier.declinaison_id AS identifiant_declinaison,
                ligne_panier.quantite AS quantite,
                declinaison.prix_declinaison * ligne_panier.quantite AS prix_total
        FROM ligne_panier
        JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
        WHERE ligne_panier.utilisateur_id = %s
    '''
    curseur.execute(requete_sql, (identifiant_client,))
    articles_panier = curseur.fetchall()
    
    if not articles_panier:
        flash(u'Pas d\'articles dans le panier', 'alert-warning')
        return redirect('/client/article/show')

    # Création de la commande
    requete_sql = '''
        INSERT INTO commande(date_achat, etat_id, utilisateur_id, adresse_livraison_id, adresse_facturation_id) 
        VALUES (NOW(), 1, %s, %s, %s)
    '''
    curseur.execute(requete_sql, (identifiant_client, identifiant_adresse_livraison, identifiant_adresse_facturation))
    
    # Mettre à jour la date d'utilisation des adresses
    requete_sql = "UPDATE adresse SET date_utilisation = NOW() WHERE id_adresse IN (%s, %s)"
    curseur.execute(requete_sql, (identifiant_adresse_livraison, identifiant_adresse_facturation))
    
    # Définir l'adresse de livraison comme adresse favorite
    requete_sql = "UPDATE adresse SET est_favori = 0 WHERE utilisateur_id = %s"
    curseur.execute(requete_sql, (identifiant_client,))
    
    requete_sql = "UPDATE adresse SET est_favori = 1 WHERE id_adresse = %s"
    curseur.execute(requete_sql, (identifiant_adresse_livraison,))
    
    # Récupération de l'identifiant de la commande créée
    requete_sql = '''SELECT LAST_INSERT_ID() AS identifiant_derniere_insertion'''
    curseur.execute(requete_sql)
    identifiant_commande = curseur.fetchone()['identifiant_derniere_insertion']

    for article in articles_panier:
        requete_sql = '''
            INSERT INTO ligne_commande(declinaison_id, commande_id, prix, quantite) 
            VALUES (%s, %s, %s, %s)
        '''
        curseur.execute(requete_sql, (
            article['identifiant_declinaison'],
            identifiant_commande,
            article['prix_total'],
            article['quantite']
        ))

        # Suppression de l'article du panier
        requete_sql = '''
            DELETE FROM ligne_panier 
            WHERE declinaison_id = %s AND utilisateur_id = %s
        '''
        curseur.execute(requete_sql, (article['identifiant_declinaison'], identifiant_client))

    get_db().commit()
    flash(u'Commande validée avec succès', 'alert-success')
    
    return redirect('/client/article/show')


@client_commande.route('/client/commande/show')
def client_commande_show():
    print('client_commande_show')
    
    curseur = get_db().cursor()
    identifiant_client = session['id_user']
    
    # Récupération de toutes les commandes du client
    sql = '''
        SELECT 
            c.id_commande AS identifiant_commande,
            c.date_achat,
            SUM(lc.quantite) AS nombre_articles,
            SUM(lc.prix * lc.quantite) AS prix_total_commande,
            e.libelle_etat,
            e.id_etat AS identifiant_etat
        FROM commande AS c
        LEFT JOIN ligne_commande AS lc ON c.id_commande = lc.commande_id
        LEFT JOIN etat AS e ON c.etat_id = e.id_etat
        WHERE c.utilisateur_id = %s
        GROUP BY c.id_commande, c.date_achat, e.libelle_etat, e.id_etat
        ORDER BY c.date_achat DESC
    '''
    curseur.execute(sql, (identifiant_client,))
    commandes = curseur.fetchall()

    articles_commande = None
    informations_adresses_commande = None
    identifiant_commande = request.args.get('id_commande', None)
    
    if identifiant_commande is not None:
        print(identifiant_commande)
        
        # Récupération des articles de la commande
        sql = '''
            SELECT 
                s.nom_skin AS nom_article,
                s.image AS image_article,
                ts.libelle_type_skin,
                u.libelle_usure,
                sp.libelle_special,
                SUM(lc.quantite) AS quantite_article,
                lc.prix AS prix_unitaire,
                SUM(lc.prix * lc.quantite) AS prix_total_ligne
            FROM ligne_commande AS lc
            JOIN declinaison AS d ON lc.declinaison_id = d.id_declinaison
            JOIN skin AS s ON d.skin_id = s.id_skin
            JOIN type_skin AS ts ON s.type_skin_id = ts.id_type_skin
            JOIN usure AS u ON d.usure_id = u.id_usure
            JOIN special AS sp ON d.special_id = sp.id_special
            WHERE lc.commande_id = %s
            GROUP BY s.nom_skin, s.image, ts.libelle_type_skin, u.libelle_usure, 
                     sp.libelle_special, lc.prix
        '''
        curseur.execute(sql, (identifiant_commande,))
        articles_commande = curseur.fetchall()
        
        # Récupération des informations d'adresses pour la commande
        requete_sql = '''
            SELECT 
                commande.adresse_livraison_id AS identifiant_adresse_livraison,
                commande.adresse_facturation_id AS identifiant_adresse_facturation,
                adresse_livraison.nom AS nom_livraison,
                adresse_livraison.rue AS rue_livraison,
                adresse_livraison.code_postal AS code_postal_livraison,
                adresse_livraison.ville AS ville_livraison,
                adresse_facturation.nom AS nom_facturation,
                adresse_facturation.rue AS rue_facturation,
                adresse_facturation.code_postal AS code_postal_facturation,
                adresse_facturation.ville AS ville_facturation,
                CASE 
                    WHEN commande.adresse_livraison_id = commande.adresse_facturation_id 
                    THEN 'adresse_identique' 
                    ELSE 'adresse_differente' 
                END AS adresse_identique
            FROM commande
            JOIN adresse AS adresse_livraison ON commande.adresse_livraison_id = adresse_livraison.id_adresse
            JOIN adresse AS adresse_facturation ON commande.adresse_facturation_id = adresse_facturation.id_adresse
            WHERE commande.id_commande = %s
        '''
        curseur.execute(requete_sql, (identifiant_commande,))
        informations_adresses_commande = curseur.fetchone()
        
    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=informations_adresses_commande
                           )

