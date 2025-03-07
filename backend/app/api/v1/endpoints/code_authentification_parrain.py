from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.code_authentification_parrain import CodeAuthentificationParrain
from app.schemas.code_authentification_parrain import CodeAuthentificationParrainBase, CodeAuthentificationParrain

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CodeAuthentificationParrain)
def create_code(code: CodeAuthentificationParrainBase, db: Session = 
Depends(get_db)):
    db_code = CodeAuthentificationParrain(**code.dict())
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

