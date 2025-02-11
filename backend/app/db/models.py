from app.db.database import engine, Base

# Création des tables
Base.metadata.create_all(bind=engine)

