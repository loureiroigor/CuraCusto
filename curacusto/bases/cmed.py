from pathlib import Path

import pandas as pd

from curacusto.config import ICMS_ALIQUOTA, RAW_DIR

CMED_FILE = RAW_DIR / "cmed_pmc.xlsx"
PMC_COLUMN = f"PMC {int(ICMS_ALIQUOTA * 100)} %"

COLUMN_MAP = {
    "SUBSTÂNCIA": "substancia",
    "PRODUTO": "produto",
    "APRESENTAÇÃO": "apresentacao",
    "LABORATÓRIO": "laboratorio",
    "CÓDIGO GGREM": "ggrem",
    "TIPO DE PRODUTO (STATUS DO PRODUTO)": "tipo",
    "REGIME DE PREÇO": "regime",
    PMC_COLUMN: "pmc_ms",
}


def parse_pmc(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text in {"", "-", "nan"}:
        return None
    text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def load_cmed(path: Path = CMED_FILE) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Lista PMC", header=0)
    df.columns = [str(column).strip() for column in df.columns]
    df = df[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)

    for column in [
        "substancia",
        "produto",
        "apresentacao",
        "laboratorio",
        "tipo",
        "regime",
    ]:
        df[column] = (
            df[column].astype(str).str.strip().replace({"nan": None, "-": None})
        )

    df["pmc_ms"] = df["pmc_ms"].map(parse_pmc)
    df = df.dropna(subset=["substancia", "produto", "pmc_ms"])
    df = df[df["pmc_ms"] > 0]
    return df.reset_index(drop=True)
