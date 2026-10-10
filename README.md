# fxlab-trade-journal

A self-hosted **forex trading journal** — log trades, see win rate, profit
factor, expectancy, max drawdown, and an equity curve, all from a small
Flask + SQLite app with zero JS framework and one dependency (Flask itself).

## Features

- Log trades: symbol, direction, entry/exit price, lot size, P&L, dates, notes
- Auto-computed stats: win rate, gross profit/loss, profit factor, expectancy,
  net P&L, best/worst trade, max drawdown
- Equity curve rendered as inline SVG (no chart library, no CDN)
- Delete trades
- Fully covered by automated tests (pure stats functions + Flask request/DB tests)

## Install & run

```bash
git clone https://github.com/Kailo2/fxlab-trade-journal.git
cd fxlab-trade-journal
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=run.py          # or: set FLASK_APP=run.py on Windows
flask init-db                    # creates instance/journal.sqlite
python3 run.py                   # http://127.0.0.1:5000
```

## Project structure

```
app/
  __init__.py       Flask app factory
  db.py             sqlite3 connection + data-access helpers (no ORM)
  schema.sql         table definition
  stats.py           pure statistics functions (win rate, profit factor,
                      expectancy, max drawdown, equity curve) -- no Flask
                      or DB dependency, trivially unit-testable
  routes.py          Blueprint: index, new trade form, delete
  templates/          Jinja2 templates
  static/css/          styling
tests/
  test_stats.py       unit tests for the pure stats functions
  test_app.py          Flask test-client integration tests (real SQLite,
                        temp file per test, full request/response cycle)
run.py                entry point
```

## Why sqlite3 directly instead of an ORM

Keeps the dependency list to exactly one package (Flask). The data-access
functions in `db.py` take a plain `sqlite3.Connection`, so `tests/test_stats.py`
doesn't need a database at all, and `tests/test_app.py` exercises the real
schema against a temp file — no mocking.

## Tests

```bash
python -m unittest discover -s tests -v
```

17 tests: 10 pure-function tests for stats/equity-curve math, 7 Flask
integration tests (form validation, persistence, stats reflecting submitted
trades, delete).

## Disclaimer

Educational / personal-use tool. Not financial advice.

## License

MIT — see [LICENSE](LICENSE).
