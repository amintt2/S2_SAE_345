DROP TABLE IF EXISTS Ligne_panier;
DROP TABLE IF EXISTS Ligne_commande;
DROP TABLE IF EXISTS Commande;
DROP TABLE IF EXISTS Skin;
DROP TABLE IF EXISTS Type_skin;
DROP TABLE IF EXISTS Usure;
DROP TABLE IF EXISTS Spécial;
DROP TABLE IF EXISTS Etat;
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

CREATE TABLE Type_skin(
   ID_type_skin INT AUTO_INCREMENT,
   Libelle_type_skin VARCHAR(50),
   PRIMARY KEY(ID_type_skin)
);

CREATE TABLE Usure(
   ID_usure INT AUTO_INCREMENT,
   Libelle_usure VARCHAR(50),
   PRIMARY KEY(ID_usure)
);

CREATE TABLE Spécial(
   ID_spécial INT AUTO_INCREMENT,
   Libelle_spécial VARCHAR(50),
   PRIMARY KEY(ID_spécial)
);

CREATE TABLE Etat(
   ID_etat INT AUTO_INCREMENT,
   Libelle_etat VARCHAR(50),
   PRIMARY KEY(ID_etat)
);

CREATE TABLE Skin(
   ID_skin INT AUTO_INCREMENT,
   Nom_skin VARCHAR(50),
   Prix_skin DECIMAL(10,2),
   Stock INT,
   ID_spécial INT NOT NULL,
   ID_usure INT NOT NULL,
   ID_type_skin INT NOT NULL,
   Image VARCHAR(255),
   PRIMARY KEY(ID_skin),
   FOREIGN KEY(ID_spécial) REFERENCES Spécial(ID_spécial),
   FOREIGN KEY(ID_usure) REFERENCES Usure(ID_usure),
   FOREIGN KEY(ID_type_skin) REFERENCES Type_skin(ID_type_skin)
);

CREATE TABLE Commande(
   ID_commande INT AUTO_INCREMENT,
   Date_achat DATE,
   ID_etat INT NOT NULL,
   ID_utilisateur INT NOT NULL,
   PRIMARY KEY(ID_commande),
   FOREIGN KEY(ID_etat) REFERENCES Etat(ID_etat),
   FOREIGN KEY(ID_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE Ligne_commande(
   ID_skin INT,
   ID_commande INT,
   Prix DECIMAL(10,2),
   Quantite INT,
   PRIMARY KEY(ID_skin, ID_commande),
   FOREIGN KEY(ID_skin) REFERENCES Skin(ID_skin),
   FOREIGN KEY(ID_commande) REFERENCES Commande(ID_commande)
);

CREATE TABLE Ligne_panier(
   ID_skin INT,
   ID_utilisateur INT,
   Quantite INT,
   Date_ajout DATETIME,
   PRIMARY KEY(ID_skin, ID_utilisateur),
   FOREIGN KEY(ID_skin) REFERENCES Skin(ID_skin),
   FOREIGN KEY(ID_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

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

-- Insertion des types de skins
INSERT INTO Type_skin (Libelle_type_skin) VALUES
('AK-47'),
('STICKER'),
('STICKERBOX'),
('AWP');

-- Insertion des états d'usure
INSERT INTO Usure (Libelle_usure) VALUES
('Neuve'),
('Trés peu usée'),
('Testé sur le terrain'),
('Usée'),
('Marqué par les combats');

-- Insertion des attributs spéciaux
INSERT INTO Spécial (Libelle_spécial) VALUES
('Normal'),
('StatTrak™'),
('Souvenir');

-- Insertion des états de commande
INSERT INTO Etat (Libelle_etat) VALUES
('En cours'),
('Validée'),
('Expédiée'),
('Livrée'),
('Annulée');

-- Insertion des skins
INSERT INTO Skin (Nom_skin, Prix_skin, Stock, ID_spécial, ID_usure, ID_type_skin, Image) VALUES
-- AK-47s
('AK-47 | Inheritance', 180.50, 3, 1, 1, 1, 'FN_AK_INHERITANCE.png'),
('AK-47 | Inheritance', 80.00, 3, 1, 5, 1, 'BS_AK_INHERITANCE.png'),

-- AWPs
('AWP | Gungnir', 11200.00, 1, 1, 1, 4, 'FN_GUNGNIR.png'),

-- Stickers
('Sticker | iBUYPOWER (Holo) | Katowice 2014', 75000.00, 1, 1, 1, 2, 'IBUYPOWER-HOLO.png'),
('Sticker | Titan (Holo) | Katowice 2014', 55000.00, 1, 1, 1, 2, 'TITAN-HOLO.png'),

-- Sticker Boxes
('Katowice 2014 Challengers', 24000.00, 2, 1, 1, 3, 'KATOWICE-CHALLENGERS.png');

-- Exemple de panier pour le client (id=2)
INSERT INTO Ligne_panier (ID_skin, ID_utilisateur, Quantite, Date_ajout) VALUES
(1, 2, 1, '2024-03-20 10:30:00');

-- Exemple de commande pour le client (id=2)
INSERT INTO Commande (Date_achat, ID_etat, ID_utilisateur) VALUES
('2024-03-19', 2, 2);

-- Lignes de la commande
INSERT INTO Ligne_commande (ID_skin, ID_commande, Prix, Quantite) VALUES
(2, 1, 80.00, 1);

