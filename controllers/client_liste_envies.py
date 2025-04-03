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
             WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    article_in_wishlist = mycursor.fetchone()
    
    if not article_in_wishlist:
        sql = '''INSERT INTO liste_envie (utilisateur_id, skin_id, date_update) 
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
             WHERE utilisateur_id = %s AND skin_id = %s'''
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
        sql = '''INSERT INTO ligne_panier (declinaison_id, utilisateur_id, quantite, date_ajout)
                 VALUES (%s, %s, %s, NOW())'''
        mycursor.execute(sql, (id_skin, id_client, quantite))
    
    sql = '''DELETE FROM liste_envie
             WHERE utilisateur_id = %s AND skin_id = %s'''
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
             WHERE utilisateur_id = %s'''
    mycursor.execute(sql, (id_client,))
    nb_articles_envies = mycursor.fetchone()['nb_articles']
    
    # Récupération des articles de la liste d'envies
    sql = '''SELECT s.id_skin, s.nom_skin as nom, s.image,
                    t.libelle_type_skin as type_skin, 
                    MIN(d.prix_declinaison) as prix_min,
                    MAX(d.prix_declinaison) as prix_max,
                    SUM(d.stock) as stock_total,
                    le.date_update
             FROM skin s
             INNER JOIN liste_envie le ON le.skin_id = s.id_skin
             INNER JOIN type_skin t ON t.id_type_skin = s.type_skin_id
             INNER JOIN declinaison d ON d.skin_id = s.id_skin
             WHERE le.utilisateur_id = %s
             GROUP BY s.id_skin, s.nom_skin, s.image, t.libelle_type_skin, le.date_update
             ORDER BY le.date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()
    
    sql = '''SELECT s.id_skin, s.nom_skin as nom, s.image,
                    t.libelle_type_skin as type_skin,
                    MIN(d.prix_declinaison) as prix_min,
                    MAX(d.prix_declinaison) as prix_max,
                    SUM(d.stock) as stock_total,
                    MAX(h.date_consultation) as date_consultation
             FROM skin s
             INNER JOIN historique h ON h.skin_id = s.id_skin
             INNER JOIN type_skin t ON t.id_type_skin = s.type_skin_id
             INNER JOIN declinaison d ON d.skin_id = s.id_skin
             WHERE h.utilisateur_id = %s
             GROUP BY s.id_skin, s.nom_skin, s.image, t.libelle_type_skin
             ORDER BY MAX(h.date_consultation) DESC
             LIMIT 3'''
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()

    #TODO: Fix le fait que quand j'appuie sur la fleche pour allez tout en haut sa change aussi celui du millieu la premiére fois et aprés sa marche bizzarement
    
    # Si un article est sélectionné, calculer les statistiques supplémentaires
    nb_autres_clients = None
    nb_articles_meme_type = None
    
    if id_article_selected:
        # Nombre d'autres clients ayant cet article dans leur wishlist
        sql = '''SELECT COUNT(DISTINCT utilisateur_id) as nb_clients
                 FROM liste_envie
                 WHERE skin_id = %s AND utilisateur_id != %s'''
        mycursor.execute(sql, (id_article_selected, id_client))
        nb_autres_clients = mycursor.fetchone()['nb_clients']
        
        # Nombre d'articles du même type dans votre wishlist
        sql = '''SELECT COUNT(*) as nb_articles
                 FROM liste_envie le
                 INNER JOIN skin s1 ON le.skin_id = s1.id_skin
                 INNER JOIN skin s2 ON s2.id_skin = %s
                 WHERE le.utilisateur_id = %s 
                 AND le.skin_id != %s
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
    sql = '''INSERT INTO historique (utilisateur_id, id_skin, date_consultation)
             VALUES (%s, %s, NOW())'''
    mycursor.execute(sql, (client_id, article_id))
    get_db().commit()

@client_liste_envies.route('/client/envies/up', methods=['get'])
def client_liste_envies_up():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    # Trouver l'article actuel et celui au-dessus
    sql = '''SELECT skin_id, date_update
             FROM liste_envie
             WHERE utilisateur_id = %s
             ORDER BY date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles = mycursor.fetchall()
    
    # Trouver l'article à déplacer et échanger avec celui au-dessus
    for i in range(len(articles)-1):
        if str(articles[i+1]['skin_id']) == str(id_skin):
            # 1. D'abord, mettre l'article actuel à une date temporaire très ancienne
            sql = '''UPDATE liste_envie 
                     SET date_update = DATE_SUB(NOW(), INTERVAL 1 YEAR)
                     WHERE utilisateur_id = %s AND skin_id = %s'''
            mycursor.execute(sql, (id_client, articles[i+1]['skin_id']))
            
            # 2. Ensuite, mettre l'article du dessus à la date de l'article actuel
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE utilisateur_id = %s AND skin_id = %s'''
            mycursor.execute(sql, (articles[i+1]['date_update'], id_client, articles[i]['skin_id']))
            
            # 3. Enfin, mettre l'article actuel à la date de l'article du dessus
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE utilisateur_id = %s AND skin_id = %s'''
            mycursor.execute(sql, (articles[i]['date_update'], id_client, articles[i+1]['skin_id']))
            break
    
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/down', methods=['get'])
def client_liste_envies_down():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    # Trouver l'article actuel et celui en-dessous
    sql = '''SELECT skin_id, date_update
             FROM liste_envie
             WHERE utilisateur_id = %s
             ORDER BY date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles = mycursor.fetchall()
    
    for i in range(len(articles)-1):
        if str(articles[i]['skin_id']) == str(id_skin):
            # 1. D'abord, mettre l'article actuel à une date temporaire très ancienne
            sql = '''UPDATE liste_envie 
                     SET date_update = DATE_SUB(NOW(), INTERVAL 1 YEAR)
                     WHERE utilisateur_id = %s AND skin_id = %s'''
            mycursor.execute(sql, (id_client, articles[i]['skin_id']))
            
            # 2. Ensuite, mettre l'article du dessous à la date de l'article actuel
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE utilisateur_id = %s AND skin_id = %s'''
            mycursor.execute(sql, (articles[i]['date_update'], id_client, articles[i+1]['skin_id']))
            
            # 3. Enfin, mettre l'article actuel à la date de l'article du dessous
            sql = '''UPDATE liste_envie 
                     SET date_update = %s 
                     WHERE utilisateur_id = %s AND skin_id = %s'''
            mycursor.execute(sql, (articles[i+1]['date_update'], id_client, articles[i]['skin_id']))
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
             WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 2. Mettre à jour tous les autres articles avec des dates uniques
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL skin_id SECOND)
             WHERE utilisateur_id = %s AND skin_id != %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 3. Finalement, mettre l'article sélectionné en premier
    sql = '''UPDATE liste_envie 
             SET date_update = NOW()
             WHERE utilisateur_id = %s AND skin_id = %s'''
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
             WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 2. Mettre à jour tous les autres articles avec des dates uniques
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL skin_id SECOND)
             WHERE utilisateur_id = %s AND skin_id != %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    # 3. Finalement, mettre l'article sélectionné en dernier
    sql = '''UPDATE liste_envie 
             SET date_update = DATE_SUB(NOW(), INTERVAL 1 HOUR)
             WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql, (id_client, id_skin))
    
    get_db().commit()
    return redirect('/client/envies/show')
