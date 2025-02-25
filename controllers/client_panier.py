#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session, url_for
 
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


def update_stock(quantite, id_article):
    mycursor = get_db().cursor()    
    sql = '''
        SELECT stock 
        FROM skin
        WHERE id_skin = %s
    '''
    mycursor.execute(sql, (id_article))
    quantite_article = mycursor.fetchone()['stock']
    if quantite > quantite_article:
        print("Quantité trop élevé")
        quantite = quantite_article

    sql = '''
        UPDATE skin
        SET stock = stock - %s
        WHERE id_skin = %s
    '''
    mycursor.execute(sql, (quantite, id_article))

    # renvoie la quantité qui peut être réellement ajouter au panier
    return quantite

@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    print("Form data:")
    print("id_client:", session['id_user'])
    print("id_article:", request.form.get('id_article'))
    print("quantite:", request.form.get('quantite'))
    print("id_declinaison_article:", request.form.get('id_declinaison_article', None))
    
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = int(request.form.get('quantite', 1))

    # ---------
    id_declinaison_article=request.form.get('id_declinaison_article',None)
    
# ajout dans le panier d'une déclinaison d'un article (si 1 declinaison : immédiat sinon => vu pour faire un choix
    if id_declinaison_article is None:
        sql = '''
            SELECT id_skin AS id_declinaison_article
            FROM skin
            WHERE nom_skin = (
                SELECT nom_skin
                FROM skin
                WHERE id_skin = %s
            );
        '''
        mycursor.execute(sql, (id_article))
        declinaisons = mycursor.fetchall()
        print("Decli: ", declinaisons)

        if len(declinaisons) == 1:
            id_declinaison_article = declinaisons[0]['id_declinaison_article']
        elif len(declinaisons) == 0:
            abort("pb nb de declinaison")
        else:
            sql = '''
                SELECT  nom_skin AS nom,
                        prix_skin AS prix,
                        image
                FROM skin
                WHERE id_skin = %s;
            '''
            mycursor.execute(sql, (id_article))
            article = mycursor.fetchone()
            return render_template('client/boutique/declinaison_article.html'
                                    , declinaisons=declinaisons
                                    , quantite=quantite
                                    , article=article)

# mise à jour des quantités
    quantite = update_stock(quantite, id_article)

# ajout dans le panier d'un article

    sql = '''
        SELECT *  FROM ligne_panier 
        WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    article_panier = mycursor.fetchone()
    print("article_panier: ", article_panier)

    if article_panier is not None:
        sql = '''
            UPDATE ligne_panier
            SET quantite = quantite + %s
            WHERE skin_id = %s AND utilisateur_id = %s;
        '''
        mycursor.execute(sql, (quantite, id_article, id_client))
    else:
        sql = '''
            INSERT INTO ligne_panier (utilisateur_id, skin_id, quantite, date_ajout)
            VALUES (%s, %s, %s, NOW());
        '''
        mycursor.execute(sql, (id_client, id_declinaison_article, quantite))
    get_db().commit()


    return redirect('/client/article/show')


@client_panier.route('/client/panier/update', methods=['POST'])
def client_panier_update():
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = int(request.form.get('quantite', 1))
    print('Change quantity to', quantite)
    
    mycursor = get_db().cursor()

    sql = '''
        SELECT quantite
        FROM ligne_panier
        WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    quantite_panier = mycursor.fetchone()['quantite']
    quantite = quantite - quantite_panier
    print('Update quantity with', quantite, 'articles')

    if quantite > 0:
        quantite = update_stock(quantite, id_article)
        print('Will add', quantite, 'articles')
        sql = '''
            UPDATE ligne_panier
            SET quantite = quantite + %s
            WHERE skin_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql, (quantite, id_article, id_client))
    elif quantite < 0:
        _delete_article_from_panier(-quantite, id_article)


    get_db().commit()
    return redirect('/client/article/show') 
    

def _delete_article_from_panier(quantite, id_article):
    id_client = session['id_user']
    
    mycursor = get_db().cursor()

    sql = ''' 
        SELECT quantite
        FROM ligne_panier
        WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    article_panier=mycursor.fetchone()

    if article_panier['quantite'] < quantite:
        quantite = article_panier['quantite']

    sql = '''
        UPDATE skin
        SET stock = stock + %s
        WHERE id_skin = %s
    '''
    mycursor.execute(sql, (quantite, id_article))

    if not(article_panier is None) and article_panier['quantite'] > quantite:
        sql = '''
            UPDATE ligne_panier
            SET quantite = quantite - %s
            WHERE skin_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql, (quantite, id_article, id_client))
    else:
        sql = '''
            DELETE FROM ligne_panier 
            WHERE skin_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql, (id_article, id_client))

    # mise à jour du stock de l'article disponible
    get_db().commit()

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article','')
    quantite = int(request.form.get('quantite', 1))

    # ---------
    # partie 2 : on supprime une déclinaison de l'article
    # id_declinaison_article = request.form.get('id_declinaison_article', None)


    _delete_article_from_panier(quantite, id_article)
 
    return redirect('/client/article/show')


def _client_panier_delete_line(id_article, quantite):
    id_client = session['id_user']
    mycursor = get_db().cursor()
    sql = ''' 
        DELETE FROM ligne_panier
        WHERE utilisateur_id = %s AND skin_id = %s 
    '''
    mycursor.execute(sql, (id_client, id_article))

    sql = ''' 
        UPDATE skin
        SET stock = stock + %s
        WHERE id_skin = %s
    '''
    mycursor.execute(sql, (quantite, id_article))

    get_db().commit()


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    sql = ''' 
        SELECT skin_id, quantite
        FROM ligne_panier
        WHERE utilisateur_id = %s
    '''
    mycursor.execute(sql, (client_id))
    items_panier = mycursor.fetchall()
    for item in items_panier:
        _client_panier_delete_line(item['skin_id'], item['quantite'])
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    #id_declinaison_article = request.form.get('id_declinaison_article')

    sql = ''' 
        SELECT quantite 
        FROM ligne_panier
        WHERE utilisateur_id = %s AND skin_id = %s  
    '''
    mycursor.execute(sql, (id_client, id_article))
    quantite = mycursor.fetchone()["quantite"]

    _client_panier_delete_line(id_article, quantite)

    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types')

    if filter_word:
        session['filter_word'] = filter_word
    elif 'filter_word' in session:
        session.pop('filter_word')

    if filter_prix_min:
        session['filter_prix_min'] = filter_prix_min
    elif 'filter_prix_min' in session:
        session.pop('filter_prix_min')

    if filter_prix_max:
        session['filter_prix_max'] = filter_prix_max
    elif 'filter_prix_max' in session:
        session.pop('filter_prix_max')

    if filter_types:
        session['filter_types'] = filter_types
    elif 'filter_types' in session:
        session.pop('filter_types')

    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_delete():
    # suppression des variables en session
    if 'filter_word' in session:
        session.pop('filter_word')
    if 'filter_prix_min' in session:
        session.pop('filter_prix_min')
    if 'filter_prix_max' in session:
        session.pop('filter_prix_max')
    if 'filter_types' in session:
        session.pop('filter_types')
    return redirect('/client/article/show')
