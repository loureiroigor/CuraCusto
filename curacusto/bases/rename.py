import re
from pathlib import Path

import pandas as pd
import pdfplumber

from curacusto.config import PROCESSED_DIR, RAW_DIR

RENAME_PDF = RAW_DIR / "rename_2024.pdf"
RENAME_CSV = PROCESSED_DIR / "rename.csv"

START_PAGE = 25
END_PAGE = 231

ATC_PATTERN = re.compile(r"^[A-Z]\d{2}[A-Z]{2}\d{2}$")


def _clean(value) -> str:
    return (value or "").replace("\n", " ").strip()


def extract_rename(pdf_path: Path = RENAME_PDF) -> pd.DataFrame:
    rows = []
    current_dcb = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[START_PAGE:END_PAGE]:
            for table in page.extract_tables():
                for row in table:
                    if not row or len(row) < 5:
                        continue
                    dcb, concentracao, forma, componente, codigo = [
                        _clean(cell) for cell in row[:5]
                    ]
                    if dcb.lower().startswith("denomina"):
                        continue
                    if dcb:
                        current_dcb = dcb
                    if not current_dcb:
                        continue
                    atc = codigo if ATC_PATTERN.match(codigo) else None
                    rows.append(
                        {
                            "dcb": current_dcb,
                            "concentracao": concentracao,
                            "forma": forma,
                            "componente": componente,
                            "atc": atc,
                        }
                    )

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["dcb", "concentracao", "forma"])
    return df.reset_index(drop=True)


def save_rename_csv(df: pd.DataFrame, path: Path = RENAME_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
