import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from curacusto.config import DB_PATH
from curacusto.models import Offer


class Cache:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store TEXT NOT NULL,
                    search_term TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    brand TEXT,
                    presentation TEXT,
                    price REAL,
                    list_price REAL,
                    available INTEGER NOT NULL,
                    url TEXT,
                    collected_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_offers_store_term
                ON offers(store, search_term)
                """
            )

    def save_offers(self, offers: list[Offer]) -> None:
        if not offers:
            return
        store = offers[0].store
        term = offers[0].search_term
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM offers WHERE store = ? AND search_term = ?",
                (store, term),
            )
            conn.executemany(
                """
                INSERT INTO offers (
                    store, search_term, product_name, brand, presentation,
                    price, list_price, available, url, collected_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        offer.store,
                        offer.search_term,
                        offer.product_name,
                        offer.brand,
                        offer.presentation,
                        offer.price,
                        offer.list_price,
                        int(offer.available),
                        offer.url,
                        offer.collected_at.isoformat(),
                    )
                    for offer in offers
                ],
            )

    def get_offers(self, store: str, term: str) -> list[Offer]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT store, search_term, product_name, brand, presentation,
                       price, list_price, available, url, collected_at
                FROM offers
                WHERE store = ? AND search_term = ?
                """,
                (store, term),
            ).fetchall()
        return [
            Offer(
                store=row[0],
                search_term=row[1],
                product_name=row[2],
                brand=row[3],
                presentation=row[4],
                price=row[5],
                list_price=row[6],
                available=bool(row[7]),
                url=row[8],
                collected_at=datetime.fromisoformat(row[9]),
            )
            for row in rows
        ]

    def is_fresh(self, store: str, term: str, ttl_hours: int) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT MAX(collected_at) FROM offers
                WHERE store = ? AND search_term = ?
                """,
                (store, term),
            ).fetchone()
        if not row or not row[0]:
            return False
        collected_at = datetime.fromisoformat(row[0])
        return datetime.now(timezone.utc) - collected_at < timedelta(hours=ttl_hours)
