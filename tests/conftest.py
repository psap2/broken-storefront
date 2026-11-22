import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    """An API client backed by a fresh, empty in-memory database.

    Like the real app, every request gets its own database session.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def make_product(client):
    """Create a product through the API and return its JSON."""

    def _make_product(name="Ceramic Mug", price_cents=1200, stock=10):
        response = client.post(
            "/products",
            json={"name": name, "price_cents": price_cents, "stock": stock},
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _make_product


@pytest.fixture
def make_cart(client):
    """Create an empty cart through the API and return its id."""

    def _make_cart():
        response = client.post("/carts")
        assert response.status_code == 201, response.text
        return response.json()["id"]

    return _make_cart


@pytest.fixture
def add_to_cart(client):
    """Add a product to a cart through the API and return the cart JSON."""

    def _add_to_cart(cart_id, product_id, quantity=1):
        response = client.post(
            f"/carts/{cart_id}/items",
            json={"product_id": product_id, "quantity": quantity},
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _add_to_cart
