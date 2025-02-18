from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.parrainage import Parrainage
from app.models.candidat import Candidat
from app.models.parrain import Parrain
from app.schemas.parrainage import ParrainageBase
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=dict)
def create_parrainage(parrainage: ParrainageBase, db: Session = Depends(get_db)):
    """
    Un électeur parraine un candidat.
    """
    # Vérifier si l'électeur est bien un parrain
    parrain = db.query(Parrain).filter(Parrain.numElecteur == parrainage.numElecteur).first()
    if not parrain:
        raise HTTPException(status_code=400, detail="Cet électeur n'est pas enregistré comme parrain.")

    # Vérifier si le candidat existe
    candidat = db.query(Candidat).filter(Candidat.numElecteur == parrainage.numCandidat).first()
    if not candidat:
        raise HTTPException(status_code=400, detail="Le candidat spécifié n'existe pas.")

    # Vérifier si l'électeur a déjà parrainé un candidat
    parrainage_existant = db.query(Parrainage).filter(Parrainage.numElecteur == parrainage.numElecteur).first()
    if parrainage_existant:
        raise HTTPException(status_code=400, detail="Un électeur ne peut parrainer qu'un seul candidat.")

    # Création du parrainage
    db_parrainage = Parrainage(
        numElecteur=parrainage.numElecteur,
        numCandidat=parrainage.numCandidat,
        codeValidation=parrainage.codeValidation,
        dateParrainage=datetime.utcnow()
    )

    try:
        db.add(db_parrainage)
        db.commit()
        db.refresh(db_parrainage)

        # Incrémenter le nombre de parrainages du candidat
        candidat.nbrParrainages += 1
        db.commit()

        return {"message": "Parrainage enregistré avec succès."}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur d'intégrité des données lors de la création du parrainage.")

@router.get("/candidat/{numCandidat}", response_model=dict)
def get_nombre_parrainages(numCandidat: str, db: Session = Depends(get_db)):
    """
    Récupère uniquement le nombre total de parrainages d'un candidat.
    """
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numCandidat).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")

    return {"numCandidat": numCandidat, "nbrParrainages": candidat.nbrParrainages}

