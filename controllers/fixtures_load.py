#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                        template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
     mycursor = get_db().cursor()
     mycursor.execute("DROP TABLE IF EXISTS ligne_panier")
     mycursor.execute("DROP TABLE IF EXISTS ligne_commande")
     mycursor.execute("DROP TABLE IF EXISTS commande")
     mycursor.execute("DROP TABLE IF EXISTS skin")
     mycursor.execute("DROP TABLE IF EXISTS type_skin")
     mycursor.execute("DROP TABLE IF EXISTS usure")
     mycursor.execute("DROP TABLE IF EXISTS special")
     mycursor.execute("DROP TABLE IF EXISTS etat")
     mycursor.execute("DROP TABLE IF EXISTS utilisateur")

     sql='''
     CREATE TABLE utilisateur(
          id_utilisateur INT AUTO_INCREMENT,
          login VARCHAR(255),
          email VARCHAR(255),
          nom VARCHAR(255), 
          password VARCHAR(255),
          role VARCHAR(50),
          est_actif TINYINT(1),
          PRIMARY KEY (id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE type_skin(
          id_type_skin INT AUTO_INCREMENT,
          libelle_type_skin VARCHAR(50),
          PRIMARY KEY(id_type_skin)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE usure(
          id_usure INT AUTO_INCREMENT,
          libelle_usure VARCHAR(50),
          PRIMARY KEY(id_usure)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE special(
          id_special INT AUTO_INCREMENT,
          libelle_special VARCHAR(50),
          PRIMARY KEY(id_special)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE etat(
          id_etat INT AUTO_INCREMENT,
          libelle_etat VARCHAR(50),
          PRIMARY KEY(id_etat)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE skin(
          id_skin INT AUTO_INCREMENT,
          nom_skin VARCHAR(50),
          prix_skin DECIMAL(10,2),
          stock INT,
          special_id INT NOT NULL,
          usure_id INT NOT NULL,
          type_skin_id INT NOT NULL,
          image VARCHAR(255),
          description TEXT,
          PRIMARY KEY(id_skin),
          FOREIGN KEY(special_id) REFERENCES special(id_special),
          FOREIGN KEY(usure_id) REFERENCES usure(id_usure),
          FOREIGN KEY(type_skin_id) REFERENCES type_skin(id_type_skin)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE commande(
          id_commande INT AUTO_INCREMENT,
          date_achat DATE,
          etat_id INT NOT NULL,
          utilisateur_id INT NOT NULL,
          PRIMARY KEY(id_commande),
          FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE ligne_commande(
          skin_id INT,
          commande_id INT,
          prix DECIMAL(10,2),
          quantite INT,
          PRIMARY KEY(skin_id, commande_id),
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
          FOREIGN KEY(commande_id) REFERENCES commande(id_commande)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     CREATE TABLE ligne_panier(
          skin_id INT,
          utilisateur_id INT,
          quantite INT,
          date_ajout DATETIME,
          PRIMARY KEY(skin_id, utilisateur_id),
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
     (1,'admin','admin@admin.fr',
          'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
          'ROLE_admin','admin','1'),
     (2,'client','client@client.fr',
          'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
          'ROLE_client','client','1'),
     (3,'client2','client2@client2.fr',
          'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
          'ROLE_client','client2','1');
     '''
     mycursor.execute(sql)
     
     
     sql='''
     INSERT INTO type_skin (libelle_type_skin) VALUES
     ('AK-47'),
     ('STICKER'),
     ('AWP'),
     ('KNIFE'),
     ('GLOVES'),
     ('M4A1-S');
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO usure (libelle_usure) VALUES
     ('Neuve'),
     ('Trés peu usée'),
     ('Testé sur le terrain'),
     ('Usée'),
     ('Marqué par les combats');
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO special (libelle_special) VALUES
     ('Normal'),
     ('StatTrak™'),
     ('Souvenir');
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO etat (libelle_etat) VALUES
     ('En cours'),
     ('Validée'),
     ('Expédiée'),
     ('Livrée'),
     ('Annulée');
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO skin (nom_skin, prix_skin, stock, special_id, usure_id, type_skin_id, image, description) VALUES
     ('Karambit | Gamma Doppler', 1005.34, 2, 2, 1, 4, 'karambit_gamma_doppler.png', 'Un couteau hypnotisant avec des couleurs changeantes de vert et noir dans un motif galactique.'),
     ('AWP | Dragon Lore', 11244.54, 1, 1, 1, 3, 'awp_dragon_lore.png', 'Le légendaire skin Dragon Lore avec un design complexe de dragon doré.'),
     ('Sport Gloves | Amphibious', 897.35, 3, 2, 2, 5, 'gloves_amphibious.png', 'Gants de sport élégants avec un motif aquatique bleu et vert.'),
     ('Skeleton Knife | Crimson Web', 490.76, 2, 2, 2, 4, 'skeleton_crimson.png', 'Un couteau menaçant avec un motif de toile cramoisie.'),
     ('AK-47 | Gold Arabesque', 4023.26, 0, 2, 1, 1, 'ak_gold_arabesque.png', 'Un AK-47 doré avec des motifs arabesques complexes.'),
     ('Butterfly Knife | Marble Fade', 2083.06, 2, 2, 1, 4, 'butterfly_marble.png', 'Un couteau papillon avec un effet dégradé marbré.'),
     ('Driver Gloves | Snow Leopard', 83.90, 4, 1, 5, 5, 'gloves_snow_leopard.png', 'Gants avec un imprimé léopard des neiges.'),
     ('M4A1-S | Knight', 2959.66, 1, 1, 1, 6, 'm4a1s_knight.png', 'Un M4A1-S sur le thème des chevaliers avec des détails complexes.'),
     ('M9 Bayonet | Doppler', 1262.63, 2, 2, 1, 4, 'm9_doppler.png', 'Une baïonnette avec un effet Doppler.'),
     ('AWP | Lightning Strike', 74.32, 3, 2, 1, 3, 'awp_lightning_st.png', 'Un AWP avec un effet éclair.'),
     ('AK-47 | Inheritance', 180.50, 3, 1, 1, 1, 'FN_AK_INHERITANCE.png', 'Un AK-47 spécial sur le thème de l''héritage.'),
     ('AWP | Gungnir', 11200.00, 1, 1, 1, 3, 'FN_GUNGNIR.png', 'Un AWP puissant avec un thème nordique.'),
     ('Sticker | iBUYPOWER (Holo) | Katowice 2014', 75000.00, 1, 1, 1, 2, 'IBUYPOWER-HOLO.png', 'Un autocollant holographique iBUYPOWER de Katowice 2014.'),
     ('Sticker | Titan (Holo) | Katowice 2014', 55000.00, 1, 1, 1, 2, 'TITAN-HOLO.png', 'Un autocollant holographique Titan de Katowice 2014.'),
     ('Karambit | Crimson Web', 433.53, 2, 1, 2, 4, 'karambit_crimson_web.png', 'Un couteau menaçant avec un motif de toile cramoisie.'),
     ('AWP | Wildfire', 47.93, 4, 1, 3, 3, 'awp_wildfire.png', 'Un AWP avec un effet de feu sauvage.'),
     ('Flip Knife | Bright Water', 206.29, 3, 1, 1, 4, 'flip_bright_water.png', 'Un couteau flip avec un effet d''eau claire.'),
     ('Bowie Knife | Autotronic', 147.36, 2, 1, 3, 4, 'bowie_autotronic.png', 'Un couteau Bowie avec un thème autotronique.'),
     ('Huntsman Knife | Gamma Doppler', 378.27, 1, 1, 1, 4, 'huntsman_gamma_doppler.png', 'Un couteau Huntsman avec un effet Gamma Doppler.'),
     ('Navaja Knife | Rust Coat', 93.19, 3, 1, 5, 4, 'navaja_rust.png', 'Un couteau navaja avec un effet rouillé.'),
     ('Specialist Gloves | Fade', 343.02, 2, 1, 3, 5, 'specialist_fade.png', 'Gants avec un effet dégradé.'),
     ('Bowie Knife | Black Laminate', 113.87, 2, 1, 2, 4, 'bowie_black_laminate.png', 'Un couteau Bowie avec un motif laminé noir.'),
     ('Skeleton Knife | Fade', 1346.34, 0, 1, 1, 4, 'skeleton_fade.png', 'Un couteau squelette avec un effet dégradé.'),
     ('Flip Knife | Doppler', 453.49, 2, 1, 1, 4, 'flip_doppler.png', 'Un couteau flip avec un effet Doppler.'),
     ('M4A1-S | Mud-Spec', 0.15, 5, 1, 3, 6, 'm4a1s_mudspec.png', 'Un motif de camouflage basique dans des tons marron boueux.'),
     ('Natus Vincere Glitter', 0.15, 5, 1, 1, 2, 'sticker_navi_glitter.png', 'Un autocollant brillant de l''équipe Natus Vincere avec des effets holographiques.');
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO ligne_panier (skin_id, utilisateur_id, quantite, date_ajout) VALUES 
          (1, 2, 1, '2024-03-20 10:30:00');
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO commande (date_achat, etat_id, utilisateur_id) VALUES 
          ('2024-03-19', 2, 2);
     '''
     mycursor.execute(sql)
     
     sql='''
     INSERT INTO ligne_commande (skin_id, commande_id, prix, quantite) VALUES 
          (1, 1, 80.00, 1);
     '''
     mycursor.execute(sql)
     

     get_db().commit()
     return redirect('/')
