from sqlalchemy.orm import Session

from app.errors import EmptyCartError, InsufficientStockError, OrderNotFoundError
from app.models import Order, OrderItem
from app.services import cart_service


def checkout(db: Session, cart_id: int) -> Order:
    """Turn a cart into an order.

    1. Make sure everything in the cart is actually in stock.
    2. Create the order, copying the current price of each product.
    3. Empty the cart.
    4. Take the purchased units out of inventory.
    """
    cart = cart_service.get_cart(db, cart_id)
    if not cart.items:
        raise EmptyCartError(cart_id)

    for item in cart.items:
        if item.quantity > item.product.stock:
            raise InsufficientStockError(
                product_id=item.product_id,
                requested=item.quantity,
                available=item.product.stock,
            )

    order = Order(cart_id=cart.id, total_cents=0)
    for item in cart.items:
        order.items.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price_cents=item.product.price_cents,
            )
        )
    order.total_cents = sum(
        line.unit_price_cents * line.quantity for line in order.items
    )
    db.add(order)

    cart.items.clear()

    db.commit()
    db.refresh(order)

    for line in order.items:
        line.product.stock -= line.quantity

    return order


def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return order
