#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')              # remplace /client
def client_article_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']
    list_param = []

########################## Livrable 3 ##########################
#    sql = '''
#        SELECT DISTINCT nom_skin AS nom
#                , MIN(id_skin) AS id_article
#                , MIN(prix_skin) AS prix_min
#                , MAX(prix_skin) AS prix_max
#                , MIN(stock) AS stock_min
#                , MAX(stock) AS stock_max
#                , MIN(image) AS image
#                , MIN(libelle_usure) AS libelle_usure
#                , MIN(libelle_type_skin) AS libelle_type_article
#                , MIN(libelle_special) AS libelle_special
#        FROM skin
#        INNER JOIN usure ON skin.usure_id = usure.id_usure
#        INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
#        INNER JOIN special ON skin.special_id = special.id_special
#        WHERE stock > 0
#        '''
#    if 'filter_types' in session and session['filter_types']:
#        placeholders = ','.join(['%s'] * len(session['filter_types']))
#        sql += f' AND type_skin.id_type_skin IN ({placeholders})'
#        list_param.extend(session['filter_types'])
#
#    sql += ' GROUP BY nom_skin ORDER BY id_article'
#
#
#    # pour les déclinaisons
#    declinaisons = []
#    for article in articles:
#        declinaisons = get_declinaison(article['nom'])
#        article['declinaisons'] = declinaisons
################################################################

    sql = '''
        SELECT id_skin AS id_article
                , nom_skin AS nom
                , prix_skin AS prix
                , stock 
                , image
                , libelle_usure AS libelle_usure
                , libelle_type_skin AS libelle_type_article
                , libelle_special AS libelle_special
        FROM skin
        INNER JOIN usure ON skin.usure_id = usure.id_usure
        INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
        INNER JOIN special ON skin.special_id = special.id_special
        WHERE 1=1
        '''
    
    if 'filter_types' in session and session['filter_types']:
        placeholders = ','.join(['%s'] * len(session['filter_types']))
        sql += f' AND type_skin.id_type_skin IN ({placeholders})'
        list_param.extend(session['filter_types'])

    if 'filter_word' in session and session['filter_word']:
        sql += ' AND nom_skin LIKE %s'

        list_param.append(f"%{session['filter_word']}%")
    if 'filter_prix_min' in session and session['filter_prix_min']:
        sql += ' AND prix_skin >= %s'
        list_param.append(session['filter_prix_min'])

    if 'filter_prix_max' in session and session['filter_prix_max']:
        sql += ' AND prix_skin <= %s'
        list_param.append(session['filter_prix_max'])
    
    mycursor.execute(sql, tuple(list_param) if list_param else None)
    articles = mycursor.fetchall()


    # pour le filtre
    types_article = []
    sql = '''
        SELECT  id_type_skin AS id_type_article
                , libelle_type_skin AS libelle
        FROM type_skin
        ORDER BY libelle_type_skin
        '''
    mycursor.execute(sql)
    types_skin = mycursor.fetchall()
    types_article = types_skin
    
    
    sql = '''
        SELECT skin.nom_skin AS designation,
            skin.id_skin AS id_article,
            type_skin.libelle_type_skin,
            usure.libelle_usure,
            special.libelle_special,
            (skin.prix_skin * ligne_panier.quantite) AS prix,
            ligne_panier.quantite
        FROM ligne_panier
        JOIN skin ON ligne_panier.skin_id = skin.id_skin
        JOIN usure ON skin.usure_id = usure.id_usure
        JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
        JOIN special ON skin.special_id = special.id_special
        WHERE ligne_panier.utilisateur_id = %s;
    '''
    #        , 10 as prix , concat('nomarticle',stylo_id) as nom 
    mycursor.execute(sql, (id_client))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql = ''' 
            SELECT SUM(ligne_panier.quantite * skin.prix_skin) AS prix_total
            FROM ligne_panier
            JOIN skin ON ligne_panier.skin_id = skin.id_skin
            WHERE ligne_panier.utilisateur_id = %s;
         '''
        mycursor.execute(sql, (id_client))
        prix_total = mycursor.fetchone()['prix_total']
    else:
        prix_total = None
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )


def get_declinaison(nom):
    mycursor = get_db().cursor()

    sql = '''
        SELECT DISTINCT libelle_usure
        FROM skin
        INNER JOIN usure ON skin.usure_id = usure.id_usure
        WHERE nom_skin = %s AND stock > 0
        '''
    mycursor.execute(sql, nom)
    declinaisons = mycursor.fetchall()

    return [declinaison['libelle_usure'] for declinaison in declinaisons]


