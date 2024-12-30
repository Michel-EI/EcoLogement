-- Détruire les anciennes tables existantes
DROP TABLE IF EXISTS Facture;
DROP TABLE IF EXISTS Mesure;
DROP TABLE IF EXISTS CapteurActionneur;
DROP TABLE IF EXISTS TypeCapteurActionneur;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Logement;

-- Table Logement
CREATE TABLE Logement (
    id_logement INTEGER PRIMARY KEY AUTOINCREMENT, -- Clé primaire pour la table logement
    adresse TEXT NOT NULL, -- adresse format texte qui ne peut pas etre vide car un logement a toujours une adresse
    numero_telephone TEXT, --Numéro de tel format text pour un traitement simple a l'avenir...
    adresse_ip TEXT,--idem
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Valeur par défaut avec la date actuelle
);

-- Table Piece
CREATE TABLE Piece (
    id_piece INTEGER PRIMARY KEY AUTOINCREMENT,-- Clé primaire pour la table Piece
    nom_piece TEXT NOT NULL,-- nom de la piece ex : salon
    localisation TEXT,
    nombre_capteur INTEGER,
    nombre_actionneur INTEGER,
    id_logement INTEGER,
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)
);

-- Table TypeCapteurActionneur
CREATE TABLE TypeCapteurActionneur (
    id_type INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_type TEXT NOT NULL,
    unite_mesure TEXT,
    plage_precision TEXT
);

-- Table CapteurActionneur
CREATE TABLE CapteurActionneur (
    id_capteur_actionneur INTEGER PRIMARY KEY AUTOINCREMENT,
    id_type INTEGER,
    reference_commerciale TEXT,
    id_piece INTEGER,
    port_communication TEXT,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_type) REFERENCES TypeCapteurActionneur(id_type),
    FOREIGN KEY (id_piece) REFERENCES Piece(id_piece)
);

-- Table Mesure
CREATE TABLE Mesure (
    id_mesure INTEGER PRIMARY KEY AUTOINCREMENT,
    id_capteur_actionneur INTEGER,
    valeur REAL NOT NULL,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_capteur_actionneur) REFERENCES CapteurActionneur(id_capteur_actionneur)
);

-- Table Facture
CREATE TABLE Facture (
    id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
    id_logement INTEGER,
    type_facture TEXT NOT NULL,
    date_facture DATE NOT NULL,
    montant REAL NOT NULL,
    valeur_consommation REAL,
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)
);


-- Insérertion un logement



-- Insérer un logement sans caractères accentués
INSERT INTO Logement (adresse, numero_telephone, adresse_ip) -- Précision des Champs à remplir
VALUES ('123 Rue de l Ecologie','0102030404','192.168.0.10');--valeur respectives des champs à remplir



-- Insérer les pièces associées au logement
-- il s'agit du meme id_logement pour les 4 pieces car les pieces sont dans le meme logement

-- Pièce 1 : Création du Salon
INSERT INTO Piece (nom_piece, localisation, id_logement) -- Précision des Champs à remplir
VALUES ('Salon', '0,0,0', 1);--valeur respectives des champs à remplir

-- Pièce 2 : Création de la Cuisine
INSERT INTO Piece (nom_piece, localisation, id_logement) -- Précision des Champs à remplir
VALUES ('Cuisine', '0,1,0', 1);--valeur respectives des champs à remplir

-- Pièce 3 : Création de la Chambre
INSERT INTO Piece (nom_piece, localisation, id_logement) -- Précision des Champs à remplir
VALUES ('Chambre', '1,0,0', 1);--valeur respectives des champs à remplir

-- Pièce 4 : Création de la Salle de bain
INSERT INTO Piece (nom_piece, localisation, id_logement) -- Précision des Champs à remplir
VALUES ('Salle de bain', '1,1,0', 1);--valeur respectives des champs à remplir

------------------------------------------------ Question 5 - partie type de capteurs ---------------------------------------
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Capteur de consommation électrique', 'kWh', '[0, 10000]');

-- Insertion du premier type de capteur: Capteur de température
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Capteur de température', '°C', '[-15, 60]');

-- Insertion du 4eme premier type de capteur: Actionneur de température
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Actionneur de température', '°C', '[15,30]');

--Insertion du Deuxième type de capteur: Capteur humidité
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Capteur humidité', '%', '[0, 100]');

INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Capteur de consommation eau (volume)', 'Litres', '[0, 10000]');


-- Insertion du 3eme type de capteur: Actionneur de panneau solaire
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Actionneur de position angulaire', 'Position angulaire(°)', '[0, 360]');

-- Insertion du 5eme premier type de capteur: Capteur de niveau de générateur
INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision) 
VALUES ('Capteur de niveau de batterie', '%', '[0, 100]');

----------------------------------------- QUESTION 6 : Ajout des capteurs/actionneurs	---------------------------------
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication)
VALUES ((SELECT id_type FROM TypeCapteurActionneur WHERE nom_type = 'Capteur de consommation eau (volume)'), 
        'WaterMeter-101', 2, 'COM2');

-- Capteur de consommation électrique dans le Salon
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication) 
VALUES ((SELECT id_type FROM TypeCapteurActionneur WHERE nom_type = 'Capteur de consommation électrique'), 
        'ElectricMeter-001', 1, 'COM5');

-- Capteur de consommation électrique dans la Cuisine
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication) 
VALUES ((SELECT id_type FROM TypeCapteurActionneur WHERE nom_type = 'Capteur de consommation électrique'), 
        'ElectricMeter-002', 2, 'COM6');


-- Capteur 1 : Capteur de température dans la pièce "Salon"
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication) 
VALUES (1, 'TP357', 1, 'COM1');

-- Capteur 2 : Capteur de consommation d'eau dans la pièce "Cuisine"
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication) 
VALUES (4, 'WaterMeter-101', 2, 'COM2');

-- Actionneur 1 : Actionneur de panneau solaire
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication) 
VALUES (5,'ME75005880', 3, 'COM3');

-- Capteur 2 : Capteur de consommation d'eau dans la pièce "sdb"
INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication) 
VALUES (4, 'WaterMeter-101',4, 'COM4');


---------------------------- QUESTION 7 : Ajout des mesures	-------------------------------------------------------
-- Mesures pour le capteur de consommation électrique (id_capteur_actionneur = 1)
INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) 
VALUES 
    (1, 320, '2024-01-01 10:00:00'),
    (1, 300, '2024-01-15 10:00:00'),
    (1, 310, '2024-02-01 10:00:00'),
    (1, 280, '2024-02-15 10:00:00'),
    (1, 290, '2024-03-01 10:00:00'),
    (1, 310, '2024-03-15 10:00:00');

-- Mesures pour le capteur de consommation d'eau (id_capteur_actionneur = 2)
INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) 
VALUES 
    (2, 1500, '2024-01-05 11:00:00'),
    (2, 1400, '2024-01-20 11:00:00'),
    (2, 1450, '2024-02-05 11:00:00'),
    (2, 1550, '2024-02-20 11:00:00'),
    (2, 1380, '2024-03-05 11:00:00'),
    (2, 1300, '2024-03-20 11:00:00');
INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES ((SELECT id_capteur_actionneur FROM CapteurActionneur WHERE reference_commerciale = 'WaterMeter-101'), 150.0);

-- Mesures pour le capteur de consommation électrique (Salon)
INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES ((SELECT id_capteur_actionneur FROM CapteurActionneur WHERE reference_commerciale = 'ElectricMeter-001'), 150);

INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES ((SELECT id_capteur_actionneur FROM CapteurActionneur WHERE reference_commerciale = 'ElectricMeter-001'), 200);

-- Mesures pour le capteur de consommation électrique (Cuisine)
INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES ((SELECT id_capteur_actionneur FROM CapteurActionneur WHERE reference_commerciale = 'ElectricMeter-002'), 100);

INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES ((SELECT id_capteur_actionneur FROM CapteurActionneur WHERE reference_commerciale = 'ElectricMeter-002'), 120);

-- Mesures pour le capteur de température (id_capteur_actionneur = 1)
INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES (1, 22.5); -- Première mesure : Température à 22.5 °C

INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES (1, 23.0); -- Deuxième mesure : Température à 23.0 °C

-- Mesures pour le capteur de consommation d'eau (id_capteur_actionneur = 2)
INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES (2, 150.0); -- Première mesure : Consommation de 150 litres

INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES (2, 180.0); -- Deuxième mesure : Consommation de 180 litres

-- Mesures pour l'actionneur de panneau solaire (id_capteur_actionneur = 3)
INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES (3, 45.0); -- Première mesure : Position angulaire à 45°

INSERT INTO Mesure (id_capteur_actionneur, valeur) 
VALUES (3, 90.0); -- Deuxième mesure : Position angulaire à 90°

------------------------------------------- QUESTION 8 : FACTURES --------------------------------------------------------

-- Facture 1 : Facture d'électricité
INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation)
VALUES (1, 'Électricité', '2024-11-01', 100.50, 300);  -- 100.50 € pour 300 kWh

-- Facture 2 : Facture d'eau
INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation)
VALUES (1, 'Eau', '2024-11-01', 45.75, 1500);  -- 45.75 € pour 1500 Litres

-- Facture 3 : Facture de gaz
INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation)
VALUES (1, 'Gaz', '2024-11-01', 112, 50);  -- 112.00 € pour 50 kg de déchets

------------------------------Facture 4 : Facture d'abonnement Internet -----------------------------------------------------
INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation)
VALUES (1, 'Abonnement Internet', '2024-11-01', 39.99, NULL);  -- 39.99 € pour l'abonnement Internet






