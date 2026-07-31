"""
tests/test_api.py

Tests for the Smart Expense Tracker API.

Run with either:
    pytest
or (no extra deps required, uses only the standard library + Flask):
    python -m unittest discover -s tests
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import create_app


class ExpenseAPITestCase(unittest.TestCase):
    def setUp(self):
        # Use a fresh temp file per test so tests never touch real data/expenses.json
        fd, self.temp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(self.temp_path, "w") as f:
            f.write("[]")

        self.app = create_app(data_file=self.temp_path)
        self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.temp_path)

    def add_sample(self, title="Coffee", amount=5.5, category="Food", date="2026-07-30"):
        return self.client.post(
            "/expenses",
            json={"title": title, "amount": amount, "category": category, "date": date},
        )

    def test_add_expense_success(self):
        resp = self.add_sample()
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["title"], "Coffee")
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["amount"], 5.5)

    def test_add_expense_missing_field(self):
        resp = self.client.post("/expenses", json={"title": "Coffee", "amount": 5.5})
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_invalid_amount(self):
        resp = self.add_sample(amount=-10)
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_non_numeric_amount(self):
        resp = self.add_sample(amount="free")
        self.assertEqual(resp.status_code, 400)

    def test_get_all_expenses_empty(self):
        resp = self.client.get("/expenses")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_all_expenses(self):
        self.add_sample(title="Coffee", category="Food")
        self.add_sample(title="Bus", amount=2.0, category="Transport")
        resp = self.client.get("/expenses")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)

    def test_filter_by_category(self):
        self.add_sample(title="Coffee", category="Food")
        self.add_sample(title="Bus", amount=2.0, category="Transport")
        resp = self.client.get("/expenses?category=Food")
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Coffee")

    def test_filter_by_category_case_insensitive(self):
        self.add_sample(title="Coffee", category="Food")
        resp = self.client.get("/expenses?category=food")
        self.assertEqual(len(resp.get_json()), 1)

    def test_total_overall(self):
        self.add_sample(title="Coffee", amount=5.5, category="Food")
        self.add_sample(title="Bus", amount=2.5, category="Transport")
        resp = self.client.get("/expenses/total")
        self.assertEqual(resp.get_json()["total"], 8.0)

    def test_total_by_category(self):
        self.add_sample(title="Coffee", amount=5.5, category="Food")
        self.add_sample(title="Lunch", amount=10.0, category="Food")
        self.add_sample(title="Bus", amount=2.0, category="Transport")
        resp = self.client.get("/expenses/total?category=Food")
        self.assertEqual(resp.get_json()["total"], 15.5)

    def test_delete_expense(self):
        add_resp = self.add_sample()
        expense_id = add_resp.get_json()["id"]
        del_resp = self.client.delete(f"/expenses/{expense_id}")
        self.assertEqual(del_resp.status_code, 200)
        resp = self.client.get("/expenses")
        self.assertEqual(len(resp.get_json()), 0)

    def test_delete_nonexistent_expense(self):
        resp = self.client.delete("/expenses/999")
        self.assertEqual(resp.status_code, 404)

    def test_search_expenses(self):
        self.add_sample(title="Morning Coffee", category="Food")
        self.add_sample(title="Bus ticket", amount=2.0, category="Transport")
        resp = self.client.get("/expenses/search?q=coffee")
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Morning Coffee")

    def test_search_missing_query(self):
        resp = self.client.get("/expenses/search")
        self.assertEqual(resp.status_code, 400)

    def test_ids_increment_and_are_stable_after_delete(self):
        self.add_sample(title="A")
        self.add_sample(title="B")
        self.client.delete("/expenses/1")
        resp = self.add_sample(title="C")
        # New id should be 3 (max existing id + 1), not reused id 1
        self.assertEqual(resp.get_json()["id"], 3)


if __name__ == "__main__":
    unittest.main()
