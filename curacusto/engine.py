import re
from dataclasses import dataclass

from curacusto.normalizer import Catalog, normalize_text


@dataclass
class ItemResult:
    text: str
    substancia: str | None
    produto: str | None
    score: float
    in_rename: bool
    pmc_ms: float | None
    offers: list
    best_offer: object | None
    max_offer: object | None
    above_pmc: bool


def pmc_for_substance(cmed, substancia: str):
    query = normalize_text(substancia)
    normalized = cmed["substancia"].map(normalize_text)
    rows = cmed[normalized == query]
    if rows.empty:
        rows = cmed[normalized.str.contains(query, regex=False)]
    if rows.empty:
        return None
    return float(rows["pmc_ms"].max())


def extract_strength(text: str):
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(mg|mcg|g|ml|ui)", normalize_text(text))
    if not match:
        return None
    return match.group(1).replace(",", "."), match.group(2)


def extract_units(text: str):
    normalized = normalize_text(text)
    match = re.search(
        r"\b(\d+)\s*(comprimidos?|capsulas?|drageas?|gotas?|ml|g)\b",
        normalized,
    )
    if match:
        return int(match.group(1))
    match = re.search(r"\bx\s*(\d+)\b", normalized)
    if match:
        return int(match.group(1))
    return None


SALT_WORDS = {
    "cloridrato",
    "dicloridrato",
    "besilato",
    "citrato",
    "maleato",
    "fumarato",
    "sulfato",
    "tartarato",
    "mesilato",
    "succinato",
    "acetato",
    "fosfato",
    "bromidrato",
    "carbonato",
    "potassico",
    "potassica",
    "sodico",
    "sodica",
    "calcico",
    "calcica",
    "magnesico",
    "magnesica",
    "monoidratado",
    "monoidratada",
    "diidratado",
    "diidratada",
    "anidro",
    "anidra",
    "de",
}


def search_term(substancia: str) -> str:
    parts = re.split(r"[;/+]", substancia)
    cleaned = []
    for part in parts:
        words = [
            word
            for word in normalize_text(part).split()
            if word not in SALT_WORDS
        ]
        if words:
            cleaned.append(" ".join(words))
    return " ".join(cleaned) or normalize_text(substancia)


def pack_size(text: str):
    normalized = normalize_text(text)
    multiple = re.search(r"ct\s*(\d+)\s*bl\b", normalized)
    per_blister = re.search(r"\bx\s*(\d+)\b", normalized)
    if multiple and per_blister:
        return int(multiple.group(1)) * int(per_blister.group(1))
    if per_blister:
        return int(per_blister.group(1))
    return None


def pmc_for_offer(cmed, substancia: str, offer):
    query = normalize_text(substancia)
    normalized = cmed["substancia"].map(normalize_text)
    rows = cmed[normalized == query]
    if rows.empty:
        rows = cmed[normalized.str.contains(query, regex=False)]
    if rows.empty:
        return None

    text = offer.presentation or offer.product_name or ""
    strength = extract_strength(text)
    units = extract_units(text)
    if strength and units:
        value, unit = strength
        strength_pattern = re.compile(rf"(?<!\d){re.escape(value)}\s*{unit}(?!\w)")
        mask = rows["apresentacao"].map(
            lambda item: bool(strength_pattern.search(normalize_text(item)))
            and pack_size(item) == units
        )
        matched = rows[mask]
        if not matched.empty:
            return float(matched["pmc_ms"].max())

    return float(rows["pmc_ms"].max())


def offer_matches(catalog, offer, target_substancia: str) -> bool:
    target_key = search_term(target_substancia)
    text = f"{offer.product_name or ''} {offer.presentation or ''}"
    match = catalog.identify(text)
    if match:
        return search_term(match["substancia"]) == target_key
    return bool(re.search(rf"\b{re.escape(target_key)}\b", normalize_text(text)))


def rename_match(rename_df, substancia: str) -> bool:
    known = {normalize_text(value) for value in rename_df["dcb"].dropna().unique()}
    parts = [normalize_text(part) for part in re.split(r"[;/+]", substancia)]
    return any(part in known for part in parts)


def analyze_item(
    text: str,
    catalog: Catalog,
    cmed,
    rename_df,
    collectors,
    cache,
    ttl_hours: int,
    limit: int = 5,
) -> ItemResult:
    match = catalog.identify(text)
    if not match:
        return ItemResult(text, None, None, 0.0, False, None, [], None, None, False)

    substancia = match["substancia"]
    term = search_term(substancia)
    in_rename = rename_match(rename_df, substancia)
    pmc = pmc_for_substance(cmed, substancia)

    offers = []
    if not in_rename:
        for store, collector in collectors.items():
            if cache.is_fresh(store, term, ttl_hours):
                store_offers = cache.get_offers(store, term)
            else:
                try:
                    store_offers = collector.search(term, limit=limit)
                    cache.save_offers(store_offers)
                except Exception:
                    store_offers = cache.get_offers(store, term)
            offers.extend(store_offers)

    offers = [offer for offer in offers if offer_matches(catalog, offer, substancia)]

    priced = [offer for offer in offers if offer.price]
    best = min(priced, key=lambda offer: offer.price, default=None)
    worst = max(priced, key=lambda offer: offer.price, default=None)

    if best:
        specific_pmc = pmc_for_offer(cmed, substancia, best)
        if specific_pmc:
            pmc = specific_pmc

    above = bool(best and pmc and best.price > pmc)

    return ItemResult(
        text=text,
        substancia=substancia,
        produto=match["produto"],
        score=match["score"],
        in_rename=in_rename,
        pmc_ms=pmc,
        offers=offers,
        best_offer=best,
        max_offer=worst,
        above_pmc=above,
    )


def analyze_recipe(
    texts,
    catalog: Catalog,
    cmed,
    rename_df,
    collectors,
    cache,
    ttl_hours: int,
    limit: int = 5,
) -> list[ItemResult]:
    return [
        analyze_item(
            text,
            catalog,
            cmed,
            rename_df,
            collectors,
            cache,
            ttl_hours,
            limit=limit,
        )
        for text in texts
    ]
