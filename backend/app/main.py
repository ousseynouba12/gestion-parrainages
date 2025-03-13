from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_router
from app.core.config import settings
from app.core.middleware import setup_middlewares

# Initialisation de l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour la gestion des parrainages aux élections présidentielles au Sénégal.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inclusion des routes
app.include_router(api_router, prefix="/api/v1")

# Route de test
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API de gestion des parrainages !"}


