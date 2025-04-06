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

     # DROP TABLE
     sql='''
     DROP TABLE IF EXISTS ligne_panier;
     DROP TABLE IF EXISTS ligne_commande;
     DROP TABLE IF EXISTS commande;
     DROP TABLE IF EXISTS declinaison;
     DROP TABLE IF EXISTS commentaire;
     DROP TABLE IF EXISTS note;
     DROP TABLE IF EXISTS historique;
     DROP TABLE IF EXISTS liste_envie;
     DROP TABLE IF EXISTS adresse;
     DROP TABLE IF EXISTS skin;
     DROP TABLE IF EXISTS etat;
     DROP TABLE IF EXISTS special;
     DROP TABLE IF EXISTS usure;
     DROP TABLE IF EXISTS type_skin;
     DROP TABLE IF EXISTS utilisateur;
     '''
     mycursor.execute(sql)
     
     # CREATE TABLE
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

     CREATE TABLE type_skin(
     id_type_skin INT AUTO_INCREMENT,
     libelle_type_skin VARCHAR(50),
     PRIMARY KEY(id_type_skin)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE usure(
     id_usure INT AUTO_INCREMENT,
     libelle_usure VARCHAR(50),
     PRIMARY KEY(id_usure)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE special(
     id_special INT AUTO_INCREMENT,
     libelle_special VARCHAR(50),
     PRIMARY KEY(id_special)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE etat(
     id_etat INT AUTO_INCREMENT,
     libelle_etat VARCHAR(50),
     PRIMARY KEY(id_etat)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE skin(
     id_skin INT AUTO_INCREMENT,
     nom_skin VARCHAR(50),
     disponible TINYINT(1),
     type_skin_id INT NOT NULL,
     image VARCHAR(255),
     description TEXT,
     PRIMARY KEY(id_skin),
     CONSTRAINT fk_skin_type
          FOREIGN KEY(type_skin_id) REFERENCES type_skin(id_type_skin)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE adresse (
     id_adresse INT AUTO_INCREMENT,
     est_favori BOOLEAN DEFAULT FALSE,
     est_valide BOOLEAN DEFAULT TRUE,
     nom VARCHAR(255),
     rue VARCHAR(255),
     code_postal VARCHAR(255),
     ville VARCHAR(255),
     date_utilisation DATETIME,
     utilisateur_id INT NOT NULL,
     PRIMARY KEY(id_adresse),
     CONSTRAINT fk_adresse_utilisateur
          FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE commande(
     id_commande INT AUTO_INCREMENT,
     date_achat DATE,
     etat_id INT NOT NULL,
     utilisateur_id INT NOT NULL,
     adresse_livraison_id INT,
     adresse_facturation_id INT,
     PRIMARY KEY(id_commande),
     CONSTRAINT fk_commande_etat
          FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
     CONSTRAINT fk_commande_utilisateur
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
     CONSTRAINT fk_commande_adresse_livraison
          FOREIGN KEY(adresse_livraison_id) REFERENCES adresse(id_adresse),
     CONSTRAINT fk_commande_adresse_facturation
          FOREIGN KEY(adresse_facturation_id) REFERENCES adresse(id_adresse)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE liste_envie(
     skin_id INT NOT NULL,
     utilisateur_id INT NOT NULL, 
     date_update DATETIME,
     PRIMARY KEY(skin_id, utilisateur_id, date_update),
     CONSTRAINT fk_liste_envie_skin
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
     CONSTRAINT fk_liste_envie_utilisateur
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE historique(
     skin_id INT NOT NULL,
     utilisateur_id INT NOT NULL,
     date_consultation DATETIME,
     PRIMARY KEY(skin_id, utilisateur_id, date_consultation),
     CONSTRAINT fk_historique_skin
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
     CONSTRAINT fk_historique_utilisateur
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE note (
     utilisateur_id INT NOT NULL,
     skin_id INT NOT NULL,
     note INT,
     PRIMARY KEY(utilisateur_id, skin_id),
     CONSTRAINT fk_note_utilisateur
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
     CONSTRAINT fk_note_skin
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE commentaire (
     id_commentaire INT AUTO_INCREMENT,
     utilisateur_id INT NOT NULL,
     skin_id INT NOT NULL,
     date_publication DATETIME NOT NULL,
     commentaire TEXT,
     valide TINYINT(1),
     commentaire_id_parent INT,
     PRIMARY KEY(id_commentaire),
     UNIQUE(utilisateur_id, skin_id, date_publication),
     CONSTRAINT fk_commentaire_utilisateur
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
     CONSTRAINT fk_commentaire_skin
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
     CONSTRAINT fk_commentaire_commentaire
          FOREIGN KEY(commentaire_id_parent) REFERENCES commentaire(id_commentaire)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE declinaison (
     id_declinaison INT AUTO_INCREMENT,
     stock INT,
     prix_declinaison DECIMAL(10,2),
     image VARCHAR(255),
     special_id INT NOT NULL,
     usure_id INT NOT NULL,
     skin_id INT,
     PRIMARY KEY(id_declinaison),
     CONSTRAINT fk_declinaison_skin
          FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
     CONSTRAINT fk_declinaison_special
          FOREIGN KEY(special_id) REFERENCES special(id_special),
     CONSTRAINT fk_declinaison_usure
          FOREIGN KEY(usure_id) REFERENCES usure(id_usure)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE ligne_commande(
     declinaison_id INT NOT NULL,
     commande_id INT NOT NULL,
     prix DECIMAL(10,2),
     quantite INT,
     PRIMARY KEY(declinaison_id, commande_id),
     CONSTRAINT fk_ligne_commande_declinaison
          FOREIGN KEY(declinaison_id) REFERENCES declinaison(id_declinaison),
     CONSTRAINT fk_ligne_commande_commande
          FOREIGN KEY(commande_id) REFERENCES commande(id_commande)
     ) DEFAULT CHARSET utf8mb4;

     CREATE TABLE ligne_panier(
     declinaison_id INT NOT NULL,
     utilisateur_id INT NOT NULL,
     quantite INT,
     date_ajout DATETIME,
     PRIMARY KEY(declinaison_id, utilisateur_id),
     CONSTRAINT fk_ligne_panier_declinaison
          FOREIGN KEY(declinaison_id) REFERENCES declinaison(id_declinaison),
     CONSTRAINT fk_ligne_panier_utilisateur
          FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
     ) DEFAULT CHARSET utf8mb4;
     '''
     mycursor.execute(sql)
     
     # INSERT utilisateur
     sql='''
     INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
          (1,'admin','admin@admin.fr', 'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988', 'ROLE_admin','admin','1'),
          (2,'client','client@client.fr', 'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349', 'ROLE_client','client','1'),
          (3,'client2','client2@client2.fr', 'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080', 'ROLE_client','client2','1');

     INSERT INTO utilisateur (login, email, password, role, nom, est_actif) VALUES
          ('player1', 'player1@csgo.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh1$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1234', 'ROLE_client', 'John Doe', 1),
          ('player2', 'player2@csgo.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh2$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1235', 'ROLE_client', 'Jane Smith', 1),
          ('pro_gamer', 'pro@esports.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh3$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1236', 'ROLE_client', 'Alex Pro', 1),
          ('collector', 'rare@collector.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh4$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1237', 'ROLE_client', 'Thomas Knight', 1),
          ('pierre', 'pierre@skins.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh5$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1238', 'ROLE_client', 'pierre', 1),
          ('trader', 'trader@skins.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh6$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1239', 'ROLE_client', 'Michael Trader', 1),
          ('streamer', 'streamer@twitch.tv', 'pbkdf2:sha256:1000000$rAnD0mHaSh7$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1240', 'ROLE_client', 'Sarah Stream', 1),
          ('investor', 'investor@csmarket.com', 'pbkdf2:sha256:1000000$rAnD0mHaSh8$123456789abcdef123456789abcdef123456789abcdef123456789abcdef1241', 'ROLE_client', 'Robert Money', 1);

     '''
     mycursor.execute(sql)
     
     # INSERT en rapport avec les skins
     sql='''
     INSERT INTO type_skin (libelle_type_skin) VALUES
          ('AK-47'),
          ('STICKER'),
          ('AWP'),
          ('KNIFE'),
          ('GLOVES'),
          ('M4A1-S');

     INSERT INTO usure (libelle_usure) VALUES
          ('Neuve'),
          ('Trés peu usée'),
          ('Testé sur le terrain'),
          ('Usée'),
          ('Marqué par les combats');

     INSERT INTO special (libelle_special) VALUES
          ('Normal'),
          ('StatTrak™'),
          ('Souvenir');

     INSERT INTO etat (libelle_etat) VALUES
          ('En cours'),
          ('Validé'),
          ('Refusée');


     INSERT INTO skin (nom_skin, disponible, type_skin_id, image, description) VALUES
          ('Karambit | Gamma Doppler', 1, 5, 'karambit_gamma_doppler.png', 'A knife with a curved blade resembling a claw with a mesmerizing gamma doppler finish.'),
          ('AWP | Dragon Lore', 1, 3, 'awp_dragon_lore.png', 'The legendary AWP skin with golden dragon motifs.'),
          ('Sport Gloves | Amphibious', 1, 5, 'gloves_amphibious.png', 'Sport gloves with a blue and green amphibious design.'),
          ('Skeleton Knife | Crimson Web', 1, 4, 'skeleton_crimson.png', 'A skeleton knife with a crimson web pattern.'),
          ('AK-47 | Gold Arabesque', 1, 1, 'ak_gold_arabesque.png', 'AK-47 with intricate gold arabesque design.'),
          ('Butterfly Knife | Marble Fade', 1, 4, 'butterfly_marble.png', 'A butterfly knife with a colorful marble fade pattern.'),
          ('Driver Gloves | Snow Leopard', 1, 5, 'gloves_snow_leopard.png', 'Driver gloves with a snow leopard pattern.'),
          ('M4A1-S | Knight', 1, 6, 'm4a1s_knight.png', 'An elegant gold-themed M4A1-S skin.'),
          ('M9 Bayonet | Doppler', 1, 4, 'm9_doppler.png', 'An M9 Bayonet with an iridescent doppler finish.'),
          ('AWP | Lightning Strike', 1, 3, 'awp_lightning_st.png', 'An AWP skin featuring a lightning strike pattern.'),
          ('AK-47 | Inheritance', 1, 1, 'FN_AK_INHERITANCE.png', 'An AK-47 with intricate inheritance design.'),
          ('AWP | Gungnir', 1, 3, 'FN_GUNGNIR.png', 'A Nordic-themed AWP with blue and gold details.'),
          ('Sticker | iBUYPOWER (Holo) | Katowice 2014', 1, 2, 'IBUYPOWER-HOLO.png', 'An extremely rare holographic sticker from Katowice 2014.'),
          ('Sticker | Titan (Holo) | Katowice 2014', 1, 2, 'TITAN-HOLO.png', 'A valuable holographic Titan sticker from Katowice 2014.'),
          ('Karambit | Crimson Web', 1, 4, 'karambit_crimson_web.png', 'A karambit with a crimson web pattern.'),
          ('AWP | Wildfire', 1, 3, 'awp_wildfire.png', 'An AWP skin with fire-themed design.'),
          ('Flip Knife | Bright Water', 1, 4, 'flip_bright_water.png', 'A flip knife with a bright water pattern.'),
          ('Bowie Knife | Autotronic', 1, 4, 'bowie_autotronic.png', 'A bowie knife with an autotronic finish.'),
          ('Huntsman Knife | Gamma Doppler', 1, 4, 'huntsman_gamma_doppler.png', 'A huntsman knife with a gamma doppler finish.'),
          ('Navaja Knife | Rust Coat', 1, 4, 'navaja_rust.png', 'A navaja knife with a rust coat finish.'),
          ('Specialist Gloves | Fade', 1, 5, 'specialist_fade.png', 'Specialist gloves with a fade pattern.'),
          ('Bowie Knife | Black Laminate', 1, 4, 'bowie_black_laminate.png', 'A bowie knife with a black laminate finish.'),
          ('Skeleton Knife | Fade', 1, 4, 'skeleton_fade.png', 'A skeleton knife with a fade pattern.'),
          ('Flip Knife | Doppler', 1, 4, 'flip_doppler.png', 'A flip knife with a doppler finish.'),
          ('M4A1-S | Mud-Spec', 1, 6, 'm4a1s_mudspec.png', 'A common M4A1-S skin with a mud spec pattern.'),
          ('Natus Vincere Glitter', 1, 2, 'sticker_navi_glitter.png', 'A glitter sticker for Natus Vincere team.');


     INSERT INTO declinaison (stock, prix_declinaison, image, special_id, usure_id, skin_id) VALUES
          -- Karambit | Gamma Doppler variations
          (5, 1005.34, 'karambit_gamma_doppler.png', 2, 1, 1),
          (2, 905.34, 'karambit_gamma_doppler.png', 2, 2, 1),
          (4, 805.34, 'karambit_gamma_doppler.png', 2, 3, 1),

          -- AWP | Dragon Lore variations
          (2, 11244.54, 'awp_dragon_lore.png', 1, 1, 2),
          (3, 9244.54, 'awp_dragon_lore.png', 1, 2, 2),
          (5, 8244.54, 'awp_dragon_lore.png', 1, 3, 2),
          (0, 7244.54, 'awp_dragon_lore.png', 1, 4, 2),

          -- Sport Gloves | Amphibious
          (8, 897.35, 'gloves_amphibious.png', 2, 2, 3),

          -- Skeleton Knife | Crimson Web
          (3, 490.76, 'skeleton_crimson.png', 2, 2, 4),

          -- AK-47 | Gold Arabesque variations
          (1, 4023.26, 'ak_gold_arabesque.png', 2, 1, 5),
          (1, 3523.26, 'ak_gold_arabesque.png', 2, 2, 5),
          (7, 3023.26, 'ak_gold_arabesque.png', 2, 3, 5),

          -- Butterfly Knife | Marble Fade
          (4, 2083.06, 'butterfly_marble.png', 2, 1, 6),

          -- Driver Gloves | Snow Leopard
          (7, 83.90, 'gloves_snow_leopard.png', 1, 5, 7),

          -- M4A1-S | Knight variations
          (2, 2959.66, 'm4a1s_knight.png', 1, 1, 8),
          (6, 2459.66, 'm4a1s_knight.png', 1, 2, 8),
          (9, 1959.66, 'm4a1s_knight.png', 1, 3, 8),

          -- M9 Bayonet | Doppler
          (6, 1262.63, 'm9_doppler.png', 2, 1, 9),

          -- Other items - single variations for the rest
          (9, 74.32, 'awp_lightning_st.png', 2, 1, 10),
          (3, 180.50, 'FN_AK_INHERITANCE.png', 1, 1, 11),
          (1, 11200.00, 'FN_GUNGNIR.png', 1, 1, 12),
          (1, 75000.00, 'IBUYPOWER-HOLO.png', 1, 1, 13),
          (1, 55000.00, 'TITAN-HOLO.png', 1, 1, 14),
          (5, 433.53, 'karambit_crimson_web.png', 1, 2, 15),
          (8, 47.93, 'awp_wildfire.png', 1, 3, 16),
          (4, 206.29, 'flip_bright_water.png', 1, 1, 17),
          (6, 147.36, 'bowie_autotronic.png', 1, 3, 18),
          (2, 378.27, 'huntsman_gamma_doppler.png', 1, 1, 19),
          (7, 93.19, 'navaja_rust.png', 1, 5, 20),
          (5, 343.02, 'specialist_fade.png', 1, 3, 21),
          (3, 113.87, 'bowie_black_laminate.png', 1, 2, 22),
          (4, 1346.34, 'skeleton_fade.png', 1, 1, 23),
          (6, 453.49, 'flip_doppler.png', 1, 1, 24),
          (10, 0.15, 'm4a1s_mudspec.png', 1, 3, 25),
          (8, 0.15, 'sticker_navi_glitter.png', 1, 1, 26);
     '''
     mycursor.execute(sql)
     
     # INSERT en rapport avec les commandes
     sql='''
     INSERT INTO commande (date_achat, etat_id, utilisateur_id) VALUES 
          ('2024-03-19', 2, 2),
          ('2024-03-15', 2, 2),
          ('2024-03-18', 1, 3),
          ('2024-03-20', 1, 3),
          ('2024-03-10', 2, 2),
          ('2024-03-25', 2, 4),
          ('2024-03-26', 1, 5),
          ('2024-03-27', 3, 6),
          ('2024-03-28', 2, 7),
          ('2024-03-29', 2, 4),
          ('2024-03-30', 1, 8),
          ('2024-03-31', 2, 9),
          ('2024-04-01', 1, 10),
          ('2024-04-01', 3, 2),
          ('2024-04-02', 2, 3);

     INSERT INTO ligne_commande (declinaison_id, commande_id, prix, quantite) VALUES 
          (1, 1, 80.00, 1),
          (3, 1, 897.35, 2),
          (7, 2, 83.90, 1),
          (10, 2, 74.32, 3),
          (4, 3, 490.76, 1),
          (15, 3, 433.53, 2),
          (2, 4, 11244.54, 1),
          (5, 5, 4023.26, 1),
          (6, 6, 2083.06, 1),
          (8, 6, 2959.66, 1),
          (9, 7, 1262.63, 2),
          (11, 7, 180.50, 3),
          (12, 8, 11200.00, 1),
          (16, 8, 47.93, 5),
          (17, 9, 206.29, 2),
          (19, 9, 378.27, 1),
          (21, 10, 343.02, 2),
          (25, 10, 0.15, 10),
          (13, 11, 75000.00, 1),
          (14, 11, 55000.00, 1),
          (6, 12, 2083.06, 2),
          (9, 12, 1262.63, 1),
          (12, 13, 11200.00, 1),
          (5, 13, 4023.26, 1),
          (18, 14, 147.36, 3),
          (22, 14, 113.87, 2),
          (20, 15, 93.19, 4),
          (24, 15, 453.49, 1);

     INSERT INTO ligne_panier (declinaison_id, utilisateur_id, quantite, date_ajout) VALUES
          (1, 2, 1, '2024-03-20 10:30:00'),
          (2, 2, 4, '2023-06-24'),
          (2, 3, 3, '2023-06-24'),
          (3, 8, 2, '2024-04-02 09:15:00'),
          (7, 8, 1, '2024-04-02 09:30:00'),
          (5, 9, 1, '2024-04-02 14:45:00'),
          (11, 9, 3, '2024-04-02 15:00:00'),
          (9, 10, 1, '2024-04-03 10:20:00'),
          (15, 10, 2, '2024-04-03 10:35:00'),
          (8, 4, 1, '2024-03-25 09:45:00'),
          (12, 5, 1, '2024-03-26 14:15:00'),
          (17, 5, 2, '2024-03-26 14:30:00'),
          (20, 6, 1, '2024-03-27 11:20:00'),
          (21, 6, 1, '2024-03-27 11:35:00'),
          (23, 7, 1, '2024-03-28 16:10:00'),
          (24, 7, 2, '2024-03-28 16:25:00');
     '''
     mycursor.execute(sql)
     
     # INSERT en rapport avec les avis
     sql='''
     INSERT INTO note (utilisateur_id, skin_id, note) VALUES
          (2, 1, 5),
          (2, 2, 5),
          (2, 3, 4),
          (3, 1, 4),
          (3, 5, 5),
          (3, 9, 3),
          (4, 2, 5),
          (4, 12, 5),
          (4, 13, 5),
          (5, 6, 4),
          (5, 10, 3),
          (5, 16, 2),
          (6, 3, 5),
          (6, 7, 4),
          (6, 21, 5),
          (7, 4, 4),
          (7, 23, 5),
          (7, 24, 3),
          (8, 1, 4),
          (8, 5, 5),
          (8, 9, 3),
          (9, 2, 5),
          (9, 6, 5),
          (9, 10, 4),
          (9, 16, 3),
          (10, 3, 4),
          (10, 7, 3),
          (2, 6, 4),
          (2, 12, 4),
          (3, 3, 3),
          (3, 7, 4),
          (3, 11, 5),
          (4, 8, 4),
          (5, 1, 3),
          (5, 5, 2);

     INSERT INTO commentaire (utilisateur_id, skin_id, date_publication, commentaire, valide) VALUES
          (2, 1, '2024-03-15 14:30:00', 'Cette Karambit est magnifique, la finition est parfaite !', 1),
          (3, 1, '2024-03-16 09:45:00', 'Très beau skin mais un peu cher à mon goût.', 1),
          (4, 2, '2024-03-16 13:20:00', 'La Dragon Lore est le meilleur skin pour AWP, un vrai chef-d\'œuvre.', 1),
          (5, 2, '2024-03-17 10:15:00', 'Je rêve d\'avoir cette AWP un jour, mais les prix sont fous !', 1),
          (6, 3, '2024-03-17 16:40:00', 'Ces gants sont superbes en jeu, les détails sont incroyables.', 1),
          (2, 5, '2024-03-18 11:25:00', 'Un des plus beaux skins pour AK, j\'adore les motifs arabesques.', 1),
          (7, 6, '2024-03-18 14:50:00', 'La Butterfly Marble Fade est mon couteau préféré, les animations sont fluides.', 1),
          (3, 9, '2024-03-19 09:10:00', 'Ce M9 est magnifique, les couleurs du Doppler sont vibrantes.', 1),
          (4, 12, '2024-03-19 15:35:00', 'J\'ai investi dans une AWP Gungnir, aucun regret. Design nordique parfait.', 1),
          (5, 13, '2024-03-20 10:20:00', 'Ce sticker iBUYPOWER est une légende, le prix est justifié par sa rareté.', 1),
          (2, 16, '2024-03-20 13:45:00', 'L\'AWP Wildfire est un excellent rapport qualité/prix.', 1),
          (6, 21, '2024-03-21 09:30:00', 'Les Specialist Gloves Fade se marient parfaitement avec mon M9 Fade.', 1),
          (7, 23, '2024-03-21 14:15:00', 'Le Skeleton Fade est magnifique, surtout en full fade !', 1),
          (3, 25, '2024-03-22 10:50:00', 'Ce skin M4A1-S est basique mais pratique pour les budgets limités.', 1),
          (4, 26, '2024-03-22 16:25:00', 'Bon sticker pour les fans de Na\'Vi, pas cher en plus.', 1),
          (8, 1, '2024-03-23 10:15:00', 'La valeur des Karambit Gamma Doppler ne cesse d\'augmenter, un excellent investissement à long terme.', 1),
          (8, 5, '2024-03-23 14:30:00', 'L\'AK-47 Gold Arabesque est l\'un des meilleurs investissements actuels pour les collectionneurs sérieux.', 1),
          (9, 2, '2024-03-24 09:45:00', 'J\'utilise la Dragon Lore pour tous mes streams, les viewers l\'adorent ! Ça ajoute vraiment une valeur à mon contenu.', 1),
          (9, 6, '2024-03-24 16:20:00', 'La Butterfly Marble Fade est si satisfaisante à manipuler en stream, parfaite pour les transitions entre les rounds.', 1),
          (10, 12, '2024-03-25 11:35:00', 'J\'ai acheté l\'AWP Gungnir il y a un an et sa valeur a augmenté de 30%. Une des meilleures décisions d\'investissement.', 1),
          (10, 14, '2024-03-25 15:50:00', 'Le sticker Titan Holo est le joyau de ma collection, son appréciation est constante même en période de baisse du marché.', 1),
          (2, 4, '2024-03-26 10:10:00', 'Le Skeleton Crimson Web est magnifique en jeu, surtout avec les bons patterns de toile.', 1),
          (3, 11, '2024-03-26 14:25:00', 'L\'AK-47 Inheritance est sous-évalué selon moi, le design est très élégant et détaillé.', 1),
          (4, 8, '2024-03-27 09:40:00', 'Le M4A1-S Knight est mon skin préféré pour ce fusil, si propre et élégant.', 1),
          (5, 20, '2024-03-27 16:15:00', 'Le Navaja Rust Coat a un charme rustique qui contraste avec les skins plus clinquants, j\'apprécie cette simplicité.', 1);


     INSERT INTO commentaire (utilisateur_id, skin_id, date_publication, commentaire, valide, commentaire_id_parent) VALUES
          (1, 1, '2024-03-16 15:45:00', 'Merci pour votre retour ! Nous sommes ravis que vous appréciez la finition de cette Karambit. C\'est effectivement l\'un de nos produits phares.', 1, 1),
          (1, 2, '2024-03-17 10:30:00', 'Nous sommes d\'accord, la Dragon Lore est un chef-d\'œuvre incontournable dans l\'univers des skins CS. Merci de partager votre enthousiasme !', 1, 3),
          (1, 12, '2024-03-20 09:15:00', 'Excellent choix d\'investissement ! L\'AWP Gungnir est très prisée pour son design unique. N\'hésitez pas à nous contacter si vous cherchez d\'autres pièces de collection.', 1, 9),
          (1, 13, '2024-03-21 11:40:00', 'Le sticker iBUYPOWER Katowice 2014 est effectivement une légende dans la communauté. Sa rareté en fait l\'un des items les plus convoités par les collectionneurs.', 1, 10),
          (1, 5, '2024-03-24 08:30:00', 'Vous avez raison concernant l\'AK-47 Gold Arabesque, c\'est un skin qui prend de la valeur avec le temps. Merci pour votre analyse pertinente !', 1, 21),
          (1, 6, '2024-03-25 10:45:00', 'Nous sommes ravis que la Butterfly Marble Fade améliore vos streams ! C\'est effectivement un couteau très apprécié pour ses animations fluides.', 1, 7),
          (1, 12, '2024-03-26 13:20:00', 'Félicitations pour votre investissement judicieux ! L\'AWP Gungnir continue en effet de prendre de la valeur sur le marché.', 1, 14);

     '''
     mycursor.execute(sql)


     get_db().commit()
     return redirect('/')
