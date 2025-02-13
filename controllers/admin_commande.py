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
    admin_id = session['id_user']
    sql = '''
        SELECT 
            commande.id_commande,
            commande.date_achat,
            etat.libelle_etat as libelle,
            etat.id_etat as etat_id,
            COUNT(ligne_commande.commande_id) as nbr_articles,
            SUM(ligne_commande.prix * ligne_commande.quantite) as prix_total,
            utilisateur.login
        FROM commande
        INNER JOIN etat ON commande.etat_id = etat.id_etat
        LEFT JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
        INNER JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
        GROUP BY commande.id_commande, commande.date_achat, etat.libelle_etat, etat.id_etat, utilisateur.login
        ORDER BY commande.date_achat DESC
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
                usure.libelle_usure,
                type_skin.libelle_type_skin,
                special.libelle_special,
                commande.etat_id,
                commande.id_commande as id
            FROM ligne_commande
            INNER JOIN skin ON ligne_commande.skin_id = skin.id_skin
            INNER JOIN usure ON skin.usure_id = usure.id_usure
            INNER JOIN type_skin ON skin.type_skin_id = type_skin.id_type_skin
            INNER JOIN special ON skin.special_id = special.id_special
            INNER JOIN commande ON ligne_commande.commande_id = commande.id_commande
            WHERE ligne_commande.commande_id = %s
        '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()
        commande_adresses = []
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
        sql = 'UPDATE commande SET etat_id = 2 WHERE id_commande = %s'
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')
