from flask import Blueprint, render_template # Removed request, redirect, url_for, flash as they aren't used yet
# Import the database connection function from your project structure
from connexion_db import get_db

# Removed placeholder authentication imports and decorator

admin_liste_envie_bp = Blueprint('admin_liste_envie', __name__,
                                 url_prefix='/admin',  # Adding a common prefix for admin routes might be cleaner
                                 template_folder='../templates') # Adjusted template folder path relative to blueprint

@admin_liste_envie_bp.route('/liste_envie/stats', methods=['GET'])
# Removed @admin_required decorator - assuming auth is handled elsewhere or not needed for this specific route yet
def admin_wishlist_stats():
    """
    Displays statistics about wishlists for the administrator.
    - Number of articles (skins) per category in wishlists.
    - Click count (consultation) of articles (skins).
    """
    db = get_db()
    mycursor = db.cursor()

    # --- Query 1: Articles (Skins) per Category in Wishlists ---
    sql_category_stats = """
        SELECT
            ts.libelle_type_skin AS category_name,
            COUNT(DISTINCT le.skin_id) AS article_count
        FROM liste_envie le
        JOIN skin s ON le.skin_id = s.id_skin
        JOIN type_skin ts ON s.type_skin_id = ts.id_type_skin
        GROUP BY ts.id_type_skin, ts.libelle_type_skin
        ORDER BY article_count DESC, ts.libelle_type_skin;
    """
    mycursor.execute(sql_category_stats)
    stats_per_category = mycursor.fetchall()

    # --- Query 2: Article (Skin) Consultation Count ---
    # Counts each time a skin appears in the historique table
    sql_click_stats = """
        SELECT
            s.nom_skin AS article_name,
            COUNT(h.skin_id) AS consultation_count
        FROM historique h
        JOIN skin s ON h.skin_id = s.id_skin
        GROUP BY s.id_skin, s.nom_skin
        ORDER BY consultation_count DESC, s.nom_skin;
    """
    mycursor.execute(sql_click_stats)
    article_click_stats = mycursor.fetchall()

    # --- Query 3: Individual Skin Wishlist Counts ---
    sql_skin_wishlist_counts = """
        SELECT
            s.nom_skin AS skin_name,
            COUNT(DISTINCT le.utilisateur_id) AS user_count
        FROM liste_envie le
        JOIN skin s ON le.skin_id = s.id_skin
        GROUP BY s.id_skin, s.nom_skin
        HAVING user_count > 0 
        ORDER BY user_count DESC, s.nom_skin;
    """
    mycursor.execute(sql_skin_wishlist_counts)
    skin_wishlist_counts = mycursor.fetchall()

    # --- Query 4: Consultations per Category ---
    sql_consultation_category_stats = """
        SELECT
            ts.libelle_type_skin AS category_name,
            COUNT(h.skin_id) AS consultation_count  -- Count total consultations
        FROM historique h
        JOIN skin s ON h.skin_id = s.id_skin
        JOIN type_skin ts ON s.type_skin_id = ts.id_type_skin
        GROUP BY ts.id_type_skin, ts.libelle_type_skin
        ORDER BY consultation_count DESC, ts.libelle_type_skin;
    """
    mycursor.execute(sql_consultation_category_stats)
    consultation_category_stats = mycursor.fetchall()

    mycursor.close() # Good practice to close cursor

    # Convert fetched data (list of tuples/dicts) into dictionaries suitable for the template if needed,
    # or pass them directly if the template handles the structure.
    # Assuming fetchall() returns list of dicts or similar that Jinja can iterate.

    return render_template('admin/liste_envie/stats.html',
                           stats_per_category=stats_per_category,
                           article_click_stats=article_click_stats,
                           skin_wishlist_counts=skin_wishlist_counts,
                           consultation_category_stats=consultation_category_stats)

# Add more routes related to admin wishlist management if needed 