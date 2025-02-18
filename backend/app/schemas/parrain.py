from pydantic import BaseModel, EmailStr

class ParrainBase(BaseModel):
    numElecteur: str
    email: EmailStr
    telephone: str
    codeAuthentification: str

class Parrain(ParrainBase):
    class Config:
        from_attributes = True

