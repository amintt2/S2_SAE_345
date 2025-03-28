-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: BDD_login_sae
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `article` (
  `idArticle` int NOT NULL AUTO_INCREMENT,
  `designation` varchar(255) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `prix` int DEFAULT NULL,
  PRIMARY KEY (`idArticle`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article`
--

LOCK TABLES `article` WRITE;
/*!40000 ALTER TABLE `article` DISABLE KEYS */;
INSERT INTO `article` VALUES (1,'D├®veloppement Web Complet','webcourse.jpg',50),(2,'Programmation Orient├®e Objet','oopcourse.jpg',45),(3,'D├®veloppement de Jeux Vid├®o','gamedevcourse.png',60),(4,'D├®veloppement Backend','backendcourse.jpg',55),(5,'D├®veloppement Mobile','mobilecourse.png',55),(6,'Cybers├®curit├® Offensive','offensivecybercourse.jpg',65),(7,'Programmation Bas Niveau','lowlevelcourse.png',45),(8,'Intelligence Artificielle','aicourse.png',70),(9,'D├®veloppement d\'Interfaces Utilisateur','uicourse.jpg',50),(10,'D├®veloppement de Mods pour Jeux','gamemoddingcourse.webp',40),(11,'D├®veloppement en Cloud','cloudcourse.png',60),(12,'Programmation pour la Finance','financecourse.jpg',65),(13,'DevOps','devopscourse.png',55),(14,'Programmation VR et AR','vrcourse.png',60),(15,'Programmation IA G├®n├®rative','aidevcourse.jpg',70);
/*!40000 ALTER TABLE `article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commande`
--

DROP TABLE IF EXISTS `commande`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commande` (
  `idCommande` int NOT NULL AUTO_INCREMENT,
  `dateCommande` date DEFAULT NULL,
  `idUtilisateur` int DEFAULT NULL,
  PRIMARY KEY (`idCommande`),
  KEY `fk_commande_utilisateur` (`idUtilisateur`),
  CONSTRAINT `fk_commande_utilisateur` FOREIGN KEY (`idUtilisateur`) REFERENCES `utilisateur` (`id_utilisateur`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commande`
--

LOCK TABLES `commande` WRITE;
/*!40000 ALTER TABLE `commande` DISABLE KEYS */;
INSERT INTO `commande` VALUES (1,'2024-01-15',1),(2,'2024-01-10',2),(3,'2024-01-05',3),(4,'2023-12-28',4),(5,'2023-12-20',5),(6,'2023-12-15',6),(7,'2023-12-10',1),(8,'2023-12-05',2),(9,'2023-11-30',3),(10,'2023-11-25',4),(11,'2023-11-20',5),(12,'2023-11-15',6),(13,'2024-01-20',1),(14,'2024-01-18',3),(15,'2024-01-16',5);
/*!40000 ALTER TABLE `commande` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ligne`
--

DROP TABLE IF EXISTS `ligne`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ligne` (
  `idCommande` int NOT NULL,
  `idArticle` int NOT NULL,
  `quantite` int DEFAULT NULL,
  PRIMARY KEY (`idCommande`,`idArticle`),
  KEY `fk_ligne_article` (`idArticle`),
  CONSTRAINT `fk_ligne_commande` FOREIGN KEY (`idCommande`) REFERENCES `commande` (`idCommande`),
  CONSTRAINT `fk_ligne_article` FOREIGN KEY (`idArticle`) REFERENCES `article` (`idArticle`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ligne`
--

LOCK TABLES `ligne` WRITE;
/*!40000 ALTER TABLE `ligne` DISABLE KEYS */;
INSERT INTO `ligne` VALUES (1,1,2),(1,2,1),(1,3,1),(2,4,2),(2,5,1),(3,6,1),(3,7,2),(3,8,1),(4,9,3),(4,10,1),(5,11,2),(5,12,1),(5,13,1),(6,14,1),(6,15,2),(7,1,1),(7,3,2),(7,5,1),(8,2,2),(8,4,1),(8,6,1),(9,7,1),(9,8,2),(9,9,1),(10,10,2),(10,11,1),(10,12,1),(11,13,3),(11,14,1),(12,1,1),(12,15,2),(13,2,2),(13,3,1),(13,4,1),(14,5,2),(14,6,1),(14,7,1),(15,8,2),(15,9,1),(15,10,1);
/*!40000 ALTER TABLE `ligne` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilisateur` (
  `id_utilisateur` int NOT NULL AUTO_INCREMENT,
  `login` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `est_actif` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_utilisateur`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilisateur`
--

LOCK TABLES `utilisateur` WRITE;
/*!40000 ALTER TABLE `utilisateur` DISABLE KEYS */;
INSERT INTO `utilisateur` VALUES (1,'admin','admin@admin.fr','admin','shaez2323233232232323233223323232','ROLE_admin',1),(2,'user1','user1@example.com','User One','hash123456789abcdef','ROLE_user',1),(3,'user2','user2@example.com','User Two','hash234567891bcdef','ROLE_user',1),(4,'user3','user3@example.com','User Three','hash345678912cdef','ROLE_user',1),(5,'user4','user4@example.com','User Four','hash456789123def','ROLE_user',1),(6,'user5','user5@example.com','User Five','hash567891234ef','ROLE_user',1);
/*!40000 ALTER TABLE `utilisateur` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-20 21:34:40
