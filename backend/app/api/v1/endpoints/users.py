# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.membre_dge import MembreDGECreate, MembreDGEOut
from app.models.membre_dge import MembreDGE
from app.core.database import get_db
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=MembreDGEOut)
def create_user(user: MembreDGECreate, db: Session = Depends(get_db)):
    hashed = get_password_hash(user.password)
    db_user = MembreDGE(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        telephone=user.telephone,
        role=user.role,
        hashed_password=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

