import sqlite3

import requests

from curacusto.bases.cmed import load_cmed
from curacusto.bases.rename import extract_rename, save_rename_csv
from curacusto.config import DB_PATH, PROCESSED_DIR, RAW_DIR

CMED_URL = (
    "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos/"
    "arquivos/lista_pmc__20261009_115232673.xlsx/@@download/file"
)
RENAME_URL = (
    "https://bvsms.saude.gov.br/bvs/publicacoes/"
    "relacao_nacional_medicamentos_2024_2ed.pdf"
)


def download_if_missing() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    arquivos = [
        (CMED_URL, "cmed_pmc.xlsx"),
        (RENAME_URL, "rename_2024.pdf"),
    ]
    for url, nome in arquivos:
        destino = RAW_DIR / nome
        if destino.exists():
            continue
        print(f"Baixando {nome}...")
        resposta = requests.get(url, timeout=180)
        resposta.raise_for_status()
        destino.write_bytes(resposta.content)
        print(f"{nome}: {len(resposta.content)} bytes")


def main() -> None:
    download_if_missing()
    cmed = load_cmed()
    cmed_path = PROCESSED_DIR / "cmed.csv"
    cmed.to_csv(cmed_path, index=False, encoding="utf-8")
    print(f"CMED: {len(cmed)} linhas -> {cmed_path}")

    rename = extract_rename()
    save_rename_csv(rename)
    print(f"RENAME: {len(rename)} linhas, {rename['dcb'].nunique()} DCBs")

    with sqlite3.connect(DB_PATH) as conn:
        cmed.to_sql("cmed", conn, if_exists="replace", index=False)
        rename.to_sql("rename", conn, if_exists="replace", index=False)
    print(f"Bases gravadas em {DB_PATH}")


if __name__ == "__main__":
    main()
