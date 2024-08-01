from fastapi import FastAPI
from database import model
from database.database import engine

from database.database import get_db



app=FastAPI()


model.Base.metadata.create_all(engine)


from router.router import router
app.include_router(router)
