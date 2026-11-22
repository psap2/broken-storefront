def test_create_product(client):
    response = client.post(
        "/products",
        json={"name": "Canvas Tote", "price_cents": 1800, "stock": 5},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Canvas Tote"
    assert body["price_cents"] == 1800
    assert body["stock"] == 5
    assert "id" in body


def test_create_product_rejects_negative_price(client):
    response = client.post("/products", json={"name": "Freebie", "price_cents": -1})

    assert response.status_code == 422


def test_list_products(client, make_product):
    make_product(name="Mug")
    make_product(name="Tote")

    response = client.get("/products")

    assert response.status_code == 200
    assert [p["name"] for p in response.json()] == ["Mug", "Tote"]


def test_list_products_can_filter_to_in_stock(client, make_product):
    make_product(name="Mug", stock=3)
    make_product(name="Poster", stock=0)

    response = client.get("/products", params={"in_stock": True})

    assert [p["name"] for p in response.json()] == ["Mug"]


def test_get_product(client, make_product):
    product = make_product(name="Mug")

    response = client.get(f"/products/{product['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Mug"


def test_get_unknown_product_returns_404(client):
    response = client.get("/products/999")

    assert response.status_code == 404


def test_update_product_price(client, make_product):
    product = make_product(price_cents=1200)

    response = client.patch(f"/products/{product['id']}", json={"price_cents": 1500})

    assert response.status_code == 200
    assert response.json()["price_cents"] == 1500
    assert response.json()["stock"] == product["stock"]
