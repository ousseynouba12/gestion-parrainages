# app/api/v1/endpoints/electoral.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.core.auth import get_current_membre, verify_admin
from app.services.electoral_services import (
    controler_fichier_electeurs,
    controler_electeurs,
    valider_importation,
    est_upload_autorise,
    reinitialiser_etat_upload,
    obtenir_statistiques_importation,
    rechercher_electeurs_problematiques
)
from app.models.membre_dge import MembreDGE

router = APIRouter()

@router.get("/statut-upload", response_model=Dict[str, bool])
def get_statut_upload():
    """
    Vérifie si un nouvel upload de fichier électoral est autorisé
    """
    return {"upload_autorise": est_upload_autorise()}

@router.post("/upload-fichier-electoral")
async def upload_fichier_electoral(
    request: Request,
    file: UploadFile = File(...),
    checksum: str = Form(...),
    db: Session = Depends(get_db),
    membre: MembreDGE = Depends(get_current_membre)
):
    """
    Upload et contrôle initial du fichier électoral
    """
    # Vérifier si l'upload est autorisé
    if not est_upload_autorise():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un fichier électoral est déjà en cours de traitement ou validé."
        )
    
    # Récupérer l'adresse IP du client
    client_ip = request.client.host
    
    # Contrôler le fichier
    result, tentative_id, message = await controler_fichier_electeurs(
        db, file, checksum, membre.idMembre, client_ip
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "message": message,
        "tentative_id": tentative_id,
        "success": True
    }

@router.post("/controler-electeurs/{tentative_id}")
def verifier_electeurs(
    tentative_id: int,
    db: Session = Depends(get_db),
    membre: MembreDGE = Depends(get_current_membre)
):
    """
    Contrôle la complétude et le format des données des électeurs
    """
    result, electeurs_problematiques = controler_electeurs(db, tentative_id)
    
    # Récupérer les statistiques
    stats = obtenir_statistiques_importation(db, tentative_id)
    
    return {
        "success": result,
        "message": "Tous les électeurs sont valides." if result else f"{len(electeurs_problematiques)} électeurs présentent des problèmes.",
        "statistiques": stats,
        "peut_valider": result and stats["nbElecteursValides"] > 0
    }

@router.post("/valider-importation/{tentative_id}")
def confirmer_importation(
    tentative_id: int,
    db: Session = Depends(get_db),
    membre: MembreDGE = Depends(get_current_membre)
):
    """
    Valide l'importation et transfère les données dans la table permanente
    """
    # Vérifier si tous les électeurs sont validés
    stats = obtenir_statistiques_importation(db, tentative_id)
    
    if stats["nbElecteursInvalides"] > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'importation ne peut pas être validée car des électeurs présentent des problèmes."
        )
    
    if stats["nbElecteursValides"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun électeur valide à importer."
        )
    
    # Valider l'importation
    result = valider_importation(db, tentative_id, membre.idMembre)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur s'est produite lors de la validation de l'importation."
        )
    
    return {
        "success": True,
        "message": f"Importation validée avec succès. {stats['nbElecteursValides']} électeurs importés.",
        "nb_electeurs_importes": stats["nbElecteursValides"]
    }

@router.get("/statistiques-importation/{tentative_id}")
def get_statistiques_importation(
    tentative_id: int,
    db: Session = Depends(get_db),
    membre: MembreDGE = Depends(get_current_membre)
):
    """
    Récupère les statistiques d'une tentative d'importation
    """
    stats = obtenir_statistiques_importation(db, tentative_id)
    return stats

@router.get("/electeurs-problematiques/{tentative_id}")
def get_electeurs_problematiques(
    tentative_id: int,
    type_erreur: Optional[str] = None,
    db: Session = Depends(get_db),
    membre: MembreDGE = Depends(get_current_membre)
):
    """
    Récupère la liste des électeurs problématiques
    Filtrable par type d'erreur
    """
    electeurs = rechercher_electeurs_problematiques(db, tentative_id, type_erreur)
    return {"electeurs": electeurs, "count": len(electeurs)}

@router.post("/reinitialiser-etat-upload", dependencies=[Depends(verify_admin)])
def reset_etat_upload(
    db: Session = Depends(get_db),
    membre: MembreDGE = Depends(get_current_membre)
):
    """
    Réinitialise l'état d'upload pour permettre un nouvel import (admin uniquement)
    """
    result = reinitialiser_etat_upload(db, membre.idMembre)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent réinitialiser l'état d'upload."
        )
    
    return {
        "success": True,
        "message": "État d'upload réinitialisé avec succès."
    }