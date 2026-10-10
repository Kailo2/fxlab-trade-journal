DROP TABLE IF EXISTS trades;

CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('long', 'short')),
    entry_price REAL NOT NULL,
    exit_price REAL,
    lots REAL NOT NULL,
    pnl REAL,
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
