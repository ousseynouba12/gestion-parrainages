# app/schemas/journal_actions.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class JournalActionCreate(BaseModel):
    idMembre: int
    action: str
    details: Optional[str] = None

class JournalActionDB(JournalActionCreate):
    idAction: int
    dateAction: datetime

    class Config:
        orm_mode = True