DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS skin;
DROP TABLE IF EXISTS type_skin;
DROP TABLE IF EXISTS usure;
DROP TABLE IF EXISTS special;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS utilisateur;

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

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATE,
   etat_id INT NOT NULL,
   utilisateur_id INT NOT NULL,
   PRIMARY KEY(id_commande),
   FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
) DEFAULT CHARSET utf8mb4;

CREATE TABLE ligne_commande(
   skin_id INT,
   commande_id INT,
   prix DECIMAL(10,2),
   quantite INT,
   PRIMARY KEY(skin_id, commande_id),
   FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
   FOREIGN KEY(commande_id) REFERENCES commande(id_commande)
) DEFAULT CHARSET utf8mb4;

CREATE TABLE ligne_panier(
   skin_id INT,
   utilisateur_id INT,
   quantite INT,
   date_ajout DATETIME,
   PRIMARY KEY(skin_id, utilisateur_id),
   FOREIGN KEY(skin_id) REFERENCES skin(id_skin),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
) DEFAULT CHARSET utf8mb4;

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
('Validée'),
('Expédiée'),
('Livrée'),
('Annulée');

INSERT INTO skin (nom_skin, prix_skin, stock, special_id, usure_id, type_skin_id, image) VALUES
('Karambit | Gamma Doppler', 1005.34, 5, 2, 1, 4, 'karambit_gamma_doppler.png'),
('AWP | Dragon Lore', 11244.54, 2, 1, 1, 3, 'awp_dragon_lore.png'),
('Sport Gloves | Amphibious', 897.35, 8, 2, 2, 5, 'gloves_amphibious.png'),
('Skeleton Knife | Crimson Web', 490.76, 3, 2, 2, 4, 'skeleton_crimson.png'),
('AK-47 | Gold Arabesque', 4023.26, 1, 2, 1, 1, 'ak_gold_arabesque.png'),
('Butterfly Knife | Marble Fade', 2083.06, 4, 2, 1, 4, 'butterfly_marble.png'),
('Driver Gloves | Snow Leopard', 83.90, 7, 1, 5, 5, 'gloves_snow_leopard.png'),
('M4A1-S | Knight', 2959.66, 2, 1, 1, 6, 'm4a1s_knight.png'),
('M9 Bayonet | Doppler', 1262.63, 6, 2, 1, 4, 'm9_doppler.png'),
('AWP | Lightning Strike', 74.32, 9, 2, 1, 3, 'awp_lightning_st.png'),
('AK-47 | Inheritance', 180.50, 3, 1, 1, 1, 'FN_AK_INHERITANCE.png'),
('AWP | Gungnir', 11200.00, 1, 1, 1, 3, 'FN_GUNGNIR.png'),
('Sticker | iBUYPOWER (Holo) | Katowice 2014', 75000.00, 1, 1, 1, 2, 'IBUYPOWER-HOLO.png'),
('Sticker | Titan (Holo) | Katowice 2014', 55000.00, 1, 1, 1, 2, 'TITAN-HOLO.png'),
('Karambit | Crimson Web', 433.53, 5, 1, 2, 4, 'karambit_crimson_web.png'),
('AWP | Wildfire', 47.93, 8, 1, 3, 3, 'awp_wildfire.png'),
('Flip Knife | Bright Water', 206.29, 4, 1, 1, 4, 'flip_bright_water.png'),
('Bowie Knife | Autotronic', 147.36, 6, 1, 3, 4, 'bowie_autotronic.png'),
('Huntsman Knife | Gamma Doppler', 378.27, 2, 1, 1, 4, 'huntsman_gamma_doppler.png'),
('Navaja Knife | Rust Coat', 93.19, 7, 1, 5, 4, 'navaja_rust.png'),
('Specialist Gloves | Fade', 343.02, 5, 1, 3, 5, 'specialist_fade.png'),
('Bowie Knife | Black Laminate', 113.87, 3, 1, 2, 4, 'bowie_black_laminate.png'),
('Skeleton Knife | Fade', 1346.34, 4, 1, 1, 4, 'skeleton_fade.png'),
('Flip Knife | Doppler', 453.49, 6, 1, 1, 4, 'flip_doppler.png'),
('M4A1-S | Mud-Spec', 0.15, 10, 1, 3, 6, 'm4a1s_mudspec.png'),
('Natus Vincere Glitter', 0.15, 8, 1, 1, 2, 'sticker_navi_glitter.png'),
('AWP | Dragon Lore', 9244.54, 3, 1, 2, 3, 'awp_dragon_lore.png'),
('AWP | Dragon Lore', 8244.54, 5, 1, 3, 3, 'awp_dragon_lore.png'),
('AWP | Dragon Lore', 7244.54, 0, 1, 4, 3, 'awp_dragon_lore.png'),
('Karambit | Gamma Doppler', 905.34, 2, 2, 2, 4, 'karambit_gamma_doppler.png'),
('Karambit | Gamma Doppler', 805.34, 4, 2, 3, 4, 'karambit_gamma_doppler.png'),
('AK-47 | Gold Arabesque', 3523.26, 1, 2, 2, 1, 'ak_gold_arabesque.png'),
('AK-47 | Gold Arabesque', 3023.26, 7, 2, 3, 1, 'ak_gold_arabesque.png'),
('M4A1-S | Knight', 2459.66, 6, 1, 2, 6, 'm4a1s_knight.png'),
('M4A1-S | Knight', 1959.66, 9, 1, 3, 6, 'm4a1s_knight.png');

INSERT INTO commande (date_achat, etat_id, utilisateur_id) VALUES 
    ('2024-03-19', 2, 2),
    ('2024-03-15', 4, 2),
    ('2024-03-18', 3, 3),
    ('2024-03-20', 1, 3),
    ('2024-03-10', 5, 2);

INSERT INTO ligne_commande (skin_id, commande_id, prix, quantite) VALUES 
    (1, 1, 80.00, 1),
    (3, 1, 897.35, 2),
    (7, 2, 83.90, 1),
    (10, 2, 74.32, 3),
    (4, 3, 490.76, 1),
    (15, 3, 433.53, 2),
    (2, 4, 11244.54, 1),
    (5, 5, 4023.26, 1);

INSERT INTO ligne_panier (skin_id, utilisateur_id, quantite, date_ajout) VALUES
(1, 2, 1, '2024-03-20 10:30:00'),
(2, 2, 4, '2023-06-24'),
(2, 3, 3, '2023-06-24');
