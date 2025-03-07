from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):  # ✅ Ajout de UserCreate
    email: str
    password: str
    role: str  # Ajoute le rôle si nécessaire