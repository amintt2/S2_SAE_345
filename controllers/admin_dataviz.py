#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    sql = '''
    
           '''
    # mycursor.execute(sql)
    # datas_show = mycursor.fetchall()
    # labels = [str(row['libelle']) for row in datas_show]
    # values = [int(row['nbr_articles']) for row in datas_show]

    # sql = '''
    #         
    #        '''
    datas_show=[]
    labels=[]
    values=[]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , datas_show=datas_show
                           , labels=labels
                           , values=values)


@admin_dataviz.route('/admin/dataviz/avis')
def show_type_article_avis():
    mycursor = get_db().cursor()

    id_type_article = None
    if request.method == 'GET':
        id_type_article = request.args.get('id_type_article', None)
        if id_type_article == '0' or (id_type_article is not None and id_type_article.isdigit() == False):
            return redirect('/admin/dataviz/avis')

    sql = '''
        SELECT id_type_skin AS id_type_article, libelle_type_skin AS libelle
        FROM type_skin
        ORDER BY libelle_type_skin
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()


    if id_type_article is not None:
        sql = '''
            SELECT skin.id_skin AS id,
                skin.nom_skin AS libelle,
                note.moyenne_notes AS note_moyenne, 
                note.nb_notes AS nb_notes,
                COUNT(DISTINCT commentaire.id_commentaire) AS nb_commentaires
            FROM skin
            JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            LEFT JOIN (
                SELECT skin_id, 
                        AVG(note.note) AS moyenne_notes,
                        COUNT(DISTINCT skin_id, utilisateur_id) AS nb_notes
                FROM note
                JOIN skin ON note.skin_id = skin.id_skin
                WHERE skin.type_skin_id = %s
                GROUP BY skin_id
            ) AS note ON skin.id_skin = note.skin_id
            LEFT JOIN commentaire ON skin.id_skin = commentaire.skin_id
            WHERE skin.type_skin_id = %s
            GROUP BY id, libelle, note_moyenne, nb_notes
            HAVING nb_commentaires > 0 or nb_notes > 0
            ORDER BY libelle
            '''
        mycursor.execute(sql, (id_type_article, id_type_article))
    else :
        sql = '''
            SELECT id_type_skin AS id, 
                libelle_type_skin AS libelle,
                note.moyenne_notes AS note_moyenne, 
                note.nb_notes AS nb_notes,
                COUNT(DISTINCT commentaire.id_commentaire) AS nb_commentaires
            FROM skin
            JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            LEFT JOIN (
                SELECT type_skin_id, 
                        AVG(note.note) AS moyenne_notes,
                        COUNT(DISTINCT skin_id, utilisateur_id) AS nb_notes
                FROM note
                JOIN skin ON note.skin_id = skin.id_skin
                GROUP BY type_skin_id
            ) AS note ON skin.type_skin_id = note.type_skin_id
            LEFT JOIN commentaire ON skin.id_skin = commentaire.skin_id
            GROUP BY id, libelle, note_moyenne, nb_notes
            ORDER BY libelle
            '''
        mycursor.execute(sql)
        print(sql)
        
    
    
    datas_show = mycursor.fetchall()
    labels = [row['libelle'] for row in datas_show if row['libelle'] is not None]
    moyenne_notes = [float(row['note_moyenne']) for row in datas_show if row['note_moyenne'] is not None]
    nb_notes = [int(row['nb_notes']) for row in datas_show if row['nb_notes'] is not None]
    nb_commentaires = [int(row['nb_commentaires']) for row in datas_show if row['nb_commentaires'] is not None]






    print(datas_show)
    print(labels)
    print(moyenne_notes)
    print(nb_notes)
    print(nb_commentaires)

    return render_template('admin/dataviz/dataviz_etat_avis.html'
                           , id_type_article=id_type_article
                           , types_article=types_article
                           , datas_show=datas_show
                           , labels=labels
                           , moyenne_notes=moyenne_notes
                           , nb_notes=nb_notes
                           , nb_commentaires=nb_commentaires
                          )


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()
    
    # Récupérer les départements (2 premiers chiffres du code postal) avec nombre de ventes et chiffre d'affaires
    sql = '''
    SELECT 
        LEFT(a.code_postal, 2) as dep,
        COUNT(DISTINCT c.id_commande) as nombre,
        SUM(lc.prix * lc.quantite) as ca
    FROM commande c
    JOIN adresse a ON c.adresse_livraison_id = a.id_adresse
    JOIN ligne_commande lc ON c.id_commande = lc.commande_id
    GROUP BY dep
    ORDER BY dep
    '''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    
    # Recherche de la valeur maximale pour le nombre de ventes et le CA
    max_nombre = 0
    max_ca = 0
    for element in adresses:
        if element['nombre'] > max_nombre:
            max_nombre = element['nombre']
        if element['ca'] > max_ca:
            max_ca = element['ca']
    
    # Calcul d'un coefficient de 0 à 1 pour chaque département
    if max_nombre != 0 and max_ca != 0:
        for element in adresses:
            indice_nombre = element['nombre'] / max_nombre
            indice_ca = element['ca'] / max_ca
            element['indice_nombre'] = round(indice_nombre, 2)
            element['indice_ca'] = round(indice_ca, 2)
            element['ca_format'] = "{:,.2f}".format(element['ca'])
    
    # Récupérer le type de visualisation (CA ou nombre de commandes)
    type_viz = request.args.get('type_viz', 'nombre')  # Par défaut: nombre de commandes
    
    return render_template('admin/dataviz/dataviz_etat_map.html',
                           adresses=adresses,
                           type_viz=type_viz)


@admin_dataviz.route('/admin/dataviz/adresses')
def show_dataviz_adresses():
    mycursor = get_db().cursor()
    
    # Récupérer le type de visualisation (CA ou nombre de commandes)
    type_viz = request.args.get('type_viz', 'nombre')  # Par défaut: nombre de commandes
    
    # Déterminer l'ordre en fonction du type de visualisation
    order_by = "ca DESC" if type_viz == 'ca' else "nombre DESC"
    
    # Récupérer les départements (2 premiers chiffres du code postal) avec nombre de ventes et chiffre d'affaires
    sql = f'''
    SELECT 
        LEFT(a.code_postal, 2) as dep,
        COUNT(DISTINCT c.id_commande) as nombre,
        SUM(lc.prix * lc.quantite) as ca
    FROM commande c
    JOIN adresse a ON c.adresse_livraison_id = a.id_adresse
    JOIN ligne_commande lc ON c.id_commande = lc.commande_id
    GROUP BY dep
    ORDER BY nombre DESC
    '''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()
    
    # Recherche de la valeur maximale pour le nombre de ventes et le CA
    max_nombre = 0
    max_ca = 0
    for element in adresses:
        if element['nombre'] > max_nombre:
            max_nombre = element['nombre']
        if element['ca'] > max_ca:
            max_ca = element['ca']
    
    # Calcul d'un coefficient de 0 à 1 pour chaque département
    if max_nombre != 0 and max_ca != 0:
        for element in adresses:
            indice_nombre = element['nombre'] / max_nombre
            indice_ca = element['ca'] / max_ca
            element['indice_nombre'] = round(indice_nombre, 2)
            element['indice_ca'] = round(indice_ca, 2)
            element['ca_format'] = "{:,.2f}".format(element['ca'])
    
    return render_template('admin/dataviz/dataviz_adresses.html',
                           adresses=adresses,
                           type_viz=type_viz)


##################
##### Stock ######
##################

@admin_dataviz.route('/admin/dataviz/stock')
def dataviz_stock():
    mycursor = get_db().cursor()
    
    sql = '''
    SELECT 
        CONCAT(s.nom_skin, ' - ', u.libelle_usure, ' - ', sp.libelle_special) as declinaison,
        d.stock as quantite,
        d.stock * d.prix_declinaison AS valeur_stock
    FROM declinaison d
    JOIN skin s ON d.skin_id = s.id_skin
    JOIN usure u ON d.usure_id = u.id_usure
    JOIN special sp ON d.special_id = sp.id_special
    ORDER BY valeur_stock DESC
    '''
    mycursor.execute(sql)
    stocks = mycursor.fetchall()

    labels = [item['declinaison'] for item in stocks]
    quantities = [float(item['quantite']) for item in stocks]
    values = [float(item['valeur_stock']) for item in stocks]
    
    total_items = sum(quantities)
    total_value = sum(values)

    return render_template('admin/dataviz/dataviz_etat_stock.html',
                         labels=labels,
                         quantities=quantities,
                         values=values,
                         total_items=total_items,
                         total_value=total_value)


