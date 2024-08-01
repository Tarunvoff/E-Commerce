from fastapi import FastAPI

from database import model
from database.database import engine, get_db
from router.router import router

app = FastAPI()

model.Base.metadata.create_all(engine)

app.include_router(router)

