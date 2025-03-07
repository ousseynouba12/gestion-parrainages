from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.periode_parrainage import PeriodeParrainage
from app.schemas.periode_parrainage import PeriodeParrainageCreate
from app.core.database import get_db

router = APIRouter()

@router.post("/")
def create_periode(periode: PeriodeParrainageCreate, db: Session = 
Depends(get_db)):
    db_periode = PeriodeParrainage(**periode.dict())
    db.add(db_periode)
    db.commit()
    return {"message": "Période de parrainage ajoutée"}

