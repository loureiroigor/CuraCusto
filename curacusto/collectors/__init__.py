from curacusto.collectors.vtex import VtexCollector
from curacusto.config import REQUEST_DELAY_SECONDS, STORES


def build_collectors(delay: float = REQUEST_DELAY_SECONDS) -> dict[str, VtexCollector]:
    return {
        name: VtexCollector(name, base_url, delay=delay)
        for name, base_url in STORES.items()
    }
