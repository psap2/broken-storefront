from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Products ----------

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    price_cents: int = Field(ge=0)
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    price_cents: Optional[int] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    price_cents: int
    stock: int


# ---------- Carts ----------

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemRead(BaseModel):
    product_id: int
    name: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int


class CartRead(BaseModel):
    id: int
    items: List[CartItemRead]
    total_cents: int


# ---------- Orders ----------

class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price_cents: int


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cart_id: int
    status: str
    total_cents: int
    created_at: datetime
    items: List[OrderItemRead]
