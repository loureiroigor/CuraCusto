from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = DATA_DIR / "curacusto.db"

UF = "MS"
ICMS_ALIQUOTA = 0.17

USER_AGENT = "CuraCusto/0.1 (projeto academico de extensao)"
REQUEST_DELAY_SECONDS = 2.0
CACHE_TTL_HOURS = 24
