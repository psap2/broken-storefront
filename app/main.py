from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import carts, orders, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Storefront API", lifespan=lifespan)

app.include_router(products.router)
app.include_router(carts.router)
app.include_router(orders.router)


@app.get("/health")
def health():
    return {"status": "ok"}
