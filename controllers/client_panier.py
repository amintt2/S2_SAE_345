#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session
 
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


# --- Refactored Helper Functions for Declinaison Stock ---

def _get_declinaison_stock(declinaison_id):
    """Fetches the current stock for a specific declinaison."""
    mycursor = get_db().cursor()
    sql = 'SELECT stock FROM declinaison WHERE id_declinaison = %s'
    mycursor.execute(sql, (declinaison_id,))
    result = mycursor.fetchone()
    return result['stock'] if result else 0

def _update_declinaison_stock(declinaison_id, quantity_change):
    """Updates the stock for a specific declinaison. Use negative quantity_change to decrease stock."""
    mycursor = get_db().cursor()
    sql = '''
        UPDATE declinaison
        SET stock = stock + %s
        WHERE id_declinaison = %s
    '''
    mycursor.execute(sql, (quantity_change, declinaison_id))
    # Note: We might want to add checks here to prevent stock going below zero
    # if the database doesn't enforce it.

def _decrease_declinaison_stock(declinaison_id, quantity_to_remove):
    """Decreases stock for a declinaison, ensuring stock doesn't go below zero. 
       Returns the actual quantity removed (might be less than requested if stock is low)."""
    current_stock = _get_declinaison_stock(declinaison_id)
    actual_quantity_to_remove = min(quantity_to_remove, current_stock)
    
    if actual_quantity_to_remove > 0:
        _update_declinaison_stock(declinaison_id, -actual_quantity_to_remove)
        
    return actual_quantity_to_remove

def _restore_declinaison_stock(declinaison_id, quantity_to_add):
    """Increases stock for a declinaison (e.g., when removing from cart)."""
    # Simple addition, assumes stock can increase indefinitely for now
    _update_declinaison_stock(declinaison_id, quantity_to_add)

# --- End Refactored Helpers ---

@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    declinaison_id = request.form.get('declinaison_id')

    if not declinaison_id:
        flash('Veuillez sélectionner une version de l\'article.', 'alert-warning')
        return redirect('/client/article/show')

    try:
        declinaison_id = int(declinaison_id)
    except ValueError:
        flash(u'ID de version invalide.', 'alert-danger')
        return redirect('/client/article/show')

    # Check stock for the selected declinaison
    sql_check_stock = 'SELECT stock FROM declinaison WHERE id_declinaison = %s'
    mycursor.execute(sql_check_stock, (declinaison_id,))
    declinaison_data = mycursor.fetchone()

    if not declinaison_data:
        flash(u'Version de l\'article non trouvée.', 'alert-danger')
        return redirect('/client/article/show')

    if declinaison_data['stock'] <= 0:
        flash(u'Cette version de l\'article est en rupture de stock.', 'alert-warning')
        return redirect('/client/article/show')

    # Check if this specific declinaison is already in the cart
    sql_check_cart = '''
        SELECT quantite 
        FROM ligne_panier 
        WHERE utilisateur_id = %s AND declinaison_id = %s
    '''
    mycursor.execute(sql_check_cart, (id_client, declinaison_id))
    ligne_panier = mycursor.fetchone()

    quantity_to_add = 1 # Add one item at a time for now

    if ligne_panier:
        # Check if adding one more exceeds stock
        if ligne_panier['quantite'] + quantity_to_add > declinaison_data['stock']:
            flash(u'Quantité demandée supérieure au stock disponible.', 'alert-warning')
            return redirect('/client/article/show')
        
        # Update quantity in cart
        sql_update = '''
            UPDATE ligne_panier 
            SET quantite = quantite + %s 
            WHERE utilisateur_id = %s AND declinaison_id = %s
        '''
        mycursor.execute(sql_update, (quantity_to_add, id_client, declinaison_id))
    else:
        # Insert new line into cart
        sql_insert = '''
            INSERT INTO ligne_panier(utilisateur_id, declinaison_id, quantite, date_ajout) 
            VALUES (%s, %s, %s, NOW())
        '''
        mycursor.execute(sql_insert, (id_client, declinaison_id, quantity_to_add))

    # Decrease stock
    actual_removed = _decrease_declinaison_stock(declinaison_id, quantity_to_add)
    if actual_removed < quantity_to_add:
         flash(u'Attention: Stock ajusté car insuffisant.', 'alert-warning') # Should not happen due to checks above, but good fallback

    get_db().commit()
    flash(u'Article ajouté au panier', 'alert-success')
    return redirect('/client/article/show')


@client_panier.route('/client/panier/update', methods=['POST'])
def client_panier_update():
    id_client = session['id_user']
    # Use declinaison_id from form  
    declinaison_id = request.form.get('declinaison_id')
    
    try:
        new_quantity = int(request.form.get('quantite', 1))
        declinaison_id = int(declinaison_id)
        if new_quantity < 0: # Cannot have negative quantity
            raise ValueError("Quantity cannot be negative")
    except (ValueError, TypeError):
        flash(u'ID de version ou quantité invalide.', 'alert-danger')
        return redirect('/client/article/show')

    mycursor = get_db().cursor()

    # Get current quantity in cart
    sql_get_cart = '''
        SELECT quantite 
        FROM ligne_panier 
        WHERE declinaison_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql_get_cart, (declinaison_id, id_client))
    cart_item = mycursor.fetchone()

    if not cart_item:
        flash(u'Article non trouvé dans le panier.', 'alert-warning')
        return redirect('/client/article/show')
    
    current_quantity_in_cart = cart_item['quantite']
    quantity_diff = new_quantity - current_quantity_in_cart

    if quantity_diff == 0:
        return redirect('/client/article/show') # No change needed

    if new_quantity == 0:
        # If new quantity is 0, effectively delete the line
        _restore_declinaison_stock(declinaison_id, current_quantity_in_cart)
        sql_delete = '''
            DELETE FROM ligne_panier 
            WHERE declinaison_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql_delete, (declinaison_id, id_client))
    elif quantity_diff > 0:
        # Increase quantity: Check stock and decrease it
        actual_removed = _decrease_declinaison_stock(declinaison_id, quantity_diff)
        if actual_removed < quantity_diff:
            message = f'Stock insuffisant. {actual_removed} article(s) ajouté(s) au lieu de {quantity_diff}.'
            flash(message, 'alert-warning')
            # Adjust the quantity to update in the cart based on actual stock removed
            quantity_to_update = current_quantity_in_cart + actual_removed
        else:
            quantity_to_update = new_quantity

        sql_update = '''
            UPDATE ligne_panier 
            SET quantite = %s 
            WHERE declinaison_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql_update, (quantity_to_update, declinaison_id, id_client))
        
    elif quantity_diff < 0:
        # Decrease quantity: Restore stock and update cart
        quantity_to_restore = abs(quantity_diff)
        _restore_declinaison_stock(declinaison_id, quantity_to_restore)
        
        sql_update = '''
            UPDATE ligne_panier 
            SET quantite = %s 
            WHERE declinaison_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql_update, (new_quantity, declinaison_id, id_client))

    get_db().commit()
    return redirect('/client/article/show')
    

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article','')
    quantite = int(request.form.get('quantite', 1))

    # ---------
    # partie 2 : on supprime une déclinaison de l'article
    id_declinaison_article = request.form.get('id_declinaison_article', None)


    _delete_article_from_panier(quantite, id_article)
 
    return redirect('/client/article/show')


# Refactored helper to delete a line and restore stock
def _delete_line_and_restore_stock(declinaison_id, utilisateur_id):
    mycursor = get_db().cursor()
    # First, find the quantity in the cart to restore stock
    sql_get_qty = '''
        SELECT quantite 
        FROM ligne_panier 
        WHERE declinaison_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql_get_qty, (declinaison_id, utilisateur_id))
    cart_item = mycursor.fetchone()

    if cart_item:
        quantity_to_restore = cart_item['quantite']
        
        # Delete the line
        sql_delete = '''
            DELETE FROM ligne_panier 
            WHERE declinaison_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql_delete, (declinaison_id, utilisateur_id))

        # Restore the stock for the specific declinaison
        _restore_declinaison_stock(declinaison_id, quantity_to_restore)
        
        return True # Indicate success
    return False # Indicate item not found


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    # Fetch declinaison_id and quantity from the cart
    sql = ''' 
        SELECT declinaison_id, quantite 
        FROM ligne_panier
        WHERE utilisateur_id = %s
    '''
    mycursor.execute(sql, (client_id,))
    items_panier = mycursor.fetchall()
    
    if items_panier:
        for item in items_panier:
            # Use the helper to delete line and restore stock
            _delete_line_and_restore_stock(item['declinaison_id'], client_id)
        get_db().commit() # Commit once after processing all items
        flash(u'Panier vidé.', 'alert-success')
    else:
        flash(u'Le panier est déjà vide.', 'alert-info')
        
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    id_client = session['id_user']
    # Use declinaison_id from form
    declinaison_id = request.form.get('declinaison_id')

    try:
        declinaison_id = int(declinaison_id)
    except (ValueError, TypeError):
        flash(u'ID de version invalide.', 'alert-danger')
        return redirect('/client/article/show')

    # Use the helper function to delete the line and restore stock
    deleted = _delete_line_and_restore_stock(declinaison_id, id_client)

    if deleted:
        get_db().commit()
        flash(u'Article supprimé du panier.', 'alert-success')
    else:
        flash(u'Article non trouvé dans le panier.', 'alert-warning')

    return redirect('/client/article/show')

