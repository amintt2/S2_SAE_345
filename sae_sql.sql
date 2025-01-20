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



INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
(1, "admin", "admin@admin.fr", "shaez2323233232232323233223323232", "ROLE_admin", "admin", 1),
(2, "user1", "user1@example.com", "hash123456789abcdef", "ROLE_user", "User One", 1),
(3, "user2", "user2@example.com", "hash234567891bcdef", "ROLE_user", "User Two", 1), 
(4, "user3", "user3@example.com", "hash345678912cdef", "ROLE_user", "User Three", 1),
(5, "user4", "user4@example.com", "hash456789123def", "ROLE_user", "User Four", 1),
(6, "user5", "user5@example.com", "hash567891234ef", "ROLE_user", "User Five", 1)

CREATE TABLE IF NOT EXISTS ARTICLE (
    idArticle INT PRIMARY KEY AUTO_INCREMENT,
    designation VARCHAR(255),
    prix INT
)CHARACTER SET 'utf8';  

LOAD DATA LOCAL INFILE '/data/article.csv' INTO TABLE ARTICLE FIELDS TERMINATED BY ',';

CREATE TABLE IF NOT EXISTS COMMANDE (
    idCommande INT PRIMARY KEY AUTO_INCREMENT,
    dateCommande DATE,
    idClient INT,
    FOREIGN KEY (idClient) REFERENCES CLIENT(idClient)
)CHARACTER SET 'utf8';  

CREATE TABLE IF NOT EXISTS LIGNE (
    idCommande INT,
    idArticle INT,
    quantite INT,
    FOREIGN KEY (idCommande) REFERENCES COMMANDE(idCommande),
    FOREIGN KEY (idArticle) REFERENCES ARTICLE(idArticle)
)CHARACTER SET 'utf8';  