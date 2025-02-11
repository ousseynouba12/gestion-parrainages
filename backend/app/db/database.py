from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Récupérer l'URL de la BD depuis une variable d'environnement
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:zMjDQSJrIfdTgCvHEXEyRQKWLDxdNJJc@junction.proxy.rlwy.net:16519/railway")

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Définition du modèle de base
Base = declarative_base()

# Fonction pour obtenir une session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
