import pdfplumber
import re
from utils import comparar_nomes, montar_tabela_final
from pathlib import Path
import pandas as pd
import streamlit as st


# EMPREGADOS_PATH = Path(__file__).resolve().parent / 'Empregados.xlsx'
plan_empregados_link = 'https://docs.google.com/spreadsheets/d/1D-eZ4jAbmAtoJ7noeJBY65cr25ufBCp9/export?format=csv'

def process_pdf(pdf_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    if not plan_empregados_link:
        raise FileNotFoundError('Empregados.xlsx não encontrado')
    
    dadosFuncionarios = pd.read_csv(plan_empregados_link)
    dadosFuncionarios['Nome'] = dadosFuncionarios['Nome'].str.strip()

    try:
        padraoNome = r"(Nome\s+do\s+Destinat[á-ú]rio:)(\s.*)"
        padraoValor = r'(Valor:.*)(R\$\s+)(\d+\,\d+)'

        padraoNome2 = r"(Correntista\s+de\s+Cr[á-ú]dito)(\s.*)"
        padraoValor2 = r'(Valor.*)(R\$\s+)(\d+\.?\d+\,\d+)'

        with pdfplumber.open(pdf_path) as pdf:
            paginas = [page.extract_text() for page in pdf.pages]

        nomes = []
        valores = []
        for n, pagina in enumerate(paginas):
            if 'Folha de Pagamento' not in pagina:
                raise ValueError('O conteudo do arquivo não é uma folha de pagamento')
            buscaNome = re.search(padraoNome, pagina)
            buscaValor = re.search(padraoValor, pagina)
            if not buscaNome:
                try:
                    buscaNome = re.search(padraoNome2, pagina)
                    buscaValor = re.search(padraoValor2, pagina)

                    nomeDestinatario = buscaNome.group(2).strip()
                    valor = buscaValor.group(3).strip()

                    nomes.append(nomeDestinatario)
                    valores.append(valor)
                    continue
                except AttributeError:
                    st.warning(f'Padrão não encontrado na página {n+1}')
                    continue
            
            nomeDestinatario = buscaNome.group(2).strip()
            valor = buscaValor.group(3).strip()

            nomes.append(nomeDestinatario)
            valores.append(valor)

        dados = {'Nome': nomes, 'Valor': valores}
        tabelaDados = pd.DataFrame(dados)
    except:
        with pdfplumber.open(pdf_path) as pdf:
            textoBruto = ''
            for page in pdf.pages:
                textoBruto += page.extract_text()

        padrao = re.compile(
            r"\d{2}/\d{2}/\d{4}\s*(?:\(cid:9\))?\s+"     # Data (não capturada)
            r"(\d{1,3}(?:[.:]\d{3})*,\d{2})\s*"          # Grupo 1: Valor
            r"((?:[A-ZÀ-ÿ]+\s*(?:\(cid:9\)\s*)?)+?)"     # Grupo 2: Nome completo
            r"(?=(?:\(cid:9\))?\s*\d{3,})"               # Lookahead para o código da agência
        )
        dados = re.findall(padrao, textoBruto)
        
        dados_corrigidos = []
        for valor_bruto, nome_bruto in dados:
            # Corrige separadores de milhar
            valor_corrigido = valor_bruto.replace('.', '').replace(':', '')
            # Remove '(cid:9)' do nome
            nome_limpo = re.sub(r'\(cid:9\)', '', nome_bruto).strip()
            dados_corrigidos.append((nome_limpo, valor_corrigido))

        paresNomeValor = {linha[0].strip():[linha[1]] for linha in dados_corrigidos}

        tabelaDados = pd.DataFrame(paresNomeValor).T.reset_index()
        tabelaDados.columns = ['Nome', 'Valor']

    validacao = comparar_nomes(tabelaDados['Nome'], dadosFuncionarios['Nome'])
    tabelaDados['Nome'] = tabelaDados['Nome'].map(validacao)

    tabelaFinal = montar_tabela_final(dadosFuncionarios, tabelaDados)
    tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()

    return tabelaFinal, tabelaDistincao
