from fastapi import FastAPI
from app.api.routes.users import router as users_router  # Import correct du router 

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}

