def test_checkout_creates_order_from_cart(
    client, make_product, make_cart, add_to_cart
):
    mug = make_product(name="Mug", price_cents=1200)
    tote = make_product(name="Tote", price_cents=1800)
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"], quantity=2)
    add_to_cart(cart_id, tote["id"], quantity=1)

    response = client.post(f"/carts/{cart_id}/checkout")

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "placed"
    assert order["total_cents"] == 4200
    assert order["items"] == [
        {"product_id": mug["id"], "quantity": 2, "unit_price_cents": 1200},
        {"product_id": tote["id"], "quantity": 1, "unit_price_cents": 1800},
    ]


def test_order_can_be_fetched_after_checkout(
    client, make_product, make_cart, add_to_cart
):
    mug = make_product(price_cents=1200)
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"], quantity=1)
    order_id = client.post(f"/carts/{cart_id}/checkout").json()["id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200
    assert response.json()["total_cents"] == 1200


def test_order_keeps_price_paid_even_if_product_price_changes(
    client, make_product, make_cart, add_to_cart
):
    mug = make_product(price_cents=1200)
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"], quantity=1)
    order_id = client.post(f"/carts/{cart_id}/checkout").json()["id"]

    client.patch(f"/products/{mug['id']}", json={"price_cents": 9900})

    order = client.get(f"/orders/{order_id}").json()
    assert order["total_cents"] == 1200
    assert order["items"][0]["unit_price_cents"] == 1200


def test_checkout_empties_the_cart(client, make_product, make_cart, add_to_cart):
    mug = make_product()
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"], quantity=1)

    client.post(f"/carts/{cart_id}/checkout")

    cart = client.get(f"/carts/{cart_id}").json()
    assert cart["items"] == []


def test_checkout_empty_cart_returns_400(client, make_cart):
    cart_id = make_cart()

    response = client.post(f"/carts/{cart_id}/checkout")

    assert response.status_code == 400


def test_checkout_unknown_cart_returns_404(client):
    response = client.post("/carts/999/checkout")

    assert response.status_code == 404


def test_get_unknown_order_returns_404(client):
    response = client.get("/orders/999")

    assert response.status_code == 404


def test_checkout_reduces_product_stock(client, make_product, make_cart, add_to_cart):
    mug = make_product(stock=10)
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"], quantity=3)

    response = client.post(f"/carts/{cart_id}/checkout")
    assert response.status_code == 201

    product = client.get(f"/products/{mug['id']}").json()
    assert product["stock"] == 7


def test_checkout_with_insufficient_stock_returns_409(
    client, make_product, make_cart, add_to_cart
):
    pin = make_product(name="Enamel Pin", stock=2)
    cart_id = make_cart()
    add_to_cart(cart_id, pin["id"], quantity=5)

    response = client.post(f"/carts/{cart_id}/checkout")

    assert response.status_code == 409
    assert "stock" in response.json()["detail"].lower()

    # Nothing should have been sold and the customer keeps their cart.
    assert client.get(f"/products/{pin['id']}").json()["stock"] == 2
    assert len(client.get(f"/carts/{cart_id}").json()["items"]) == 1
