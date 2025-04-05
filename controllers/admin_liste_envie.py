from flask import Blueprint, render_template, request
from connexion_db import get_db

admin_liste_envie_bp = Blueprint('admin_liste_envie', __name__,
                                 url_prefix='/admin',
                                 template_folder='../templates')

@admin_liste_envie_bp.route('/liste_envie/stats', methods=['GET'])
def admin_wishlist_stats():
    db = get_db()
    mycursor = db.cursor()

    selected_category = request.args.get('category', None)

    # Statistiques globales des articles par catégorie dans les wishlists
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
    wishlist_cat_labels_py = [item['category_name'] for item in stats_per_category]
    wishlist_cat_values_py = [item['article_count'] for item in stats_per_category]

    # Nombre total de consultations par article
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

    # Nombre d'utilisateurs ayant ajouté chaque skin en wishlist
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

    # Statistiques de consultation par catégorie (total)
    sql_consultation_category_stats = """
        SELECT
            ts.libelle_type_skin AS category_name,
            COUNT(h.skin_id) AS consultation_count
        FROM historique h
        JOIN skin s ON h.skin_id = s.id_skin
        JOIN type_skin ts ON s.type_skin_id = ts.id_type_skin
        GROUP BY ts.id_type_skin, ts.libelle_type_skin
        ORDER BY consultation_count DESC, ts.libelle_type_skin;
    """
    mycursor.execute(sql_consultation_category_stats)
    consultation_category_stats = mycursor.fetchall()

    # Statistiques de consultation par catégorie (30 derniers jours)
    sql_consultation_category_monthly_stats = """
        SELECT
            ts.libelle_type_skin AS category_name,
            COUNT(h.skin_id) AS consultation_count
        FROM historique h
        JOIN skin s ON h.skin_id = s.id_skin
        JOIN type_skin ts ON s.type_skin_id = ts.id_type_skin
        WHERE h.date_consultation >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY ts.id_type_skin, ts.libelle_type_skin
        ORDER BY consultation_count DESC, ts.libelle_type_skin;
    """
    mycursor.execute(sql_consultation_category_monthly_stats)
    consultation_category_monthly_stats = mycursor.fetchall()
    history_cat_monthly_labels_py = [item['category_name'] for item in consultation_category_monthly_stats]
    history_cat_monthly_values_py = [item['consultation_count'] for item in consultation_category_monthly_stats]

    if selected_category:
        # Détails des articles en wishlist et consultations pour la catégorie sélectionnée (30 derniers jours)
        sql_category_articles = """
            SELECT 
                s.nom_skin AS article_name,
                COUNT(DISTINCT le.utilisateur_id) AS wishlist_count,
                COUNT(h.skin_id) AS consultation_count
            FROM skin s
            LEFT JOIN liste_envie le ON s.id_skin = le.skin_id
            LEFT JOIN historique h ON s.id_skin = h.skin_id 
                AND h.date_consultation >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            JOIN type_skin ts ON s.type_skin_id = ts.id_type_skin
            WHERE ts.libelle_type_skin = %s
            GROUP BY s.id_skin, s.nom_skin
            ORDER BY wishlist_count DESC, s.nom_skin;
        """
        mycursor.execute(sql_category_articles, (selected_category,))
        category_articles = mycursor.fetchall()

        category_articles_labels = [item['article_name'] for item in category_articles]
        category_wishlist_values = [item['wishlist_count'] for item in category_articles]
        category_history_values = [item['consultation_count'] for item in category_articles]
    else:
        category_articles = []
        category_articles_labels = []
        category_wishlist_values = []
        category_history_values = []

    mycursor.close()

    return render_template('admin/liste_envie/stats.html',
                           stats_per_category=stats_per_category,
                           article_click_stats=article_click_stats,
                           skin_wishlist_counts=skin_wishlist_counts,
                           consultation_category_stats=consultation_category_stats,
                           wishlist_cat_labels_py=wishlist_cat_labels_py,
                           wishlist_cat_values_py=wishlist_cat_values_py,
                           history_cat_monthly_labels_py=history_cat_monthly_labels_py,
                           history_cat_monthly_values_py=history_cat_monthly_values_py,
                           selected_category=selected_category,
                           category_articles_wishlist=category_articles,
                           category_articles_history=category_articles,
                           category_articles_labels=category_articles_labels,
                           category_wishlist_values=category_wishlist_values,
                           category_history_values=category_history_values)

# Add more routes related to admin wishlist management if needed 