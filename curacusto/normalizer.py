import re
import unicodedata

from rapidfuzz import fuzz, process


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class Catalog:
    def __init__(self, cmed):
        unique_products = cmed.drop_duplicates(subset=["produto", "substancia"])
        self.products = [
            {
                "produto": row.produto,
                "substancia": row.substancia,
                "produto_norm": normalize_text(row.produto),
            }
            for row in unique_products.itertuples()
        ]
        self.product_names = [product["produto_norm"] for product in self.products]
        self.product_lookup = {}
        for product in self.products:
            self.product_lookup.setdefault(
                product["produto_norm"],
                {
                    "substancia": product["substancia"],
                    "produto": product["produto"],
                    "score": 100.0,
                    "origem": "produto",
                },
            )

        substances = [value for value in cmed["substancia"].dropna().unique()]
        self.substance_lookup = {}
        self.single_lookup = {}
        self.combination_lookup = {}
        for value in substances:
            key = normalize_text(value)
            self.substance_lookup[key] = value
            if ";" in value or "+" in value:
                self.combination_lookup[key] = value
            else:
                self.single_lookup[key] = value

    def _clean_query(self, text: str) -> str:
        query = normalize_text(text)
        query = re.sub(
            r"\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml|ui|%)\b",
            " ",
            query,
        )
        query = re.sub(
            r"\b(?:comprimidos?|capsulas?|gotas?|solucao|suspensao|creme|pomada)\b",
            " ",
            query,
        )
        return re.sub(r"\s+", " ", query).strip()

    def _match_substances(self, query: str, lookup: dict, threshold: int):
        if not lookup:
            return None
        match = process.extractOne(query, list(lookup), scorer=fuzz.WRatio)
        if match and match[1] >= threshold:
            return {
                "substancia": lookup[match[0]],
                "produto": None,
                "score": match[1],
                "origem": "substancia",
            }
        return None

    def _match_products(self, query: str, threshold: int):
        match = process.extractOne(query, self.product_names, scorer=fuzz.WRatio)
        if match and match[1] >= threshold:
            product = self.products[match[2]]
            return {
                "substancia": product["substancia"],
                "produto": product["produto"],
                "score": match[1],
                "origem": "produto",
            }
        return None

    def identify(self, text: str, threshold: int = 85):
        query = self._clean_query(text)
        if not query:
            return None

        is_combination = any(token in text.lower() for token in ["+", " e ", " com "])

        if is_combination:
            match = self._match_substances(query, self.combination_lookup, threshold)
            if match:
                return match

        if query in self.product_lookup:
            return self.product_lookup[query]

        if query in self.substance_lookup:
            return {
                "substancia": self.substance_lookup[query],
                "produto": None,
                "score": 100.0,
                "origem": "substancia",
            }

        match = self._match_substances(query, self.single_lookup, threshold)
        if match:
            return match

        match = self._match_products(query, threshold)
        if match:
            return match

        return self._match_substances(query, self.combination_lookup, threshold)
