import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement

class Settings:
    PROJECT_NAME: str = "Gestion des Parrainages"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()


