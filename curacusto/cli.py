import argparse
import sys

from curacusto.collectors import build_collectors
from curacusto.config import CACHE_TTL_HOURS
from curacusto.storage import Cache


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta de precos nas farmacias")
    parser.add_argument("termo", help="nome do medicamento")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    cache = Cache()
    collectors = build_collectors()

    for store, collector in collectors.items():
        if not args.no_cache and cache.is_fresh(store, args.termo, CACHE_TTL_HOURS):
            offers = cache.get_offers(store, args.termo)
            origem = "cache"
        else:
            try:
                offers = collector.search(args.termo, limit=args.limit)
                cache.save_offers(offers)
                origem = "online"
            except Exception as erro:
                offers = cache.get_offers(store, args.termo)
                origem = f"fallback ({erro})"

        print(f"== {store} [{origem}] ==")
        for offer in offers[: args.limit]:
            preco = "sem preco" if offer.price is None else f"R$ {offer.price:8.2f}"
            print(f"  {preco} | {offer.product_name} | {offer.presentation}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    main()
