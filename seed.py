"""Load a few sample products so you can poke at the API by hand.

    python seed.py
    uvicorn app.main:app --reload
"""
from app.database import Base, SessionLocal, engine
from app.models import Product

PRODUCTS = [
    dict(name="Ceramic Mug", description="12oz, dishwasher safe", price_cents=1200, stock=40),
    dict(name="Canvas Tote", description="Heavyweight cotton", price_cents=1800, stock=15),
    dict(name="Enamel Pin", description="Limited run", price_cents=500, stock=3),
    dict(name="Poster (A2)", description="Sold out for now", price_cents=2500, stock=0),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Product).count() == 0:
            db.add_all(Product(**p) for p in PRODUCTS)
            db.commit()
            print(f"Seeded {len(PRODUCTS)} products")
        else:
            print("Products already present, nothing to do")


if __name__ == "__main__":
    main()
