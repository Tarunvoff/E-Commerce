from fastapi import FastAPI
from model import model
from database.database import engine

app=FastAPI()


model.Base.metadata.create_all(engine)
from router.router import router
app.include_router(router)
