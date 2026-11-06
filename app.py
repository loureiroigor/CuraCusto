import pandas as pd
import streamlit as st

from curacusto.collectors import build_collectors
from curacusto.config import CACHE_TTL_HOURS, PROCESSED_DIR
from curacusto.engine import analyze_recipe
from curacusto.normalizer import Catalog
from curacusto.storage import Cache

st.set_page_config(
    page_title="Cura Custo",
    page_icon="ðŸ’Š",
    layout="wide",
)


@st.cache_data
def load_bases():
    cmed_path = PROCESSED_DIR / "cmed.csv"
    rename_path = PROCESSED_DIR / "rename.csv"
    if not cmed_path.exists() or not rename_path.exists():
        return None, None
    return pd.read_csv(cmed_path), pd.read_csv(rename_path)


@st.cache_resource
def load_catalog():
    cmed, _ = load_bases()
    return Catalog(cmed)


def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_sidebar() -> None:
    with st.sidebar:
        st.header("ConfiguraÃ§Ã£o")
        st.write("UF: **MS**")
        st.write("ICMS: **17%**")
        st.write("FarmÃ¡cias: **Pague Menos** e **Pacheco**")
        st.write(f"Cache: **{CACHE_TTL_HOURS} h**")
        st.divider()
        st.caption("Fontes: CMED/ANVISA e RENAME 2024")
        st.caption("Projeto de extensÃ£o â€” ODS 3 e ODS 10")


def render_summary(resultados) -> None:
    total = len(resultados)
    gratuitos = sum(1 for item in resultados if item.in_rename)
    nao_identificados = sum(1 for item in resultados if not item.substancia)
    alertas = sum(1 for item in resultados if item.above_pmc)

    pagos = [
        item
        for item in resultados
        if not item.in_rename and item.best_offer and item.pmc_ms
    ]
    custo = sum(item.best_offer.price for item in pagos)
    total_pmc = sum(item.pmc_ms for item in pagos)
    economia = max(total_pmc - custo, 0)
    percentual = (economia / total_pmc * 100) if total_pmc else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Itens", total)
    col2.metric("Gratuitos no SUS", gratuitos)
    col3.metric("Custo otimizado", format_brl(custo))
    col4.metric("Economia vs teto PMC", format_brl(economia), f"{percentual:.1f}%")

    if pagos:
        st.caption(
            "Economia calculada em relaÃ§Ã£o ao PMC (teto legal), nÃ£o ao preÃ§o de mercado."
        )

    if alertas:
        st.warning(f"{alertas} oferta(s) acima do PMC. Confira os detalhes.")
    if nao_identificados:
        st.warning(
            f"{nao_identificados} item(ns) nÃ£o identificado(s). Revise a grafia."
        )


def render_table(resultados) -> None:
    rows = []
    for item in resultados:
        if item.in_rename:
            onde = "SUS / FarmÃ¡cia Popular"
        elif item.best_offer:
            onde = item.best_offer.store
        else:
            onde = "â€”"

        if item.above_pmc:
            status = "Acima do PMC"
        elif item.in_rename:
            status = "Gratuito"
        elif item.substancia:
            status = "OK"
        else:
            status = "NÃ£o identificado"

        rows.append(
            {
                "Medicamento": item.text,
                "PrincÃ­pio ativo (DCB)": item.substancia or "â€”",
                "Onde obter": onde,
                "PMC MS": "â€”" if item.in_rename or not item.pmc_ms else format_brl(item.pmc_ms),
                "Melhor preÃ§o": (
                    format_brl(item.best_offer.price) if item.best_offer else "â€”"
                ),
                "Status": status,
            }
        )

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_details(resultados) -> None:
    st.subheader("Detalhamento")
    for item in resultados:
        with st.expander(f"{item.text} â€” {item.substancia or 'nÃ£o identificado'}"):
            if item.in_rename:
                st.success("DisponÃ­vel gratuitamente pelo SUS (RENAME).")

            if item.offers:
                tabela = pd.DataFrame(
                    [
                        {
                            "FarmÃ¡cia": offer.store,
                            "PreÃ§o": format_brl(offer.price),
                            "ApresentaÃ§Ã£o": offer.presentation,
                            "Link": offer.url,
                        }
                        for offer in sorted(
                            item.offers,
                            key=lambda offer: offer.price or 0,
                        )[:10]
                    ]
                )
                st.dataframe(tabela, width="stretch", hide_index=True)
            elif not item.in_rename:
                st.info("Nenhuma oferta coletada no momento.")


def main() -> None:
    st.title("Cura Custo")
    st.caption("Comparador de preÃ§os e otimizador de receitas mÃ©dicas")

    cmed, rename = load_bases()
    if cmed is None:
        st.error(
            "Bases nÃ£o encontradas. Execute `python -m scripts.atualizar_bases`."
        )
        return

    catalog = load_catalog()
    cache = Cache()
    collectors = build_collectors()

    render_sidebar()

    with st.form("receita"):
        texto = st.text_area(
            "Medicamentos da receita (um por linha)",
            height=160,
            placeholder="Losartana 50mg\nMetformina 500mg\nDiclofenaco 50mg",
        )
        enviado = st.form_submit_button("Analisar receita")

    if enviado and texto.strip():
        itens = [linha.strip() for linha in texto.splitlines() if linha.strip()]
        with st.spinner("Consultando bases e farmÃ¡cias..."):
            st.session_state["resultados"] = analyze_recipe(
                itens,
                catalog,
                cmed,
                rename,
                collectors,
                cache,
                CACHE_TTL_HOURS,
            )

    resultados = st.session_state.get("resultados")
    if not resultados:
        st.info("Digite os medicamentos da receita e clique em Analisar.")
        return

    render_summary(resultados)
    render_table(resultados)
    render_details(resultados)

    st.divider()
    st.caption(
        "Ferramenta informativa. NÃ£o substitui a orientaÃ§Ã£o mÃ©dica ou farmacÃªutica."
    )


if __name__ == "__main__":
    main()

