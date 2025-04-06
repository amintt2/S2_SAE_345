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
   id_adresse_fav BOOLEAN,
   nom VARCHAR(255),
   rue VARCHAR(255),
   code_postal VARCHAR(255),
   ville VARCHAR(255),
   date_utilisation DATETIME,
   utilisateur_id INT NOT NULL,
   PRIMARY KEY(id_adresse),
   CONSTRAINT fk_adresse_utilisateur
      FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   CONSTRAINT fk_adresse_favorite
      FOREIGN KEY (id_adresse_fav) REFERENCES adresse(id_adresse)
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
('Expédiée');


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


INSERT INTO commande (date_achat, etat_id, utilisateur_id) VALUES 
    ('2024-03-19', 2, 2),
    ('2024-03-15', 2, 2),
    ('2024-03-18', 1, 3),
    ('2024-03-20', 1, 3),
    ('2024-03-10', 2, 2);

INSERT INTO ligne_commande (declinaison_id, commande_id, prix, quantite) VALUES 
    (1, 1, 80.00, 1),
    (3, 1, 897.35, 2),
    (7, 2, 83.90, 1),
    (10, 2, 74.32, 3),
    (4, 3, 490.76, 1),
    (15, 3, 433.53, 2),
    (2, 4, 11244.54, 1),
    (5, 5, 4023.26, 1);

INSERT INTO ligne_panier (declinaison_id, utilisateur_id, quantite, date_ajout) VALUES
(1, 2, 1, '2024-03-20 10:30:00'),
(2, 2, 4, '2023-06-24'),
(2, 3, 3, '2023-06-24');