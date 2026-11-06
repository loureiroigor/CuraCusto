from curacusto.normalizer import Catalog, normalize_text


def test_normalize_text():
    assert normalize_text("  Losartana Potássica  ") == "losartana potassica"
    assert normalize_text("Cloridrato de Metformina") == "cloridrato de metformina"


def test_catalog_identifica_produto():
    import pandas as pd

    cmed = pd.DataFrame(
        {
            "substancia": [
                "LOSARTANA POTÁSSICA",
                "CLORIDRATO DE METFORMINA",
                "BESILATO DE ANLODIPINO;LOSARTANA POTÁSSICA",
            ],
            "produto": ["COZAAR", "GLIFAGE", "ANLODIPINO + LOSARTANA"],
        }
    )
    catalog = Catalog(cmed)

    assert catalog.identify("cozaar")["substancia"] == "LOSARTANA POTÁSSICA"
    assert catalog.identify("glifage")["substancia"] == "CLORIDRATO DE METFORMINA"
    assert catalog.identify("losartana 50mg")["substancia"] == "LOSARTANA POTÁSSICA"
