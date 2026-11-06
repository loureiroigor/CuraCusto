from datetime import datetime, timezone

from curacusto.collectors.vtex import VtexCollector


def test_parse_product_extrai_oferta():
    collector = VtexCollector("Loja", "https://exemplo.com")
    produto = {
        "productName": "Dipirona 500mg",
        "brand": "Marca X",
        "linkText": "dipirona-500mg",
        "items": [
            {
                "name": "Dipirona 500mg 20 comprimidos",
                "sellers": [
                    {
                        "commertialOffer": {
                            "Price": 9.99,
                            "ListPrice": 12.99,
                            "IsAvailable": True,
                        }
                    }
                ],
            }
        ],
    }

    ofertas = list(
        collector._parse_product(produto, "dipirona", datetime.now(timezone.utc))
    )

    assert len(ofertas) == 1
    assert ofertas[0].price == 9.99
    assert ofertas[0].list_price == 12.99
    assert ofertas[0].url == "https://exemplo.com/dipirona-500mg/p"
    assert ofertas[0].presentation == "Dipirona 500mg 20 comprimidos"
