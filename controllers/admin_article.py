#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
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
        skin.nom_skin As nom,
        skin.image,
        skin.description,
        type_skin.id_type_skin AS type_article_id,
        type_skin.libelle_type_skin AS libelle,
        MIN(declinaison.prix_declinaison) AS prix_min,
        MAX(declinaison.prix_declinaison) AS prix_max,
        SUM(declinaison.stock) AS stock_total,
        MIN(declinaison.stock) AS min_stock,
        COUNT(DISTINCT commande.id_commande) AS nb_commandes,
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
    SELECT id_type_skin as id_type_article, libelle_type_skin as libelle 
    FROM type_skin
    ORDER BY libelle_type_skin
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
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    stock = request.form.get('stock', 0)
    usure_id = request.form.get('usure_id', '')
    special_id = request.form.get('special_id', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    sql = '''
    INSERT INTO skin(nom_skin, image, prix_declinaison, type_skin_id, usure_id, special_id, stock, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    tuple_add = (nom, filename, prix, type_article_id, usure_id, special_id, stock, description)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'article ajouté , nom: ', nom, ' - type_article:', type_article_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'article ajouté , nom:' + nom + '- type_article:' + type_article_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    
    # Vérifier si l'article est dans un panier
    sql = '''
    SELECT COUNT(*) as count 
    FROM ligne_panier 
    WHERE skin_id = %s
    '''
    mycursor.execute(sql, (id_article,))
    count_panier = mycursor.fetchone()['count']

    # Vérifier si l'article est dans une commande
    sql = '''
    SELECT COUNT(*) as count 
    FROM ligne_commande 
    WHERE skin_id = %s
    '''
    mycursor.execute(sql, (id_article,))
    count_commande = mycursor.fetchone()['count']

    if count_panier > 0:
        flash("Impossible de supprimer l'article : il est présent dans un panier", 'error')
        return redirect('/admin/article/show')

    if count_commande > 0:
        flash("Impossible de supprimer l'article : il est présent dans une commande", 'error')
        return redirect('/admin/article/show')
    
    # Récupérer l'image avant la suppression
    sql = '''
    SELECT image 
    FROM skin 
    WHERE id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    image = mycursor.fetchone()['image']
    
    # Supprimer l'article
    sql = '''
    DELETE FROM skin 
    WHERE id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    get_db().commit()
    
    # Supprimer l'image si elle existe
    if image and os.path.exists(os.path.join('static/images/', image)):
        os.remove(os.path.join('static/images/', image))
    
    flash('Article supprimé avec succès', 'success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        skin.id_skin as id_article,
        skin.nom_skin as nom,
        MIN(d.prix_declinaison) as prix_min,
        MAX(d.prix_declinaison) as prix_max,
        SUM(d.stock) as stock,
        skin.image,
        skin.description,
        skin.type_skin_id as type_article_id,
        type_skin.libelle_type_skin as libelle
    FROM skin
    LEFT JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
    LEFT JOIN declinaison d ON skin.id_skin = d.skin_id
    WHERE skin.id_skin = %s
    GROUP BY skin.id_skin, skin.nom_skin, skin.image, 
             skin.description, skin.type_skin_id, type_skin.libelle_type_skin
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    sql = '''
    SELECT id_type_skin as id_type_article, libelle_type_skin as libelle 
    FROM type_skin
    ORDER BY libelle_type_skin
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html',
                         article=article,
                         types_article=types_article)


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    nom = request.form.get('nom')
    prix = request.form.get('prix')
    stock = request.form.get('stock')  # Get stock value from form
    description = request.form.get('description')
    type_article_id = request.form.get('type_article_id')
    image = request.files.get('image', None)

    # Start transaction
    mycursor.execute("START TRANSACTION")

    # Update skin table
    if image:
        sql = '''
        UPDATE skin 
        SET nom_skin = %s, type_skin_id = %s, 
            description = %s, image = %s
        WHERE id_skin = %s
        RETURNING image as old_image
        '''
        tuple_update = (nom, type_article_id, description, image.filename, id_article)
    else:
        sql = '''
        UPDATE skin 
        SET nom_skin = %s, type_skin_id = %s, 
            description = %s
        WHERE id_skin = %s
        '''
        tuple_update = (nom, type_article_id, description, id_article)

    mycursor.execute(sql, tuple_update)

    # Update stock in declinaison table
    if stock is not None and stock != '':
        stock = int(stock)
        if stock >= 0:
            sql_stock = '''
            UPDATE declinaison 
            SET stock = %s 
            WHERE skin_id = %s
            '''
            mycursor.execute(sql_stock, (stock, id_article))
        else:
            flash('Le stock ne peut pas être négatif', 'error')

    # Update price in declinaison table
    if prix and prix.strip() != '':
        prix = float(prix.replace(',', '.'))
        sql_price = '''
        UPDATE declinaison 
        SET prix_declinaison = %s
        WHERE skin_id = %s
        '''
        mycursor.execute(sql_price, (prix, id_article))

    # Handle image upload and deletion
    if image and mycursor.rowcount > 0:
        image.save(os.path.join('static/images/', image.filename))
        if 'old_image' in locals():
            old_image = mycursor.fetchone()['old_image']
            if old_image and os.path.exists(os.path.join('static/images/', old_image)):
                os.remove(os.path.join('static/images/', old_image))

    # Commit transaction
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
    
    # Start transaction
    mycursor.execute("START TRANSACTION")
    
    # Update stock in declinaison table
    sql = '''
    UPDATE declinaison 
    SET stock = %s 
    WHERE id_declinaison = %s
    '''
    mycursor.execute(sql, (new_stock, id_declinaison))
    
    if mycursor.rowcount == 0:
        get_db().rollback()
        flash('Erreur : déclinaison non trouvée', 'alert-danger')
        return redirect('/admin/article/show')
        
    # Commit transaction
    get_db().commit()
    flash('Stock mis à jour avec succès', 'alert-success')
        
    
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/choose-declinaison')
def choose_declinaison():
    id_article = request.args.get('id_article')
    action = request.args.get('action')
    
    if not id_article or not action:
        flash(u'Paramètres manquants', 'error')
        return redirect('/admin/article/show')
        
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        d.id_declinaison,
        s.nom_skin as nom_article,
        d.prix_declinaison,
        d.stock,
        u.libelle_usure,
        sp.libelle_special
    FROM declinaison d
    JOIN skin s ON d.skin_id = s.id_skin
    JOIN usure u ON d.usure_id = u.id_usure
    JOIN special sp ON d.special_id = sp.id_special
    WHERE s.id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    declinaisons = mycursor.fetchall()
    
    if not declinaisons:
        flash(u'Article non trouvé', 'error')
        return redirect('/admin/article/show')
        
    return render_template('admin/article/choose_declinaison.html', 
                         declinaisons=declinaisons,
                         action=action,
                         id_article=id_article)
