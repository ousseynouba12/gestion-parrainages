from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import hashlib
import shutil
from datetime import datetime
import aiohttp
import tempfile

from app.core.database import get_db
from app.models.fichier_electoral import FichierElectoral
from app.models.tentative_upload import TentativeUpload
from app.models.electeur_temporaire import ElecteurTemporaire
from app.models.electeur_temporaire_valide import ElecteurTemporaireValide
from app.models.parametres import Parametres
from app.models.journal_actions import JournalActions
from app.schemas.fichier_electoral import FichierElectoralCreate, FichierElectoralDB
from app.schemas.tentative_upload import TentativeUploadDB
from app.core.auth import get_current_membre

router = APIRouter()

# Configuration pour le stockage des fichiers
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Fonction pour calculer le SHA256 d'un fichier
def calculer_sha256(fichier_path):
    sha256_hash = hashlib.sha256()
    with open(fichier_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Vérifier si un fichier est encodé en UTF-8
def est_utf8(fichier_path):
    try:
        with open(fichier_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False

# Route pour uploader un fichier électoral
@router.post("/upload/", response_model=TentativeUploadDB)
async def upload_fichier_electoral(
    request: Request,
    fichier: UploadFile = File(...),
    checksum: str = Form(...),
    db: Session = Depends(get_db),
    membre_actuel = Depends(get_current_membre)
):
    # Vérifier si un upload est déjà en cours
    parametres = db.query(Parametres).first()
    if parametres and parametres.etatUploadElecteurs:
        raise HTTPException(
            status_code=400,
            detail="Un upload est déjà en cours. Veuillez réessayer plus tard."
        )
    
    # Créer un chemin de fichier unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"{timestamp}_{fichier.filename}"
    chemin_fichier = os.path.join(UPLOAD_DIR, nom_fichier)
    
    # Sauvegarder le fichier
    with open(chemin_fichier, "wb") as buffer:
        shutil.copyfileobj(fichier.file, buffer)

    # Obtenir l'adresse IP du client
    client_ip = request.client.host
    
    try:
        # Appeler la fonction ControlerFichierElecteurs via une procédure SQL
        query = """
        SELECT ControlerFichierElecteurs(:p_checksum, :p_idMembre, :p_ip, :p_cheminFichier) AS id_tentative
        """
        result = db.execute(
            query, 
            {
                "p_checksum": checksum,
                "p_idMembre": membre_actuel.idMembre,
                "p_ip": client_ip,
                "p_cheminFichier": chemin_fichier
            }
        ).first()
        
        id_tentative = result.id_tentative
        
        if id_tentative < 0:
            raise HTTPException(
                status_code=400,
                detail="Erreur lors du contrôle du fichier électoral."
            )
        
        # Récupérer les informations de la tentative
        tentative = db.query(TentativeUpload).filter(TentativeUpload.idTentative == id_tentative).first()
        
        if not tentative:
            raise HTTPException(
                status_code=404,
                detail="Tentative non trouvée."
            )
        
        # Journaliser l'action
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="UPLOAD_FICHIER",
            details=f"Upload du fichier électoral: {nom_fichier}, ID tentative: {id_tentative}"
        )
        db.add(journal)
        db.commit()
        
        return tentative
        
    except Exception as e:
        # En cas d'erreur, supprimer le fichier uploadé
        if os.path.exists(chemin_fichier):
            os.remove(chemin_fichier)
        
        # Journaliser l'erreur
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="ERREUR_UPLOAD",
            details=f"Erreur lors de l'upload: {str(e)}"
        )
        db.add(journal)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'upload du fichier: {str(e)}"
        )

# Route pour contrôler les électeurs d'une tentative
@router.post("/controle-electeurs/{id_tentative}", response_model=dict)
async def controle_electeurs(
    id_tentative: int,
    db: Session = Depends(get_db),
    membre_actuel = Depends(get_current_membre)
):
    try:
        # Vérifier si la tentative existe
        tentative = db.query(TentativeUpload).filter(TentativeUpload.idTentative == id_tentative).first()
        if not tentative:
            raise HTTPException(
                status_code=404,
                detail="Tentative non trouvée."
            )
        
        # Appeler la fonction ControlerElecteurs
        query = """
        SELECT ControlerElecteurs(:p_idTentative) AS resultat
        """
        result = db.execute(query, {"p_idTentative": id_tentative}).first()
        
        # Récupérer le résultat
        resultat = result.resultat
        
        # Compter les électeurs valides et invalides
        nb_valides = db.query(ElecteurTemporaireValide).filter(
            ElecteurTemporaireValide.idTentative == id_tentative
        ).count()
        
        nb_invalides = db.query(ElecteurTemporaire).filter(
            ElecteurTemporaire.idTentative == id_tentative
        ).count()
        
        # Journaliser l'action
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="CONTROLE_ELECTEURS",
            details=f"Contrôle des électeurs pour la tentative {id_tentative}. Valides: {nb_valides}, Invalides: {nb_invalides}"
        )
        db.add(journal)
        db.commit()
        
        return {
            "success": resultat,
            "message": "Tous les électeurs sont valides." if resultat else "Des électeurs invalides ont été détectés.",
            "nb_valides": nb_valides,
            "nb_invalides": nb_invalides
        }
        
    except Exception as e:
        # Journaliser l'erreur
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="ERREUR_CONTROLE",
            details=f"Erreur lors du contrôle des électeurs: {str(e)}"
        )
        db.add(journal)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du contrôle des électeurs: {str(e)}"
        )

# Route pour récupérer les électeurs invalides d'une tentative
@router.get("/electeurs-invalides/{id_tentative}", response_model=List[dict])
async def get_electeurs_invalides(
    id_tentative: int,
    db: Session = Depends(get_db),
    membre_actuel = Depends(get_current_membre)
):
    electeurs_invalides = db.query(ElecteurTemporaire).filter(
        ElecteurTemporaire.idTentative == id_tentative
    ).all()
    
    return [
        {
            "numElecteur": e.numElecteur,
            "numCIN": e.numCIN,
            "nom": e.nom,
            "prenom": e.prenom,
            "erreur": e.erreur
        }
        for e in electeurs_invalides
    ]

# Route pour valider l'importation
@router.post("/valider-importation/{id_tentative}", response_model=dict)
async def valider_importation(
    id_tentative: int,
    db: Session = Depends(get_db),
    membre_actuel = Depends(get_current_membre)
):
    try:
        # Appeler la procédure ValiderImportation
        query = """
        CALL ValiderImportation(:p_idTentative, :p_idMembre)
        """
        db.execute(
            query, 
            {
                "p_idTentative": id_tentative,
                "p_idMembre": membre_actuel.idMembre
            }
        )
        
        db.commit()
        
        return {
            "success": True,
            "message": "L'importation a été validée avec succès."
        }
        
    except Exception as e:
        db.rollback()
        
        # Journaliser l'erreur
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="ERREUR_VALIDATION",
            details=f"Erreur lors de la validation de l'importation: {str(e)}"
        )
        db.add(journal)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la validation de l'importation: {str(e)}"
        )

# Route pour obtenir l'historique des tentatives d'upload
@router.get("/tentatives/", response_model=List[dict])
async def get_tentatives(
    db: Session = Depends(get_db),
    membre_actuel = Depends(get_current_membre)
):
    tentatives = db.query(
        TentativeUpload.idTentative,
        TentativeUpload.dateTentative,
        TentativeUpload.ip,
        TentativeUpload.resultat,
        FichierElectoral.checksum,
        FichierElectoral.etatValidation
    ).join(
        FichierElectoral,
        TentativeUpload.idFichier == FichierElectoral.idFichier
    ).order_by(
        TentativeUpload.dateTentative.desc()
    ).all()
    
    return [
        {
            "idTentative": t.idTentative,
            "dateTentative": t.dateTentative,
            "ip": t.ip,
            "resultat": t.resultat,
            "checksum": t.checksum,
            "etatValidation": t.etatValidation
        }
        for t in tentatives
    ]

# Route pour télécharger un fichier électoral depuis GitHub
@router.post("/download-github/", response_model=TentativeUploadDB)
async def download_github_file(
    request: Request,
    github_url: str = Form(...),
    checksum: str = Form(...),
    db: Session = Depends(get_db),
    membre_actuel = Depends(get_current_membre)
):
    # Vérifier si un upload est déjà en cours
    parametres = db.query(Parametres).first()
    if parametres and parametres.etatUploadElecteurs:
        raise HTTPException(
            status_code=400,
            detail="Un upload est déjà en cours. Veuillez réessayer plus tard."
        )
    
    # Création d'un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    try:
        # Télécharger le fichier depuis GitHub
        async with aiohttp.ClientSession() as session:
            async with session.get(github_url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Erreur lors du téléchargement du fichier: {response.reason}"
                    )
                
                # Extraire le nom du fichier de l'URL
                nom_fichier = github_url.split('/')[-1]
                
                # Créer un chemin de fichier unique
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nom_fichier_final = f"{timestamp}_{nom_fichier}"
                chemin_fichier = os.path.join(UPLOAD_DIR, nom_fichier_final)
                
                # Sauvegarder le contenu dans le fichier temporaire
                with open(temp_file_path, "wb") as f:
                    f.write(await response.read())
                
                # Copier le fichier temporaire vers le dossier d'uploads
                shutil.copy(temp_file_path, chemin_fichier)
        
        # Obtenir l'adresse IP du client
        client_ip = request.client.host
        
        # Appeler la fonction ControlerFichierElecteurs
        query = """
        SELECT ControlerFichierElecteurs(:p_checksum, :p_idMembre, :p_ip, :p_cheminFichier) AS id_tentative
        """
        result = db.execute(
            query, 
            {
                "p_checksum": checksum,
                "p_idMembre": membre_actuel.idMembre,
                "p_ip": client_ip,
                "p_cheminFichier": chemin_fichier
            }
        ).first()
        
        id_tentative = result.id_tentative
        
        if id_tentative < 0:
            raise HTTPException(
                status_code=400,
                detail="Erreur lors du contrôle du fichier électoral."
            )
        
        # Récupérer les informations de la tentative
        tentative = db.query(TentativeUpload).filter(TentativeUpload.idTentative == id_tentative).first()
        
        if not tentative:
            raise HTTPException(
                status_code=404,
                detail="Tentative non trouvée."
            )
        
        # Journaliser l'action
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="DOWNLOAD_GITHUB",
            details=f"Téléchargement depuis GitHub: {github_url}, ID tentative: {id_tentative}"
        )
        db.add(journal)
        db.commit()
        
        return tentative
        
    except HTTPException:
        raise
    except Exception as e:
        # En cas d'erreur, supprimer les fichiers
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if 'chemin_fichier' in locals() and os.path.exists(chemin_fichier):
            os.remove(chemin_fichier)
        
        # Journaliser l'erreur
        journal = JournalActions(
            idMembre=membre_actuel.idMembre,
            action="ERREUR_DOWNLOAD_GITHUB",
            details=f"Erreur lors du téléchargement depuis GitHub: {str(e)}"
        )
        db.add(journal)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du téléchargement du fichier: {str(e)}"
        )
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)