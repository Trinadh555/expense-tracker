"""
main.py
Smart Expense Tracker API (Flask).

Endpoints:
  POST   /expenses            -> add an expense
  GET    /expenses             -> list all expenses (optional ?category=Food)
  GET    /expenses/total       -> total of all expenses (optional ?category=Food)
  GET    /expenses/search      -> search expenses by title (?q=coffee)  [bonus]
  DELETE /expenses/<id>        -> delete an expense by id

Uses an app-factory (create_app) so tests can point at an isolated data file
instead of the real data/expenses.json used in production.
"""

import os
from flask import Flask, jsonify, request

from src.storage import ExpenseStore

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expenses.json")

REQUIRED_FIELDS = {"title", "amount", "category", "date"}


def create_app(data_file: str = DEFAULT_DATA_FILE) -> Flask:
    app = Flask(__name__)
    store = ExpenseStore(data_file)
    app.store = store  # exposed for convenience / tests

    @app.post("/expenses")
    def add_expense():
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "Request body must be JSON"}), 400

        missing = REQUIRED_FIELDS - body.keys()
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(sorted(missing))}"}), 400

        title = body["title"]
        category = body["category"]
        date = body["date"]
        amount = body["amount"]

        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "title must be a non-empty string"}), 400
        if not isinstance(category, str) or not category.strip():
            return jsonify({"error": "category must be a non-empty string"}), 400
        if not isinstance(date, str) or not date.strip():
            return jsonify({"error": "date must be a non-empty string (e.g. 2026-07-31)"}), 400
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return jsonify({"error": "amount must be a number"}), 400
        if amount <= 0:
            return jsonify({"error": "amount must be greater than 0"}), 400

        record = store.add(title=title, amount=amount, category=category, date=date)
        return jsonify(record), 201

    @app.get("/expenses")
    def list_expenses():
        category = request.args.get("category")
        return jsonify(store.get_all(category=category)), 200

    @app.get("/expenses/total")
    def total_expenses():
        category = request.args.get("category")
        total = store.get_total(category=category)
        if category:
            return jsonify({"category": category, "total": total}), 200
        return jsonify({"total": total}), 200

    @app.get("/expenses/search")
    def search_expenses():
        query = request.args.get("q", "")
        if not query:
            return jsonify({"error": "Query param 'q' is required"}), 400
        return jsonify(store.search(query)), 200

    @app.delete("/expenses/<int:expense_id>")
    def delete_expense(expense_id):
        deleted = store.delete(expense_id)
        if not deleted:
            return jsonify({"error": f"Expense {expense_id} not found"}), 404
        return jsonify({"message": f"Expense {expense_id} deleted"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
