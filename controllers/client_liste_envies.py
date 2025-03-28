#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                        template_folder='templates')

@client_liste_envies.route('/client/envie/add', methods=['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    sql = '''SELECT * FROM liste_envie
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    article_in_wishlist = mycursor.fetchone()
    
    if not article_in_wishlist:
        sql = '''INSERT INTO liste_envie (id_utilisateur, id_skin, date_update) 
                 VALUES (%s, %s, NOW())'''
        mycursor.execute(sql, (id_client, id_skin))
        get_db().commit()
        flash(u'Article ajouté à votre liste d\'envies')
    else:
        flash(u'Article déjà dans votre liste d\'envies')
    
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envie/delete', methods=['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    sql = '''DELETE FROM liste_envie
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    get_db().commit()
    flash(u'Article retiré de votre liste d\'envies')
    
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envie/commander', methods=['post'])
def client_liste_envies_commander():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.form.get('id_article')
    quantite = request.form.get('quantite', 1)

    # Vérifier si l'article est déjà dans le panier
    sql = '''SELECT quantite FROM ligne_panier 
             WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    article_in_panier = mycursor.fetchone()

    if article_in_panier:
        sql = '''UPDATE ligne_panier 
                 SET quantite = quantite + %s, date_ajout = NOW()
                 WHERE utilisateur_id = %s AND skin_id = %s'''
        mycursor.execute(sql, (quantite, id_client, id_skin))
    else:
        sql = '''INSERT INTO ligne_panier (skin_id, utilisateur_id, quantite, date_ajout)
                 VALUES (%s, %s, %s, NOW())'''
        mycursor.execute(sql, (id_skin, id_client, quantite))
    
    sql = '''DELETE FROM liste_envie
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    get_db().commit()
    flash(u'Article ajouté au panier et retiré de la liste d\'envies')
    
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article_selected = request.args.get('id_article', None)
    
    # Compte le nombre d'articles dans la liste d'envies
    sql = '''SELECT COUNT(*) as nb_articles
             FROM liste_envie
             WHERE id_utilisateur = %s'''
    mycursor.execute(sql, (id_client,))
    nb_articles_envies = mycursor.fetchone()['nb_articles']
    
    # Récupération des articles de la liste d'envies
    sql = '''SELECT s.*, t.libelle_type_skin as type_skin, u.libelle_usure as usure, 
                    sp.libelle_special as special, s.nom_skin as nom, s.prix_skin as prix,
                    s.image as image, s.stock as stock, le.date_update
             FROM skin s
             INNER JOIN liste_envie le ON le.id_skin = s.id_skin
             INNER JOIN type_skin t ON t.id_type_skin = s.type_skin_id
             INNER JOIN usure u ON u.id_usure = s.usure_id
             INNER JOIN special sp ON sp.id_special = s.special_id
             WHERE le.id_utilisateur = %s
             ORDER BY le.date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()
    
    sql = '''SELECT s.*, t.libelle_type_skin as type_skin, u.libelle_usure as usure, 
                    sp.libelle_special as special, s.nom_skin as nom, s.prix_skin as prix,
                    s.image as image, s.stock as stock
             FROM skin s
             INNER JOIN historique h ON h.id_skin = s.id_skin
             INNER JOIN type_skin t ON t.id_type_skin = s.type_skin_id
             INNER JOIN usure u ON u.id_usure = s.usure_id
             INNER JOIN special sp ON sp.id_special = s.special_id
             WHERE h.id_utilisateur = %s
             ORDER BY h.date_consultation DESC
             LIMIT 3'''
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()
    
    # Si un article est sélectionné, calculer les statistiques supplémentaires
    nb_autres_clients = None
    nb_articles_meme_type = None
    
    if id_article_selected:
        # Nombre d'autres clients ayant cet article dans leur wishlist
        sql = '''SELECT COUNT(DISTINCT id_utilisateur) as nb_clients
                 FROM liste_envie
                 WHERE id_skin = %s AND id_utilisateur != %s'''
        mycursor.execute(sql, (id_article_selected, id_client))
        nb_autres_clients = mycursor.fetchone()['nb_clients']
        
        # Nombre d'articles du même type dans votre wishlist
        sql = '''SELECT COUNT(*) as nb_articles
                 FROM liste_envie le
                 INNER JOIN skin s1 ON le.id_skin = s1.id_skin
                 INNER JOIN skin s2 ON s2.id_skin = %s
                 WHERE le.id_utilisateur = %s 
                 AND le.id_skin != %s
                 AND s1.type_skin_id = s2.type_skin_id'''
        mycursor.execute(sql, (id_article_selected, id_client, id_article_selected))
        nb_articles_meme_type = mycursor.fetchone()['nb_articles']
    
    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_articles_envies=nb_articles_envies,
                           id_article_selected=id_article_selected,
                           nb_autres_clients=nb_autres_clients,
                           nb_articles_meme_type=nb_articles_meme_type)

def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    sql = '''INSERT INTO historique (id_utilisateur, id_skin, date_consultation)
             VALUES (%s, %s, NOW())'''
    mycursor.execute(sql, (client_id, article_id))
    get_db().commit()

@client_liste_envies.route('/client/envies/up', methods=['get'])
def client_liste_envies_up():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    # Trouver l'article actuel et celui au-dessus
    sql = '''SELECT id_skin, date_update
             FROM liste_envie
             WHERE id_utilisateur = %s
             ORDER BY date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles = mycursor.fetchall()
    
    # Trouver l'article à déplacer et échanger avec celui au-dessus
    for i in range(len(articles)-1):
        if str(articles[i+1]['id_skin']) == str(id_skin):
            # 1. D'abord, mettre l'article actuel à une date temporaire très ancienne
            sql = '''UPDATE liste_envie 
                     SET date_update = DATE_SUB(NOW(), INTERVAL 1 YEAR)
                     WHERE id_utilisateur = %s AND id_skin = %s'''
            mycursor.execute(sql, (id_client, articles[i+1]['id_skin']))
            
            # 2. Ensuite, mettre l'article du dessus à la date de l'article actuel
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE id_utilisateur = %s AND id_skin = %s'''
            mycursor.execute(sql, (articles[i+1]['date_update'], id_client, articles[i]['id_skin']))
            
            # 3. Enfin, mettre l'article actuel à la date de l'article du dessus
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE id_utilisateur = %s AND id_skin = %s'''
            mycursor.execute(sql, (articles[i]['date_update'], id_client, articles[i+1]['id_skin']))
            break
    
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/down', methods=['get'])
def client_liste_envies_down():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    # Trouver l'article actuel et celui en-dessous
    sql = '''SELECT id_skin, date_update
             FROM liste_envie
             WHERE id_utilisateur = %s
             ORDER BY date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles = mycursor.fetchall()
    
    for i in range(len(articles)-1):
        if str(articles[i]['id_skin']) == str(id_skin):
            # 1. D'abord, mettre l'article actuel à une date temporaire très ancienne
            sql = '''UPDATE liste_envie 
                     SET date_update = DATE_SUB(NOW(), INTERVAL 1 YEAR)
                     WHERE id_utilisateur = %s AND id_skin = %s'''
            mycursor.execute(sql, (id_client, articles[i]['id_skin']))
            
            # 2. Ensuite, mettre l'article du dessous à la date de l'article actuel
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE id_utilisateur = %s AND id_skin = %s'''
            mycursor.execute(sql, (articles[i]['date_update'], id_client, articles[i+1]['id_skin']))
            
            # 3. Enfin, mettre l'article actuel à la date de l'article du dessous
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE id_utilisateur = %s AND id_skin = %s'''
            mycursor.execute(sql, (articles[i+1]['date_update'], id_client, articles[i]['id_skin']))
            break
    
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_first():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    # 1. D'abord, mettre l'article sélectionné à une date temporaire très ancienne
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL 2 YEAR)
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 2. Mettre à jour tous les autres articles avec des dates uniques
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL id_skin SECOND)
             WHERE id_utilisateur = %s AND id_skin != %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 3. Finalement, mettre l'article sélectionné en premier
    sql = '''UPDATE liste_envie 
             SET date_update = NOW()
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/last', methods=['get'])
def client_liste_envies_last():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    # 1. D'abord, mettre l'article sélectionné à une date temporaire très future
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_ADD(NOW(), INTERVAL 2 YEAR)
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 2. Mettre à jour tous les autres articles avec des dates uniques
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL id_skin SECOND)
             WHERE id_utilisateur = %s AND id_skin != %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 3. Finalement, mettre l'article sélectionné en dernier
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL 1 HOUR)
             WHERE id_utilisateur = %s AND id_skin = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    get_db().commit()
    return redirect('/client/envies/show')
