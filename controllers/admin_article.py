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
        s.id_skin as id_article,
        s.nom_skin as nom,
        s.prix_skin as prix,
        s.stock,
        s.image,
        s.description,
        ts.id_type_skin as type_article_id,
        ts.libelle_type_skin as libelle,
        MIN(s2.stock) as min_stock,
        COUNT(DISTINCT c.id_commande) as nb_commandes,
        COUNT(DISTINCT lp.utilisateur_id) as nb_paniers
    FROM skin s
    LEFT JOIN type_skin ts ON s.type_skin_id = ts.id_type_skin
    LEFT JOIN skin s2 ON s.type_skin_id = s2.type_skin_id
    LEFT JOIN ligne_commande lc ON s.id_skin = lc.skin_id
    LEFT JOIN commande c ON lc.commande_id = c.id_commande
    LEFT JOIN ligne_panier lp ON s.id_skin = lp.skin_id
    GROUP BY s.id_skin, s.nom_skin, s.prix_skin, s.stock, s.image, 
             s.description, ts.id_type_skin, ts.libelle_type_skin
    ORDER BY s.nom_skin
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
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = ''' requête admin_article_3 '''
    mycursor.execute(sql, id_article)
    nb_declinaison = mycursor.fetchone()
    if nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet article : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' requête admin_article_4 '''
        mycursor.execute(sql, id_article)
        article = mycursor.fetchone()
        print(article)
        image = article['image']

        sql = ''' requête admin_article_5  '''
        mycursor.execute(sql, id_article)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un article supprimé, id :", id_article)
        message = u'un article supprimé, id : ' + id_article
        flash(message, 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''
    requête admin_article_6    
    '''
    mycursor.execute(sql, id_article)
    article = mycursor.fetchone()
    print(article)
    sql = '''
    requête admin_article_7
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    # sql = '''
    # requête admin_article_6
    # '''
    # mycursor.execute(sql, id_article)
    # declinaisons_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html'
                           ,article=article
                           ,types_article=types_article
                         #  ,declinaisons_article=declinaisons_article
                           )


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')
    sql = '''
       requête admin_article_8
       '''
    mycursor.execute(sql, id_article)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    sql = '''  requête admin_article_9 '''
    mycursor.execute(sql, (nom, image_nom, prix, type_article_id, description, id_article))

    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'article modifié , nom:' + nom + '- type_article :' + type_article_id + ' - prix:' + prix  + ' - image:' + image_nom + ' - description: ' + description
    flash(message, 'alert-success')
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
