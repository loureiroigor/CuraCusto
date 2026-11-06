import time

import pandas as pd

from curacusto.collectors import build_collectors
from curacusto.config import CACHE_TTL_HOURS, PROCESSED_DIR
from curacusto.engine import analyze_recipe
from curacusto.normalizer import Catalog
from curacusto.storage import Cache

CENARIOS = {
    "Hipertensão + dor": [
        "Losartana 50mg",
        "Hidroclorotiazida 25mg",
        "Diclofenaco 50mg",
    ],
    "Diabetes + inflamação": [
        "Metformina 500mg",
        "Sinvastatina 20mg",
        "Nimesulida 100mg",
    ],
    "Alergia + dor": [
        "Cetirizina 10mg",
        "Orfenadrina 35mg",
        "Domperidona 10mg",
    ],
}


def resumir(nome: str, resultados, duracao: float) -> dict:
    total = len(resultados)
    identificados = sum(1 for item in resultados if item.substancia)
    gratuitos = sum(1 for item in resultados if item.in_rename)
    pagos = [
        item
        for item in resultados
        if not item.in_rename and item.best_offer and item.pmc_ms
    ]
    custo = sum(item.best_offer.price for item in pagos)
    total_pmc = sum(item.pmc_ms for item in pagos)
    economia = max(total_pmc - custo, 0)

    return {
        "cenario": nome,
        "itens": total,
        "identificados": identificados,
        "cobertura_pct": round(identificados / total * 100, 1) if total else 0,
        "gratuitos_sus": gratuitos,
        "itens_com_preco": len(pagos),
        "custo_otimizado": round(custo, 2),
        "total_pmc": round(total_pmc, 2),
        "economia_vs_pmc": round(economia, 2),
        "economia_pct": round(economia / total_pmc * 100, 1) if total_pmc else 0,
        "alertas_pmc": sum(1 for item in resultados if item.above_pmc),
        "duracao_s": round(duracao, 1),
    }


def main() -> None:
    cmed = pd.read_csv(PROCESSED_DIR / "cmed.csv")
    rename = pd.read_csv(PROCESSED_DIR / "rename.csv")
    catalog = Catalog(cmed)
    cache = Cache()
    collectors = build_collectors()

    resumos = []
    linhas = []

    for nome, itens in CENARIOS.items():
        inicio = time.time()
        resultados = analyze_recipe(
            itens,
            catalog,
            cmed,
            rename,
            collectors,
            cache,
            CACHE_TTL_HOURS,
        )
        duracao = time.time() - inicio
        resumos.append(resumir(nome, resultados, duracao))

        for resultado in resultados:
            linhas.append(
                {
                    "cenario": nome,
                    "medicamento": resultado.text,
                    "substancia": resultado.substancia,
                    "gratuito_sus": resultado.in_rename,
                    "pmc_ms": resultado.pmc_ms,
                    "melhor_farmacia": (
                        resultado.best_offer.store if resultado.best_offer else None
                    ),
                    "melhor_preco": (
                        resultado.best_offer.price if resultado.best_offer else None
                    ),
                    "acima_pmc": resultado.above_pmc,
                }
            )
        print(f"[{nome}] concluído em {duracao:.1f}s")

    resumo_df = pd.DataFrame(resumos)
    detalhe_df = pd.DataFrame(linhas)
    resumo_df.to_csv(
        PROCESSED_DIR / "resumo_cenarios.csv",
        index=False,
        encoding="utf-8",
    )
    detalhe_df.to_csv(
        PROCESSED_DIR / "detalhe_cenarios.csv",
        index=False,
        encoding="utf-8",
    )

    print(resumo_df.to_string(index=False))
    print(f"Arquivos salvos em {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
