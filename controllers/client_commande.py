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
    mycursor = get_db().cursor()
    id_client = session['id_user']
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
    mycursor = get_db().cursor()
    id_client = session['id_user']
    
    # Récupération des articles du panier
    sql = ''' 
        SELECT  lp.declinaison_id,
                lp.quantite,
                d.prix_declinaison * lp.quantite as prix
        FROM ligne_panier lp
        JOIN declinaison d ON lp.declinaison_id = d.id_declinaison
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()
    
    if not items_ligne_panier:
        flash(u'Pas d\'articles dans le panier', 'alert-warning')
        return redirect('/client/article/show')

    # Création de la commande
    sql = '''
        INSERT INTO commande(
            date_achat,
            etat_id,
            utilisateur_id
        ) VALUES (
            NOW(),
            1,
            %s
        )
    '''
    mycursor.execute(sql, (id_client,))
    
    # Récupération de l'id de la commande créée
    sql = '''SELECT LAST_INSERT_ID() as last_insert_id'''
    mycursor.execute(sql)
    id_commande = mycursor.fetchone()['last_insert_id']

    # Traitement des lignes du panier
    for item in items_ligne_panier:
        # Ajout ligne de commande
        sql = '''
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
        mycursor.execute(sql, (
            item['declinaison_id'],
            id_commande,
            item['prix'],
            item['quantite']
        ))

        # Suppression ligne panier
        sql = '''
            DELETE FROM ligne_panier 
            WHERE declinaison_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql, (item['declinaison_id'], id_client))

    get_db().commit()
    flash(u'Commande validée avec succès', 'alert-success')
    
    return redirect('/client/article/show')


@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    print('client_commande_show')
    
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''
        SELECT 
            commande.id_commande,
            commande.date_achat,
            etat.libelle_etat as libelle,
            etat.id_etat as etat_id,
            COUNT(ligne_commande.commande_id) as nbr_articles,
            SUM(ligne_commande.prix * ligne_commande.quantite) as prix_total
        FROM commande
        INNER JOIN etat ON commande.etat_id = etat.id_etat
        LEFT JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
        WHERE commande.utilisateur_id = %s
        GROUP BY commande.id_commande, commande.date_achat, etat.libelle_etat, etat.id_etat
        ORDER BY commande.date_achat DESC
        '''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        print(id_commande)
        sql = '''
            SELECT 
                skin.nom_skin AS nom,
                skin.image,
                ligne_commande.quantite,
                ligne_commande.prix,
                (ligne_commande.prix * ligne_commande.quantite) AS prix_ligne,
                usure.libelle_usure,
                type_skin.libelle_type_skin,
                special.libelle_special
            FROM ligne_commande
            INNER JOIN declinaison d ON ligne_commande.declinaison_id = d.id_declinaison
            INNER JOIN skin ON d.skin_id = skin.id_skin
            INNER JOIN usure ON d.usure_id = usure.id_usure
            INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            INNER JOIN special ON d.special_id = special.id_special
            WHERE ligne_commande.commande_id = %s
        '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()
        
    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )

