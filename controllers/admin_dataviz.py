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
    # mycursor = get_db().cursor()
    # sql = '''    '''
    # mycursor.execute(sql)
    # adresses = mycursor.fetchall()

    #exemples de tableau "résultat" de la requête
    adresses =  [{'dep': '25', 'nombre': 1}, {'dep': '83', 'nombre': 1}, {'dep': '90', 'nombre': 3}]

    # recherche de la valeur maxi "nombre" dans les départements
    # maxAddress = 0
    # for element in adresses:
    #     if element['nbr_dept'] > maxAddress:
    #         maxAddress = element['nbr_dept']
    # calcul d'un coefficient de 0 à 1 pour chaque département
    # if maxAddress != 0:
    #     for element in adresses:
    #         indice = element['nbr_dept'] / maxAddress
    #         element['indice'] = round(indice,2)

    print(adresses)

    return render_template('admin/dataviz/dataviz_etat_map.html'
                           , adresses=adresses
                          )


