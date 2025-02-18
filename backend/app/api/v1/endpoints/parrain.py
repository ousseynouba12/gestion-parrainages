from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.parrain import Parrain
from app.schemas.parrain import ParrainBase, Parrain

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Parrain)
def create_parrain(parrain: ParrainBase, db: Session = Depends(get_db)):
    db_parrain = Parrain(**parrain.dict())
    db.add(db_parrain)
    db.commit()
    db.refresh(db_parrain)
    return db_parrain

