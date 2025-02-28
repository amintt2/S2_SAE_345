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
        skin.id_skin as id_article,
        skin.nom_skin as nom,
        skin.prix_skin as prix,
        skin.stock,
        skin.image,
        skin.description,
        type_skin.id_type_skin as type_article_id,
        type_skin.libelle_type_skin as libelle,
        MIN(skin2.stock) as min_stock,
        COUNT(DISTINCT commande.id_commande) as nb_commandes,
        COUNT(DISTINCT ligne_panier.utilisateur_id) as nb_paniers
    FROM skin
    LEFT JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
    LEFT JOIN skin skin2 ON skin.type_skin_id = skin2.type_skin_id
    LEFT JOIN ligne_commande ON skin.id_skin = ligne_commande.skin_id
    LEFT JOIN commande ON ligne_commande.commande_id = commande.id_commande
    LEFT JOIN ligne_panier ON skin.id_skin = ligne_panier.skin_id
    GROUP BY skin.id_skin, skin.nom_skin, skin.prix_skin, skin.stock, skin.image, 
             skin.description, type_skin.id_type_skin, type_skin.libelle_type_skin
    ORDER BY skin.nom_skin
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
    INSERT INTO skin(nom_skin, image, prix_skin, type_skin_id, usure_id, special_id, stock, description)
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
        skin.prix_skin as prix,
        skin.stock,
        skin.image,
        skin.description,
        skin.type_skin_id as type_article_id,
        type_skin.libelle_type_skin as libelle
    FROM skin
    LEFT JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
    WHERE skin.id_skin = %s
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
    stock = request.form.get('stock', 0)
    description = request.form.get('description')
    type_article_id = request.form.get('type_article_id')
    image = request.files.get('image', None)

    if image:
        sql = '''
        UPDATE skin 
        SET nom_skin = %s, prix_skin = %s, stock = %s, 
            type_skin_id = %s, description = %s, image = %s
        WHERE id_skin = %s
        RETURNING image as old_image
        '''
        tuple_update = (nom, prix, stock, type_article_id, description, image.filename, id_article)
    else:
        sql = '''
        UPDATE skin 
        SET nom_skin = %s, prix_skin = %s, stock = %s, 
            type_skin_id = %s, description = %s
        WHERE id_skin = %s
        '''
        tuple_update = (nom, prix, stock, type_article_id, description, id_article)

    mycursor.execute(sql, tuple_update)

    if image:
        image.save(os.path.join('static/images/', image.filename))
        if mycursor.rowcount > 0:
            old_image = mycursor.fetchone()['old_image']
            if old_image and os.path.exists(os.path.join('static/images/', old_image)):
                os.remove(os.path.join('static/images/', old_image))

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
    UPDATE skin 
    SET stock = %s 
    WHERE id_skin = %s
    '''
    mycursor.execute(sql, (new_stock, id_article))
    get_db().commit()
    
    flash('Stock mis à jour avec succès', 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/stock/update', methods=['POST'])
def update_article_stock():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    new_stock = request.form.get('stock', type=int)
    
    if new_stock is None:
        flash('Le stock doit être spécifié', 'alert-danger')
        return redirect('/admin/article/show')
        
    if new_stock < 0:
        flash('Le stock ne peut pas être négatif', 'alert-danger')
        return redirect('/admin/article/show')
    
    sql = '''
    UPDATE skin 
    SET stock = %s 
    WHERE id_skin = %s
    '''
    mycursor.execute(sql, (new_stock, id_article))
    get_db().commit()
    
    flash('Stock mis à jour avec succès', 'alert-success')
    return redirect('/admin/article/show')
