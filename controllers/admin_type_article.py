#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_article = Blueprint('admin_type_article', __name__,
                        template_folder='templates')

@admin_type_article.route('/admin/type-article/show')
def show_type_article():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        ts.id_type_skin as id_type_article,
        ts.libelle_type_skin as libelle,
        COUNT(s.id_skin) as nbr_articles
    FROM type_skin ts
    LEFT JOIN skin s ON ts.id_type_skin = s.type_skin_id
    GROUP BY ts.id_type_skin, ts.libelle_type_skin
    ORDER BY ts.libelle_type_skin
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()
    return render_template('admin/type_article/show_type_article.html', types_article=types_article)

@admin_type_article.route('/admin/type-article/add', methods=['GET'])
def add_type_article():
    return render_template('admin/type_article/add_type_article.html')

@admin_type_article.route('/admin/type-article/add', methods=['POST'])
def valid_add_type_article():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''
    INSERT INTO type_skin (libelle_type_skin)
    VALUES (%s)
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-article/show') 

@admin_type_article.route('/admin/type-article/delete', methods=['GET'])
def delete_type_article():
    id_type_article = request.args.get('id_type_article', '')
    mycursor = get_db().cursor()
    
    # Vérifier si le type est utilisé
    sql = '''
    SELECT COUNT(*) as nb_articles
    FROM skin
    WHERE type_skin_id = %s
    '''
    mycursor.execute(sql, (id_type_article,))
    result = mycursor.fetchone()
    
    if result['nb_articles'] > 0:
        flash(u'Impossible de supprimer ce type car il est utilisé par ' + str(result['nb_articles']) + ' des articles', 'alert-warning')
    else:
        sql = '''
        DELETE FROM type_skin
        WHERE id_type_skin = %s
        '''
        mycursor.execute(sql, (id_type_article,))
        get_db().commit()
        flash(u'Type article supprimé, id : ' + id_type_article, 'alert-success')
    
    return redirect('/admin/type-article/show')

@admin_type_article.route('/admin/type-article/edit', methods=['GET'])
def edit_type_article():
    id_type_article = request.args.get('id_type_article', '')
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        id_type_skin as id_type_article,
        libelle_type_skin as libelle
    FROM type_skin
    WHERE id_type_skin = %s
    '''
    mycursor.execute(sql, (id_type_article,))
    type_article = mycursor.fetchone()
    return render_template('admin/type_article/edit_type_article.html', type_article=type_article)

@admin_type_article.route('/admin/type-article/edit', methods=['POST'])
def valid_edit_type_article():
    libelle = request.form['libelle']
    id_type_article = request.form.get('id_type_article', '')
    tuple_update = (libelle, id_type_article)
    mycursor = get_db().cursor()
    sql = '''
    UPDATE type_skin
    SET libelle_type_skin = %s
    WHERE id_type_skin = %s
    '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'type article modifié, id: ' + id_type_article + " libelle : " + libelle, 'alert-success')
    return redirect('/admin/type-article/show')