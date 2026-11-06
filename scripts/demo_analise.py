import pandas as pd

from curacusto.collectors import build_collectors
from curacusto.config import CACHE_TTL_HOURS, PROCESSED_DIR
from curacusto.engine import analyze_item
from curacusto.normalizer import Catalog
from curacusto.storage import Cache


def main() -> None:
    cmed = pd.read_csv(PROCESSED_DIR / "cmed.csv")
    rename = pd.read_csv(PROCESSED_DIR / "rename.csv")
    catalog = Catalog(cmed)
    cache = Cache()
    collectors = build_collectors()

    for text in ["diclofenaco 50mg", "losartana 50mg", "dipirona 500mg"]:
        result = analyze_item(
            text,
            catalog,
            cmed,
            rename,
            collectors,
            cache,
            CACHE_TTL_HOURS,
        )
        print(
            f"{text} -> {result.substancia} | RENAME: {result.in_rename} | PMC: {result.pmc_ms}"
        )
        if result.best_offer:
            print(
                f"  melhor: {result.best_offer.store} R$ {result.best_offer.price:.2f} "
                f"| acima PMC: {result.above_pmc}"
            )
        for offer in result.offers[:5]:
            print(f"   {offer.store} | R$ {offer.price} | {offer.presentation}")


if __name__ == "__main__":
    main()
