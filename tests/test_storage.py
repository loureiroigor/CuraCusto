from datetime import datetime, timezone

from curacusto.models import Offer
from curacusto.storage import Cache


def test_salva_e_recupera(tmp_path):
    cache = Cache(tmp_path / "teste.db")
    oferta = Offer(
        store="Loja",
        search_term="dipirona",
        product_name="Dipirona",
        brand="Marca",
        presentation="20 comprimidos",
        price=9.99,
        list_price=12.99,
        available=True,
        url="https://exemplo.com/dipirona/p",
        collected_at=datetime.now(timezone.utc),
    )

    cache.save_offers([oferta])
    recuperadas = cache.get_offers("Loja", "dipirona")

    assert len(recuperadas) == 1
    assert recuperadas[0].price == 9.99
    assert cache.is_fresh("Loja", "dipirona", 24)
