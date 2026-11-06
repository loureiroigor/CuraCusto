# Cura Custo

Aplicação web para comparação de preços de medicamentos e otimização de receitas médicas.

## Estrutura

- `docs/`: texto do artigo
- `curacusto/`: código-fonte
- `data/`: bases baixadas e banco SQLite (não versionados)
- `tests/`: testes

## Requisitos

- Python 3.11+

## Instalação

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução

```powershell
streamlit run app.py
```
