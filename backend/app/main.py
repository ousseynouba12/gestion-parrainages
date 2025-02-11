from fastapi import FastAPI
from app.api.routes import users 
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

