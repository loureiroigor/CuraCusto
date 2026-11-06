from dataclasses import dataclass
from datetime import datetime


@dataclass
class Offer:
    store: str
    search_term: str
    product_name: str
    brand: str | None
    presentation: str | None
    price: float | None
    list_price: float | None
    available: bool
    url: str | None
    collected_at: datetime
