-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: reportmysql_db
-- ------------------------------------------------------
-- Server version	8.0.29-0ubuntu0.22.04.2

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
-- Table structure for table `link`
--

DROP TABLE IF EXISTS `link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `page_url` varchar(512) NOT NULL,
  `anchor` varchar(255) NOT NULL,
  `link_url` varchar(512) NOT NULL,
  `da` decimal(10,2) DEFAULT NULL,
  `dr` decimal(10,2) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `screenshot_url` varchar(512) NOT NULL,
  `contact` varchar(255) NOT NULL,
  `user_id` int DEFAULT NULL,
  `page_url_domain_id` int DEFAULT NULL,
  `link_url_domain_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_link_screenshot_url` (`screenshot_url`),
  KEY `ix_link_contact` (`contact`),
  KEY `ix_link_page_url` (`page_url`),
  KEY `ix_link_anchor` (`anchor`),
  KEY `ix_link_link_url` (`link_url`),
  KEY `ix_link_price` (`price`),
  KEY `link_ibfk_2` (`page_url_domain_id`),
  KEY `link_ibfk_3` (`link_url_domain_id`),
  KEY `link_ibfk_1` (`user_id`),
  CONSTRAINT `link_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL,
  CONSTRAINT `link_ibfk_2` FOREIGN KEY (`page_url_domain_id`) REFERENCES `page_url_domain` (`id`) ON DELETE CASCADE,
  CONSTRAINT `link_ibfk_3` FOREIGN KEY (`link_url_domain_id`) REFERENCES `link_url_domain` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=422 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `link`
--

LOCK TABLES `link` WRITE;
/*!40000 ALTER TABLE `link` DISABLE KEYS */;
INSERT INTO `link` VALUES (402,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://graphictutorials.net/not-avoiding-but-solving-the-problem-what-are-the-benefits-of-conflict/','22Bet best online worldwide bookmaker','https://22bet.com/',53.00,53.00,66.61,'http://joxi.ru/E2pleP0C43qoX3','caneplusguestpost@gmail.com',1,124,259),(403,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://magazinetoday.in/an-all-out-overview-of-22bet-games-betting-in-nigeria/','22Bet Nigeria','https://22betlogin.ng/',56.00,37.00,14.25,'http://joxi.ru/E2pleP0C43qoX414','admin@guestpostt.com',1,126,260),(404,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.myfrugalfitness.com/2022/01/tips-improve-your-slot-wins.html','BizzoCasino.com','https://bizzocasino.com/',28.00,35.00,71.44,'http://joxi.ru/E2pleP0C43qoX404','mikeschiemer@gmail.com',1,125,261),(405,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.veteranstoday.com/2020/04/27/new-zealand-covid-19-cases-dramatically-decrease/','play online casino games','https://www.playamo.com/en-NZ/games',77.00,71.00,73.33,'http://joxi.ru/E2pleP0C43qoX407','support@veteranstoday.com',1,127,262),(406,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://reviewfix.com/2022/04/top-5-most-thrilling-war-games/','try National Casino','https://nationalcasino.com/',45.00,55.00,71.43,'http://joxi.ru/E2pleP0C43qoX408','patrickhickeyjr@reviewfix.com',1,128,263),(407,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://agile-unternehmen.de/online-casinos-so-kam-es-dazu/','PlayAmo','https://playamologin.com/de/',33.00,37.00,125.00,'http://joxi.ru/E2pleP0C43qoX409','Dominic.Lindner@agile-unternehmen.de',1,129,264),(408,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.forumbrico.fr/news/r_gles_du_blackjack_et_chances_de_gagner.html','jeux de blackjack sur PlayAmo','https://www.playamo.com/fr-CA/games/blackjack',38.00,30.00,169.81,'http://joxi.ru/E2pleP0C43qoX410','foulijames@gmail.com',1,130,262),(409,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.onlinesportmanagers.com/article/610-the-most-popular-game-in-february-2022-my-racing-career/','casino online','https://nationalcasino.com/',30.00,35.00,80.00,'http://joxi.ru/E2pleP0C43qoX411','info@onlinesportmanagers.com',1,131,263),(410,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://tellingdad.com/what-is-the-best-strategy-to-make-combination-bets/','22Bet Uganda','https://22betuganda.com/',75.00,68.00,9.50,'http://joxi.ru/E2pleP0C43qoX412','support@gposting.com',1,132,265),(411,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://jewelbeat.com/understanding-sports-betting-odds/','22Bet Uganda','https://bet22.ug/',39.00,46.00,57.02,'http://joxi.ru/E2pleP0C43qoX413','kravitzcj@gmail.com',1,133,266),(412,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://newscons.com/3-features-to-implement-before-launching-a-mobile-app/','22Bet','https://22bet.online/',54.00,53.00,107.79,'http://joxi.ru/E2pleP0C43qoX419','orders@rankcastle.com',1,134,267),(413,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://ideasforeurope.com/how-does-modern-technology-affect-peoples-lives/','22Bet','https://22bet.online/',46.00,31.00,107.79,'http://joxi.ru/E2pleP0C43qoX420','orders@rankcastle.com',1,135,267),(414,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://scholarshipgiant.com/most-unusual-college-degrees-you-have-not-heard-about/','22Bet','https://22bet.online/',46.00,37.00,107.79,'http://joxi.ru/E2pleP0C43qoX421','orders@rankcastle.com',1,136,267),(415,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://programminginsider.com/the-most-popular-casino-ball-games-in-2022/','online casino Philippines','https://nationalcasino.com/',57.00,74.00,38.10,'http://joxi.ru/E2pleP0C43qoX405','marc@programminginsider.com',1,137,263),(416,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://techbuggle.com/5-key-steps-to-clean-your-skin/','PlayAmo','https://play-amo.ca/',54.00,46.00,51.53,'http://joxi.ru/E2pleP0C43qoX406','janimalikseo@gmail.com',1,138,268),(417,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.myfrugalfitness.com/2022/01/tips-improve-your-slot-wins.html','BizzoCasino.com','https://bizzocasino.com/',27.00,35.00,71.44,'http://joxi.ru/E2pleP0C43qoX404','mikeschiemer@gmail.com',1,125,261),(418,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.seorankone1.com/blog/sports-betting/','22Bet ','https://22betsenegal.sn/',65.00,36.00,47.51,'http://joxi.ru/E2pleP0C43qoX415','seorankone1@gmail.com',1,139,269),(419,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://tellingdad.com/five-recommendations-to-not-fail-in-your-sports-bets/','22Bet ','https://22bet-cd.com/',75.00,68.00,9.50,'http://joxi.ru/E2pleP0C43qoX416','support@gposting.com',1,132,270),(420,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://www.grapevinebirmingham.com/advantages-of-betting-online/','22Bet ','https://22bet-cd.com/',41.00,31.00,95.03,'http://joxi.ru/E2pleP0C43qoX417','info@grapevinebirmingham.com, nickbyng@hotmail.com',1,140,270),(421,'2022-06-03 10:06:21','2022-06-03 10:06:21','https://yeyelife.com/how-to-get-rid-of-insomnia-tips-to-consider/','22Bet login','https://22bet.online/',63.00,46.00,107.79,'http://joxi.ru/E2pleP0C43qoX418','orders@rankcastle.com',1,141,267);
/*!40000 ALTER TABLE `link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `link_check`
--

DROP TABLE IF EXISTS `link_check`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `link_check` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `href_is_found` tinyint(1) DEFAULT NULL,
  `href_has_rel` tinyint(1) DEFAULT NULL,
  `rel_has_nofollow` tinyint(1) DEFAULT NULL,
  `rel_has_sponsored` tinyint(1) DEFAULT NULL,
  `meta_robots_has_noindex` tinyint(1) DEFAULT NULL,
  `meta_robots_has_nofollow` tinyint(1) DEFAULT NULL,
  `anchor_text_found` varchar(255) DEFAULT NULL,
  `anchor_count` int DEFAULT NULL,
  `ssl_expiration_date` datetime DEFAULT NULL,
  `ssl_expires_in_days` int DEFAULT NULL,
  `result_message` varchar(512) DEFAULT NULL,
  `response_code` int DEFAULT NULL,
  `redirect_codes_list` varchar(255) DEFAULT NULL,
  `redirect_url` varchar(512) DEFAULT NULL,
  `link_url_others_count` int DEFAULT NULL,
  `link_id` int DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_link_check_redirect_url` (`redirect_url`),
  KEY `ix_link_check_anchor_text_found` (`anchor_text_found`),
  KEY `link_check_ibfk_1` (`link_id`),
  CONSTRAINT `link_check_ibfk_1` FOREIGN KEY (`link_id`) REFERENCES `link` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=476 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `link_check`
--

LOCK TABLES `link_check` WRITE;
/*!40000 ALTER TABLE `link_check` DISABLE KEYS */;
INSERT INTO `link_check` VALUES (456,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'BizzoCasino.com',1,'2022-08-30 12:47:07',87,'warn: href does not have \"rel\";',200,'[]','',8,417,'yellow'),(457,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'BizzoCasino.com',1,'2022-08-30 12:47:07',87,'warn: href does not have \"rel\";',200,'[]','',8,404,'yellow'),(458,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet best online worldwide bookmaker',1,'2022-12-31 23:59:59',211,'warn: href does not have \"rel\";',200,'[]','',30,402,'yellow'),(459,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet Nigeria',1,'2022-08-29 13:49:57',87,'warn: href does not have \"rel\";',200,'[]','',12,403,'yellow'),(460,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'casino online',1,'2022-08-21 12:22:29',78,'warn: href does not have \"rel\";',200,'[]','',1,409,'yellow'),(461,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'PlayAmo',1,'2022-07-27 04:28:56',53,'warn: href does not have \"rel\";',200,'[]','',18,416,'yellow'),(462,'2022-06-03 10:06:22',NULL,1,1,0,0,0,0,'22Bet',1,'2023-04-08 23:59:59',309,'ok: href has \"rel\"; \"rel\" does not have \"nofollow\": ([\'noreferrer\', \'noopener\']);',200,'[]','',22,420,'green'),(463,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'PlayAmo',1,'2022-08-18 12:44:45',75,'warn: href does not have \"rel\";',200,'[]','',8,407,'yellow'),(464,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'play online casino games',1,'2023-05-16 23:59:59',347,'warn: href does not have \"rel\";',200,'[]','',149,405,'yellow'),(465,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22 Bet',1,'2022-07-20 18:08:03',47,'warn: href does not have \"rel\";',200,'[]','',69,413,'yellow'),(466,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'online casino Philippines',1,'2022-07-14 23:59:59',41,'warn: href does not have \"rel\";',200,'[]','',14,415,'yellow'),(467,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet',1,'2022-08-21 11:33:56',78,'warn: href does not have \"rel\";',200,'[]','',52,419,'yellow'),(468,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet Uganda',1,'2022-08-21 11:33:56',78,'warn: href does not have \"rel\";',200,'[]','',53,410,'yellow'),(469,'2022-06-03 10:06:22',NULL,0,0,0,0,0,0,'',0,NULL,-1,'error while checking https://www.seorankone1.com/blog/sports-betting/, please refer to admin',NULL,'[]','',0,418,'red'),(470,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22bet Uganda',1,'2023-05-24 23:59:59',355,'warn: href does not have \"rel\";',200,'[301]','https://www.jewelbeat.com/understanding-sports-betting-odds/',5,411,'yellow'),(471,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet',1,'2022-12-16 23:59:59',196,'warn: href does not have \"rel\";',200,'[]','',11,414,'yellow'),(472,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet',1,'2023-05-07 23:59:59',338,'warn: href does not have \"rel\";',200,'[]','',12,412,'yellow'),(473,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'22Bet login',1,'2022-08-31 23:59:59',89,'warn: href does not have \"rel\";',200,'[]','',35,421,'yellow'),(474,'2022-06-03 10:06:22',NULL,0,0,0,0,1,0,'',0,'2022-08-27 07:41:25',84,'error: href not found;',404,'[]','',14,408,'red'),(475,'2022-06-03 10:06:22',NULL,1,0,0,0,0,0,'try National Casino',1,'2022-07-20 16:10:27',47,'warn: href does not have \"rel\";',200,'[]','',8,406,'yellow');
/*!40000 ALTER TABLE `link_check` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `link_url_domain`
--

DROP TABLE IF EXISTS `link_url_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `link_url_domain` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=271 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `link_url_domain`
--

LOCK TABLES `link_url_domain` WRITE;
/*!40000 ALTER TABLE `link_url_domain` DISABLE KEYS */;
INSERT INTO `link_url_domain` VALUES (259,'2022-06-03 10:06:22',NULL,'22bet.com'),(260,'2022-06-03 10:06:22',NULL,'22betlogin.ng'),(261,'2022-06-03 10:06:22',NULL,'bizzocasino.com'),(262,'2022-06-03 10:06:22',NULL,'playamo.com'),(263,'2022-06-03 10:06:22',NULL,'nationalcasino.com'),(264,'2022-06-03 10:06:22',NULL,'playamologin.com'),(265,'2022-06-03 10:06:22',NULL,'22betuganda.com'),(266,'2022-06-03 10:06:22',NULL,'bet22.ug'),(267,'2022-06-03 10:06:22',NULL,'22bet.online'),(268,'2022-06-03 10:06:22',NULL,'play-amo.ca'),(269,'2022-06-03 10:06:22',NULL,'22betsenegal.sn'),(270,'2022-06-03 10:06:22',NULL,'22bet-cd.com');
/*!40000 ALTER TABLE `link_url_domain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_url_domain`
--

DROP TABLE IF EXISTS `page_url_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `page_url_domain` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=208 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_url_domain`
--

LOCK TABLES `page_url_domain` WRITE;
/*!40000 ALTER TABLE `page_url_domain` DISABLE KEYS */;
INSERT INTO `page_url_domain` VALUES (124,'2022-06-02 12:13:44',NULL,'graphictutorials.net'),(125,'2022-06-02 12:15:51',NULL,'myfrugalfitness.com'),(126,'2022-06-02 13:50:00',NULL,'magazinetoday.in'),(127,'2022-06-02 13:50:00',NULL,'veteranstoday.com'),(128,'2022-06-02 13:50:00',NULL,'reviewfix.com'),(129,'2022-06-02 13:50:00',NULL,'agile-unternehmen.de'),(130,'2022-06-02 13:50:00',NULL,'forumbrico.fr'),(131,'2022-06-02 13:50:00',NULL,'onlinesportmanagers.com'),(132,'2022-06-02 13:50:00',NULL,'tellingdad.com'),(133,'2022-06-02 13:50:00',NULL,'jewelbeat.com'),(134,'2022-06-02 13:58:53',NULL,'newscons.com'),(135,'2022-06-02 13:58:53',NULL,'ideasforeurope.com'),(136,'2022-06-02 13:58:53',NULL,'scholarshipgiant.com'),(137,'2022-06-02 13:58:53',NULL,'programminginsider.com'),(138,'2022-06-02 13:58:53',NULL,'techbuggle.com'),(139,'2022-06-02 14:22:28',NULL,'seorankone1.com'),(140,'2022-06-02 14:22:28',NULL,'grapevinebirmingham.com'),(141,'2022-06-02 14:22:28',NULL,'yeyelife.com'),(142,'2022-06-03 08:55:56',NULL,'womenhealth1.com'),(143,'2022-06-03 08:55:56',NULL,'alagoasalerta.com.br'),(144,'2022-06-03 08:55:56',NULL,'thetokenclock.com'),(145,'2022-06-03 08:55:56',NULL,'websplashers.com'),(146,'2022-06-03 08:55:56',NULL,'masstamilanfree.in'),(147,'2022-06-03 08:55:56',NULL,'happy2hub.co'),(148,'2022-06-03 08:55:56',NULL,'paisabank.org'),(149,'2022-06-03 08:55:56',NULL,'thetimeposts.com'),(150,'2022-06-03 08:55:56',NULL,'ihowtoarticle.com'),(151,'2022-06-03 08:55:56',NULL,'cleverwedo.com'),(152,'2022-06-03 08:55:56',NULL,'coinfaqs.org'),(153,'2022-06-03 08:55:56',NULL,'technoscriptz.com'),(154,'2022-06-03 08:55:56',NULL,'spellangel.com'),(155,'2022-06-03 08:55:56',NULL,'fullformis.com'),(156,'2022-06-03 08:55:56',NULL,'campusdoc.net'),(157,'2022-06-03 08:55:56',NULL,'prnewsblog.com'),(158,'2022-06-03 08:55:56',NULL,'lifestyleheart.com'),(159,'2022-06-03 08:55:56',NULL,'evedonusfilm.com'),(160,'2022-06-03 08:55:56',NULL,'myviralmagazine.com'),(161,'2022-06-03 08:55:56',NULL,'foodstrend.com'),(162,'2022-06-03 08:55:56',NULL,'naasongsmp3.net'),(163,'2022-06-03 08:55:56',NULL,'pagalworldnew.in'),(164,'2022-06-03 08:55:56',NULL,'gambden.com'),(165,'2022-06-03 08:55:56',NULL,'cannabisbeezer.com'),(166,'2022-06-03 08:55:56',NULL,'alltimespost.com'),(167,'2022-06-03 08:55:56',NULL,'hardgeek.net'),(168,'2022-06-03 08:55:56',NULL,'kennygorman.com'),(169,'2022-06-03 08:55:56',NULL,'hitechdroid.com'),(170,'2022-06-03 08:55:56',NULL,'sportsfanfare.com'),(171,'2022-06-03 08:55:56',NULL,'varsitygaming.net'),(172,'2022-06-03 08:55:56',NULL,'gadgetsng.com'),(173,'2022-06-03 08:55:56',NULL,'wikibio123.com'),(174,'2022-06-03 08:55:56',NULL,'winscrabble.com'),(175,'2022-06-03 08:55:56',NULL,'mobituner.com'),(176,'2022-06-03 08:55:56',NULL,'kartunsmovie.in'),(177,'2022-06-03 08:55:56',NULL,'algeriemondeinfos.com'),(178,'2022-06-03 08:55:56',NULL,'7seizh.info'),(179,'2022-06-03 08:55:56',NULL,'southfloridareporter.com'),(180,'2022-06-03 08:55:56',NULL,'nach-welt.com'),(181,'2022-06-03 08:55:56',NULL,'thegeeklyfe.com'),(182,'2022-06-03 08:55:56',NULL,'filmshortage.com'),(183,'2022-06-03 08:55:56',NULL,'thestuffofsuccess.com'),(184,'2022-06-03 08:55:56',NULL,'whudat.de'),(185,'2022-06-03 08:55:56',NULL,'tricotin.com'),(186,'2022-06-03 08:55:56',NULL,'fishduck.com'),(187,'2022-06-03 08:55:56',NULL,'gamersapparel.co.uk'),(188,'2022-06-03 08:55:56',NULL,'ineedmedic.com'),(189,'2022-06-03 08:55:56',NULL,'askanyquery.com'),(190,'2022-06-03 08:55:56',NULL,'justinresults.com'),(191,'2022-06-03 08:55:56',NULL,'thehollynews.com'),(192,'2022-06-03 08:55:56',NULL,'naasongsnew.info'),(193,'2022-06-03 08:55:56',NULL,'isaiminia.com'),(194,'2022-06-03 08:55:56',NULL,'pagalmusiq.com'),(195,'2022-06-03 08:55:56',NULL,'pagalsongs.me'),(196,'2022-06-03 08:55:56',NULL,'smihub.info'),(197,'2022-06-03 08:55:56',NULL,'bestcitytrips.com'),(198,'2022-06-03 08:55:56',NULL,'wizarticle.com'),(199,'2022-06-03 08:55:56',NULL,'technologyidea.info'),(200,'2022-06-03 08:55:56',NULL,'koupani.cz'),(201,'2022-06-03 08:55:56',NULL,'treking.cz'),(202,'2022-06-03 08:55:56',NULL,'jmais.com.br'),(203,'2022-06-03 08:55:56',NULL,'directmag.com'),(204,'2022-06-03 08:55:56',NULL,'mccourier.com'),(205,'2022-06-03 08:55:56',NULL,'mvdemocrat.com'),(206,'2022-06-03 08:55:56',NULL,'occupygh.com'),(207,'2022-06-03 08:55:56',NULL,'thetecheducation.com');
/*!40000 ALTER TABLE `page_url_domain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `is_head` tinyint(1) DEFAULT NULL,
  `is_teamlead` tinyint(1) DEFAULT NULL,
  `is_accepting_emails` tinyint(1) DEFAULT NULL,
  `is_accepting_telegram` tinyint(1) DEFAULT NULL,
  `telegram_id` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `teamlead_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_email` (`email`),
  UNIQUE KEY `ix_user_uuid` (`uuid`),
  KEY `teamlead_id` (`teamlead_id`),
  KEY `ix_user_id` (`id`),
  KEY `ix_user_name` (`first_name`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`teamlead_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'7306c6fc-eeb7-4c1a-9dca-8934854543be','2022-06-05 14:13:49','2022-05-30 11:51:47','pavelmirosh@gmail.com','Pavel','Mirosh',1,1,0,0,'869962202',1,NULL),(7,'a4c22ad6-1d97-40f5-85f2-287942008003',NULL,'2022-05-30 12:20:46','guuurd@gmail.com','ANDREY','FIADOTAU',1,0,0,0,'154605381',1,NULL),(8,'fb7d16b4-193a-4e67-a008-c9dbfc397395',NULL,'2022-05-30 12:22:04','brilevsky@22betpartners.com','Dmitry','Brilevsky',1,0,0,0,'215999245',1,NULL),(9,'59a92549-5a59-4220-b465-9e6fca0f9f1a','2022-06-01 18:09:37','2022-05-30 12:22:56','am.amsti@gmail.com','Alexandra','Volkova',0,0,0,0,'5145376534',1,NULL),(22,'9c3fc62f-8368-4963-9956-165bdce54c3b',NULL,'2022-06-05 13:24:24','o.zdioruk@22bet.com','Olha','Zdioruk',0,1,0,0,NULL,1,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-06-06 15:21:15
