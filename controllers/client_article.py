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

    # V1 - Adjusted for ONLY_FULL_GROUP_BY
    sql = '''
        SELECT 
                MIN(skin.id_skin) AS id_skin, # Aggregate id_skin
                skin.nom_skin AS nom, 
                skin.image,
                type_skin.libelle_type_skin AS libelle_type_article
                , ROUND(AVG(note.note),1) AS moyenne_notes
                , COUNT(note.note) AS nb_notes
                , COUNT(commentaire.commentaire) AS nb_commentaires
        FROM skin
        LEFT JOIN note ON skin.id_skin = note.skin_id
        LEFT JOIN commentaire ON skin.id_skin = commentaire.skin_id
        INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
        WHERE 1=1
    '''
    # Version avant modification des declinaisons
    # sql = '''
    #     SELECT DISTINCT nom_skin AS nom
    #             , MIN(id_skin) AS id_article
    #             , MIN(prix_skin) AS prix_min
    #             , MAX(prix_skin) AS prix_max
    #             , MIN(image) AS image
    #             , MIN(libelle_type_skin) AS libelle_type_article
    #     FROM skin
    #     INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
    #     WHERE 1=1
    #     '''

    if 'filter_types' in session and session['filter_types']:
        placeholders = ','.join(['%s'] * len(session['filter_types']))
        sql += f' AND ts.id_type_skin IN ({placeholders})'
        list_param.extend(session['filter_types'])

    if 'filter_word' in session and session['filter_word']:
        sql += ' AND nom_skin LIKE %s'
        list_param.append(f"%{session['filter_word']}%")

    if 'filter_prix_min' in session and session['filter_prix_min'] and 'filter_prix_max' in session and session['filter_prix_max']:
        if not session['filter_prix_min'].isdigit() or not session['filter_prix_max'].isdigit():
            message = u'Les valeurs du prix doivent être numériques'
            flash(message, 'alert-warning')
        else:
            min_val = int(session['filter_prix_min'])
            max_val = int(session['filter_prix_max'])
            if min_val > max_val:
                message = u'Le prix minimum doit être inférieur au prix maximum'
                flash(message, 'alert-warning')
            else:
                sql += ' AND prix_skin BETWEEN %s AND %s'
                list_param.extend([min_val, max_val])

    elif 'filter_prix_min' in session and session['filter_prix_min']:
        if not session['filter_prix_min'].isdigit():
            message = u'Les valeurs du prix doivent être numériques'
            flash(message, 'alert-warning')
        else:
            sql += ' AND prix_skin >= %s'
            list_param.append(int(session['filter_prix_min']))

    elif 'filter_prix_max' in session and session['filter_prix_max']:
        if not session['filter_prix_max'].isdigit():
            message = u'Les valeurs du prix doivent être numériques'
            flash(message, 'alert-warning')
        else:
            sql += ' AND prix_skin <= %s'
            list_param.append(int(session['filter_prix_max']))
            
    # Group by all non-aggregated columns
    sql += ' GROUP BY skin.nom_skin, skin.image, type_skin.libelle_type_skin' 
    
    # Fetch articles from base query
    mycursor.execute(sql, tuple(list_param) if list_param else None)
    articles = mycursor.fetchall()

    # Fetch declinations for each article
    articles_with_declinaisons = []
    if articles:
        for article in articles:
            declinaisons = get_declinaison(article['nom']) # Use base skin name
            # Only include articles that have available declinations
            if declinaisons: 
                article['declinaisons'] = declinaisons
                # Add price info for display (optional, could be done in template)
                article['prix_min'] = min(d['prix_declinaison'] for d in declinaisons) if declinaisons else 0
                article['prix_max'] = max(d['prix_declinaison'] for d in declinaisons) if declinaisons else 0
                articles_with_declinaisons.append(article)
    
    articles = articles_with_declinaisons # Replace original list

    # pour le filtre (type_skin should be correct)
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
    
    
    # Refactored articles_panier query
    sql = '''
        SELECT 
            ligne_panier.quantite,
            declinaison.id_declinaison,
            declinaison.prix_declinaison AS prix_unitaire,
            (declinaison.prix_declinaison * ligne_panier.quantite) AS prix_total_ligne,
            skin.nom_skin AS designation,
            skin.image, 
            type_skin.libelle_type_skin,
            usure.libelle_usure,
            special.libelle_special
        FROM ligne_panier
        JOIN declinaison ON ligne_panier.declinaison_id = declinaison.id_declinaison
        JOIN skin ON declinaison.skin_id = skin.id_skin
        JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
        JOIN usure ON declinaison.usure_id = usure.id_usure
        JOIN special ON declinaison.special_id = special.id_special
        WHERE ligne_panier.utilisateur_id = %s;
    '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    # Calculate overall total price for the cart
    if articles_panier:
        prix_total = sum(item['prix_total_ligne'] for item in articles_panier)
    else:
        prix_total = 0
    
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )


def get_declinaison(nom_skin_base):
    mycursor = get_db().cursor()

    sql = '''
        SELECT 
            declinaison.id_declinaison, 
            declinaison.prix_declinaison, 
            declinaison.stock,
            usure.libelle_usure,
            special.libelle_special
        FROM declinaison
        JOIN skin ON declinaison.skin_id = skin.id_skin
        JOIN usure ON declinaison.usure_id = usure.id_usure
        JOIN special ON declinaison.special_id = special.id_special
        WHERE skin.nom_skin = %s AND declinaison.stock > 0
        ORDER BY usure.id_usure, special.id_special  # Optional: order for consistent display
    '''
    mycursor.execute(sql, (nom_skin_base,))
    declinaisons = mycursor.fetchall()

    # Return the list of declinaison details
    return declinaisons


@client_article.route('/client/article/filtre', methods=['POST'])
def client_article_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types')

    # Gestion du filtre mot
    if filter_word:
        session['filter_word'] = filter_word
    elif 'filter_word' in session:
        session.pop('filter_word')

    # Gestion des filtres prix
    prix_valid = True

    # Validation des prix
    if filter_prix_min or filter_prix_max:
        if filter_prix_min and not filter_prix_min.isdigit():
            flash(u'Les valeurs du prix doivent être numériques', 'alert-warning')
            prix_valid = False
        if filter_prix_max and not filter_prix_max.isdigit():
            flash(u'Les valeurs du prix doivent être numériques', 'alert-warning')
            prix_valid = False
        
        if prix_valid and filter_prix_min and filter_prix_max:
            min_val = int(filter_prix_min)
            max_val = int(filter_prix_max)
            if min_val > max_val:
                flash(u'Le prix minimum doit être inférieur au prix maximum', 'alert-warning')
                prix_valid = False

    # Sauvegarde des prix si valides
    if prix_valid:
        if filter_prix_min:
            session['filter_prix_min'] = filter_prix_min
        elif 'filter_prix_min' in session:
            session.pop('filter_prix_min')
            
        if filter_prix_max:
            session['filter_prix_max'] = filter_prix_max
        elif 'filter_prix_max' in session:
            session.pop('filter_prix_max')
    else:
        # Si prix invalides, on supprime les filtres de prix
        if 'filter_prix_min' in session:
            session.pop('filter_prix_min')
        if 'filter_prix_max' in session:
            session.pop('filter_prix_max')

    # Gestion du filtre types
    if filter_types:
        session['filter_types'] = filter_types
    elif 'filter_types' in session:
        session.pop('filter_types')

    return redirect('/client/article/show')


@client_article.route('/client/article/filtre/delete', methods=['POST'])
def client_article_filtre_delete():
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


