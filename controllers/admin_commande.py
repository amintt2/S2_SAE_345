#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    sql = '''
        SELECT 
            c.id_commande,
            c.date_achat,
            e.libelle_etat AS libelle,
            e.id_etat AS etat_id,
            SUM(lc.quantite) AS nbr_articles,
            SUM(lc.prix * lc.quantite) AS prix_total,
            utilisateur.login
        FROM commande AS c
        LEFT JOIN ligne_commande AS lc ON c.id_commande = lc.commande_id
        LEFT JOIN etat AS e ON c.etat_id = e.id_etat
        LEFT JOIN utilisateur ON c.utilisateur_id = utilisateur.id_utilisateur
        GROUP BY c.id_commande, c.date_achat, e.libelle_etat, e.id_etat, utilisateur.login
        ORDER BY e.id_etat ASC, c.date_achat DESC
    '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    print(id_commande)
    if id_commande != None:
        sql = '''
            SELECT 
                skin.nom_skin AS nom,
                skin.image,
                ligne_commande.quantite,
                ligne_commande.prix,
                (ligne_commande.prix * ligne_commande.quantite) AS prix_ligne,
                u.libelle_usure,
                ts.libelle_type_skin,
                sp.libelle_special,
                commande.etat_id,
                commande.id_commande as id
            FROM ligne_commande
            INNER JOIN declinaison d ON ligne_commande.declinaison_id = d.id_declinaison
            INNER JOIN skin ON d.skin_id = skin.id_skin
            INNER JOIN usure u ON d.usure_id = u.id_usure
            INNER JOIN type_skin ts ON skin.type_skin_id = ts.id_type_skin
            INNER JOIN special sp ON d.special_id = sp.id_special
            INNER JOIN commande ON ligne_commande.commande_id = commande.id_commande
            WHERE ligne_commande.commande_id = %s
            ORDER BY commande.etat_id
        '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql = '''
            SELECT 
                utilisateur.login,
                utilisateur.email,
                utilisateur.nom,
                adresse_livraison.id_adresse AS id_adresse_livraison,
                adresse_livraison.nom AS nom_livraison,
                adresse_livraison.rue AS rue_livraison,
                adresse_livraison.code_postal AS code_postal_livraison,
                adresse_livraison.ville AS ville_livraison,
                adresse_facturation.id_adresse AS id_adresse_facturation,
                adresse_facturation.nom AS nom_facturation,
                adresse_facturation.rue AS rue_facturation,
                adresse_facturation.code_postal AS code_postal_facturation,
                adresse_facturation.ville AS ville_facturation,
                CASE 
                    WHEN commande.adresse_livraison_id = commande.adresse_facturation_id 
                    THEN 'adresse_identique' 
                    ELSE 'adresse_differente' 
                END AS adresse_identique
            FROM commande
            INNER JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
            INNER JOIN adresse AS adresse_livraison ON commande.adresse_livraison_id = adresse_livraison.id_adresse
            INNER JOIN adresse AS adresse_facturation ON commande.adresse_facturation_id = adresse_facturation.id_adresse
            WHERE commande.id_commande = %s
        '''
        mycursor.execute(sql, (id_commande,))
        commande_adresses = mycursor.fetchone()

    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = '''
        UPDATE commande 
        SET etat_id = 2 
        WHERE id_commande = %s
        '''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')
