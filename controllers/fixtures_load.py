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
     ('GLOCK-17'),
     ('AWP'),
     ('AGENT'),
     ('CHARMS'),
     ('KNIFE'),
     ('GLOVES'),
     ('CASE'),
     ('MAC-10'),
     ('M4A1-S'),
     ('DESERT EAGLE'),
     ('MP7'),
     ('USP-S'),
     ('FIVE-SEVEN'),
     ('FAMAS'),
     ('UMP-45'),
     ('MAG-7'),
     ('SAWED-OFF');
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
     INSERT INTO skin (nom_skin, prix_skin, stock, special_id, usure_id, type_skin_id, image) VALUES
     ('Karambit | Gamma Doppler', 1005.34, 522, 2, 1, 7, 'karambit_gamma_doppler.png'),
     ('AWP | Dragon Lore', 11244.54, 917, 1, 1, 4, 'awp_dragon_lore.png'),
     ('Sport Gloves | Amphibious', 897.35, 636, 2, 2, 8, 'gloves_amphibious.png'),
     ('Skeleton Knife | Crimson Web', 490.76, 252, 2, 2, 7, 'skeleton_crimson.png'),
     ('AK-47 | Gold Arabesque', 4023.26, 497, 2, 1, 1, 'ak_gold_arabesque.png'),
     ('MAC-10 | Stalker', 61.95, 687, 2, 1, 10, 'mac10_stalker.png'),
     ('Butterfly Knife | Marble Fade', 2083.06, 574, 2, 1, 7, 'butterfly_marble.png'),
     ('Driver Gloves | Snow Leopard', 83.90, 777, 1, 5, 8, 'gloves_snow_leopard.png'),
     ('M4A1-S | Knight', 2959.66, 872, 1, 1, 11, 'm4a1s_knight.png'),
     ('Glock-18 | Fade', 1464.47, 337, 2, 1, 3, 'glock_fade.png'),
     ('M9 Bayonet | Doppler', 1262.63, 942, 2, 1, 7, 'm9_doppler.png'),
     ('AWP | Lightning Strike', 74.32, 244, 2, 1, 4, 'awp_lightning_st.png'),
     ('Glock-18 | Bullet Queen', 32.37, 253, 2, 1, 3, 'glock_bullet_queen.png'),
     ('Desert Eagle | Blaze', 433.59, 314, 1, 1, 12, 'deagle_blaze.png'),
     ('AK-47 | Inheritance', 180.50, 3, 1, 1, 1, 'FN_AK_INHERITANCE.png'),
     ('AWP | Gungnir', 11200.00, 1, 1, 1, 4, 'FN_GUNGNIR.png'),
     ('Sticker | iBUYPOWER (Holo) | Katowice 2014', 75000.00, 1, 1, 1, 2, 'IBUYPOWER-HOLO.png'),
     ('Sticker | Titan (Holo) | Katowice 2014', 55000.00, 1, 1, 1, 2, 'TITAN-HOLO.png'),
     ('Katowice 2014 Challengers', 24000.00, 2, 1, 1, 9, 'KATOWICE-CHALLENGERS.png'),
     ('Karambit | Crimson Web', 433.53, 791, 1, 2, 7, 'karambit_crimson_web.png'),
     ('MP7 | Bloodsport', 1.76, 583, 1, 2, 13, 'mp7_bloodsport.png'),
     ('USP-S | The Traitor', 10.93, 849, 1, 3, 14, 'usps_traitor.png'),
     ('Paracord Knife | Forest DDPAT', 101.60, 293, 1, 3, 7, 'paracord_forest.png'),
     ('AWP | Wildfire', 47.93, 268, 1, 3, 4, 'awp_wildfire.png'),
     ('Flip Knife | Bright Water', 206.29, 578, 1, 1, 7, 'flip_bright_water.png'),
     ('Bowie Knife | Autotronic', 147.36, 578, 1, 3, 7, 'bowie_autotronic.png'),
     ('Huntsman Knife | Gamma Doppler', 378.27, 245, 1, 1, 7, 'huntsman_gamma_doppler.png'),
     ('Navaja Knife | Rust Coat', 93.19, 301, 1, 5, 7, 'navaja_rust.png'),
     ('USP-S | Printstream', 29.08, 965, 1, 3, 14, 'usps_printstream.png'),
     ('Specialist Gloves | Fade', 343.02, 500, 1, 3, 8, 'specialist_fade.png'),
     ('Bowie Knife | Black Laminate', 113.87, 400, 1, 2, 7, 'bowie_black_laminate.png'),
     ('Skeleton Knife | Fade', 1346.34, 416, 1, 1, 7, 'skeleton_fade.png'),
     ('Flip Knife | Doppler', 453.49, 450, 1, 1, 7, 'flip_doppler.png'),
     ('Glock-18 | Gamma Doppler', 75.01, 792, 1, 1, 3, 'glock_gamma_doppler.png'),
     ('Desert Eagle | Mecha Industries', 8.47, 690, 1, 1, 12, 'deagle_mecha.png'),
     ('MAG-7 | Heat', 0.92, 950, 1, 2, 18, 'mag7_heat.png'),
     ('Cmdr. Mae Dead Cold Jamison', 8.02, 500, 1, 1, 5, 'agent_mae_jamison.png'),
     ('Sir Bloody Silent Darryl', 23.85, 400, 1, 1, 5, 'agent_darryl.png'),
     ('Five-SeveN | Monkey Business', 6.67, 300, 1, 3, 15, 'fiveseven_monkey.png'),
     ('FAMAS | Rapid Eye Movement', 0.93, 450, 1, 4, 16, 'famas_rapid_eye.png'),
     ('UMP-45 | Wild Child', 1.12, 500, 1, 4, 17, 'ump_wild_child.png'),
     ('MAG-7 | Monster Call', 1.74, 400, 1, 1, 18, 'mag7_monster.png'),
     ('Sawed-Off | Limelight', 0.81, 600, 1, 2, 19, 'sawedoff_limelight.png'),
     ('M4A1-S | Mud-Spec', 0.15, 115, 1, 3, 11, 'm4a1s_mudspec.png'),
     ('Rezan the Redshirt', 4.10, 300, 1, 1, 5, 'agent_rezan.png'),
     ('Lil SAS Charm', 23.74, 84, 1, 1, 6, 'charm_sas.png'),
     ('Kilowatt Case', 0.56, 1000, 1, 1, 9, 'case_kilowatt.png'),
     ('Recoil Case', 0.18, 1000, 1, 1, 9, 'case_recoil.png'),
     ('Natus Vincere Glitter', 0.15, 1000, 1, 1, 2, 'sticker_navi_glitter.png');
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
          (2, 1, 80.00, 1);
     '''
     mycursor.execute(sql)
     

     get_db().commit()
     return redirect('/')
