from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.membre_dge import MembreDGE
from app.schemas.membre_dge import MembreDGECreation, MembreDGEOUT
import traceback

router = APIRouter()

@router.post("/", response_model=MembreDGEOUT)
def create_membre(membre: MembreDGECreation, db: Session = Depends(get_db)):
    db_membre = db_membre = MembreDGE(**membre.dict())
    try:
        db.add(db_membre)
        db.commit()
        db.refresh(db_membre)
        return db_membre
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création : {str(e)}")

@router.get("/", response_model=list[MembreDGEOUT])
def get_membres(db: Session = Depends(get_db)):
    return db.query(MembreDGE).all()

