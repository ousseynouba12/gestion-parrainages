# app/services/electoral_services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile, HTTPException, status
import os
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional

from app.models.fichier_electoral import FichierElectoral
from app.models.tentative_upload import TentativeUpload
from app.models.electeur_temporaire_valide import ElecteurTemporaireValide
from app.models.electeur import Electeur
from app.models.electeur_temporaire import ElecteurTemporaire
from app.models.journal_actions import JournalActions
from app.schemas.electeur_temporaire_valide import ElecteurTemporaireValideBase
from app.utils.file_utils import (
    calculate_sha256, 
    is_utf8, 
    save_uploaded_file, 
    parse_csv_electeurs,
    has_accents,
    validate_cin_format,
    validate_electeur_number
)

# Variable globale pour l'état d'upload des électeurs
ETAT_UPLOAD_ELECTEURS = False

async def controler_fichier_electeurs(
    db: Session, 
    file: UploadFile, 
    checksum: str, 
    membre_id: int, 
    ip_address: str
) -> Tuple[bool, int, str]:
    """
    Cette fonction implémente la logique de ControlerFichierElecteurs.
    Elle vérifie l'empreinte du fichier et son encodage UTF-8.
    """
    # Lire le contenu du fichier
    file_content = await file.read()
    
    # Vérifier si le fichier est déjà en cours de traitement
    if ETAT_UPLOAD_ELECTEURS:
        return False, 0, "Un fichier électoral est déjà en cours de traitement ou validé."
    
    # Calculer l'empreinte SHA256 du fichier
    calculated_checksum = calculate_sha256(file_content)
    
    # Vérifier si l'empreinte correspond
    checksum_match = calculated_checksum.lower() == checksum.lower()
    
    # Vérifier l'encodage UTF-8
    utf8_valid = is_utf8(file_content)
    
    # Si l'une des vérifications échoue, enregistrer une tentative échouée
    if not (checksum_match and utf8_valid):
        # Créer une entrée dans le fichier électoral
        fichier = FichierElectoral(
            checksum=calculated_checksum,
            dateUpload=datetime.now(),
            idMembre=membre_id,
            etatValidation=False
        )
        db.add(fichier)
        db.commit()
        db.refresh(fichier)
        
        # Créer une entrée dans les tentatives d'upload
        tentative = TentativeUpload(
            idFichier=fichier.idFichier,
            dateTentative=datetime.now(),
            ip=ip_address,
            clefUtilisee=checksum,
            resultat=False
        )
        db.add(tentative)
        db.commit()
        db.refresh(tentative)
        
        # Journaliser l'action
        journal = JournalActions(
            idMembre=membre_id,
            action="CONTROLE_FICHIER",
            dateAction=datetime.now(),
            details=f"Fichier ID: {fichier.idFichier}, Résultat: ÉCHEC, Raisons: "
                   f"{'Checksum incorrect' if not checksum_match else ''} "
                   f"{'Encodage non UTF-8' if not utf8_valid else ''}"
        )
        db.add(journal)
        db.commit()
        
        return False, tentative.idTentative, "L'empreinte du fichier ou l'encodage UTF-8 n'est pas valide."
    
    # Si tout est OK, sauvegarder le fichier et créer les entrées en base
    file_path = save_uploaded_file(
        file_content, 
        file.filename, 
        os.path.join("uploads", "electoral_files")
    )
    
    # Créer une entrée dans le fichier électoral
    fichier = FichierElectoral(
        checksum=checksum,
        dateUpload=datetime.now(),
        idMembre=membre_id,
        etatValidation=False
    )
    db.add(fichier)
    db.commit()
    db.refresh(fichier)
    
    # Créer une entrée dans les tentatives d'upload
    tentative = TentativeUpload(
        idFichier=fichier.idFichier,
        dateTentative=datetime.now(),
        ip=ip_address,
        clefUtilisee=checksum,
        resultat=True
    )
    db.add(tentative)
    db.commit()
    db.refresh(tentative)
    
    # Journaliser l'action
    journal = JournalActions(
        idMembre=membre_id,
        action="CONTROLE_FICHIER",
        dateAction=datetime.now(),
        details=f"Fichier ID: {fichier.idFichier}, Résultat: SUCCÈS"
    )
    db.add(journal)
    db.commit()
    
    # Traiter le fichier CSV pour insertion dans la table temporaire
    await file.seek(0)  # Réinitialiser la position du fichier
    
    # Analyser le fichier CSV et insérer dans la table temporaire
    valid_rows, invalid_rows = parse_csv_electeurs(file_path)
    
    # Insérer les lignes valides dans la table temporaire
    for row in valid_rows:
        electeur_temp = ElecteurTemporaireValide(
            numElecteur=row['numElecteur'],
            numCIN=row['numCIN'],
            nom=row['nom'],
            prenom=row['prenom'],
            dateNaissance=row['dateNaissance'],
            lieuNaissance=row['lieuNaissance'],
            sexe=row['sexe'],
            bureauVote=row['bureauVote'],
            idTentative=tentative.idTentative
        )
        db.add(electeur_temp)
    
    # Insérer les lignes invalides dans la table des électeurs problématiques
    for row in invalid_rows:
        electeur_invalide = ElecteurTemporaire(
            numElecteur=row.get('numElecteur', 'INCONNU'),
            numCIN=row.get('numCIN', 'INCONNU'),
            nom=row.get('nom', 'INCONNU'),
            prenom=row.get('prenom', 'INCONNU'),
            erreur=row.get('erreur', 'Format incorrect'),
            idTentative=tentative.idTentative
        )
        db.add(electeur_invalide)
    
    db.commit()
    
    return True, tentative.idTentative, "Le fichier a été validé et chargé avec succès."

def controler_electeurs(db: Session, tentative_id: int) -> Tuple[bool, List[Dict]]:
    """
    Cette fonction implémente la logique de ControlerElecteurs.
    Elle vérifie la complétude et le format des données des électeurs.
    """
    # Récupérer les électeurs temporaires
    electeurs = db.query(ElecteurTemporaire).filter(
        ElecteurTemporaire.idTentative == tentative_id
    ).all()
    
    # Liste pour stocker les erreurs trouvées
    electeurs_problematiques = []
    
    # Parcourir chaque électeur pour validation
    for electeur in electeurs:
        erreurs = []
        
        # Vérifier le format du numéro d'électeur
        if not validate_electeur_number(electeur.numElecteur):
            erreurs.append("Format numéro électeur invalide")
        
        # Vérifier l'unicité du numéro d'électeur
        if db.query(Electeur).filter(Electeur.numElecteur == electeur.numElecteur).first():
            erreurs.append("Numéro électeur déjà existant")
        
        # Vérifier le format de la CIN
        if not validate_cin_format(electeur.numCIN):
            erreurs.append("Format CIN invalide")
        
        # Vérifier l'unicité de la CIN
        if db.query(Electeur).filter(Electeur.numCIN == electeur.numCIN).first():
            erreurs.append("CIN déjà existante")
        
        # Vérifier le nom (non vide et sans accent)
        if not electeur.nom or has_accents(electeur.nom):
            erreurs.append("Nom invalide ou avec accents")
        
        # Vérifier le prénom (non vide et sans accent)
        if not electeur.prenom or has_accents(electeur.prenom):
            erreurs.append("Prénom invalide ou avec accents")
        
        # Vérifier la date de naissance
        if not electeur.dateNaissance or electeur.dateNaissance > datetime.now().date():
            erreurs.append("Date de naissance invalide")
        
        # Vérifier le lieu de naissance
        if not electeur.lieuNaissance:
            erreurs.append("Lieu de naissance non renseigné")
        
        # Vérifier le sexe
        if not electeur.sexe or electeur.sexe not in ['M', 'F']:
            erreurs.append("Sexe invalide (doit être M ou F)")
        
        # Vérifier le bureau de vote
        if not electeur.bureauVote:
            erreurs.append("Bureau de vote non renseigné")
        
        # Si des erreurs ont été trouvées, ajouter l'électeur à la liste des problématiques
        if erreurs:
            # Ajouter l'électeur à la table des problèmes
            electeur_invalide = ElecteurTemporaire(
                numElecteur=electeur.numElecteur,
                numCIN=electeur.numCIN,
                nom=electeur.nom,
                prenom=electeur.prenom,
                erreur="; ".join(erreurs),
                idTentative=tentative_id
            )
            db.add(electeur_invalide)
            
            # Supprimer de la table temporaire valide
            db.delete(electeur)
            
            # Ajouter aux résultats
            electeurs_problematiques.append({
                "numElecteur": electeur.numElecteur,
                "numCIN": electeur.numCIN,
                "nom": electeur.nom,
                "prenom": electeur.prenom,
                "erreurs": erreurs
            })
    
    db.commit()
    
    # Retourner TRUE si aucun électeur problématique n'a été trouvé
    return len(electeurs_problematiques) == 0, electeurs_problematiques

def valider_importation(db: Session, tentative_id: int, membre_id: int) -> bool:
    """
    Cette fonction implémente la logique de ValiderImportation.
    Elle transfère les électeurs temporaires vers la table permanente.
    """
    global ETAT_UPLOAD_ELECTEURS
    
    try:
        # Récupérer l'ID du fichier associé à la tentative
        tentative = db.query(TentativeUpload).filter(
            TentativeUpload.idTentative == tentative_id
        ).first()
        
        if not tentative:
            return False
        
        fichier_id = tentative.idFichier
        
        # Transférer les électeurs temporaires validés vers la table permanente
        electeurs_temp = db.query(ElecteurTemporaireValide).filter(
            ElecteurTemporaireValide.idTentative == tentative_id
        ).all()
        
        for electeur_temp in electeurs_temp:
            electeur = Electeur(
                numElecteur=electeur_temp.numElecteur,
                numCIN=electeur_temp.numCIN,
                nom=electeur_temp.nom,
                prenom=electeur_temp.prenom,
                dateNaissance=electeur_temp.dateNaissance,
                lieuNaissance=electeur_temp.lieuNaissance,
                sexe=electeur_temp.sexe,
                bureauVote=electeur_temp.bureauVote
            )
            db.add(electeur)
        
        # Mettre à jour l'état de validation du fichier
        fichier = db.query(FichierElectoral).filter(
            FichierElectoral.idFichier == fichier_id
        ).first()
        
        if fichier:
            fichier.etatValidation = True
            
        # Supprimer les données temporaires
        db.query(ElecteurTemporaireValide).filter(
            ElecteurTemporaireValide.idTentative == tentative_id
        ).delete()
        
        # Mettre à jour la variable globale pour empêcher un nouvel upload
        ETAT_UPLOAD_ELECTEURS = True
        
        # Journaliser l'action
        journal = JournalActions(
            idMembre=membre_id,
            action="VALIDATION_IMPORTATION",
            dateAction=datetime.now(),
            details=f"Tentative ID: {tentative_id}, Fichier ID: {fichier_id}"
        )
        db.add(journal)
        
        db.commit()
        return True
    
    except SQLAlchemyError as e:
        db.rollback()
        return False

def est_upload_autorise() -> bool:
    """
    Cette fonction vérifie si un nouvel upload est autorisé.
    """
    return not ETAT_UPLOAD_ELECTEURS

def reinitialiser_etat_upload(db: Session, membre_id: int) -> bool:
    """
    Cette fonction réinitialise l'état d'upload (réservée aux administrateurs).
    """
    global ETAT_UPLOAD_ELECTEURS
    
    # Vérifier si le membre est un administrateur
    from app.models.membre_dge import MembreDGE
    membre = db.query(MembreDGE).filter(MembreDGE.idMembre == membre_id).first()
    
    if membre and membre.role == "ADMIN":
        ETAT_UPLOAD_ELECTEURS = False
        
        # Journaliser l'action
        journal = JournalActions(
            idMembre=membre_id,
            action="REINITIALISATION_ETAT_UPLOAD",
            dateAction=datetime.now(),
            details="Réinitialisation de l'état d'upload des électeurs"
        )
        db.add(journal)
        db.commit()
        
        return True
    
    return False

def obtenir_statistiques_importation(db: Session, tentative_id: int) -> Dict:
    """
    Cette fonction récupère les statistiques d'importation.
    """
    # Nombre d'électeurs valides
    nb_valides = db.query(ElecteurTemporaireValide).filter(
        ElecteurTemporaireValide.idTentative == tentative_id
    ).count()
    
    # Nombre d'électeurs invalides
    nb_invalides = db.query(ElecteurTemporaire).filter(
        ElecteurTemporaire.idTentative == tentative_id
    ).count()
    
    # Types d'erreurs
    electeurs_problematiques = db.query(ElecteurTemporaire).filter(
        ElecteurTemporaire.idTentative == tentative_id
    ).all()
    
    erreurs = []
    for electeur in electeurs_problematiques:
        erreurs.extend(electeur.erreur.split(';'))
    
    types_erreurs = list(set([err.strip() for err in erreurs if err.strip()]))
    
    return {
        "nbElecteursValides": nb_valides,
        "nbElecteursInvalides": nb_invalides,
        "typesErreurs": types_erreurs
    }

def rechercher_electeurs_problematiques(db: Session, tentative_id: int, type_erreur: str = None) -> List:
    """
    Cette fonction recherche les électeurs problématiques.
    """
    query = db.query(ElecteurTemporaire).filter(
        ElecteurTemporaire.idTentative == tentative_id
    )
    
    if type_erreur:
        query = query.filter(ElecteurTemporaire.erreur.like(f"%{type_erreur}%"))
    
    electeurs = query.all()
    
    return [
        {
            "numElecteur": e.numElecteur,
            "numCIN": e.numCIN,
            "nom": e.nom,
            "prenom": e.prenom,
            "erreur": e.erreur
        }
        for e in electeurs
    ]