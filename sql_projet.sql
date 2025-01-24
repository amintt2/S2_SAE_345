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