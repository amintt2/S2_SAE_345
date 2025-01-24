DROP TABLE IF EXISTS LIGNE;
DROP TABLE IF EXISTS COMMANDE;
DROP TABLE IF EXISTS ARTICLE;
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

CREATE TABLE  ARTICLE (
    idArticle INT PRIMARY KEY AUTO_INCREMENT,
    designation VARCHAR(255),
    photo VARCHAR(255),
    prix INT
) CHARACTER SET 'utf8';

CREATE TABLE COMMANDE (
    idCommande INT PRIMARY KEY AUTO_INCREMENT,
    dateCommande DATE,
    idUtilisateur INT,
    FOREIGN KEY (idUtilisateur) REFERENCES utilisateur(id_utilisateur)
) CHARACTER SET 'utf8';

CREATE TABLE LIGNE (
    idCommande INT,
    idArticle INT,
    quantite INT,
    FOREIGN KEY (idCommande) REFERENCES COMMANDE(idCommande),
    FOREIGN KEY (idArticle) REFERENCES ARTICLE(idArticle),
    PRIMARY KEY (idCommande, idArticle)
) CHARACTER SET 'utf8';

-- Load data from CSV files
SET GLOBAL local_infile = 1;
LOAD DATA LOCAL INFILE 'data/article.csv' INTO TABLE ARTICLE FIELDS TERMINATED BY ',';
LOAD DATA LOCAL INFILE 'data/commande.csv' INTO TABLE COMMANDE FIELDS TERMINATED BY ',';
LOAD DATA LOCAL INFILE 'data/ligne.csv' INTO TABLE LIGNE FIELDS TERMINATED BY ',';

-- Verify data
SELECT * FROM utilisateur;
SELECT * FROM ARTICLE;
SELECT * FROM COMMANDE;
SELECT * FROM LIGNE;