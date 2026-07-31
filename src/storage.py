"""
storage.py
Simple JSON-file backed storage for expenses.

Design notes:
- Data is persisted to a JSON file on disk (no database required by the assignment).
- A threading.Lock guards writes so concurrent requests don't corrupt the file.
- IDs are integers, auto-incremented based on the current max id in the file.
"""

import json
import os
import threading
from typing import Dict, List, Optional


class ExpenseStore:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._lock = threading.Lock()
        directory = os.path.dirname(self.filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.filepath):
            self._write([])

    def _read(self) -> List[Dict]:
        with open(self.filepath, "r") as f:
            return json.load(f)

    def _write(self, data: List[Dict]) -> None:
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, title: str, amount: float, category: str, date: str) -> Dict:
        with self._lock:
            data = self._read()
            new_id = (max((e["id"] for e in data), default=0)) + 1
            record = {
                "id": new_id,
                "title": title,
                "amount": round(float(amount), 2),
                "category": category,
                "date": date,
            }
            data.append(record)
            self._write(data)
            return record

    def get_all(self, category: Optional[str] = None) -> List[Dict]:
        data = self._read()
        if category:
            data = [e for e in data if e["category"].lower() == category.lower()]
        return data

    def get_total(self, category: Optional[str] = None) -> float:
        data = self.get_all(category=category)
        return round(sum(e["amount"] for e in data), 2)

    def search(self, query: str) -> List[Dict]:
        q = query.lower()
        return [e for e in self._read() if q in e["title"].lower()]

    def delete(self, expense_id: int) -> bool:
        with self._lock:
            data = self._read()
            new_data = [e for e in data if e["id"] != expense_id]
            if len(new_data) == len(data):
                return False
            self._write(new_data)
            return True

    def clear(self) -> None:
        with self._lock:
            self._write([])
