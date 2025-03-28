#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session
 
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
    mycursor.execute(sql, (id_article,)) 
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
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    if not id_article:
        flash(u'Article non trouvé', 'alert-warning')
        return redirect('/client/article/show')

    # Vérifier si l'article a plusieurs déclinaisons
    sql = '''
        SELECT COUNT(DISTINCT usure.id_usure) as nb_declinaisons
        FROM skin 
        INNER JOIN usure ON skin.usure_id = usure.id_usure
        WHERE nom_skin = (SELECT nom_skin FROM skin WHERE id_skin = %s)
        AND stock > 0
    '''
    mycursor.execute(sql, (id_article,))
    result = mycursor.fetchone()
    
    if result['nb_declinaisons'] > 1:
        # Si plusieurs déclinaisons, afficher la page de choix de déclinaison
        sql = '''
            SELECT s.id_skin, s.nom_skin, s.prix_skin, s.stock, s.image,
                   u.libelle_usure, u.id_usure
            FROM skin s
            INNER JOIN usure u ON s.usure_id = u.id_usure
            WHERE s.nom_skin = (SELECT nom_skin FROM skin WHERE id_skin = %s)
            AND s.stock > 0
        '''
        mycursor.execute(sql, (id_article,))
        declinaisons = mycursor.fetchall()
        
        # Avoir l'image de l'article
        sql = '''
            SELECT image, nom_skin as nom
            FROM skin 
            WHERE id_skin = %s
        '''
        mycursor.execute(sql, (id_article,))
        article = mycursor.fetchone()
        
        return render_template('client/boutique/declinaison_article.html',
                             declinaisons=declinaisons,
                             nom_article=declinaisons[0]['nom_skin'],
                             article=article)

    # Si un seul article, ajouter directement au panier
    print("Form data:")
    print("id_client:", session['id_user'])
    print("id_article:", request.form.get('id_article'))
    print("quantite:", request.form.get('quantite'))
    print("id_declinaison_article:", request.form.get('id_declinaison_article', None))
    
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    if not id_article:
        flash(u'Article non trouvé', 'alert-warning')
        return redirect('/client/article/show')

    # Vérifie si l'article est en stock / existe
    sql = '''
        SELECT id_skin, stock 
        FROM skin 
        WHERE id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    
    if not article:
        flash(u'Article non trouvé', 'alert-warning')
        return redirect('/client/article/show')
    
    if article['stock'] <= 0:
        flash(u'Article en rupture de stock', 'alert-warning')
        return redirect('/client/article/show')

    # Vérifie si l'article est déjà dans le panier
    sql = '''
        SELECT quantite 
        FROM ligne_panier 
        WHERE utilisateur_id = %s AND skin_id = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    ligne_panier = mycursor.fetchone()

    if ligne_panier:
        # Met à jour la quantité si déjà dans le panier
        sql = '''
            UPDATE ligne_panier 
            SET quantite = quantite + 1 
            WHERE utilisateur_id = %s AND skin_id = %s
        '''
        mycursor.execute(sql, (id_client, id_article))
        
    else:
        # Ajouter une nouvelle ligne au panier
        sql = '''
            INSERT INTO ligne_panier(utilisateur_id, skin_id, quantite) 
            VALUES (%s, %s, 1)
        '''
        mycursor.execute(sql, (id_client, id_article))
        update_stock(1, id_article)

    get_db().commit()
    flash(u'Article ajouté au panier', 'alert-success')
    return redirect('/client/article/show')


@client_panier.route('/client/panier/add_declinaison', methods=['POST'])
def client_panier_add_declinaison():
    id_article = request.form.get('id_article')
    if not id_article:
        flash(u'Article non trouvé', 'alert-warning')
        return redirect('/client/article/show')
        
    id_client = session['id_user']
    mycursor = get_db().cursor()

    # Vérifier le stock
    sql = '''
        SELECT stock 
        FROM skin 
        WHERE id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    
    if not article or article['stock'] <= 0:
        flash(u'Article non disponible', 'alert-warning')
        return redirect('/client/article/show')

    # Ajouter au panier
    sql = '''
        SELECT quantite 
        FROM ligne_panier 
        WHERE utilisateur_id = %s AND skin_id = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    ligne_panier = mycursor.fetchone()

    if ligne_panier:
        # Met à jour la quantité si déjà dans le panier
        sql = '''
            UPDATE ligne_panier 
            SET quantite = quantite + 1 
            WHERE utilisateur_id = %s AND skin_id = %s
        '''
        mycursor.execute(sql, (id_client, id_article))
        # Met à jour le stock
        update_stock(1, id_article)
    else:
        # Ajouter une nouvelle ligne au panier
        sql = '''
            INSERT INTO ligne_panier(utilisateur_id, skin_id, quantite) 
            VALUES (%s, %s, 1)
        '''
        mycursor.execute(sql, (id_client, id_article))
        update_stock(1, id_article)

    get_db().commit()
    flash(u'Article ajouté au panier', 'alert-success')
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
    id_declinaison_article = request.form.get('id_declinaison_article', None)


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
    id_declinaison_article = request.form.get('id_declinaison_article')

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

