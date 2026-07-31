# Smart Expense Tracker API

A small REST API to manage personal expenses, built with **Flask** (Python).
Data is persisted to a local JSON file (`data/expenses.json`) — no database required.

## What it does

- **Add an expense** — `POST /expenses` with `title`, `amount`, `category`, `date`
- **View all expenses** — `GET /expenses`
- **Filter expenses by category** — `GET /expenses?category=Food`
- **Calculate total expenses** (overall and by category) — `GET /expenses/total` and `GET /expenses/total?category=Food`
- **Delete an expense** — `DELETE /expenses/<id>`
- **Bonus: search expenses by title** — `GET /expenses/search?q=coffee`

## Project structure

```
your-repo/
  README.md
  AI_NOTES.md
  requirements.txt
  src/
    __init__.py
    main.py        # Flask app + routes
    storage.py      # JSON-file backed storage layer
  tests/
    test_api.py     # unittest test suite (15 tests)
  data/
    .gitkeep        # expenses.json is created here at runtime (git-ignored)
```

## 1. Install dependencies

```bash

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

python -m pip install -r requirements.txt
```

## 2. Run the server

```bash
python -m flask --app src.main run --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## 3. Run the tests

Tests use only the Python standard library (`unittest`) plus Flask's built-in test
client, so no extra test dependencies are required.

```bash
python -m unittest discover -s tests -v
```

(If you prefer pytest, `pip install pytest` and then just run `pytest` — pytest can
discover and run these `unittest`-style tests too.)

## Example requests

```bash
# Add an expense
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title": "Coffee", "amount": 5.5, "category": "Food", "date": "2026-07-30"}'

# View all expenses
curl http://127.0.0.1:8000/expenses

# Filter by category
curl "http://127.0.0.1:8000/expenses?category=Food"

# Total (overall)
curl http://127.0.0.1:8000/expenses/total

# Total for a category
curl "http://127.0.0.1:8000/expenses/total?category=Food"

# Search by title
curl "http://127.0.0.1:8000/expenses/search?q=coffee"

# Delete an expense
curl -X DELETE http://127.0.0.1:8000/expenses/1
```

## Design notes

- **Storage**: `src/storage.py` wraps all reads/writes to `data/expenses.json` behind
  a small `ExpenseStore` class, guarded by a lock so concurrent requests can't
  corrupt the file. This keeps the persistence logic separate from the HTTP layer.
- **IDs**: auto-incremented integers (`max existing id + 1`), so ids stay stable and
  are never reused after a delete.
- **Validation**: `title`, `category`, and `date` must be non-empty strings; `amount`
  must be a positive number. Invalid input returns `400` with an error message.
- **Testability**: `create_app(data_file=...)` is a small app-factory, so tests point
  at an isolated temp JSON file instead of the real `data/expenses.json`.

## Bonus feature implemented

Search expenses by title: `GET /expenses/search?q=<text>` (case-insensitive substring match).
