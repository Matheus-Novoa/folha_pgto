import pdfplumber
import re
from validador_nomes import comparar_nomes
import pandas as pd


dadosFuncionarios = pd.read_excel('folha_pgto\Empregados.xls', 'dados')
dadosFuncionarios['Nome'] = dadosFuncionarios['Nome'].str.strip()

arquivo = "folha_pgto\CCO_000003.pdf"
with pdfplumber.open(arquivo) as pdf:
    textoBruto = ''
    for page in pdf.pages:
        textoBruto += page.extract_text()

padrao = r'(\d{2}/\d{2}/\d{4})\s+(\d{1,3}(?:\.\d{3})*,\d{2})(\(cid:9\)|\s)([^\d(]*)'
dados = re.findall(padrao, textoBruto)

paresNomeValor = {linha[-1].strip():[linha[1]] for linha in dados}

tabelaDados = pd.DataFrame(paresNomeValor).T.reset_index()
tabelaDados.columns = ['Nome', 'Valor']

validacao = comparar_nomes(tabelaDados['Nome'].tail(7), dadosFuncionarios['Nome'])
tabelaDados['Nome'] = tabelaDados['Nome'].map(validacao)

tabelaFinal = pd.merge(dadosFuncionarios, tabelaDados, on='Nome')
tabelaFinal.drop_duplicates(inplace=True)
tabelaFinal.reset_index(drop=True,inplace=True)

tabelaFinal['Valor'] = (tabelaFinal['Valor']
                        .str.replace('.','')
                        .str.replace(',', '.')
                        .astype('float32')
                        .apply(round, args=(2,))
                        )

tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()
print(tabelaDistincao)
