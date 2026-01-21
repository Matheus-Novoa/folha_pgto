import pdfplumber
import re
from utils import comparar_nomes, montar_tabela_final
from pathlib import Path
import logging
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# EMPREGADOS_PATH = Path(__file__).resolve().parent / 'Empregados.xlsx'
plan_empregados_link = 'https://docs.google.com/spreadsheets/d/1D-eZ4jAbmAtoJ7noeJBY65cr25ufBCp9/export?format=csv'

def process_pdf(pdf_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    logger.info(f"Iniciando processamento do arquivo PDF: {pdf_path}")
    if not plan_empregados_link:
        logger.error("Link da planilha de empregados não encontrado")
        raise FileNotFoundError('Empregados.xlsx não encontrado')
    
    logger.debug("Carregando dados dos funcionários da planilha online")
    dadosFuncionarios = pd.read_csv(plan_empregados_link)
    dadosFuncionarios['Nome'] = dadosFuncionarios['Nome'].str.strip()
    logger.info(f"Dados de {len(dadosFuncionarios)} funcionários carregados")

    try:
        logger.debug("Definindo padrões de expressão regular para extração")
        padraoNome = r"(Nome\s+do\s+Destinat[á-ú]rio:)(\s.*)"
        padraoValor = r'(Valor:.*)(R\$\s+)(\d+\,\d+)'

        padraoNome2 = r"(Correntista\s+de\s+Cr[á-ú]dito)(\s.*)"
        padraoValor2 = r'(Valor.*)(R\$\s+)(\d+\.?\d+\,\d+)'

        logger.debug("Abrindo arquivo PDF para extração de texto")
        with pdfplumber.open(pdf_path) as pdf:
            paginas = [page.extract_text() for page in pdf.pages]
        logger.info(f"PDF carregado com {len(paginas)} páginas")

        nomes = []
        valores = []
        for n, pagina in enumerate(paginas):
            if 'Folha de Pagamento' not in pagina:
                logger.error(f"Página {n+1} não contém o cabeçalho 'Folha de Pagamento'")
                raise ValueError('O conteudo do arquivo não é uma folha de pagamento')
            buscaNome = re.search(padraoNome, pagina)
            buscaValor = re.search(padraoValor, pagina)
            if not buscaNome:
                try:
                    logger.debug(f"Tentando padrão alternativo para página {n+1}")
                    buscaNome = re.search(padraoNome2, pagina)
                    buscaValor = re.search(padraoValor2, pagina)

                    nomeDestinatario = buscaNome.group(2).strip()
                    valor = buscaValor.group(3).strip()

                    nomes.append(nomeDestinatario)
                    valores.append(valor)
                    logger.debug(f"Dados extraídos com padrão alternativo: {nomeDestinatario}")
                    continue
                except AttributeError:
                    logger.warning(f"Nenhum padrão encontrado na página {n+1}")
                    st.warning(f'Padrão não encontrado na página {n+1}')
                    continue
            
            nomeDestinatario = buscaNome.group(2).strip()
            valor = buscaValor.group(3).strip()

            nomes.append(nomeDestinatario)
            valores.append(valor)
            logger.debug(f"Dados extraídos com padrão principal: {nomeDestinatario}")

        dados = {'Nome': nomes, 'Valor': valores}
        tabelaDados = pd.DataFrame(dados)
        logger.info(f"Primeira tentativa de extração concluída: {len(tabelaDados)} registros encontrados")
    except Exception as e:
        logger.warning(f"Primeira tentativa falhou, tentando método alternativo. Erro: {str(e)}")
        with pdfplumber.open(pdf_path) as pdf:
            textoBruto = ''
            for page in pdf.pages:
                textoBruto += page.extract_text()
        logger.debug("Texto bruto extraído para processamento alternativo")

        padrao = re.compile(
            r"\d{2}/\d{2}/\d{4}\s*(?:\(cid:9\))?\s+"     # Data (não capturada)
            r"(\d{1,3}(?:[.:]\d{3})*,\d{2})\s*"          # Grupo 1: Valor
            r"((?:[A-ZÀ-ÿ]+\s*(?:\(cid:9\)\s*)?)+?)"     # Grupo 2: Nome completo
            r"(?=(?:\(cid:9\))?\s*\d{3,})"               # Lookahead para o código da agência
        )
        dados = re.findall(padrao, textoBruto)
        logger.debug(f"Encontrados {len(dados)} registros no método alternativo")
        
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
        logger.info(f"Método alternativo concluído: {len(tabelaDados)} registros processados")

    logger.debug("Iniciando validação e comparação de nomes")
    validacao = comparar_nomes(tabelaDados['Nome'], dadosFuncionarios['Nome'])
    tabelaDados['Nome'] = tabelaDados['Nome'].map(validacao)
    logger.info("Nomes validados e corrigidos")

    logger.debug("Montando tabela final")
    tabelaFinal = montar_tabela_final(dadosFuncionarios, tabelaDados)
    tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()
    logger.info(f"Processamento concluído. Tabela final com {len(tabelaFinal)} registros em {len(tabelaDistincao)} centros de custo")

    return tabelaFinal, tabelaDistincao


if __name__ == "__main__":
    t = process_pdf(r"C:\Users\novoa\Downloads\CCO_000061.pdf")
