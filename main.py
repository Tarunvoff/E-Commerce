from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import model
from database.database import engine, get_db
from router.router import router

app = FastAPI()

model.Base.metadata.create_all(engine)

app.include_router(router)

#app.mount("/static", StaticFiles(directory="static"), name="static")



#app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
#app.mount("/images", StaticFiles(directory="images"), name="images")
