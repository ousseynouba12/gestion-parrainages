from fastapi import FastAPI
from app.api.routes.users import router

app = FastAPI()

app.include_router(router, prefix="/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}
