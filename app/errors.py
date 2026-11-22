"""Domain errors raised by the service layer.

Services know nothing about HTTP. Routers are responsible for translating
these into HTTP responses.
"""


class StorefrontError(Exception):
    pass


class ProductNotFoundError(StorefrontError):
    def __init__(self, product_id: int):
        super().__init__(f"Product {product_id} not found")
        self.product_id = product_id


class CartNotFoundError(StorefrontError):
    def __init__(self, cart_id: int):
        super().__init__(f"Cart {cart_id} not found")
        self.cart_id = cart_id


class CartItemNotFoundError(StorefrontError):
    def __init__(self, cart_id: int, product_id: int):
        super().__init__(f"Product {product_id} is not in cart {cart_id}")
        self.cart_id = cart_id
        self.product_id = product_id


class OrderNotFoundError(StorefrontError):
    def __init__(self, order_id: int):
        super().__init__(f"Order {order_id} not found")
        self.order_id = order_id


class EmptyCartError(StorefrontError):
    def __init__(self, cart_id: int):
        super().__init__(f"Cart {cart_id} is empty")
        self.cart_id = cart_id


class InsufficientStockError(StorefrontError):
    def __init__(self, product_id: int, requested: int, available: int):
        super().__init__(
            f"Not enough stock for product {product_id}: "
            f"requested {requested}, only {available} available"
        )
        self.product_id = product_id
        self.requested = requested
        self.available = available
