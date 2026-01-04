from fastapi import FastAPI

from app.core.database import engine
from app.models.user import Base
from app.routers import users

#Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "listening"}
