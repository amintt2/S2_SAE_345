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

    # Sélection des articles avec leurs informations
    sql = '''
    SELECT a.idArticle, a.designation, a.photo, a.prix
    FROM ARTICLE a
    ORDER BY a.designation
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    # Récupération des articles dans le panier de l'utilisateur (si nécessaire)
    articles_panier = []
    prix_total = 0

    return render_template('client/boutique/panier_article.html',
                           articles=articles,
                           articles_panier=articles_panier,
                           prix_total=prix_total
                           )
