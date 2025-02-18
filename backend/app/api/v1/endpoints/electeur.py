from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.electeur import Electeur
from app.schemas.electeur import ElecteurCreation, ElecteurOut, ElecteurBase

router = APIRouter()

@router.post("/", response_model=ElecteurOut)
def create_electeur(electeur: ElecteurCreation, db: Session = Depends(get_db)):
    # Vérifier si l'électeur existe déjà
    electeur_existant = db.query(Electeur).filter(Electeur.numElecteur == electeur.numElecteur).first()
    if electeur_existant:
        raise HTTPException(status_code=400, detail="Cet électeur existe déjà.")

    db_electeur = Electeur(**electeur.model_dump())
    db.add(db_electeur)
    db.commit()
    db.refresh(db_electeur)
    return db_electeur

@router.get("/{numElecteur}", response_model=ElecteurOut)
def get_electeur(numElecteur: str, db: Session = Depends(get_db)):
    electeur = db.query(Electeur).filter(Electeur.numElecteur == numElecteur).first()
    if not electeur:
        raise HTTPException(status_code=404, detail="Électeur non trouvé")
    return electeur

@router.put("/{numElecteur}", response_model=ElecteurOut)
def update_electeur(numElecteur: str, electeur_update: ElecteurCreation, db: Session = Depends(get_db)):
    electeur = db.query(Electeur).filter(Electeur.numElecteur == numElecteur).first()
    if not electeur:
        raise HTTPException(status_code=404, detail="Électeur non trouvé")

    for key, value in electeur_update.model_dump().items():
        setattr(electeur, key, value)

    db.commit()
    db.refresh(electeur)
    return electeur

@router.delete("/{numElecteur}")
def delete_electeur(numElecteur: str, db: Session = Depends(get_db)):
    electeur = db.query(Electeur).filter(Electeur.numElecteur == numElecteur).first()
    if not electeur:
        raise HTTPException(status_code=404, detail="Électeur non trouvé")

    db.delete(electeur)
    db.commit()
    return {"message": "Électeur supprimé avec succès"}

