import pdfplumber
import re
from utils import comparar_nomes, montar_tabela_final
import pandas as pd
from customtkinter import filedialog
from pathlib import Path



arquivo = Path(filedialog.askopenfilename())
dadosFuncionarios = pd.read_excel('folha_pgto/Empregados.xls', 'dados')
dadosFuncionarios['Nome'] = dadosFuncionarios['Nome'].str.strip()

with pdfplumber.open(arquivo) as pdf:
    textoBruto = ''
    for page in pdf.pages:
        textoBruto += page.extract_text()

padrao = r'(\d{2}/\d{2}/\d{4})\s+(\d{1,3}(?:\.\d{3})*,\d{2})(\(cid:9\)|\s)([^\d(]*)'
dados = re.findall(padrao, textoBruto)

paresNomeValor = {linha[-1].strip():[linha[1]] for linha in dados}

tabelaDados = pd.DataFrame(paresNomeValor).T.reset_index()
tabelaDados.columns = ['Nome', 'Valor']

validacao = comparar_nomes(tabelaDados['Nome'], dadosFuncionarios['Nome'])
tabelaDados['Nome'] = tabelaDados['Nome'].map(validacao)

tabelaFinal = montar_tabela_final(dadosFuncionarios, tabelaDados, arquivo.parent)

tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()

with open(arquivo.parent / 'resultado.txt', 'w') as f:
    f.write(tabelaDistincao.to_string())
