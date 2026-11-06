import requests

ENDPOINTS = {
    "Pague Menos": "https://www.paguemenos.com.br/api/catalog_system/pub/products/search",
    "Pacheco": "https://www.drogariaspacheco.com.br/api/catalog_system/pub/products/search",
}

HEADERS = {"User-Agent": "CuraCusto/0.1 (projeto academico de extensao)"}


def extrair_preco(produto):
    for item in produto.get("items", []):
        for seller in item.get("sellers", []):
            oferta = seller.get("commertialOffer", {})
            preco = oferta.get("Price")
            if preco:
                return preco
    return None


def buscar(loja, url, termo):
    resposta = requests.get(
        url,
        params={"ft": termo, "_from": 0, "_to": 2},
        headers=HEADERS,
        timeout=30,
    )
    resposta.raise_for_status()
    resultados = []
    for produto in resposta.json():
        resultados.append((produto.get("productName"), extrair_preco(produto)))
    return resultados


for loja, url in ENDPOINTS.items():
    print(f"== {loja} ==")
    try:
        for nome, preco in buscar(loja, url, "dipirona"):
            print(f"  R$ {preco} | {nome}")
    except Exception as erro:
        print(f"  erro: {erro}")
