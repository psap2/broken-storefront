from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ProductNotFoundError
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session, in_stock_only: bool = False) -> List[Product]:
    query = select(Product).order_by(Product.id)
    if in_stock_only:
        query = query.where(Product.stock > 0)
    return list(db.scalars(query))


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError(product_id)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product
