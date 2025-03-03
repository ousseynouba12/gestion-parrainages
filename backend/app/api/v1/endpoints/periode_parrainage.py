from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.periode_parrainage import PeriodeParrainage
from app.schemas.periode_parrainage import PeriodeParrainageBase, PeriodeParrainage

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PeriodeParrainage)
def create_periode(periode: PeriodeParrainageBase, db: Session = Depends(get_db)):
    db_periode = PeriodeParrainage(**periode.dict())
    db.add(db_periode)
    db.commit()
    db.refresh(db_periode)
    return db_periode

