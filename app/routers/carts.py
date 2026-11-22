from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import CartItemNotFoundError, CartNotFoundError, ProductNotFoundError
from app.schemas import CartItemAdd, CartItemUpdate, CartRead
from app.services import cart_service

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post("", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def create_cart(db: Session = Depends(get_db)):
    cart = cart_service.create_cart(db)
    return cart_service.build_cart_summary(cart)


@router.get("/{cart_id}", response_model=CartRead)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    try:
        cart = cart_service.get_cart(db, cart_id)
    except CartNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    return cart_service.build_cart_summary(cart)


@router.post("/{cart_id}/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def add_item(cart_id: int, data: CartItemAdd, db: Session = Depends(get_db)):
    try:
        cart = cart_service.add_item(db, cart_id, data.product_id, data.quantity)
    except (CartNotFoundError, ProductNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    return cart_service.build_cart_summary(cart)


@router.patch("/{cart_id}/items/{product_id}", response_model=CartRead)
def update_item(
    cart_id: int,
    product_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.update_item_quantity(db, cart_id, product_id, data.quantity)
    except (CartNotFoundError, CartItemNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    return cart_service.build_cart_summary(cart)


@router.delete("/{cart_id}/items/{product_id}", response_model=CartRead)
def remove_item(cart_id: int, product_id: int, db: Session = Depends(get_db)):
    try:
        cart = cart_service.remove_item(db, cart_id, product_id)
    except (CartNotFoundError, CartItemNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    return cart_service.build_cart_summary(cart)
