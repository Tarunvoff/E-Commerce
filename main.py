from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import model
from database.database import engine, get_db
from router.router import router
from router.productrouter import product_router
from router.userrouter import user_router

app = FastAPI()

model.Base.metadata.create_all(engine)

app.include_router(router)
app.include_router(product_router)
app.include_router(user_router)





#app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

