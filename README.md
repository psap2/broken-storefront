# Broken Storefront

You've just joined the team that owns a small e-commerce API. The previous
maintainer has moved on, a few bug reports have piled up, and the test suite
is red.

Over the next hour you'll work with one of our engineers to get it healthy
again, and then extend it.

## Getting set up

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest              # run the whole suite
pytest -x           # stop at the first failure
pytest -k checkout  # only tests whose name matches "checkout"
```

Start here: **run the tests**

If you'd like to poke at the API by hand:

```bash
python seed.py
uvicorn app.main:app --reload    # interactive docs at http://127.0.0.1:8000/docs
```

## What's in the box

A FastAPI app backed by SQLAlchemy (SQLite), tested with pytest.

```
app/
  main.py          app wiring
  database.py      engine, session, get_db dependency
  models.py        SQLAlchemy models (tables)
  schemas.py       Pydantic request/response shapes
  errors.py        domain errors raised by services
  routers/         HTTP layer: parse the request, call a service, shape the response
  services/        business logic: all the rules and all the database work
tests/             pytest suite, drives the app over HTTP
```

A request flows **router -> service -> database** and back.

| Method | Path                                  | What it does                 |
| ------ | ------------------------------------- | ---------------------------- |
| POST   | `/products`                           | Create a product             |
| GET    | `/products`                           | List products                |
| GET    | `/products/{id}`                      | Fetch one product            |
| PATCH  | `/products/{id}`                      | Update a product             |
| POST   | `/carts`                              | Create an empty cart         |
| GET    | `/carts/{id}`                         | View a cart and its total    |
| POST   | `/carts/{id}/items`                   | Add a product to a cart      |
| PATCH  | `/carts/{id}/items/{product_id}`      | Change a line's quantity     |
| DELETE | `/carts/{id}/items/{product_id}`      | Remove a line                |
| POST   | `/carts/{id}/checkout`                | Turn the cart into an order  |
| GET    | `/orders/{id}`                        | Fetch an order               |

All money is stored as integer cents.

## What's been reported

These came in from the support team. They describe what customers saw, not
where the problem is.

**Ticket 1: Carts are showing the wrong thing.**
> "A customer bought three mugs and the cart total only charged them for one.
> Separately, someone else says a product they added never appeared in their
> cart at all, and another customer says the quantity in theirs went up on
> its own."

**Ticket 2: Inventory is a mess after checkout.**
> "The warehouse says stock numbers on the site never go down no matter how
> much we sell. And when somebody tries to buy more than we have, they get a
> generic 'Internal Server Error' page instead of a sensible message."

## How the hour will go

1. **Diagnose and fix** the reported issues. The failing tests are your map.
2. **A new requirement** will arrive from your interviewer once the suite is
   in better shape. It will be less precisely specified than the bugs.

Some notes:

- You are **not** expected to finish everything. A careful fix you understand
  beats three rushed ones.
- Talk through what you're thinking: what you expect to see, what you
  actually saw, what you're going to check next.
- Find the root cause. Please fix the application, not the tests.
- Ask questions whenever something is ambiguous, especially in the later part.
- Look things up freely. Nobody expects you to have this stack memorised.
