from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.tentative_upload import TentativeUpload
from app.schemas.tentative_upload import TentativeUploadBase, TentativeUpload

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TentativeUpload)
def create_tentative(tentative: TentativeUploadBase, db: Session = 
Depends(get_db)):
    db_tentative = TentativeUpload(**tentative.dict())
    db.add(db_tentative)
    db.commit()
    db.refresh(db_tentative)
    return db_tentative

