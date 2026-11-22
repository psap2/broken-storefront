def test_new_cart_is_empty(client):
    response = client.post("/carts")

    assert response.status_code == 201
    body = response.json()
    assert body["items"] == []
    assert body["total_cents"] == 0


def test_get_unknown_cart_returns_404(client):
    response = client.get("/carts/999")

    assert response.status_code == 404


def test_add_item_to_cart(client, make_product, make_cart):
    mug = make_product(name="Mug", price_cents=1200)
    cart_id = make_cart()

    response = client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": mug["id"], "quantity": 1},
    )

    assert response.status_code == 201
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["product_id"] == mug["id"]
    assert items[0]["name"] == "Mug"
    assert items[0]["quantity"] == 1


def test_add_unknown_product_returns_404(client, make_cart):
    cart_id = make_cart()

    response = client.post(f"/carts/{cart_id}/items", json={"product_id": 999})

    assert response.status_code == 404


def test_add_item_rejects_zero_quantity(client, make_product, make_cart):
    mug = make_product()
    cart_id = make_cart()

    response = client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": mug["id"], "quantity": 0},
    )

    assert response.status_code == 422


def test_adding_same_product_twice_combines_into_one_line(
    client, make_product, make_cart, add_to_cart
):
    mug = make_product()
    cart_id = make_cart()

    add_to_cart(cart_id, mug["id"], quantity=1)
    cart = add_to_cart(cart_id, mug["id"], quantity=2)

    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 3


def test_update_item_quantity(client, make_product, make_cart, add_to_cart):
    mug = make_product()
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"], quantity=1)

    response = client.patch(
        f"/carts/{cart_id}/items/{mug['id']}", json={"quantity": 5}
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 5


def test_remove_item_from_cart(client, make_product, make_cart, add_to_cart):
    mug = make_product(name="Mug")
    tote = make_product(name="Tote")
    cart_id = make_cart()
    add_to_cart(cart_id, mug["id"])
    add_to_cart(cart_id, tote["id"])

    response = client.delete(f"/carts/{cart_id}/items/{mug['id']}")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == ["Tote"]


def test_remove_item_that_is_not_in_cart_returns_404(client, make_product, make_cart):
    mug = make_product()
    cart_id = make_cart()

    response = client.delete(f"/carts/{cart_id}/items/{mug['id']}")

    assert response.status_code == 404


def test_cart_total_sums_different_products(
    client, make_product, make_cart, add_to_cart
):
    mug = make_product(name="Mug", price_cents=1200)
    tote = make_product(name="Tote", price_cents=1800)
    cart_id = make_cart()

    add_to_cart(cart_id, mug["id"], quantity=1)
    cart = add_to_cart(cart_id, tote["id"], quantity=1)

    assert cart["total_cents"] == 3000


def test_cart_total_accounts_for_quantity(
    client, make_product, make_cart, add_to_cart
):
    mug = make_product(name="Mug", price_cents=1200)
    tote = make_product(name="Tote", price_cents=1800)
    cart_id = make_cart()

    add_to_cart(cart_id, mug["id"], quantity=3)
    cart = add_to_cart(cart_id, tote["id"], quantity=1)

    # 3 x $12.00 + 1 x $18.00
    assert cart["total_cents"] == 5400


def test_each_cart_keeps_its_own_items(client, make_product, make_cart, add_to_cart):
    mug = make_product(name="Mug")
    first_cart_id = make_cart()
    second_cart_id = make_cart()

    add_to_cart(first_cart_id, mug["id"], quantity=1)
    add_to_cart(second_cart_id, mug["id"], quantity=2)

    first_cart = client.get(f"/carts/{first_cart_id}").json()
    second_cart = client.get(f"/carts/{second_cart_id}").json()

    assert len(first_cart["items"]) == 1
    assert first_cart["items"][0]["quantity"] == 1

    assert len(second_cart["items"]) == 1
    assert second_cart["items"][0]["quantity"] == 2
