from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import model
from database.database import engine, get_db
#from router.router import router
from router.product import product_router
from router.user import user_router
from router.order import order_router
from router.cart import cart_router

app = FastAPI()

model.Base.metadata.create_all(engine)

#app.include_router(router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(order_router)





#app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

