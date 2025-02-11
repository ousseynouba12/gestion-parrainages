from fastapi import FastAPI
from app.api.routes import users 
app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}

