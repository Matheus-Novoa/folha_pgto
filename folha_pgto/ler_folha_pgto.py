import pdfplumber
import re
from utils import comparar_nomes, montar_tabela_final
from customtkinter import filedialog
from pathlib import Path
from pyautogui import alert
import pandas as pd


arquivo = Path(filedialog.askopenfilename())

pasta_atual = Path(__file__).parent
# Procurar pelo arquivo na pasta atual e em subpastas
arquivo_planilha = next(pasta_atual.rglob('Empregados.xlsx'), None)
dadosFuncionarios = pd.read_excel(arquivo_planilha, 'dados')
dadosFuncionarios['Nome'] = dadosFuncionarios['Nome'].str.strip()

try:
    padraoNome = r"(Nome\s+do\s+Destinat[á-ú]rio:)(\s.*)"
    padraoValor = r'(Valor:.*)(R\$\s+)(\d+\,\d+)'

    padraoNome2 = r"(Correntista\s+de\s+Cr[á-ú]dito)(\s.*)"
    padraoValor2 = r'(Valor.*)(R\$\s+)(\d+\.?\d+\,\d+)'

    with pdfplumber.open(arquivo) as pdf:
        paginas = [page.extract_text() for page in pdf.pages]

    with open('teste.txt', 'w') as f:
        f.write('\n'.join(paginas))

    nomes = []
    valores = []
    for n, pagina in enumerate(paginas):
        if 'Folha de Pagamento' not in pagina:
            raise
        buscaNome = re.search(padraoNome, pagina)
        buscaValor = re.search(padraoValor, pagina)
        if not buscaNome:
            try:
                buscaNome = re.search(padraoNome2, pagina)
                buscaValor = re.search(padraoValor2, pagina)

                nomeDestinatario = buscaNome.group(2).strip()
                print(nomeDestinatario)
                valor = buscaValor.group(3).strip()

                nomes.append(nomeDestinatario)
                valores.append(valor)
                continue
            except AttributeError:
                alert(f'Padrão não encontrado na página {n}')
                continue
        
        nomeDestinatario = buscaNome.group(2).strip()
        valor = buscaValor.group(3).strip()

        nomes.append(nomeDestinatario)
        valores.append(valor)

    dados = {'Nome': nomes, 'Valor': valores}
    tabelaDados = pd.DataFrame(dados)
except:
    with pdfplumber.open(arquivo) as pdf:
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

tabelaFinal = montar_tabela_final(dadosFuncionarios, tabelaDados, arquivo.parent)
tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()

with open(arquivo.parent / 'resultado.txt', 'w') as f:
    f.write(tabelaDistincao.to_string())
