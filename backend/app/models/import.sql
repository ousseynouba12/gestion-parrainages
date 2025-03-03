-- Fonction pour vérifier si une chaîne contient des accents (à implémenter)
DELIMITER //
CREATE FUNCTION ContientAccent(p_chaine VARCHAR(255)) RETURNS BOOLEAN
BEGIN
    DECLARE result BOOLEAN;
    -- Utilisation d'une expression régulière pour détecter les caractères accentués
    SET result = p_chaine REGEXP '[À-ÖØ-öø-ÿ]';
    RETURN result;
END//
DELIMITER ;

-- Fonction pour diviser une chaîne avec un délimiteur
DELIMITER //
CREATE FUNCTION SPLIT_STRING(str VARCHAR(4000), delim VARCHAR(10)) RETURNS TEXT
BEGIN
    RETURN str;
    -- Note: MySQL n'a pas de fonction native équivalente à DBMS_SQL.VARCHAR2_TABLE
    -- En production, vous devrez utiliser une approche différente comme des tables temporaires
    -- ou l'utilisation de JSON_ARRAY et JSON_EXTRACT
END//
DELIMITER ;

-- Fonction pour contrôler si le fichier électoral correspond à l'empreinte saisie
DELIMITER //
CREATE FUNCTION ControlerFichierElecteurs(
    p_checksum VARCHAR(64),
    p_idMembre INT,
    p_ip VARCHAR(45),
    p_cheminFichier VARCHAR(500)
) RETURNS INT
BEGIN
    DECLARE v_idFichier INT;
    DECLARE v_fichier_checksum VARCHAR(64);
    DECLARE v_est_utf8 BOOLEAN DEFAULT TRUE;
    DECLARE v_resultat BOOLEAN DEFAULT FALSE;
    DECLARE v_idTentative INT;
    
    -- Capture d'erreur
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- En cas d'erreur, enregistrer l'échec de la tentative
        IF v_idFichier IS NOT NULL THEN
            INSERT INTO Tentative_upload (
                idFichier,
                dateTentative,
                ip,
                clefUtilisee,
                resultat
            ) VALUES (
                v_idFichier,
                NOW(),
                p_ip,
                p_checksum,
                FALSE
            );
        END IF;
        RETURN -1; -- Valeur négative pour indiquer une erreur
    END;
    
    -- Enregistrer le fichier électoral
    INSERT INTO Fichier_electoral (
        checksum,
        dateUpload,
        idMembre,
        etatValidation,
        cheminFichier
    ) VALUES (
        p_checksum,
        NOW(),
        p_idMembre,
        FALSE,
        p_cheminFichier
    );
    
    SET v_idFichier = LAST_INSERT_ID();
    
    -- Calculer le checksum du fichier pour vérification (à implémenter en fonction des capacités MySQL)
    SET v_fichier_checksum = SHA2(CONCAT('file:', p_cheminFichier), 256);
    -- Note: Cette implémentation est simplifiée et nécessitera une approche spécifique
    -- pour calculer réellement le SHA256 d'un fichier en MySQL
    
    -- Vérifier si le checksum correspond
    IF v_fichier_checksum = p_checksum THEN
        -- Vérifier si le contenu est en UTF-8 (à implémenter)
        -- Dans un environnement réel, cette vérification serait faite côté application
        SET v_est_utf8 = TRUE;
        
        IF v_est_utf8 THEN
            SET v_resultat = TRUE;
        END IF;
    END IF;
    
    -- Historisation de la tentative d'upload
    INSERT INTO Tentative_upload (
        idFichier,
        dateTentative,
        ip,
        clefUtilisee,
        resultat
    ) VALUES (
        v_idFichier,
        NOW(),
        p_ip,
        p_checksum,
        v_resultat
    );
    
    SET v_idTentative = LAST_INSERT_ID();
    
    -- Si tout est valide, importer le fichier dans la table temporaire
    IF v_resultat THEN
        CALL ImporterFichierCSV(v_idFichier, v_idTentative, p_cheminFichier);
    END IF;
    
    -- Retourner l'ID de la tentative
    RETURN v_idTentative;
END//
DELIMITER ;

-- Fonction pour vérifier le format et la complétude des données des électeurs
DELIMITER //
CREATE FUNCTION ControlerElecteurs(
    p_idTentative INT
) RETURNS BOOLEAN
BEGIN
    DECLARE v_electeurs_invalides INT DEFAULT 0;
    DECLARE v_count INT;
    DECLARE v_fin INT DEFAULT 0;
    
    -- Variables pour les électeurs
    DECLARE v_numElecteur VARCHAR(20);
    DECLARE v_numCIN VARCHAR(20);
    DECLARE v_nom VARCHAR(100);
    DECLARE v_prenom VARCHAR(100);
    DECLARE v_dateNaissance DATE;
    DECLARE v_lieuNaissance VARCHAR(100);
    DECLARE v_sexe CHAR(1);
    DECLARE v_bureauVote VARCHAR(100);
    
    -- Variables pour les validations
    DECLARE v_cin_valide BOOLEAN;
    DECLARE v_num_electeur_valide BOOLEAN;
    DECLARE v_info_complete BOOLEAN;
    DECLARE v_format_valide BOOLEAN;
    DECLARE v_cin_unique BOOLEAN;
    DECLARE v_num_electeur_unique BOOLEAN;
    DECLARE v_erreur VARCHAR(4000);
    
    -- Curseur pour parcourir les électeurs
    DECLARE c_electeurs CURSOR FOR
        SELECT numElecteur, numCIN, nom, prenom, dateNaissance, lieuNaissance, sexe, bureauVote
        FROM ElecteurTemporaireValide 
        WHERE idTentative = p_idTentative;
    
    -- Handler pour fin de curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;
    
    OPEN c_electeurs;
    
    -- Parcourir tous les électeurs importés dans la table temporaire
    c_electeurs_loop: LOOP
        FETCH c_electeurs INTO v_numElecteur, v_numCIN, v_nom, v_prenom, v_dateNaissance, 
                              v_lieuNaissance, v_sexe, v_bureauVote;
        
        IF v_fin = 1 THEN
            LEAVE c_electeurs_loop;
        END IF;
        
        SET v_erreur = '';
        SET v_cin_valide = TRUE;
        SET v_num_electeur_valide = TRUE;
        SET v_info_complete = TRUE;
        SET v_format_valide = TRUE;
        SET v_cin_unique = TRUE;
        SET v_num_electeur_unique = TRUE;
        
        -- Vérifier format CIN (20 caractères max)
        IF LENGTH(v_numCIN) > 20 OR LENGTH(v_numCIN) < 5 THEN
            SET v_cin_valide = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Format CIN invalide; ');
        END IF;
        
        -- Vérifier format numéro électeur (20 caractères max)
        IF LENGTH(v_numElecteur) > 20 OR LENGTH(v_numElecteur) < 5 THEN
            SET v_num_electeur_valide = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Format numéro électeur invalide; ');
        END IF;
        
        -- Vérifier unicité CIN (hors table temporaire)
        SELECT COUNT(*) INTO v_count FROM Electeur WHERE numCIN = v_numCIN;
        IF v_count > 0 THEN
            SET v_cin_unique = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'CIN déjà utilisé; ');
        END IF;
        
        -- Vérifier unicité numéro électeur (hors table temporaire)
        SELECT COUNT(*) INTO v_count FROM Electeur WHERE numElecteur = v_numElecteur;
        IF v_count > 0 THEN
            SET v_num_electeur_unique = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Numéro électeur déjà utilisé; ');
        END IF;
        
        -- Vérifier complétude des informations
        IF v_nom IS NULL OR TRIM(v_nom) = '' THEN
            SET v_info_complete = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Nom manquant; ');
        END IF;
        
        IF v_prenom IS NULL OR TRIM(v_prenom) = '' THEN
            SET v_info_complete = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Prénom manquant; ');
        END IF;
        
        IF v_dateNaissance IS NULL THEN
            SET v_info_complete = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Date de naissance manquante; ');
        END IF;
        
        IF v_lieuNaissance IS NULL OR TRIM(v_lieuNaissance) = '' THEN
            SET v_info_complete = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Lieu de naissance manquant; ');
        END IF;
        
        IF v_sexe IS NULL OR (v_sexe != 'M' AND v_sexe != 'F') THEN
            SET v_info_complete = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Sexe invalide (doit être M ou F); ');
        END IF;
        
        IF v_bureauVote IS NULL OR TRIM(v_bureauVote) = '' THEN
            SET v_info_complete = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Bureau de vote manquant; ');
        END IF;
        
        -- Vérifier présence de caractères avec accent
        IF ContientAccent(v_nom) OR ContientAccent(v_prenom) OR ContientAccent(v_lieuNaissance) THEN
            SET v_format_valide = FALSE;
            SET v_erreur = CONCAT(v_erreur, 'Caractères avec accent détectés; ');
        END IF;
        
        -- Si des erreurs sont détectées, insérer dans la table des électeurs invalides
        IF NOT (v_cin_valide AND v_num_electeur_valide AND v_info_complete AND 
                v_format_valide AND v_cin_unique AND v_num_electeur_unique) THEN
            
            INSERT INTO Electeur_temporaire (
                numElecteur,
                numCIN,
                nom,
                prenom,
                erreur,
                idTentative
            ) VALUES (
                v_numElecteur,
                v_numCIN,
                v_nom,
                v_prenom,
                v_erreur,
                p_idTentative
            );
            
            SET v_electeurs_invalides = v_electeurs_invalides + 1;
        END IF;
    END LOOP;
    
    CLOSE c_electeurs;
    
    -- Retourner vrai si aucun électeur invalide n'a été trouvé
    RETURN (v_electeurs_invalides = 0);
END//
DELIMITER ;

-- Procédure pour valider l'importation après contrôle
DELIMITER //
CREATE PROCEDURE ValiderImportation(
    p_idTentative INT,
    p_idMembre INT
)
BEGIN
    DECLARE v_etat_upload BOOLEAN;
    DECLARE v_idFichier INT;
    DECLARE v_role VARCHAR(50);
    
    -- Gestion des erreurs
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Réinitialiser l'état d'upload et annuler la transaction
        UPDATE Parametres SET etatUploadElecteurs = FALSE;
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erreur lors de la validation de l\'importation';
    END;
    
    START TRANSACTION;
    
    -- Vérifier si un upload est déjà en cours
    SELECT etatUploadElecteurs INTO v_etat_upload FROM Parametres LIMIT 1;
    
    IF v_etat_upload = TRUE THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un upload est déjà en cours. Opération impossible.';
    END IF;
    
    -- Vérifier si le membre a les droits nécessaires
    SELECT role INTO v_role FROM Membre_dge WHERE idMembre = p_idMembre;
    
    IF v_role != 'ADMIN' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seuls les administrateurs peuvent valider une importation.';
    END IF;
    
    -- Obtenir l'ID du fichier associé à la tentative
    SELECT idFichier INTO v_idFichier FROM Tentative_upload WHERE idTentative = p_idTentative;
    
    -- Définir l'état d'upload comme actif
    UPDATE Parametres SET etatUploadElecteurs = TRUE;
    
    -- Transférer les électeurs de la table temporaire vers la table persistante
    INSERT INTO Electeur (
        numElecteur,
        numCIN,
        nom,
        prenom,
        dateNaissance,
        lieuNaissance,
        sexe,
        bureauVote
    )
    SELECT 
        numElecteur,
        numCIN,
        nom,
        prenom,
        dateNaissance,
        lieuNaissance,
        sexe,
        bureauVote
    FROM ElecteurTemporaireValide
    WHERE idTentative = p_idTentative;
    
    -- Mettre à jour l'état de validation du fichier
    UPDATE Fichier_electoral 
    SET etatValidation = TRUE,
        dateValidation = NOW(),
        idMembreValidation = p_idMembre
    WHERE idFichier = v_idFichier;
    
    -- Enregistrer l'action dans le journal
    INSERT INTO Journal_actions (
        idMembre,
        action,
        dateAction,
        details
    ) VALUES (
        p_idMembre,
        'VALIDATION_FICHIER',
        NOW(),
        CONCAT('Validation du fichier électoral ID: ', v_idFichier, ', Tentative ID: ', p_idTentative)
    );
    
    -- Vider la table temporaire des électeurs valides pour cette tentative
    DELETE FROM ElecteurTemporaireValide WHERE idTentative = p_idTentative;
    
    -- Vider également la table des électeurs invalides pour cette tentative
    DELETE FROM Electeur_temporaire WHERE idTentative = p_idTentative;
    
    -- Réinitialiser l'état d'upload
    UPDATE Parametres SET etatUploadElecteurs = FALSE;
    
    COMMIT;
END//
DELIMITER ;

-- Procédure pour importer le fichier CSV dans la table temporaire
DELIMITER //
CREATE PROCEDURE ImporterFichierCSV(
    p_idFichier INT,
    p_idTentative INT,
    p_cheminFichier VARCHAR(500)
)
BEGIN
    -- Note: MySQL n'a pas d'équivalent direct à UTL_FILE d'Oracle
    -- L'importation de fichiers CSV doit généralement se faire via LOAD DATA INFILE
    -- Cet exemple suppose que vous avez la commande LOAD DATA INFILE activée

    -- Créer une table temporaire pour l'importation
    CREATE TEMPORARY TABLE temp_import (
        ligne TEXT
    );
    
    -- Importer le fichier CSV dans la table temporaire
    -- Note: Cette commande nécessite des privilèges FILE sur le serveur MySQL
    SET @sql = CONCAT('LOAD DATA INFILE ''', p_cheminFichier, 
                     ''' INTO TABLE temp_import LINES TERMINATED BY ''\n''');
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    -- Ignorer la première ligne (en-tête)
    DELETE FROM temp_import LIMIT 1;
    
    -- Traiter les données ligne par ligne
    -- Note: Cette approche est simplifiée et nécessiterait un traitement plus robuste en production
    INSERT INTO ElecteurTemporaireValide (
        numElecteur,
        numCIN,
        nom,
        prenom,
        dateNaissance,
        lieuNaissance,
        sexe,
        bureauVote,
        idTentative
    )
    SELECT 
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 1), ',', -1),
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 2), ',', -1),
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 3), ',', -1),
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 4), ',', -1),
        STR_TO_DATE(SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 5), ',', -1), '%Y-%m-%d'),
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 6), ',', -1),
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 7), ',', -1),
        SUBSTRING_INDEX(SUBSTRING_INDEX(ligne, ',', 8), ',', -1),
        p_idTentative
    FROM temp_import;
    
    -- Supprimer la table temporaire
    DROP TEMPORARY TABLE IF EXISTS temp_import;
END//
DELIMITER ;

-- Procédure pour obtenir les informations sur un membre DGE
DELIMITER //
CREATE PROCEDURE ObtenirInfosMembre(
    IN p_idMembre INT
)
BEGIN
    SELECT 
        idMembre,
        nom,
        prenom,
        email,
        telephone,
        role
    FROM Membre_dge
    WHERE idMembre = p_idMembre;
END//
DELIMITER ;

-- Procédure pour journaliser les actions des membres
DELIMITER //
CREATE PROCEDURE JournaliserAction(
    p_idMembre INT,
    p_action VARCHAR(100),
    p_details VARCHAR(4000)
)
BEGIN
    INSERT INTO Journal_actions (
        idMembre,
        action,
        dateAction,
        details
    ) VALUES (
        p_idMembre,
        p_action,
        NOW(),
        p_details
    );
END//
DELIMITER ;

-- Création des tables nécessaires
CREATE TABLE Journal_actions (
 idAction INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
 idMembre INTEGER NOT NULL REFERENCES Membre_dge(idMembre),
action VARCHAR2(100) NOT NULL,
 dateAction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
 details VARCHAR2(4000)
);
-- Ajout d'un champ pour stocker le chemin du fichier
ALTER TABLE Fichier_electoral ADD (
 cheminFichier VARCHAR2(500),
 dateValidation TIMESTAMP WITH TIME ZONE,
 idMembreValidation INTEGER REFERENCES Membre_dge(idMembre)
);
-- Création d'une table de paramètres (si elle n'existe pas déjà)
CREATE TABLE Parametres (
 etatUploadElecteurs BOOLEAN DEFAULT FALSE
);
-- Insertion d'une ligne initiale dans la table de paramètres
INSERT INTO Parametres (etatUploadElecteurs) VALUES (FALSE);
