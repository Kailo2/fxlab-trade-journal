import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app import db as db_module


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        with self.app.app_context():
            db_module.init_db()
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_index_loads_empty(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("هنوز معامله", resp.get_data(as_text=True))

    def test_new_trade_form_loads(self):
        resp = self.client.get("/trades/new")
        self.assertEqual(resp.status_code, 200)

    def test_submit_trade_redirects_and_persists(self):
        resp = self.client.post("/trades/new", data={
            "symbol": "eurusd",
            "direction": "long",
            "entry_price": "1.0850",
            "exit_price": "1.0900",
            "lots": "1",
            "pnl": "50",
            "opened_at": "2026-01-15",
            "closed_at": "2026-01-16",
            "notes": "test trade",
        })
        self.assertEqual(resp.status_code, 302)

        index = self.client.get("/")
        body = index.get_data(as_text=True)
        self.assertIn("EURUSD", body)  # symbol uppercased
        self.assertIn("50.0", body)

    def test_missing_required_field_shows_error_not_crash(self):
        resp = self.client.post("/trades/new", data={
            "symbol": "",
            "direction": "long",
            "entry_price": "1.0850",
            "lots": "1",
            "opened_at": "2026-01-15",
        })
        self.assertEqual(resp.status_code, 200)  # re-renders form with flash, no redirect
        self.assertIn("الزامی", resp.get_data(as_text=True))

    def test_invalid_number_shows_error(self):
        resp = self.client.post("/trades/new", data={
            "symbol": "EURUSD",
            "direction": "long",
            "entry_price": "not-a-number",
            "lots": "1",
            "opened_at": "2026-01-15",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("عدد", resp.get_data(as_text=True))

    def test_delete_trade(self):
        self.client.post("/trades/new", data={
            "symbol": "GBPUSD", "direction": "short", "entry_price": "1.27",
            "lots": "1", "opened_at": "2026-02-01", "pnl": "-30",
        })
        with self.app.app_context():
            conn = db_module.get_db()
            trade_id = db_module.list_trades(conn)[0]["id"]

        resp = self.client.post(f"/trades/{trade_id}/delete")
        self.assertEqual(resp.status_code, 302)

        index_body = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("GBPUSD", index_body)

    def test_stats_reflect_submitted_trades(self):
        self.client.post("/trades/new", data={
            "symbol": "EURUSD", "direction": "long", "entry_price": "1.08",
            "lots": "1", "opened_at": "2026-01-01", "pnl": "100",
        })
        self.client.post("/trades/new", data={
            "symbol": "EURUSD", "direction": "short", "entry_price": "1.09",
            "lots": "1", "opened_at": "2026-01-02", "pnl": "-40",
        })
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("60.0", body)  # net pnl = 100 - 40


if __name__ == "__main__":
    unittest.main()
