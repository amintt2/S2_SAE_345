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
        COUNT(DISTINCT commentaire.id_commentaire) as nb_commentaires
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
        commentaire.id_commentaire,
        commentaire.skin_id AS id_article, 
        commentaire.utilisateur_id AS id_utilisateur, 
        commentaire.commentaire,
        commentaire.date_publication,
        commentaire.valide,
        utilisateur.nom as nom_utilisateur,

        commentaire_admin.id_commentaire AS id_commentaire_admin,
        commentaire_admin.utilisateur_id AS id_admin,
        commentaire_admin.commentaire AS commentaire_admin,
        commentaire_admin.date_publication AS date_publication_admin,
        commentaire_admin.valide AS valide_admin,
        admin.nom as nom_utilisateur_admin
        
    FROM commentaire
    JOIN utilisateur ON commentaire.utilisateur_id = utilisateur.id_utilisateur
    LEFT JOIN (
        SELECT * FROM commentaire 
        WHERE commentaire_id_parent IS NOT NULL
    ) AS commentaire_admin ON commentaire_admin.commentaire_id_parent = commentaire.id_commentaire
    LEFT JOIN utilisateur AS admin ON commentaire_admin.utilisateur_id = admin.id_utilisateur
    WHERE commentaire.skin_id = %s AND commentaire.commentaire_id_parent IS NULL
    ORDER BY commentaire.valide DESC, commentaire.date_publication DESC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    print(commentaires)

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
    id_commentaire = request.form.get('id_commentaire', None)
    
    if not id_commentaire:
        flash('Erreur lors de la suppression du commentaire', 'alert-danger')
        if not id_article:
            return redirect('/admin/article/show')
        return redirect('/admin/article/commentaires?id_article=' + str(id_article))
    
    sql = '''
    SELECT COUNT(*)
    FROM commentaire
    WHERE commentaire_id_parent = %s
    '''
    mycursor.execute(sql, (id_commentaire,))
    nb_reponses = mycursor.fetchone()['COUNT(*)']
    
    if nb_reponses > 0:
        flash('Erreur lors de la suppression du commentaire (il y a des réponses)', 'alert-danger')
        if not id_article:
            return redirect('/admin/article/show')
        return redirect('/admin/article/commentaires?id_article=' + str(id_article))

    sql = '''
        DELETE FROM commentaire 
        WHERE id_commentaire = %s
    '''
    mycursor.execute(sql, (id_commentaire))
    get_db().commit()
    
    flash('Commentaire supprimé avec succès', 'alert-success')
    if not id_article:
            return redirect('/admin/article/show')
    return redirect('/admin/article/commentaires?id_article=' + str(id_article))

@admin_commentaire.route('/admin/article/commentaires/repondre', methods=['POST','GET'])
def admin_comment_add():
    mycursor = get_db().cursor()

    def have_already_replied(id_commentaire_parent):
        sql = '''
        SELECT COUNT(*)
        FROM commentaire
        WHERE commentaire_id_parent = %s;
        '''
        mycursor.execute(sql, (id_commentaire_parent))
        count = mycursor.fetchone()['COUNT(*)']
        if count >= 1:
            flash("Vous ne pouvez pas répondre plus de 2 fois à un avis", 'alert-danger')
            return True
        return False
    
    if request.method == 'GET':
        id_article = request.args.get('id_article', None)
        id_commentaire_parent = request.args.get('id_commentaire', None)
        if have_already_replied(id_commentaire_parent):
            return redirect('/admin/article/commentaires?id_article=' + str(id_article))
        
        sql = '''
        SELECT nom AS nom_utilisateur, date_publication, commentaire
        FROM commentaire
        JOIN utilisateur ON utilisateur.id_utilisateur = commentaire.utilisateur_id
        WHERE id_commentaire = %s
        '''
        mycursor.execute(sql, (id_commentaire_parent,))
        commentaire_parent = mycursor.fetchone()
        
        return render_template('admin/article/add_commentaire.html',
                             commentaire_parent=commentaire_parent,
                             id_article=id_article,
                             id_commentaire_parent=id_commentaire_parent)

    id_article = request.form.get('id_article', None)
    commentaire = request.form.get('commentaire', None)
    id_commentaire_parent = request.form.get('id_commentaire_parent', None)
    
    if have_already_replied(id_commentaire_parent):
        return redirect('/admin/article/commentaires?id_article=' + str(id_article))

    sql = '''
    INSERT INTO commentaire(skin_id, utilisateur_id, commentaire, date_publication, valide, commentaire_id_parent)
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