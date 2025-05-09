from fastapi.middleware.cors import CORSMiddleware

def setup_middlewares(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Mettre les domaines autorisés en prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

