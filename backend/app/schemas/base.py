from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # Pour SQLAlchemy ORM

