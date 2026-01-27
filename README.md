# Robô para Leitura de PDF de Folha de Pagamento

O robô automatiza a extração de dados de folhas de pagamento em PDF, aplicando extração de texto, OCR quando necessário, e regras para normalização e validação dos campos.

## Objetivo

- Extrair automaticamente informações relevantes de folhas de pagamento em PDF e consolidá-las em uma planilha estruturada (Excel).
- Aplicar OCR (quando o PDF não contém texto), expressões regulares e heurísticas de matching para mapear valores aos funcionários.
- Gerar uma saída pronta para análise e integração (arquivo `.xlsx`) contendo colunas normalizadas como nome, matrícula, rubricas e valores.

## Instalação

- Requisitos: Python 3.12+ e `pip` (ou gerenciador de sua preferência). Verifique dependências em `pyproject.toml`.
- Instale dependências Python com o comando (na raiz do projeto):

```bash
pip install .
```

## Como executar o robô

- Crie um arquivo `.env` na raiz com sua chave de API Groq (veja `.env.example`). Exemplo de variável necessária: `GROQ_API_KEY`.
- Para executar a interface web (recomendada):

```bash
streamlit run folha_pgto/app.py
```

- Para executar o processamento como script (sem UI):

```bash
python folha_pgto/ler_folha_pgto.py
```

- Faça upload do PDF pela interface; o robô processará e oferecerá o arquivo Excel resultante para download. Consulte os logs para depuração.

## Observações

- O projeto usa serviços de LLM (Groq), certifique-se de fornecer `GROQ_API_KEY` no `.env` antes de iniciar a aplicação.