from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import CartNotFoundError, EmptyCartError, OrderNotFoundError
from app.schemas import OrderRead
from app.services import order_service

router = APIRouter(tags=["orders"])


@router.post(
    "/carts/{cart_id}/checkout",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def checkout(cart_id: int, db: Session = Depends(get_db)):
    try:
        return order_service.checkout(db, cart_id)
    except CartNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except EmptyCartError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    try:
        return order_service.get_order(db, order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
