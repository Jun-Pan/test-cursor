from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from quant_system.core.types import Fill, MarketTick, Order


class SQLiteStorage:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS market_ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                ts TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                ts TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS fills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                ts TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL
            );
            """
        )
        self._conn.commit()

    def insert_tick(self, tick: MarketTick) -> None:
        self._conn.execute(
            "INSERT INTO market_ticks(symbol, ts, price, volume) VALUES (?, ?, ?, ?)",
            (tick.symbol, tick.ts.isoformat(), tick.price, tick.volume),
        )
        self._conn.commit()

    def insert_order(self, order: Order) -> None:
        self._conn.execute(
            "INSERT INTO orders(symbol, ts, side, qty, price) VALUES (?, ?, ?, ?, ?)",
            (order.symbol, order.ts.isoformat(), order.side.value, order.qty, order.price),
        )
        self._conn.commit()

    def insert_fill(self, fill: Fill) -> None:
        self._conn.execute(
            "INSERT INTO fills(symbol, ts, side, qty, price) VALUES (?, ?, ?, ?, ?)",
            (fill.symbol, fill.ts.isoformat(), fill.side.value, fill.qty, fill.price),
        )
        self._conn.commit()

    def get_recent_ticks(self, symbol: str, window_size: int) -> list[MarketTick]:
        with closing(
            self._conn.execute(
                """
                SELECT symbol, ts, price, volume
                FROM market_ticks
                WHERE symbol = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (symbol, window_size),
            )
        ) as cursor:
            rows = cursor.fetchall()

        ticks = [
            MarketTick(
                symbol=row[0],
                ts=datetime.fromisoformat(row[1]),
                price=float(row[2]),
                volume=float(row[3]),
            )
            for row in reversed(rows)
        ]
        return ticks

    def close(self) -> None:
        self._conn.close()
