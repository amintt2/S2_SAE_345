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
    sql = ''' selection des articles d'un panier 
    '''
    articles_panier = []
    if len(articles_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    # etape 2 : selection des adresses
    return render_template('client/boutique/panier_validation_adresses.html'
                           #, adresses=adresses
                           , articles_panier=articles_panier
                           , prix_total= prix_total
                           , validation=1
                           #, id_adresse_fav=id_adresse_fav
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    curseur = get_db().cursor()
    identifiant_client = session['id_user']
    
    # Récupération des informations d'adresse
    identifiant_adresse_livraison = request.form.get('adresse_livraison_id', None)
    adresse_identique = request.form.get('adresse_identique', None)
    
    # Si l'adresse de facturation est identique à l'adresse de livraison
    if adresse_identique == 'adresse_identique':
        identifiant_adresse_facturation = identifiant_adresse_livraison
    else:
        identifiant_adresse_facturation = request.form.get('adresse_facturation_id', None)
    
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
        INSERT INTO commande(
            date_achat,
            etat_id,
            utilisateur_id,
            adresse_livraison_id,
            adresse_facturation_id
        ) VALUES (
            NOW(),
            1,
            %s,
            %s,
            %s
        )
    '''
    curseur.execute(requete_sql, (identifiant_client, identifiant_adresse_livraison, identifiant_adresse_facturation))
    
    # Récupération de l'identifiant de la commande créée
    requete_sql = '''SELECT LAST_INSERT_ID() AS identifiant_derniere_insertion'''
    curseur.execute(requete_sql)
    identifiant_commande = curseur.fetchone()['identifiant_derniere_insertion']

    # Traitement des articles du panier
    for article in articles_panier:
        # Ajout d'une ligne de commande
        requete_sql = '''
            INSERT INTO ligne_commande(
                declinaison_id,
                commande_id,
                prix,
                quantite
            ) VALUES (
                %s,
                %s,
                %s,
                %s
            )
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


@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    print('client_commande_show')
    
    curseur = get_db().cursor()
    identifiant_client = session['id_user']
    
    # Récupération de toutes les commandes du client
    requete_sql = '''
        SELECT 
            commande.id_commande AS identifiant_commande,
            commande.date_achat AS date_achat,
            etat.libelle_etat AS libelle_etat,
            etat.id_etat AS identifiant_etat,
            COUNT(ligne_commande.commande_id) AS nombre_articles,
            SUM(ligne_commande.prix * ligne_commande.quantite) AS prix_total_commande
        FROM commande
        INNER JOIN etat ON commande.etat_id = etat.id_etat
        LEFT JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
        WHERE commande.utilisateur_id = %s
        GROUP BY commande.id_commande, commande.date_achat, etat.libelle_etat, etat.id_etat
        ORDER BY commande.date_achat DESC
        '''
    curseur.execute(requete_sql, (identifiant_client,))
    commandes = curseur.fetchall()

    articles_commande = None
    informations_adresses_commande = None
    identifiant_commande = request.args.get('id_commande', None)
    
    if identifiant_commande is not None:
        print(identifiant_commande)
        
        # Récupération des articles de la commande
        requete_sql = '''
            SELECT 
                skin.nom_skin AS nom_article,
                skin.image AS image_article,
                ligne_commande.quantite AS quantite_article,
                ligne_commande.prix AS prix_unitaire,
                (ligne_commande.prix * ligne_commande.quantite) AS prix_total_ligne,
                usure.libelle_usure AS libelle_usure,
                type_skin.libelle_type_skin AS libelle_type_skin,
                special.libelle_special AS libelle_special
            FROM ligne_commande
            INNER JOIN declinaison ON ligne_commande.declinaison_id = declinaison.id_declinaison
            INNER JOIN skin ON declinaison.skin_id = skin.id_skin
            INNER JOIN usure ON declinaison.usure_id = usure.id_usure
            INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            INNER JOIN special ON declinaison.special_id = special.id_special
            WHERE ligne_commande.commande_id = %s
        '''
        curseur.execute(requete_sql, (identifiant_commande,))
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

