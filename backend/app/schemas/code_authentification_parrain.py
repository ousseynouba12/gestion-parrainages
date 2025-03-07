from pydantic import BaseModel
from datetime import datetime

class CodeAuthentificationParrainBase(BaseModel):
    numParrain: str
    code: str
    dateEnvoi: datetime

class CodeAuthentificationParrain(CodeAuthentificationParrainBase):
    idCode: int

    class Config:
        from_attributes = True

