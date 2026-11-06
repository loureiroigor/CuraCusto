from datetime import datetime, timezone

import pandas as pd

from curacusto.engine import (
    analyze_item,
    pack_size,
    pmc_for_substance,
    rename_match,
    search_term,
)
from curacusto.models import Offer


def test_pmc_usa_maior_valor_da_substancia():
    cmed = pd.DataFrame(
        {
            "substancia": ["LOSARTANA POTÁSSICA", "LOSARTANA POTÁSSICA"],
            "pmc_ms": [10.0, 25.0],
        }
    )
    assert pmc_for_substance(cmed, "losartana potássica") == 25.0


def test_rename_match_com_combinacao():
    rename = pd.DataFrame({"dcb": ["losartana potássica", "anlodipino"]})
    assert rename_match(rename, "BESILATO DE ANLODIPINO;LOSARTANA POTÁSSICA")
    assert not rename_match(rename, "DIPIRONA")


def test_pack_size():
    assert pack_size("50 MG COM REV CT BL AL PLAS TRANS X 20") == 20
    assert pack_size("50 MG COM REV CT 25 BL AL PLAS TRANS X 20") == 500
    assert pack_size("10 MG/G + 0,443 MG/G CREME") is None


def test_search_term_remove_sal():
    assert search_term("DICLOFENACO POTÁSSICO") == "diclofenaco"
    assert search_term("DICLORIDRATO DE CETIRIZINA") == "cetirizina"
    assert search_term("BESILATO DE ANLODIPINO;LOSARTANA POTÁSSICA") == (
        "anlodipino losartana"
    )


class FakeCatalog:
    def identify(self, text):
        return {
            "substancia": "TESTE",
            "produto": "TESTE",
            "score": 100.0,
            "origem": "produto",
        }


class FakeCollector:
    def search(self, term, limit=5):
        return [
            Offer(
                store="Fake",
                search_term=term,
                product_name="Teste 50mg",
                brand="Fake",
                presentation="Teste 50mg 20 comprimidos",
                price=99.0,
                list_price=None,
                available=True,
                url="https://exemplo.com/teste",
                collected_at=datetime.now(timezone.utc),
            )
        ]


class FakeCache:
    def is_fresh(self, store, term, ttl):
        return False

    def save_offers(self, offers):
        pass

    def get_offers(self, store, term):
        return []


def test_alerta_quando_preco_supera_pmc():
    cmed = pd.DataFrame(
        {
            "substancia": ["TESTE"],
            "apresentacao": ["50 MG COM X 20"],
            "pmc_ms": [10.0],
        }
    )
    rename = pd.DataFrame({"dcb": []})

    resultado = analyze_item(
        "teste 50mg",
        FakeCatalog(),
        cmed,
        rename,
        {"Fake": FakeCollector()},
        FakeCache(),
        24,
    )

    assert resultado.above_pmc is True
    assert resultado.pmc_ms == 10.0
