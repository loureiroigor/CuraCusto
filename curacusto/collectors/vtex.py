import time
from datetime import datetime, timezone

import requests

from curacusto.config import REQUEST_DELAY_SECONDS, USER_AGENT, VTEX_SEARCH_PATH
from curacusto.models import Offer


class VtexCollector:
    def __init__(
        self,
        store: str,
        base_url: str,
        delay: float = REQUEST_DELAY_SECONDS,
    ):
        self.store = store
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            }
        )

    def search(self, term: str, limit: int = 10) -> list[Offer]:
        response = self.session.get(
            f"{self.base_url}{VTEX_SEARCH_PATH}",
            params={"ft": term, "_from": 0, "_to": max(limit - 1, 0)},
            timeout=30,
        )
        response.raise_for_status()
        collected_at = datetime.now(timezone.utc)
        offers: list[Offer] = []
        for product in response.json():
            offers.extend(self._parse_product(product, term, collected_at))
        time.sleep(self.delay)
        return offers

    def _parse_product(
        self,
        product: dict,
        term: str,
        collected_at: datetime,
    ):
        link = product.get("linkText")
        url = f"{self.base_url}/{link}/p" if link else None
        product_name = product.get("productName") or ""
        brand = product.get("brand")

        for item in product.get("items", []):
            presentation = item.get("name")
            for seller in item.get("sellers", []):
                offer = seller.get("commertialOffer", {})
                price = offer.get("Price")
                if not price:
                    continue
                yield Offer(
                    store=self.store,
                    search_term=term,
                    product_name=product_name,
                    brand=brand,
                    presentation=presentation,
                    price=float(price),
                    list_price=(
                        float(offer["ListPrice"]) if offer.get("ListPrice") else None
                    ),
                    available=bool(
                        offer.get(
                            "IsAvailable",
                            offer.get("AvailableQuantity", 0) > 0,
                        )
                    ),
                    url=url,
                    collected_at=collected_at,
                )
