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
          ('STICKERBOX'), 
          ('AWP');
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
          ('StatTrak'), 
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
          ('AK-47 | Inheritance', 180.50, 3, 1, 1, 1, 'FN_AK_INHERITANCE.png'),
          ('AK-47 | Inheritance', 80.00, 3, 1, 5, 1, 'BS_AK_INHERITANCE.png'),
          ('AWP | Gungnir', 11200.00, 1, 1, 1, 4, 'FN_GUNGNIR.png'),
          ('Sticker | iBUYPOWER (Holo) | Katowice 2014', 75000.00, 1, 1, 1, 2, 'IBUYPOWER-HOLO.png'),
          ('Sticker | Titan (Holo) | Katowice 2014', 55000.00, 1, 1, 1, 2, 'TITAN-HOLO.png'),
          ('Katowice 2014 Challengers', 24000.00, 2, 1, 1, 3, 'KATOWICE-CHALLENGERS.png');
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
