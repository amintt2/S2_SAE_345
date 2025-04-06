#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        skin.id_skin AS id_article,
        skin.nom_skin AS nom,
        skin.image,
        skin.description,
        type_skin.id_type_skin AS type_article_id,
        type_skin.libelle_type_skin AS libelle,
        MIN(declinaison.prix_declinaison) AS prix_min,
        MAX(declinaison.prix_declinaison) AS prix_max,
        SUM(declinaison.stock) AS stock_total,
        MIN(declinaison.stock) AS min_stock,
        COUNT(DISTINCT commande.id_commande) AS nb_commandes,
        COUNT(DISTINCT declinaison.id_declinaison) AS nb_declinaisons,
        COUNT(DISTINCT ligne_panier.utilisateur_id) AS nb_paniers,
        COUNT(DISTINCT CASE WHEN valide = 0 THEN id_commentaire ELSE NULL END) AS nb_commentaires_nouveaux,
        COUNT(DISTINCT commentaire.id_commentaire) AS nb_commentaires,
        AVG(note.note) AS note_moyenne,
        COUNT(DISTINCT note.skin_id, note.utilisateur_id) AS nb_notes
    FROM skin
    LEFT JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
    LEFT JOIN declinaison ON skin.id_skin = declinaison.skin_id
    LEFT JOIN ligne_commande ON declinaison.id_declinaison = ligne_commande.declinaison_id
    LEFT JOIN commande ON ligne_commande.commande_id = commande.id_commande
    LEFT JOIN ligne_panier ON declinaison.id_declinaison = ligne_panier.declinaison_id
    LEFT JOIN note ON skin.id_skin = note.skin_id
    LEFT JOIN commentaire ON skin.id_skin = commentaire.skin_id
    GROUP BY skin.id_skin, skin.nom_skin, skin.image, 
            skin.description, type_skin.id_type_skin, type_skin.libelle_type_skin
    ORDER BY nb_commentaires_nouveaux DESC, nb_commentaires DESC, note_moyenne DESC, skin.nom_skin, skin.nom_skin, skin.image, skin.description, type_skin.id_type_skin, type_skin.libelle_type_skin;
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('admin/article/show_article.html', articles=articles)


@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()
    sql = '''
    SELECT id_type_skin AS id_type_article, libelle_type_skin AS libelle 
    FROM type_skin
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()
    
    sql = '''
    SELECT id_usure, libelle_usure 
    FROM usure
    '''
    mycursor.execute(sql)
    usures = mycursor.fetchall()
    
    sql = '''
    SELECT id_special, libelle_special 
    FROM special
    '''
    mycursor.execute(sql)
    specials = mycursor.fetchall()

    return render_template('admin/article/add_article.html',
                         types_article=types_article,
                         usures=usures,
                         specials=specials)


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom', '')
    prix = request.form.get('prix', '')
    stock = request.form.get('stock', '')
    description = request.form.get('description', '')
    type_article_id = request.form.get('type_article_id', '')
    usure_id = request.form.get('usure_id', '')
    special_id = request.form.get('special_id', '')
    image = request.form.get('image', 'no_photo.jpeg')

    mycursor.execute("START TRANSACTION")
    sql = '''
    INSERT INTO skin (nom_skin, disponible, type_skin_id, image, description)
    VALUES (%s, 1, %s, %s, %s)
    '''
    mycursor.execute(sql, (nom, type_article_id, image, description))
    
    skin_id = mycursor.lastrowid

    sql = '''
    INSERT INTO declinaison (stock, prix_declinaison, usure_id, special_id, skin_id)
    VALUES (%s, %s, %s, %s, %s)
    '''
    mycursor.execute(sql, (stock, prix, usure_id, special_id, skin_id))

    get_db().commit()
    flash(u'Article ajouté avec succès', 'success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    mycursor.execute("START TRANSACTION")
    
    sql = '''
    SELECT COUNT(*) as nb_commandes
    FROM ligne_commande lc
    JOIN declinaison d ON lc.declinaison_id = d.id_declinaison
    WHERE d.skin_id = %s
    '''
    mycursor.execute(sql, (id_article,))
    result = mycursor.fetchone()
    
    if result and result['nb_commandes'] > 0:
        flash(u'Impossible de supprimer cet article : il a déjà été commandé', 'alert-warning')
        return redirect('/admin/article/show')

    sql = '''
    DELETE FROM declinaison 
    WHERE skin_id = %s
    '''
    mycursor.execute(sql, (id_article,))

    sql = '''
    DELETE FROM skin 
    WHERE id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))

    get_db().commit()
    flash(u'Article supprimé', 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    
    sql = '''
    SELECT 
        skin.id_skin as id_article,
        skin.nom_skin as nom,
        skin.description,
        skin.image,
        skin.type_skin_id as type_article_id
    FROM skin
    WHERE skin.id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    sql = '''
    SELECT 
        d.id_declinaison,
        d.prix_declinaison,
        d.stock,
        d.usure_id,
        d.special_id,
        u.libelle_usure,
        s.libelle_special,
        COUNT(lc.declinaison_id) as nb_commandes
    FROM declinaison d
    JOIN usure u ON d.usure_id = u.id_usure
    JOIN special s ON d.special_id = s.id_special
    LEFT JOIN ligne_commande lc ON d.id_declinaison = lc.declinaison_id
    WHERE d.skin_id = %s
    GROUP BY d.id_declinaison
    '''
    mycursor.execute(sql, (id_article,))
    declinaisons = mycursor.fetchall()

    sql = "SELECT id_usure, libelle_usure FROM usure ORDER BY libelle_usure"
    mycursor.execute(sql)
    usures = mycursor.fetchall()

    sql = "SELECT id_special, libelle_special FROM special ORDER BY libelle_special"
    mycursor.execute(sql)
    specials = mycursor.fetchall()

    sql = '''
    SELECT id_type_skin as id_type_article, libelle_type_skin as libelle 
    FROM type_skin
    ORDER BY libelle_type_skin
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html',
                         article=article,
                         types_article=types_article,
                         declinaisons=declinaisons,
                         usures=usures,
                         specials=specials)


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    nom = request.form.get('nom')
    prix = request.form.get('prix')
    stock = request.form.get('stock')
    description = request.form.get('description')
    type_article_id = request.form.get('type_article_id')
    image = request.form.get('image')

    mycursor.execute("START TRANSACTION")

    if image:
        sql = '''
        UPDATE skin 
        SET nom_skin = %s, type_skin_id = %s, 
            description = %s, image = %s
        WHERE id_skin = %s
        '''
        tuple_update = (nom, type_article_id, description, image, id_article)
    else:
        sql = '''
        UPDATE skin 
        SET nom_skin = %s, type_skin_id = %s, 
            description = %s
        WHERE id_skin = %s
        '''
        tuple_update = (nom, type_article_id, description, id_article)
    
    mycursor.execute(sql, tuple_update)

    if prix and prix.strip() != '':
        prix = float(prix.replace(',', '.'))
        sql_price = '''
        UPDATE declinaison 
        SET prix_declinaison = %s
        WHERE skin_id = %s
        '''
        mycursor.execute(sql_price, (prix, id_article))

    if stock and stock.strip() != '':
        stock = int(stock)
        if stock >= 0:
            sql_stock = '''
            UPDATE declinaison 
            SET stock = %s 
            WHERE skin_id = %s
            '''
            mycursor.execute(sql_stock, (stock, id_article))

    get_db().commit()
    flash(f'Article {nom} modifié avec succès', 'success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article=[]
    commentaires = {}
    return render_template('admin/article/show_avis.html'
                           , article=article
                           , commentaires=commentaires
                           )


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)

    return admin_avis(article_id)


@admin_article.route('/admin/article/stock/edit/<int:id>', methods=['POST'])
def update_stock():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    new_stock = request.form.get('stock', type=int)
    
    if new_stock < 0:
        flash('Le stock ne peut pas être négatif', 'alert-danger')
        return redirect('/admin/article/show')
        
    sql = '''
    UPDATE declinaison 
    SET stock = %s 
    WHERE skin_id = %s
    '''
    mycursor.execute(sql, (new_stock, id_article))
    get_db().commit()
    
    flash('Stock mis à jour avec succès', 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/stock/update', methods=['POST'])
def update_article_stock():
    mycursor = get_db().cursor()
    id_declinaison = request.form.get('id_declinaison')
    new_stock = request.form.get('stock', type=int)
    
    if new_stock is None:
        flash('Le stock doit être spécifié', 'alert-danger')
        return redirect('/admin/article/show')
        
    if new_stock < 0:
        flash('Le stock ne peut pas être négatif', 'alert-danger')
        return redirect('/admin/article/show')
    
    mycursor.execute("START TRANSACTION")
    
    sql = '''
    UPDATE declinaison 
    SET stock = %s 
    WHERE id_declinaison = %s
    '''
    mycursor.execute(sql, (new_stock, id_declinaison))
        
    get_db().commit()
    flash('Stock mis à jour avec succès', 'alert-success')
        
    return redirect('/admin/article/show')
