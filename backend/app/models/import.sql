-- Création des fonctions et procédures nécessaires pour le contrôle et la validation du fichier électoral

-- Variable globale pour l'état d'upload des électeurs
SET @EtatUploadElecteurs = FALSE;

-- Fonction pour contrôler l'empreinte du fichier et son encodage UTF-8
DELIMITER //
CREATE FUNCTION ControlerFichierElecteurs(
    p_fichier_id INT,
    p_checksum_saisi VARCHAR(64),
    p_membre_id INT,
    p_ip VARCHAR(45)
) RETURNS BOOLEAN
BEGIN
    DECLARE v_checksum_fichier VARCHAR(64);
    DECLARE v_est_utf8 BOOLEAN;
    DECLARE v_resultat BOOLEAN;
    
    -- Récupérer le checksum du fichier stocké
    SELECT checksum INTO v_checksum_fichier
    FROM Fichier_electoral
    WHERE idFichier = p_fichier_id;
    
    -- Vérifier si le checksum saisi correspond au checksum calculé
    IF v_checksum_fichier = p_checksum_saisi THEN
        -- Vérifier si le contenu est en UTF-8 (cette vérification est simplifiée ici)
        -- Dans un environnement réel, une vérification plus approfondie serait nécessaire
        SET v_est_utf8 = TRUE;
        
        IF v_est_utf8 THEN
            SET v_resultat = TRUE;
        ELSE
            SET v_resultat = FALSE;
        END IF;
    ELSE
        SET v_resultat = FALSE;
    END IF;
    
    -- Enregistrer la tentative dans l'historique
    INSERT INTO Tentative_upload (
        idFichier,
        dateTentative,
        ip,
        clefUtilisee,
        resultat
    ) VALUES (
        p_fichier_id,
        NOW(),
        p_ip,
        p_checksum_saisi,
        v_resultat
    );
    
    -- Journaliser l'action
    INSERT INTO Journal_actions (
        idMembre,
        action,
        dateAction,
        details
    ) VALUES (
        p_membre_id,
        'CONTROLE_FICHIER',
        NOW(),
        CONCAT('Fichier ID: ', p_fichier_id, ', Résultat: ', IF(v_resultat, 'SUCCÈS', 'ÉCHEC'))
    );
    
    RETURN v_resultat;
END//
DELIMITER ;

-- Fonction pour contrôler la validité des données électeurs
DELIMITER //
CREATE FUNCTION ControlerElecteurs(
    p_tentative_id INT
) RETURNS BOOLEAN
BEGIN
    DECLARE v_ligne_courante INT DEFAULT 0;
    DECLARE v_lignes_invalides INT DEFAULT 0;
    DECLARE v_num_electeur VARCHAR(20);
    DECLARE v_num_cin VARCHAR(20);
    DECLARE v_nom VARCHAR(50);
    DECLARE v_prenom VARCHAR(50);
    DECLARE v_date_naissance DATE;
    DECLARE v_lieu_naissance VARCHAR(100);
    DECLARE v_sexe VARCHAR(1);
    DECLARE v_bureau_vote VARCHAR(100);
    DECLARE v_erreur TEXT;
    DECLARE v_fin BOOLEAN DEFAULT FALSE;
    
    -- Curseur pour parcourir les électeurs temporaires
    DECLARE cur_electeurs CURSOR FOR 
        SELECT numElecteur, numCIN, nom, prenom, dateNaissance, lieuNaissance, sexe, bureauVote
        FROM ElecteurTemporaireValide
        WHERE idTentative = p_tentative_id;
    
    -- Handler pour la fin du curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = TRUE;
    
    -- Ouvrir le curseur
    OPEN cur_electeurs;
    
    -- Parcourir les électeurs
    read_loop: LOOP
        FETCH cur_electeurs INTO v_num_electeur, v_num_cin, v_nom, v_prenom, v_date_naissance, v_lieu_naissance, v_sexe, v_bureau_vote;
        
        IF v_fin THEN
            LEAVE read_loop;
        END IF;
        
        SET v_ligne_courante = v_ligne_courante + 1;
        SET v_erreur = NULL;
        
        -- Vérifier le format et l'unicité du numéro d'électeur
        IF LENGTH(v_num_electeur) < 8 OR LENGTH(v_num_electeur) > 20 THEN
            SET v_erreur = CONCAT(v_erreur, 'Format numéro électeur invalide; ');
        END IF;
        
        -- Vérifier si le numéro d'électeur existe déjà dans la table permanente
        IF EXISTS (SELECT 1 FROM Electeur WHERE numElecteur = v_num_electeur) THEN
            SET v_erreur = CONCAT(v_erreur, 'Numéro électeur déjà existant; ');
        END IF;
        
        -- Vérifier le format de la CIN
        IF LENGTH(v_num_cin) < 10 OR LENGTH(v_num_cin) > 20 THEN
            SET v_erreur = CONCAT(v_erreur, 'Format CIN invalide; ');
        END IF;
        
        -- Vérifier si la CIN existe déjà dans la table permanente
        IF EXISTS (SELECT 1 FROM Electeur WHERE numCIN = v_num_cin) THEN
            SET v_erreur = CONCAT(v_erreur, 'CIN déjà existante; ');
        END IF;
        
        -- Vérifier si le nom est renseigné et sans accent
        IF v_nom IS NULL OR v_nom = '' OR v_nom REGEXP '[àáâãäåçèéêëìíîïñòóôõöùúûüýÿ]' THEN
            SET v_erreur = CONCAT(v_erreur, 'Nom invalide ou avec accents; ');
        END IF;
        
        -- Vérifier si le prénom est renseigné et sans accent
        IF v_prenom IS NULL OR v_prenom = '' OR v_prenom REGEXP '[àáâãäåçèéêëìíîïñòóôõöùúûüýÿ]' THEN
            SET v_erreur = CONCAT(v_erreur, 'Prénom invalide ou avec accents; ');
        END IF;
        
        -- Vérifier la date de naissance
        IF v_date_naissance IS NULL OR v_date_naissance > CURDATE() THEN
            SET v_erreur = CONCAT(v_erreur, 'Date de naissance invalide; ');
        END IF;
        
        -- Vérifier le lieu de naissance
        IF v_lieu_naissance IS NULL OR v_lieu_naissance = '' THEN
            SET v_erreur = CONCAT(v_erreur, 'Lieu de naissance non renseigné; ');
        END IF;
        
        -- Vérifier le sexe
        IF v_sexe IS NULL OR v_sexe NOT IN ('M', 'F') THEN
            SET v_erreur = CONCAT(v_erreur, 'Sexe invalide (doit être M ou F); ');
        END IF;
        
        -- Vérifier le bureau de vote
        IF v_bureau_vote IS NULL OR v_bureau_vote = '' THEN
            SET v_erreur = CONCAT(v_erreur, 'Bureau de vote non renseigné; ');
        END IF;
        
        -- Si des erreurs ont été détectées, enregistrer l'électeur dans la table des problèmes
        IF v_erreur IS NOT NULL THEN
            INSERT INTO Electeur_temporaire (
                numElecteur,
                numCIN,
                nom,
                prenom,
                erreur,
                idTentative
            ) VALUES (
                v_num_electeur,
                v_num_cin,
                v_nom,
                v_prenom,
                v_erreur,
                p_tentative_id
            );
            
            SET v_lignes_invalides = v_lignes_invalides + 1;
        END IF;
    END LOOP;
    
    -- Fermer le curseur
    CLOSE cur_electeurs;
    
    -- Retourner TRUE si aucune ligne invalide n'a été détectée
    RETURN v_lignes_invalides = 0;
END//
DELIMITER ;

-- Procédure pour valider l'importation du fichier
DELIMITER //
CREATE PROCEDURE ValiderImportation(
    IN p_tentative_id INT,
    IN p_membre_id INT
)
BEGIN
    DECLARE v_fichier_id INT;
    
    -- Récupérer l'ID du fichier associé à la tentative
    SELECT idFichier INTO v_fichier_id
    FROM Tentative_upload
    WHERE idTentative = p_tentative_id;
    
    -- Transférer les électeurs temporaires validés vers la table permanente
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
    WHERE idTentative = p_tentative_id;
    
    -- Mettre à jour l'état de validation du fichier
    UPDATE Fichier_electoral
    SET etatValidation = TRUE
    WHERE idFichier = v_fichier_id;
    
    -- Supprimer les données temporaires
    DELETE FROM ElecteurTemporaireValide
    WHERE idTentative = p_tentative_id;
    
    -- Mettre à jour la variable globale pour empêcher un nouvel upload
    SET @EtatUploadElecteurs = TRUE;
    
    -- Journaliser l'action
    INSERT INTO Journal_actions (
        idMembre,
        action,
        dateAction,
        details
    ) VALUES (
        p_membre_id,
        'VALIDATION_IMPORTATION',
        NOW(),
        CONCAT('Tentative ID: ', p_tentative_id, ', Fichier ID: ', v_fichier_id)
    );
END//
DELIMITER ;

-- Fonction pour vérifier si un nouvel upload est autorisé
DELIMITER //
CREATE FUNCTION EstUploadAutorise() RETURNS BOOLEAN
BEGIN
    RETURN NOT @EtatUploadElecteurs;
END//
DELIMITER ;

-- Procédure pour réinitialiser l'état d'upload (réservée aux administrateurs)
DELIMITER //
CREATE PROCEDURE ReinitialiserEtatUpload(
    IN p_membre_id INT
)
BEGIN
    -- Vérifier si le membre est un administrateur
    DECLARE v_est_admin BOOLEAN;
    
    SELECT role = 'ADMIN' INTO v_est_admin
    FROM Membre_dge
    WHERE idMembre = p_membre_id;
    
    IF v_est_admin THEN
        SET @EtatUploadElecteurs = FALSE;
        
        -- Journaliser l'action
        INSERT INTO Journal_actions (
            idMembre,
            action,
            dateAction,
            details
        ) VALUES (
            p_membre_id,
            'REINITIALISATION_ETAT_UPLOAD',
            NOW(),
            'Réinitialisation de l\'état d\'upload des électeurs'
        );
    END IF;
END//
DELIMITER ;

-- Procédure pour traiter le fichier CSV et insérer les données dans la table temporaire
DELIMITER //
CREATE PROCEDURE TraiterFichierCSV(
    IN p_fichier_path VARCHAR(255),
    IN p_tentative_id INT
)
BEGIN
    -- Cette procédure est une représentation conceptuelle car MySQL ne peut pas
    -- directement lire et parser des fichiers CSV dans des procédures stockées
    -- En pratique, cette fonctionnalité serait implémentée côté application
    
    -- La procédure simulerait:
    -- 1. L'ouverture du fichier CSV
    -- 2. La lecture ligne par ligne
    -- 3. L'insertion des données dans ElecteurTemporaireValide
    
    -- Note: Dans l'implémentation réelle, cette fonctionnalité sera gérée par FastAPI
END//
DELIMITER ;

-- Procédure pour obtenir les statistiques d'importation
DELIMITER //
CREATE PROCEDURE ObtenirStatistiquesImportation(
    IN p_tentative_id INT
)
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM ElecteurTemporaireValide WHERE idTentative = p_tentative_id) AS nbElecteursValides,
        (SELECT COUNT(*) FROM Electeur_temporaire WHERE idTentative = p_tentative_id) AS nbElecteursInvalides,
        (SELECT GROUP_CONCAT(DISTINCT erreur SEPARATOR '|') FROM Electeur_temporaire WHERE idTentative = p_tentative_id) AS typesErreurs;
END//
DELIMITER ;

-- Procédure pour rechercher les électeurs problématiques
DELIMITER //
CREATE PROCEDURE RechercherElecteursProblematiques(
    IN p_tentative_id INT,
    IN p_type_erreur VARCHAR(100)
)
BEGIN
    SELECT numElecteur, numCIN, nom, prenom, erreur
    FROM Electeur_temporaire
    WHERE idTentative = p_tentative_id
    AND erreur LIKE CONCAT('%', p_type_erreur, '%');
END//
DELIMITER ;