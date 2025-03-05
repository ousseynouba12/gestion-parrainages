from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.parrainage import Parrainage
from app.models.candidat import Candidat
from app.models.parrain import Parrain
from app.schemas.parrainage import ParrainageBase
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
from datetime import date

from app.core.database import get_db
from app.models.parrain import Parrain
from app.models.electeur import Electeur
from app.models.candidat import Candidat
from app.schemas.parrain import ParrainBase, ParrainCreate, Parrain as ParrainSchema
from app.services.code_validation_generator import parrain_code_generator_service
from app.services.hashing import hash_code, verify_code

router = APIRouter()

@router.post("/", response_model=dict)
def create_parrainage(parrainage: ParrainageBase, db: Session = Depends(get_db)):
    """
    Un électeur parraine un candidat après validation du code
    """
    # Vérifications existantes
    parrain = db.query(Parrain).filter(Parrain.numElecteur == parrainage.numElecteur).first()
    if not parrain:
        raise HTTPException(status_code=400, detail="Cet électeur n'est pas enregistré comme parrain.")

    candidat = db.query(Candidat).filter(Candidat.numElecteur == parrainage.numCandidat).first()
    if not candidat:
        raise HTTPException(status_code=400, detail="Le candidat spécifié n'existe pas.")

    parrainage_existant = db.query(Parrainage).filter(Parrainage.numElecteur == parrainage.numElecteur).first()
    if parrainage_existant:
        raise HTTPException(status_code=400, detail="Un électeur ne peut parrainer qu'un seul candidat.")

    # Nouvelle vérification du code
    try:
        is_valid = parrain_code_generator_service.verify_code(
            db=db,
            num_parrain=parrainage.numElecteur,
            code=parrainage.code_validation
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code de validation invalide ou expiré"
            )

        # Création du parrainage si le code est valide
        db_parrainage = Parrainage(
            numElecteur=parrainage.numElecteur,
            numCandidat=parrainage.numCandidat,
            dateParrainage=datetime.utcnow()
        )

        db.add(db_parrainage)
        db.commit()
        db.refresh(db_parrainage)

        candidat.nbrParrainages += 1
        db.commit()

        return {"message": "Parrainage enregistré avec succès."}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la validation: {str(e)}"
        )
@router.post("/request-codeValidation", status_code=status.HTTP_200_OK)
def request_authentication_code(num_electeur: str, db: Session = Depends(get_db)):
    """
    Demande un nouveau code d'authentification
    """
    try:
        parrain = db.query(Parrain).filter(Parrain.numElecteur == num_electeur).first()
        if not parrain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parrain non trouvé"
            )
        # Générer un nouveau code
        new_code = parrain_code_generator_service.create_authentication_code(db, num_electeur, send_notifications=True)

        return {"message": "Nouveau code envoyé"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )
@router.post("/verify-codeValidation", status_code=status.HTTP_200_OK)
def verify_authentication_code(num_electeur: str, code: str, db: Session = Depends(get_db)):
    """
    Vérifie un code d'authentification avec gestion des tentatives
    """
    try:
        is_valid = parrain_code_generator_service.verify_code(db, num_electeur, code)
        return {"valid": is_valid}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur vérification: {str(e)}"
        )
@router.get("/candidat/{numCandidat}", response_model=dict)
def get_nombre_parrainages(numCandidat: str, db: Session = Depends(get_db)):
    """
    Récupère uniquement le nombre total de parrainages d'un candidat.
    """
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numCandidat).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")

    return {"numCandidat": numCandidat, "nbrParrainages": candidat.nbrParrainages}

