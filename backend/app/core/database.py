from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Création de l'engine SQLAlchemy
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Création du sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Dépendance pour obtenir une session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

