#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime

from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__,
                        template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    
    # Récupérer les informations de l'utilisateur
    sql = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql, (id_client,))
    utilisateur = mycursor.fetchone()
    
    # Récupérer les adresses de l'utilisateur
    sql = """
    SELECT adresse.*, 
           (SELECT COUNT(*) FROM commande WHERE commande.adresse_livraison_id = adresse.id_adresse) AS nbr_commandes
    FROM adresse
    WHERE adresse.utilisateur_id = %s
    """
    mycursor.execute(sql, (id_client,))
    adresses = mycursor.fetchall()
    
    # Ajouter des valeurs par défaut pour valide et favori
    for adresse in adresses:
        adresse['valide'] = 1  # Toutes les adresses sont considérées comme valides
        adresse['favori'] = 0  # Par défaut, aucune adresse n'est favorite
    
    # Compter le nombre total d'adresses (toutes sont valides)
    nb_adresses = len(adresses)
    nb_adresses_tot = nb_adresses

    return render_template('client/coordonnee/show_coordonnee.html',
                           utilisateur=utilisateur,
                           adresses=adresses,
                           nb_adresses=nb_adresses,
                           nb_adresses_tot=nb_adresses_tot
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    
    # Récupérer les informations de l'utilisateur
    sql = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql, (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_coordonnee.html',
                           utilisateur=utilisateur)

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')
    
    # Vérifier si le login ou l'email existe déjà
    sql = """
    SELECT * FROM utilisateur 
    WHERE (login = %s OR email = %s) 
    AND id_utilisateur != %s
    """
    mycursor.execute(sql, (login, email, id_client))
    utilisateur_existant = mycursor.fetchone()
    
    if utilisateur_existant:
        flash(u'Cet Email ou ce Login existe déjà pour un autre utilisateur', 'alert-warning')
        
        # Récupérer les informations de l'utilisateur actuel
        sql = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
        mycursor.execute(sql, (id_client,))
        utilisateur = mycursor.fetchone()
        
        return render_template('client/coordonnee/edit_coordonnee.html',
                               utilisateur=utilisateur)
    
    # Mettre à jour les informations de l'utilisateur
    sql = """
    UPDATE utilisateur 
    SET nom = %s, login = %s, email = %s
    WHERE id_utilisateur = %s
    """
    mycursor.execute(sql, (nom, login, email, id_client))
    get_db().commit()
    
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')
    
    # Vérifier que l'adresse appartient bien à l'utilisateur
    sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s"
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()
    
    if adresse:
        # Supprimer l'adresse
        sql = "DELETE FROM adresse WHERE id_adresse = %s"
        mycursor.execute(sql, (id_adresse,))
        get_db().commit()

    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    
    # Récupérer les informations de l'utilisateur
    sql = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql, (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html',
                           utilisateur=utilisateur,
                           nom="",
                           rue="",
                           code_postal="",
                           ville="")

@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    
    # Insérer la nouvelle adresse
    sql = """
    INSERT INTO adresse (nom, rue, code_postal, ville, utilisateur_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    mycursor.execute(sql, (nom, rue, code_postal, ville, id_client))
    get_db().commit()
    
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')
    
    # Récupérer les informations de l'utilisateur
    sql = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql, (id_client,))
    utilisateur = mycursor.fetchone()
    
    # Récupérer les informations de l'adresse
    sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s"
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()
    
    if not adresse:
        # Si l'adresse n'existe pas ou n'appartient pas à l'utilisateur
        return redirect('/client/coordonnee/show')

    return render_template('client/coordonnee/edit_adresse.html',
                           utilisateur=utilisateur,
                           adresse=adresse)

@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')
    
    # Vérifier que l'adresse appartient bien à l'utilisateur
    sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s"
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()
    
    if adresse:
        # Mettre à jour l'adresse
        sql = """
        UPDATE adresse
        SET nom = %s, rue = %s, code_postal = %s, ville = %s
        WHERE id_adresse = %s
        """
        mycursor.execute(sql, (nom, rue, code_postal, ville, id_adresse))
        get_db().commit()

    return redirect('/client/coordonnee/show')
