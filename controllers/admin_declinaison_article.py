#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                         template_folder='templates')


@admin_declinaison_article.route('/admin/declinaison_article/add')
def add_declinaison_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    
    sql = '''
    SELECT 
        s.id_skin as id_article,
        s.nom_skin as nom,
        s.image,
        s.description
    FROM skin s
    WHERE s.id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    sql = '''SELECT id_usure, libelle_usure 
    FROM usure 
    ORDER BY libelle_usure'''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()

    sql = '''
    SELECT id_special, libelle_special 
    FROM special 
    ORDER BY libelle_special
    '''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()

    return render_template('admin/article/add_declinaison_article.html',
                         article=article,
                         tailles=tailles,
                         couleurs=couleurs)

@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    mycursor = get_db().cursor()

    id_article = request.form.get('id_article')
    prix = request.form.get('prix')
    stock = request.form.get('stock')
    usure_id = request.form.get('id_taille')
    special_id = request.form.get('id_couleur')

    sql = '''
    SELECT COUNT(*) as nb_declinaisons
    FROM declinaison
    WHERE skin_id = %s AND usure_id = %s AND special_id = %s
    '''
    mycursor.execute(sql, (id_article, usure_id, special_id))
    result = mycursor.fetchone()

    if result and result['nb_declinaisons'] > 0:
        flash(u'Cette combinaison état/type existe déjà pour cet article', 'alert-warning')
        return redirect(f'/admin/declinaison_article/add?id_article={id_article}')

    sql = '''
    INSERT INTO declinaison (skin_id, prix_declinaison, stock, usure_id, special_id)  
    VALUES (%s, %s, %s, %s, %s)
    '''
    mycursor.execute(sql, (id_article, prix, stock, usure_id, special_id))
    get_db().commit()

    flash(u'Déclinaison ajoutée avec succès', 'alert-success')
    return redirect(f'/admin/article/edit?id_article={id_article}')

@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['GET'])
def edit_declinaison_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    
    sql = '''
    SELECT 
        s.id_skin as article_id,
        s.nom_skin as nom,
        s.image as image_article
    FROM skin s
    WHERE s.id_skin = %s
    '''
    mycursor.execute(sql, (id_article,))
    declinaison_article = mycursor.fetchone()
    
    sql = '''
    SELECT 
        d.id_declinaison as id_declinaison_article,
        d.prix_declinaison,
        d.stock,
        d.skin_id as article_id,
        u.id_usure,
        u.libelle_usure,
        sp.id_special,
        sp.libelle_special
    FROM declinaison d
    JOIN usure u ON d.usure_id = u.id_usure
    JOIN special sp ON d.special_id = sp.id_special
    WHERE d.skin_id = %s
    '''
    mycursor.execute(sql, (id_article,))
    declinaisons = mycursor.fetchall()

    sql = "SELECT id_usure, libelle_usure FROM usure"
    mycursor.execute(sql)
    tailles = mycursor.fetchall() 

    sql = "SELECT id_special, libelle_special FROM special"
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()  

    return render_template('admin/article/edit_declinaison_article.html',
                         declinaison_article=declinaison_article,
                         declinaisons=declinaisons,
                         tailles=tailles,
                         couleurs=couleurs,
                         d_taille_uniq=None,
                         d_couleur_uniq=None)

@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    id_declinaison_article = request.form.get('id_declinaison_article')
    id_article = request.form.get('id_article')
    stock = request.form.get('stock')
    usure_id = request.form.get('id_taille')  
    special_id = request.form.get('id_couleur')  
    prix = request.form.get('prix')

    mycursor = get_db().cursor()
    sql = '''
    UPDATE declinaison 
    SET stock = %s, usure_id = %s, special_id = %s, prix_declinaison = %s
    WHERE id_declinaison = %s AND skin_id = %s
    '''
    mycursor.execute(sql, (stock, usure_id, special_id, prix, id_declinaison_article, id_article))
    get_db().commit()

    message = f'déclinaison modifiée , id:{id_declinaison_article} - stock:{stock} - usure_id:{usure_id} - special_id:{special_id}'
    flash(message, 'alert-success')
    
    return redirect('/admin/article/edit?id_article=' + str(id_article))



@admin_declinaison_article.route('/admin/declinaison_article/delete')
def delete_declinaison_article():
    mycursor = get_db().cursor()
    id_declinaison = request.args.get('id_declinaison')
    id_article = request.args.get('id_article')

    sql = '''
    SELECT COUNT(*) as nb_commandes
    FROM ligne_commande
    WHERE declinaison_id = %s
    '''
    mycursor.execute(sql, (id_declinaison,))
    result = mycursor.fetchone()

    if result['nb_commandes'] > 0:
        flash(u'Impossible de supprimer une déclinaison qui a été commandée', 'alert-warning')
        return redirect(f'/admin/article/edit?id_article={id_article}')

    sql = "DELETE FROM declinaison WHERE id_declinaison = %s"
    mycursor.execute(sql, (id_declinaison,))
    get_db().commit()

    flash(u'Déclinaison supprimée avec succès', 'alert-success')
    return redirect(f'/admin/article/edit?id_article={id_article}')
