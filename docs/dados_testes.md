# Dados dos Testes — Cura Custo

## Ambiente e fontes

- Python 3.11.9, Streamlit, SQLite.
- CMED/ANVISA: lista PMC publicada em 09/10/2026, coluna de ICMS 17% (Mato Grosso do Sul).
- RENAME 2024 (2ª edição): 1.017 registros normalizados, 544 DCBs distintos.
- Farmácias consultadas: Pague Menos e Pacheco, via endpoint público de catálogo VTEX.
- Data dos testes: 06/11/2026.

## Definições das métricas

- **Cobertura**: itens identificados pelo normalizador divididos pelo total de itens.
- **Gratuitos no SUS**: itens cujo princípio ativo (DCB) consta na RENAME.
- **Itens com preço**: itens pagos para os quais ao menos uma oferta foi coletada.
- **Custo otimizado**: soma do menor preço encontrado para cada item pago.
- **Total PMC**: soma do PMC (teto de MS) das apresentações correspondentes aos itens pagos.
- **Economia vs PMC**: diferença entre o total PMC e o custo otimizado, em valor absoluto e percentual.
- **Alertas PMC**: ofertas coletadas acima do teto legal.
- **Duração**: tempo de execução do cenário (com uso de cache quando indicado).

## Resumo por cenário

| Cenário | Itens | Cobertura | Gratuitos SUS | Itens com preço | Custo otimizado | Total PMC | Economia vs PMC | % | Alertas | Duração |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hipertensão + dor | 3 | 100% | 2 | 1 | R$ 6,69 | R$ 58,20 | R$ 51,51 | 88,5% | 0 | 6,1 s |
| Diabetes + inflamação | 3 | 100% | 2 | 1 | R$ 3,99 | R$ 77,51 | R$ 73,52 | 94,9% | 0 | 0,4 s |
| Alergia + dor | 3 | 100% | 0 | 3 | R$ 52,57 | R$ 258,37 | R$ 205,80 | 79,7% | 0 | 0,6 s |

## Detalhe por item

| Cenário | Medicamento | DCB identificado | SUS | PMC MS | Melhor farmácia | Melhor preço | Acima do PMC |
|---|---|---|---:|---:|---|---:|---:|
| Hipertensão + dor | Losartana 50mg | Losartana potássica | Sim | — | — | — | Não |
| Hipertensão + dor | Hidroclorotiazida 25mg | Hidroclorotiazida | Sim | — | — | — | Não |
| Hipertensão + dor | Diclofenaco 50mg | Diclofenaco potássico | Não | R$ 58,20 | Pague Menos | R$ 6,69 | Não |
| Diabetes + inflamação | Metformina 500mg | Cloridrato de metformina | Sim | — | — | — | Não |
| Diabetes + inflamação | Sinvastatina 20mg | Sinvastatina | Sim | — | — | — | Não |
| Diabetes + inflamação | Nimesulida 100mg | Nimesulida | Não | R$ 77,51 | Pacheco | R$ 3,99 | Não |
| Alergia + dor | Cetirizina 10mg | Dicloridrato de cetirizina | Não | R$ 92,33 | Pacheco | R$ 35,99 | Não |
| Alergia + dor | Orfenadrina 35mg | Citrato de orfenadrina | Não | R$ 127,39 | Pacheco | R$ 5,99 | Não |
| Alergia + dor | Domperidona 10mg | Domperidona | Não | R$ 38,65 | Pague Menos | R$ 10,59 | Não |

## Observações

- O primeiro cenário foi executado com coleta ao vivo (cerca de 6 s); os demais aproveitaram o cache local, por isso a duração menor.
- Nenhuma oferta acima do PMC foi identificada nos cenários avaliados (alertas = 0).
- A economia é calculada em relação ao teto legal (PMC), não ao preço de mercado.
- A RENAME cobre integralmente os medicamentos de hipertensão e diabetes utilizados nos cenários, o que reforça o papel assistencial do sistema.

## Telas sugeridas para captura

1. Tela inicial: formulário de receita e barra lateral (UF/MS, ICMS 17%, farmácias e cache).
2. Resultado de "Hipertensão + dor": dois itens gratuitos no SUS e um item pago.
3. Resultado de "Alergia + dor": três itens pagos, com comparação entre as duas redes.
4. Detalhamento expandido de um item, exibindo as ofertas por farmácia e os links.

## Como executar

```powershell
.\.venv\Scripts\Activate.ps1
python -m scripts.atualizar_bases
streamlit run app.py
```
