import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# ---- data access helpers (kept separate from Flask app/request context so
#      they're easy to unit-test against an in-memory sqlite connection) ----

def insert_trade(conn: sqlite3.Connection, trade: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO trades (symbol, direction, entry_price, exit_price, lots,
                             pnl, opened_at, closed_at, notes)
        VALUES (:symbol, :direction, :entry_price, :exit_price, :lots,
                :pnl, :opened_at, :closed_at, :notes)
        """,
        trade,
    )
    conn.commit()
    return cur.lastrowid


def list_trades(conn: sqlite3.Connection, limit: int = 500) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM trades ORDER BY opened_at DESC, id DESC LIMIT ?", (limit,)
    ).fetchall()


def get_trade(conn: sqlite3.Connection, trade_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()


def delete_trade(conn: sqlite3.Connection, trade_id: int) -> None:
    conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
    conn.commit()


def closed_pnls(conn: sqlite3.Connection) -> list[float]:
    rows = conn.execute(
        "SELECT pnl FROM trades WHERE pnl IS NOT NULL ORDER BY opened_at ASC, id ASC"
    ).fetchall()
    return [r["pnl"] for r in rows]
