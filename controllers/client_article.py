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

    sql = '''   selection des articles   '''
    list_param = []
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    articles = []

    sql = '''
        SELECT  id_skin AS id_article
                , nom_skin AS nom
                , prix_skin AS prix
                , stock AS stock
                , image
                , libelle_usure
                , libelle_type_skin
                , libelle_special
        FROM skin
        INNER JOIN usure ON skin.usure_id = usure.id_usure
        INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
        INNER JOIN special ON skin.special_id = special.id_special
        ORDER BY id_skin
        '''
    
    mycursor.execute(sql)
    articles = mycursor.fetchall()


    # pour les déclinaisons
    declinaisons = []
    for article in articles:
        declinaisons = get_declinaison(article['nom'])
        article['declinaisons'] = declinaisons



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


    articles_panier = []

    if len(articles_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           #, prix_total=prix_total
                           , items_filtre=types_article
                           )


def get_declinaison(nom):
    mycursor = get_db().cursor()

    sql = '''
        SELECT DISTINCT libelle_usure
        FROM skin
        INNER JOIN usure ON skin.usure_id = usure.id_usure
        WHERE nom_skin = %s
        '''
    mycursor.execute(sql, nom)
    declinaisons = mycursor.fetchall()

    return [declinaison['libelle_usure'] for declinaison in declinaisons]


