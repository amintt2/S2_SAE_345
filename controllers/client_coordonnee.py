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
    SELECT 
        adresse.id_adresse,
        adresse.nom,
        adresse.rue,
        adresse.code_postal,
        adresse.ville,
        adresse.utilisateur_id,
        adresse.est_favori,
        adresse.date_utilisation,
        adresse.est_valide,
        (SELECT COUNT(*) FROM commande 
         WHERE commande.adresse_livraison_id = adresse.id_adresse 
         OR commande.adresse_facturation_id = adresse.id_adresse) AS nbr_commandes,
        (SELECT MAX(date_achat) FROM commande 
         WHERE (commande.adresse_livraison_id = adresse.id_adresse 
         OR commande.adresse_facturation_id = adresse.id_adresse)) AS derniere_utilisation
    FROM adresse
    WHERE adresse.utilisateur_id = %s
    ORDER BY est_favori DESC, derniere_utilisation DESC
    """
    mycursor.execute(sql, (id_client,))
    adresses = mycursor.fetchall()
    
    # Compter le nombre d'adresses valides
    nb_adresses = sum(1 for adresse in adresses if adresse['est_valide'] == 1)
    nb_adresses_tot = len(adresses)

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
    
    if not adresse:
        flash(u'Cette adresse ne vous appartient pas ou n\'existe pas.', 'alert-warning')
        return redirect('/client/coordonnee/show')
    
    # Vérifier si l'adresse est utilisée dans une commande
    sql = """
    SELECT COUNT(*) as count FROM commande 
    WHERE (adresse_livraison_id = %s OR adresse_facturation_id = %s)
    """
    mycursor.execute(sql, (id_adresse, id_adresse))
    order_count = mycursor.fetchone()['count']
    
    # Si l'adresse est favorite, il faudra trouver une nouvelle adresse favorite
    is_favorite = adresse['est_favori']
    
    if order_count > 0:
        # L'adresse est utilisée dans une commande, la marquer comme non valide
        sql = "UPDATE adresse SET est_valide = 0 WHERE id_adresse = %s"
        mycursor.execute(sql, (id_adresse,))
        flash(u'L\'adresse a été marquée comme non valide car elle est utilisée dans des commandes.', 'alert-warning')
    else:
        # L'adresse n'est pas utilisée, la supprimer physiquement
        sql = "DELETE FROM adresse WHERE id_adresse = %s"
        mycursor.execute(sql, (id_adresse,))
        flash(u'L\'adresse a été supprimée.', 'alert-success')
    
    # Si l'adresse supprimée était la favorite, désigner une nouvelle adresse favorite
    if is_favorite:
        # Chercher l'adresse la plus récemment utilisée qui est valide
        sql = """
        SELECT id_adresse FROM adresse 
        WHERE utilisateur_id = %s AND id_adresse != %s AND est_valide = 1
        ORDER BY date_utilisation DESC 
        LIMIT 1
        """
        mycursor.execute(sql, (id_client, id_adresse))
        new_favorite = mycursor.fetchone()
        
        if new_favorite:
            # Définir cette adresse comme la nouvelle favorite
            sql = "UPDATE adresse SET est_favori = 1 WHERE id_adresse = %s"
            mycursor.execute(sql, (new_favorite['id_adresse'],))
            flash(u'Une nouvelle adresse favorite a été désignée.', 'alert-info')
    
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
    
    # Vérifier le format du code postal (5 chiffres)
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash(u'Le code postal doit être composé de 5 chiffres', 'alert-warning')
        return render_template('client/coordonnee/add_adresse.html',
                               utilisateur=session,
                               nom=nom,
                               rue=rue,
                               code_postal=code_postal,
                               ville=ville)
    
    # Vérifier le nombre maximum d'adresses valides (4)
    sql = "SELECT COUNT(*) as count FROM adresse WHERE utilisateur_id = %s AND est_valide = 1"
    mycursor.execute(sql, (id_client,))
    valid_address_count = mycursor.fetchone()['count']
    
    if valid_address_count >= 4:
        flash(u'Vous avez déjà atteint le nombre maximum d\'adresses valides (4)', 'alert-warning')
        return redirect('/client/coordonnee/show')
    
    # Toute nouvelle adresse devient automatiquement l'adresse favorite
    # Mettre toutes les autres adresses comme non favorites
    sql = "UPDATE adresse SET est_favori = 0 WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    
    # Insérer la nouvelle adresse
    sql = """
    INSERT INTO adresse (nom, rue, code_postal, ville, utilisateur_id, est_favori, date_utilisation, est_valide)
    VALUES (%s, %s, %s, %s, %s, 1, NOW(), 1)
    """
    mycursor.execute(sql, (nom, rue, code_postal, ville, id_client))
    get_db().commit()
    
    flash(u'Adresse ajoutée et définie comme favorite.', 'alert-success')
    
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
    
    # Vérifier le format du code postal (5 chiffres)
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash(u'Le code postal doit être composé de 5 chiffres', 'alert-warning')
        
        # Récupérer l'adresse initiale
        sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s"
        mycursor.execute(sql, (id_adresse, id_client))
        adresse = mycursor.fetchone()
        
        # Récupérer les informations de l'utilisateur
        sql = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
        mycursor.execute(sql, (id_client,))
        utilisateur = mycursor.fetchone()
        
        return render_template('client/coordonnee/edit_adresse.html',
                           utilisateur=utilisateur,
                           adresse={
                               'id_adresse': id_adresse,
                               'nom': nom, 
                               'rue': rue, 
                               'code_postal': code_postal, 
                               'ville': ville,
                               'est_favori': adresse['est_favori']
                           })
    
    # Vérifier que l'adresse appartient bien à l'utilisateur
    sql = "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s"
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()
    
    if not adresse:
        flash(u'Cette adresse ne vous appartient pas ou n\'existe pas.', 'alert-warning')
        return redirect('/client/coordonnee/show')
    
    # Vérifier si l'adresse est utilisée dans une commande
    sql = """
    SELECT COUNT(*) as count FROM commande 
    WHERE (adresse_livraison_id = %s OR adresse_facturation_id = %s)
    """
    mycursor.execute(sql, (id_adresse, id_adresse))
    order_count = mycursor.fetchone()['count']
    
    # Vérifier le nombre d'adresses valides si on doit créer une nouvelle adresse
    if order_count > 0:
        sql = "SELECT COUNT(*) as count FROM adresse WHERE utilisateur_id = %s AND est_valide = 1"
        mycursor.execute(sql, (id_client,))
        address_count = mycursor.fetchone()['count']
        
        if address_count >= 4:
            flash(u'Vous avez déjà atteint le nombre maximum d\'adresses valides (4)', 'alert-warning')
            return redirect('/client/coordonnee/show')
    
    # L'adresse modifiée devient automatiquement l'adresse favorite
    # Mettre toutes les autres adresses comme non favorites
    sql = "UPDATE adresse SET est_favori = 0 WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    
    # Si l'adresse n'est pas utilisée dans une commande, la mettre à jour directement
    if order_count == 0:
        sql = """
        UPDATE adresse
        SET nom = %s, rue = %s, code_postal = %s, ville = %s, date_utilisation = NOW(), est_favori = 1
        WHERE id_adresse = %s
        """
        mycursor.execute(sql, (nom, rue, code_postal, ville, id_adresse))
        flash(u'Adresse mise à jour avec succès et définie comme favorite.', 'alert-success')
    else:
        # L'adresse est utilisée dans une commande, on crée une nouvelle adresse et on marque l'ancienne comme non valide
        
        # Marquer l'ancienne adresse comme non valide
        sql = "UPDATE adresse SET est_valide = 0 WHERE id_adresse = %s"
        mycursor.execute(sql, (id_adresse,))
        
        # Créer une nouvelle adresse avec les nouvelles informations
        sql = """
        INSERT INTO adresse (nom, rue, code_postal, ville, utilisateur_id, est_favori, date_utilisation, est_valide)
        VALUES (%s, %s, %s, %s, %s, 1, NOW(), 1)
        """
        mycursor.execute(sql, (nom, rue, code_postal, ville, id_client))
        
        flash(u'Une nouvelle adresse a été créée et définie comme favorite car l\'ancienne était utilisée dans des commandes.', 'alert-info')
    
    get_db().commit()
    return redirect('/client/coordonnee/show')
