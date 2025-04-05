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
    id_skin = request.form.get('id_article') # This is the base skin ID
    quantite_a_ajouter = 1 

    # 1. Find the first available declination_id for the given skin_id
    sql_find_decl = '''SELECT id_declinaison 
                       FROM declinaison 
                       WHERE skin_id = %s AND stock > 0 
                       ORDER BY id_declinaison ASC 
                       LIMIT 1'''
    mycursor.execute(sql_find_decl, (id_skin,))
    available_decl = mycursor.fetchone()

    if not available_decl:
        flash(u'Désolé, cet article (ou ses déclinaisons) est actuellement en rupture de stock.', 'alert-warning')
        return redirect('/client/envies/show')
    
    id_declinaison_a_ajouter = available_decl['id_declinaison']

    # 2. Check if this specific declination is already in the user's cart
    sql_check_panier = '''SELECT quantite FROM ligne_panier 
                          WHERE utilisateur_id = %s AND declinaison_id = %s'''
    mycursor.execute(sql_check_panier, (id_client, id_declinaison_a_ajouter))
    article_in_panier = mycursor.fetchone()

    if article_in_panier:
        # 3a. Update quantity if already in cart
        sql_update_panier = '''UPDATE ligne_panier 
                             SET quantite = quantite + %s, date_ajout = NOW()
                             WHERE utilisateur_id = %s AND declinaison_id = %s'''
        mycursor.execute(sql_update_panier, (quantite_a_ajouter, id_client, id_declinaison_a_ajouter))
    else:
        # 3b. Insert new line if not in cart
        sql_insert_panier = '''INSERT INTO ligne_panier (declinaison_id, utilisateur_id, quantite, date_ajout)
                             VALUES (%s, %s, %s, NOW())'''
        mycursor.execute(sql_insert_panier, (id_declinaison_a_ajouter, id_client, quantite_a_ajouter))
    
    # 4. Remove the base skin from the wishlist (assuming this is desired behavior)
    sql_delete_envie = '''DELETE FROM liste_envie
                          WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql_delete_envie, (id_client, id_skin))
    
    get_db().commit()
    flash(u'Article ajouté au panier (première déclinaison disponible) et retiré de la liste d\'envies.', 'alert-success')
    
    # Redirect to cart page to show the added item might be better UX
    # return redirect(url_for('client_panier.client_panier_show')) 
    return redirect('/client/article/show') # Or back to main article list

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
                    -- Ajout des colonnes pour les infos spécifiques de la déclinaison si nécessaire
                    -- d.id_declinaison, u.libelle_usure as usure, sp.libelle_special as special,
                    MAX(h.date_consultation) as last_consultation_date
             FROM historique h
             JOIN skin s ON h.skin_id = s.id_skin
             JOIN type_skin t ON s.type_skin_id = t.id_type_skin
             LEFT JOIN declinaison d ON s.id_skin = d.skin_id -- LEFT JOIN au cas où un skin n'a pas de déclinaison
             -- LEFT JOIN usure u ON d.usure_id = u.id_usure
             -- LEFT JOIN special sp ON d.special_id = sp.id_special
             WHERE h.utilisateur_id = %s
             GROUP BY s.id_skin, s.nom_skin, s.image, t.libelle_type_skin
             ORDER BY last_consultation_date DESC
             LIMIT 6''' # Limiter à 6 articles distincts maximum
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

def client_historique_add(skin_id, client_id):
    mycursor = get_db().cursor()
    
    # 1. Supprimer les entrées de plus d'un mois pour cet utilisateur
    sql_delete_old = '''DELETE FROM historique
                      WHERE utilisateur_id = %s AND date_consultation < DATE_SUB(NOW(), INTERVAL 1 MONTH)'''
    mycursor.execute(sql_delete_old, (client_id,))

    # 2. Vérifier si l'article est déjà dans l'historique récent
    sql_check_exists = '''SELECT COUNT(*) as count FROM historique
                          WHERE utilisateur_id = %s AND skin_id = %s'''
    mycursor.execute(sql_check_exists, (client_id, skin_id))
    exists = mycursor.fetchone()['count'] > 0
    
    if exists:
        # 3a. Si oui, mettre à jour la date de consultation
        sql_update_date = '''UPDATE historique SET date_consultation = NOW()
                           WHERE utilisateur_id = %s AND skin_id = %s'''
        mycursor.execute(sql_update_date, (client_id, skin_id))
    else:
        # 3b. Si non, vérifier le nombre d'articles distincts dans l'historique
        sql_count = '''SELECT COUNT(*) as count FROM historique WHERE utilisateur_id = %s'''
        mycursor.execute(sql_count, (client_id,))
        count = mycursor.fetchone()['count']
        
        if count >= 6:
            # 4. Si l'historique est plein (6 articles), supprimer le plus ancien
            sql_delete = '''DELETE FROM historique 
                          WHERE utilisateur_id = %s 
                          ORDER BY date_consultation ASC 
                          LIMIT 1'''
            mycursor.execute(sql_delete, (client_id,))

        # 5. Insérer la nouvelle entrée
        sql_insert_new = '''INSERT INTO historique (utilisateur_id, skin_id, date_consultation)
                        VALUES (%s, %s, NOW())'''
        mycursor.execute(sql_insert_new, (client_id, skin_id))
        
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
    
    sql = '''SELECT skin_id, date_update 
             FROM liste_envie 
             WHERE utilisateur_id = %s 
             ORDER BY date_update DESC 
             LIMIT 1'''
    mycursor.execute(sql, (id_client,))
    current_first = mycursor.fetchone()
    
    if current_first and current_first['skin_id'] != id_skin:
        sql = '''UPDATE liste_envie 
                 SET date_update = CASE 
                     WHEN skin_id = %s THEN %s
                     WHEN skin_id = %s THEN %s
                 END
                 WHERE utilisateur_id = %s AND skin_id IN (%s, %s)'''
        mycursor.execute(sql, (id_skin, current_first['date_update'], current_first['skin_id'], 'NOW()', id_client, id_skin, current_first['skin_id']))
    
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/last', methods=['get'])
def client_liste_envies_last():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_skin = request.args.get('id_article')
    
    sql = '''SELECT skin_id, date_update 
             FROM liste_envie 
             WHERE utilisateur_id = %s 
             ORDER BY date_update ASC 
             LIMIT 1'''
    mycursor.execute(sql, (id_client,))
    current_last = mycursor.fetchone()
    
    if current_last and current_last['skin_id'] != id_skin:
        sql = '''UPDATE liste_envie 
                 SET date_update = CASE 
                     WHEN skin_id = %s THEN %s
                     WHEN skin_id = %s THEN %s
                 END
                 WHERE utilisateur_id = %s AND skin_id IN (%s, %s)'''
        mycursor.execute(sql, (id_skin, current_last['date_update'], current_last['skin_id'], 'NOW()', id_client, id_skin, current_last['skin_id']))
    
    get_db().commit()
    return redirect('/client/envies/show')
