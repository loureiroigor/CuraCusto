# Cura Custo — Como executar

## Requisitos

- Python 3.11 ou superior.
- Windows, Linux ou macOS.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Gerar as bases (CMED + RENAME)

```powershell
python -m scripts.atualizar_bases
```

O comando baixa a planilha da CMED e o PDF da RENAME (se ainda não existirem) e gera:

- `data/processed/cmed.csv`
- `data/processed/rename.csv`
- `data/curacusto.db`

## Executar a aplicação

```powershell
streamlit run app.py
```

Acesse `http://localhost:8501`.

## Executar os testes

```powershell
python -m pytest -q
```

## Observação (Windows 11)

Se o Windows bloquear bibliotecas do pandas com a mensagem de "Controle de Aplicativo", desative o Smart App Control ou execute o projeto no WSL2.
