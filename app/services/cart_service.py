from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import CartItemNotFoundError, CartNotFoundError
from app.models import Cart, CartItem
from app.schemas import CartItemRead, CartRead
from app.services import product_service


def create_cart(db: Session) -> Cart:
    cart = Cart()
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart(db: Session, cart_id: int) -> Cart:
    cart = db.get(Cart, cart_id)
    if cart is None:
        raise CartNotFoundError(cart_id)
    return cart


def add_item(db: Session, cart_id: int, product_id: int, quantity: int) -> Cart:
    cart = get_cart(db, cart_id)
    product = product_service.get_product(db, product_id)

    # If the product is already in the cart, bump the quantity instead of
    # adding a second line.
    existing = db.scalars(
        select(CartItem).where(CartItem.product_id == product.id)
    ).first()

    if existing is not None:
        existing.quantity += quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity))

    db.commit()
    db.refresh(cart)
    return cart


def update_item_quantity(db: Session, cart_id: int, product_id: int, quantity: int) -> Cart:
    cart = get_cart(db, cart_id)
    item = _get_item(db, cart, product_id)
    item.quantity = quantity
    db.commit()
    db.refresh(cart)
    return cart


def remove_item(db: Session, cart_id: int, product_id: int) -> Cart:
    cart = get_cart(db, cart_id)
    item = _get_item(db, cart, product_id)
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart


def _get_item(db: Session, cart: Cart, product_id: int) -> CartItem:
    item = db.scalars(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    ).first()
    if item is None:
        raise CartItemNotFoundError(cart.id, product_id)
    return item


def calculate_total(cart: Cart) -> int:
    """Total price of everything in the cart, in cents."""
    return sum(item.product.price_cents for item in cart.items)


def build_cart_summary(cart: Cart) -> CartRead:
    """Shape a Cart into the response the API returns."""
    items = [
        CartItemRead(
            product_id=item.product_id,
            name=item.product.name,
            unit_price_cents=item.product.price_cents,
            quantity=item.quantity,
            line_total_cents=item.product.price_cents * item.quantity,
        )
        for item in cart.items
    ]
    return CartRead(id=cart.id, items=items, total_cents=calculate_total(cart))
