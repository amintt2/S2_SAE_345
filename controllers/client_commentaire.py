#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__,
                        template_folder='templates')


@client_commentaire.route('/client/article/details', methods=['GET'])
def client_article_details():
    mycursor = get_db().cursor()
    id_article =  request.args.get('id_article', None)
    print(id_article)
    id_client = session['id_user']

    ## partie 4
    client_historique_add(id_article, id_client)

    sql = '''
    SELECT 
        id_skin AS id_article,
        nom_skin AS nom, 
        prix_skin AS prix,
        description,
        image,
        ROUND(AVG(note), 1) AS moyenne_notes,
        COUNT(note) AS nb_notes
    FROM skin
    LEFT JOIN note ON note.skin_id = skin.id_skin
    WHERE id_skin = %s
    GROUP BY id_skin, nom_skin, prix_skin, description, image;
    '''
    # -- Description, moyenne_notes, nb_notes
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    print(article)
    #article=[]
    commandes_articles=[]
    nb_commentaires=[]
    if article is None:
        abort(404, "pb id article")
    
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
    mycursor.execute(sql, ( id_article))
    commentaires = mycursor.fetchall()
    sql = '''
        SELECT COUNT(declinaison_id) AS nb_commandes_article
        FROM ligne_commande
        JOIN commande ON commande.id_commande = ligne_commande.commande_id
        WHERE commande.utilisateur_id=%s and ligne_commande.declinaison_id=%s;
    '''
    mycursor.execute(sql, (id_client, id_article))
    commandes_articles = mycursor.fetchone()
    print(f"id_client: {id_client} - id_article: {id_article}")
    print(commandes_articles)
    sql = ''' 
        SELECT note 
        FROM note
        WHERE utilisateur_id=%s and skin_id=%s;
    '''
    mycursor.execute(sql, (id_client, id_article))
    note = mycursor.fetchone()
    print('note',note)
    if note:
        note=note['note']
    sql = '''
        SELECT  COUNT(*) AS nb_commentaires_total
                , COUNT(IF(valide = 1, 1, NULL)) AS nb_commentaires_total_valide
                , COUNT(IF(utilisateur_id = %s, 1, NULL)) AS nb_commentaires_utilisateur
                , COUNT(IF(utilisateur_id = %s AND valide = 1, 1, NULL)) AS nb_commentaires_utilisateur_valide

        FROM commentaire
        WHERE skin_id = %s
        GROUP BY skin_id;
    '''
    mycursor.execute(sql, (id_client, id_client, id_article))
    nb_commentaires = mycursor.fetchone()
    return render_template('client/article_info/article_details.html'
                           , article=article
                           , commentaires=commentaires
                           , commandes_articles=commandes_articles
                           , note=note
                            , nb_commentaires=nb_commentaires
                           )

@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', None)
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    if commentaire == '':
        flash(u'Commentaire non prise en compte')
        return redirect('/client/article/details?id_article='+id_article)
    if commentaire != None and len(commentaire)>0 and len(commentaire) <3 :
        flash(u'Commentaire avec plus de 2 caractères','alert-warning')              # 
        return redirect('/client/article/details?id_article='+id_article)

    tuple_insert = (id_client, id_article, commentaire)
    print(tuple_insert)

    sql='''
    SELECT commande.utilisateur_id, declinaison.skin_id
    FROM ligne_commande
    JOIN commande ON commande.id_commande = ligne_commande.commande_id
    JOIN declinaison ON declinaison.id_declinaison = ligne_commande.declinaison_id
    WHERE commande.utilisateur_id=%s AND declinaison.skin_id=%s
    '''
    mycursor.execute(sql, (id_client, id_article))
    commande = mycursor.fetchone()
    if not commande:
        flash(u'Vous ne pouvez pas commenter cet article sans l\'avoir acheté', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)
    
    sql = '''
    SELECT COUNT(*) AS nb_commentaires
    FROM commentaire
    WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    nb_commentaires = mycursor.fetchone()
    if nb_commentaires['nb_commentaires'] >= 3:
        flash(u'Vous avez deja commenté cet article 3 fois', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)
    
    sql = '''  
        INSERT INTO commentaire(utilisateur_id, skin_id, commentaire, date_publication, valide)
        VALUES (%s, %s, %s, NOW(), 0);
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_detete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_author = request.form.get('utilisateur_id', None)
    id_article = request.form.get('id_article', None)
    date_publication = request.form.get('date_publication', None)
    id_commentaire = request.form.get('id_commentaire', None)

    if (id_author == id_client):
        flash(u'Vous ne pouvez pas supprimer un commentaire qui ne vous appartien pas', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)

    sql = '''
    DELETE FROM commentaire
    WHERE id_commentaire = %s;
    '''
    tuple_delete=(id_commentaire)
    print(tuple_delete)
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_insert = (note, id_client, id_article)
    print(tuple_insert)

    sql='''
        SELECT commande.utilisateur_id, declinaison.skin_id
        FROM ligne_commande
        JOIN commande ON commande.id_commande = ligne_commande.commande_id
        JOIN declinaison ON declinaison.id_declinaison = ligne_commande.declinaison_id
        WHERE commande.utilisateur_id=%s AND declinaison.skin_id=%s
    '''
    mycursor.execute(sql, (id_client, id_article))
    commande = mycursor.fetchone()
    if not commande:
        flash(u'Vous ne pouvez pas noter un skin que vous n\'avez jamais acheté', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)
    

    sql = '''
        SELECT *
        FROM note
        WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    nb_notes = mycursor.fetchone()
    if nb_notes is not None:
        flash(u'Vous avez deja noté cet article', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)
    
    sql = '''
        INSERT INTO note (note, utilisateur_id, skin_id)
        VALUES (%s, %s, %s)
        '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_update = (note, id_client, id_article)
    print(tuple_update)

    sql = '''
    SELECT *
    FROM note
    WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    nb_notes = mycursor.fetchone()
    if nb_notes is None:
        flash(u'Vous n\'avez pas encore noté cet article', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)
    
    
    sql = '''
        UPDATE note
        SET note = %s
        WHERE utilisateur_id = %s AND skin_id = %s
    '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    tuple_delete = (id_client, id_article)
    print(tuple_delete)
    sql = '''
    SELECT *
    FROM note
    WHERE skin_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    nb_notes = mycursor.fetchone()
    if nb_notes is None:
        flash(u'Vous ne pouvez pas supprimer une note que vous n\'avez jamais noté', 'alert-info')
        return redirect('/client/article/details?id_article='+id_article)
    
    sql = ''' 
        DELETE FROM note
        WHERE utilisateur_id = %s AND skin_id = %s;
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect(u'/client/article/details?id_article='+id_article)
