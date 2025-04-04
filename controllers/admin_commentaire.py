#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                        template_folder='templates')

@admin_commentaire.route('/admin/article/commentaires', methods=['GET'])
def admin_article_details():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)
    
    # Récupérer les informations de l'article et ses commentaires
    sql = '''
    SELECT 
        skin.id_skin as id_article,
        skin.nom_skin as nom,
        skin.image,
        skin.description,
        COUNT(DISTINCT commentaire.skin_id, commentaire.utilisateur_id, commentaire.date_publication) as nb_commentaires
    FROM skin
    LEFT JOIN commentaire ON skin.id_skin = commentaire.skin_id
    WHERE skin.id_skin = %s
    GROUP BY skin.id_skin, skin.nom_skin, skin.image, skin.description
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    # Récupérer les commentaires de l'article
    sql = '''
    SELECT 
        commentaire.skin_id AS id_article, 
        commentaire.utilisateur_id AS id_utilisateur, 
        commentaire.commentaire,
        commentaire.date_publication,
        commentaire.valide,
        utilisateur.nom as nom_utilisateur,
        utilisateur.email
    FROM skin
    JOIN commentaire ON skin.id_skin = commentaire.skin_id
    JOIN utilisateur ON commentaire.utilisateur_id = utilisateur.id_utilisateur
    WHERE skin.id_skin = %s
    ORDER BY commentaire.valide DESC, commentaire.date_publication DESC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    # Compter les commentaires non validés
    sql = '''
    SELECT COUNT(*) as nb_new
    FROM commentaire 
    WHERE skin_id = %s AND valide = 0
    '''
    mycursor.execute(sql, (id_article,))
    nb_commentaires = mycursor.fetchone()

    return render_template('admin/article/show_article_commentaires.html',
                         commentaires=commentaires,
                         article=article,
                         nb_commentaires=nb_commentaires)

@admin_commentaire.route('/admin/article/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_utilisateur = request.form.get('id_utilisateur', None)
    id_article = request.form.get('id_article', None)
    date_publication = request.form.get('date_publication', None)
    
    if not id_utilisateur or not id_article or not date_publication:
        flash('Erreur lors de la suppression du commentaire', 'alert-danger')
        if not id_article:
            return redirect('/admin/article/show')
        return redirect('/admin/article/commentaires?id_article=' + str(id_article))

    sql = '''
        DELETE FROM commentaire 
        WHERE utilisateur_id = %s AND skin_id = %s AND date_publication = %s
    '''
    mycursor.execute(sql, (id_utilisateur, id_article, date_publication))
    get_db().commit()
    
    flash('Commentaire supprimé avec succès', 'alert-success')
    return redirect('/admin/article/commentaires?id_article=' + str(id_article))

@admin_commentaire.route('/admin/article/commentaires/repondre', methods=['POST','GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_article = request.args.get('id_article', None)
        id_commentaire_parent = request.args.get('id_commentaire', None)
        return render_template('admin/article/add_commentaire.html',
                             id_article=id_article,
                             id_commentaire_parent=id_commentaire_parent)

    mycursor = get_db().cursor()
    id_article = request.form.get('id_article', None)
    commentaire = request.form.get('commentaire', None)
    id_commentaire_parent = request.form.get('id_commentaire_parent', None)
    
    sql = '''
    INSERT INTO commentaire(skin_id, utilisateur_id, commentaire, date_publication, valide, commentaire_parent_id)
    VALUES (%s, %s, %s, NOW(), 1, %s)
    '''
    mycursor.execute(sql, (id_article, session['id_user'], commentaire, id_commentaire_parent))
    get_db().commit()
    
    flash('Réponse ajoutée avec succès', 'alert-success')
    return redirect('/admin/article/commentaires?id_article=' + str(id_article))

@admin_commentaire.route('/admin/article/commentaires/valider', methods=['GET'])
def admin_comment_valider():
    id_article = request.args.get('id_article', None)
    mycursor = get_db().cursor()

    if not id_article:
        flash('Article is not provided', 'alert-danger')
        return redirect('/admin/article/show')
    
    sql = '''
        UPDATE commentaire 
        SET valide = 1 
        WHERE skin_id = %s AND valide = 0
    '''
    mycursor.execute(sql, (id_article,))
    get_db().commit()
    
    flash('Tous les commentaires ont été validés', 'alert-success')
    return redirect('/admin/article/commentaires?id_article=' + str(id_article))